"""Review end-to-end screens step by step: walk a sub-epic by hand, run its browser story tests, list the steps whose
screen changed against the accepted run, record a verdict on each, and accept a reviewed run as the next baseline.

A run folder is `<project>/.sessions/<release>/e2e-test-results/<epic>/<sub-epic>/<run>/`: its `results.json` holds one
row per step (written by the step capture hook, or by `record_verdict` on a walk), `screens/` its screenshots, and
`review.json` its verdicts. The pixel check, the verdict rules and the reports are `harness/e2e_review/report/`, run
through Node; this toolset is the seam an agent and the cdd server call."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, tool_subject
from harness.installation.data_class import data_field
from harness.mcp.mcp_annotations import long_call, mcp
from harness.process.process import BackgroundStart

RESULTS_FOLDER = "e2e-test-results"
RESULTS_FILE = "results.json"
REVIEW_FILE = "review.json"
BASELINE_FILE = "baseline.json"
# The keys of a run's changed steps, kept when the review lists them, so reading the health report never runs Node.
CHANGED_FILE = "changed.json"
STORY_TESTS = "story_tests"
# The board's Playwright config runs every browser story test under story_tests/ as its story-ui project.
PLAYWRIGHT_APP = Path("space") / "kanban" / "app"
REPORT_TOOL = Path(__file__).resolve().parent / "report"
WALK_VERDICTS = ("meets the intent", "misses the intent")
REVIEW_VERDICTS = ("intended", "regression caught", "missed by the tests", "noise")
# What the daily review's agent may do: read the screenshots, list the changed pairs, and record a verdict on each.
REVIEW_AGENT_TOOLS = "Read,mcp__plugin_cdd_cdd__e2e-review_changed_pairs,mcp__plugin_cdd_cdd__e2e-review_record_verdict"
AGENT_RUNS_OFF = "CDD_AGENT_RUNS_OFF"


class E2eReviewRefused(ValueError):
    """A call the review cannot do: no such run, no run to compare with, or a verdict the rules refuse."""


class ReportTool:
    """The boundary to `harness/e2e_review/report/`: its review and report commands, run with tsx."""

    def __init__(self, folder: Path = REPORT_TOOL) -> None:
        self.folder = folder

    def run(self, script: str, *args: str) -> str:
        npx = shutil.which("npx")
        if npx is None:
            raise E2eReviewRefused("npx is not on PATH, so the e2e review tool cannot run")
        done = subprocess.run([npx, "tsx", script, *args], cwd=self.folder, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", check=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if done.returncode != 0:
            raise E2eReviewRefused((done.stderr or done.stdout).strip().splitlines()[-1] if (done.stderr or done.stdout).strip() else f"{script} failed")
        return done.stdout


class E2eRun:
    """One run of a sub-epic: walked by hand or run by its browser story tests, with each step's row and verdicts."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder

    @property
    @data_field
    def run_folder(self) -> Path:
        return self.folder

    @property
    @data_field
    def name(self) -> str:
        return self.folder.name

    @property
    @data_field
    def sub_epic(self) -> str:
        return f"{self.folder.parent.parent.name}/{self.folder.parent.name}"

    @property
    @data_field
    def steps(self) -> int:
        return len(self.rows)

    @property
    @data_field
    def changed_steps(self) -> list[str]:
        """The steps whose screen changed against the accepted run, as the review last listed them."""
        file = self.folder / CHANGED_FILE
        return json.loads(file.read_text(encoding="utf-8")) if file.exists() else []

    @property
    @data_field
    def unjudged_steps(self) -> list[str]:
        """The changed steps with no verdict yet."""
        verdicts = self.verdicts
        return [key for key in self.changed_steps if key not in verdicts]

    @property
    @data_field
    def review_id(self) -> str:
        """Names the run's review, so the chat raises each missed step's toast once."""
        return f"{self.sub_epic}/{self.name}"

    @property
    @data_field
    def missed_steps(self) -> list[str]:
        """The steps judged missed by the tests, and the walked steps that miss the intent."""
        missed = [key for key, review in self.verdicts.items() if review.get("verdict") == "missed by the tests"]
        return missed + [row["key"] for row in self.rows if row.get("verdict") == "misses the intent"]

    @property
    @data_field
    def report(self) -> Path:
        compare = self.folder / "compare.html"
        return compare if compare.exists() else self.folder / "report.html"

    @property
    def rows(self) -> list[dict]:
        file = self.folder / RESULTS_FILE
        return json.loads(file.read_text(encoding="utf-8")) if file.exists() else []

    @property
    def verdicts(self) -> dict[str, dict]:
        file = self.folder / REVIEW_FILE
        return json.loads(file.read_text(encoding="utf-8")).get("pairs", {}) if file.exists() else {}

    def was_run_by_a_test(self, key: str) -> bool:
        return any(row["key"] == key and row.get("by") == "run by a test" for row in self.rows)

    def add_walked_step(self, key: str, step: str, screenshot: str, verdict: str, reason: str) -> None:
        """A step of a walk by hand: its screenshot, saved in the run folder, and its verdict. Walking it again replaces it."""
        if not (self.folder / screenshot).is_file():
            raise E2eReviewRefused(f"save the step's screenshot at {self.folder / screenshot} first")
        row = {"key": key, "step": step, "screenshot": screenshot, "by": "walked by hand", "verdict": verdict, "reason": reason}
        rows = [earlier for earlier in self.rows if earlier["key"] != key] + [row]
        (self.folder / RESULTS_FILE).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


class E2eRunReview:
    """One end-to-end run across every sub-epic it ran: the line the server health report shows. A step is named
    `<epic>/<sub-epic>: <step key>`, since step keys repeat only within a sub-epic."""

    def __init__(self, name: str, runs: list[E2eRun], story_map: Path) -> None:
        self._name = name
        self.runs = runs
        self._story_map = story_map

    @property
    @data_field
    def run(self) -> str:
        return self._name

    @property
    @data_field
    def sub_epics(self) -> int:
        return len(self.runs)

    @property
    @data_field
    def steps(self) -> int:
        return sum(run.steps for run in self.runs)

    @property
    @data_field
    def changed_steps(self) -> list[str]:
        return [f"{run.sub_epic}: {key}" for run in self.runs for key in run.changed_steps]

    @property
    @data_field
    def unjudged_steps(self) -> list[str]:
        return [f"{run.sub_epic}: {key}" for run in self.runs for key in run.unjudged_steps]

    @property
    @data_field
    def missed_steps(self) -> list[str]:
        return [f"{run.sub_epic}: {key}" for run in self.runs for key in run.missed_steps]

    @property
    @data_field
    def report(self) -> Path:
        """The e2e story map page, each sub-epic linked to its run's report."""
        return self._story_map

    @property
    @data_field
    def review_id(self) -> str:
        """Names the run, so the chat raises each missed step's toast once."""
        return self._name


@agent_toolset
class E2eReview:
    """Review end-to-end screens: walk a sub-epic by hand, run its browser story tests, judge each step whose screen
    changed against the accepted run, and accept a reviewed run as the baseline, as TDD's Reviewing e2e screens says."""

    def __init__(self, project: Path | str, release: str = "local", tool: ReportTool | None = None,
                 starter: Callable[[list[str], Path, dict[str, str], Path], int] | None = None) -> None:
        self.project = Path(project).resolve()
        self.release = release
        self._tool = tool or ReportTool()
        self._start = starter or _start_in_background

    @classmethod
    @tool_subject
    def load(cls, *, project: Path | str) -> E2eReview:
        """The end-to-end runs of project, the folder the call names, under its `.sessions/local/`."""
        return cls(project)

    @property
    def results_root(self) -> Path:
        return self.project / ".sessions" / self.release / RESULTS_FOLDER

    def sub_epic_folder(self, target: str) -> Path:
        """target is `<epic>/<sub-epic>`, as its story tests sit under story_tests/."""
        parts = [part for part in target.replace("\\", "/").strip("/").split("/") if part]
        if len(parts) != 2:
            raise E2eReviewRefused(f"name the sub-epic as <epic>/<sub-epic>, as under {STORY_TESTS}/: {target!r}")
        return self.results_root.joinpath(*parts)

    def run_of(self, run: str) -> E2eRun:
        """run is a run folder, or `<epic>/<sub-epic>/<run>` under this project's results."""
        folder = Path(run) if Path(run).is_absolute() else self.results_root / run
        if not folder.is_dir():
            raise E2eReviewRefused(f"no e2e run at {folder}")
        return E2eRun(folder)

    @mcp
    @agent_tool
    def walk(self, target: str) -> E2eRun:
        """Open a walk by hand of target, `<epic>/<sub-epic>`: a new run folder whose steps the agent records. Walk each
        scenario of the sub-epic's story markdown in the running app; after each Given, When and Then save the page's
        screenshot under the run folder's screens/ and call record_verdict with the step's key (`Story › Scenario ›
        <number> <step text>`), its text, the screenshot, and meets the intent or misses the intent with the reason."""
        folder = self.sub_epic_folder(target) / f"walk-{_stamp()}"
        (folder / "screens").mkdir(parents=True, exist_ok=True)
        (folder / RESULTS_FILE).write_text("[]\n", encoding="utf-8")
        return E2eRun(folder)

    @long_call
    @mcp
    @agent_tool
    def run(self, target: str) -> E2eRun:
        """Run target's browser story tests, `<epic>/<sub-epic>`, in the background, each step screenshotted into a new
        run folder; its results.json grows as the steps run. Compare it with changed_pairs once it has finished."""
        spec_folder = self.project / STORY_TESTS / target
        if not spec_folder.is_dir():
            raise E2eReviewRefused(f"no story tests at {spec_folder}")
        name = f"run-{_stamp()}"
        folder = self.sub_epic_folder(target) / name
        folder.mkdir(parents=True, exist_ok=True)
        env = {**os.environ, "E2E_RELEASE": self.release, "E2E_RUN": name}
        npx = shutil.which("npx") or "npx"
        self._start([npx, "playwright", "test", "--project=story-ui", f"{STORY_TESTS}/{target}"], self.project / PLAYWRIGHT_APP, env,
                    folder / "playwright.log")
        return E2eRun(folder)

    @mcp
    @agent_tool
    def changed_pairs(self, run: str, against: str = "") -> list[dict]:
        """The steps of run whose screen changed against the accepted run (or against, another run folder), each with
        both screenshots: what to judge. Read both images before giving a verdict."""
        found = self.run_of(run)
        args = ["pairs", str(found.folder)] + (["--against", str(self.run_of(against).folder)] if against else [])
        pairs = json.loads(self._tool.run("review.ts", *args))
        (found.folder / CHANGED_FILE).write_text(json.dumps([pair["key"] for pair in pairs], indent=2) + "\n", encoding="utf-8")
        base = self.run_of(against).folder if against else self._baseline_of(found.folder.parent)
        for pair in pairs:
            pair["ours"] = str(found.folder / pair["ours"]) if pair.get("ours") else ""
            pair["theirs"] = str(base / pair["theirs"]) if pair.get("theirs") and base else ""
        return pairs

    @mcp
    @agent_tool
    def record_verdict(self, run: str, step: str, verdict: str, reason: str, cites: str = "", step_text: str = "",
                       screenshot: str = "", against: str = "") -> E2eRun:
        """Record one step's verdict with its reason. On a walk: meets the intent or misses the intent, with step_text and
        screenshot (relative to the run folder). On a step a test ran, the same two are the judge's verdict: does its
        screen show what the step says. On a compared run: intended (cites the story or code change), regression caught
        (cites the failing test), missed by the tests, or noise."""
        found = self.run_of(run)
        if verdict in WALK_VERDICTS and found.was_run_by_a_test(step):
            self._tool.run("review.ts", "judge", str(found.folder), step, verdict, reason)
        elif verdict in WALK_VERDICTS:
            found.add_walked_step(step, step_text or step.split(" › ")[-1], screenshot, verdict, reason)
        elif verdict in REVIEW_VERDICTS:
            args = ["verdict", str(found.folder), step, verdict, reason] + (["--cites", cites] if cites else [])
            args += ["--against", str(self.run_of(against).folder)] if against else []
            self._tool.run("review.ts", *args)
        else:
            raise E2eReviewRefused(f"no verdict {verdict!r}: give one of {', '.join(WALK_VERDICTS + REVIEW_VERDICTS)}")
        return found

    @mcp
    @agent_tool
    def accept(self, run: str, by: str) -> E2eRun:
        """The person accepts run as its sub-epic's baseline: refused while a changed step is not judged intended. Only the
        person accepts, so by names them."""
        found = self.run_of(run)
        self._tool.run("review.ts", "accept", str(found.folder), "--by", by)
        self._tool.run("report.ts", str(found.folder))
        return found

    def latest(self) -> E2eRunReview | None:
        """The newest run under this project's results, each sub-epic it ran together; none before any run."""
        folders = [file.parent for file in self.results_root.glob(f"*/*/*/{RESULTS_FILE}")] if self.results_root.is_dir() else []
        if not folders:
            return None
        # Run names carry their start time, so a later name breaks a tie between runs written in the same instant.
        newest = max(folders, key=lambda folder: ((folder / RESULTS_FILE).stat().st_mtime, folder.name)).name
        return E2eRunReview(newest, [E2eRun(folder) for folder in sorted(folders) if folder.name == newest], self.results_root / "story-map.html")

    def _baseline_of(self, sub_epic: Path) -> Path | None:
        file = sub_epic / BASELINE_FILE
        return sub_epic / json.loads(file.read_text(encoding="utf-8"))["run"] if file.exists() else None


class ScheduledReview:
    """What the daily e2e run does after its tests end: list each sub-epic's changed pairs against its baseline, write
    the reports, and start a background agent session that judges the changed pairs."""

    RELEASE = "scheduled"

    def __init__(self, checkout: Path, run_name: str, review: E2eReview | None = None,
                 agent_start: Callable[[str, Path], None] | None = None) -> None:
        self.checkout = checkout
        self.run_name = run_name
        self.review = review or E2eReview(checkout, self.RELEASE)
        self._agent_start = agent_start or _start_review_agent

    @property
    def runs(self) -> list[E2eRun]:
        root = self.review.results_root
        return [E2eRun(folder) for folder in sorted(root.glob(f"*/*/{self.run_name}")) if (folder / RESULTS_FILE).exists()] if root.is_dir() else []

    def start(self) -> list[str]:
        """Write each run's reports, and start the agent on the runs whose screens changed; answer what was done."""
        done: list[str] = []
        to_judge: list[E2eRun] = []
        for run in self.runs:
            if self.review._baseline_of(run.folder.parent) is None:
                self.review._tool.run("report.ts", str(run.folder))
                done.append(f"{run.sub_epic}: no accepted run yet, so nothing to compare; accept {run.name} to start")
                continue
            changed = self.review.changed_pairs(str(run.folder))
            self.review._tool.run("report.ts", str(run.folder), "--against", str(self.review._baseline_of(run.folder.parent)))
            done.append(f"{run.sub_epic}: {len(changed)} changed step(s)")
            if changed:
                to_judge.append(run)
        if to_judge:
            self._agent_start(self.agent_prompt(to_judge), self.checkout)
            done.append(f"review agent started on {len(to_judge)} run(s)")
        return done

    def agent_prompt(self, runs: list[E2eRun]) -> str:
        folders = "\n".join(f"- {run.folder}" for run in runs)
        return ("Review the scheduled end-to-end run's screens, as cdd_guidance/practices/tdd/tdd.md 'Reviewing e2e screens' says. "
                f"For each run folder below call e2e-review changed_pairs, Read both screenshots of each pair, and call "
                f"record_verdict with one of intended (cite the commit on main since the baseline), regression caught (cite the "
                f"failing test), missed by the tests, or noise, each with its reason. Change no file and accept nothing: the fix "
                f"happens in a ticket, and only the person accepts a baseline.\n{folders}")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")


def _start_in_background(command: list[str], cwd: Path, env: dict[str, str], log_path: Path) -> int:
    with log_path.open("w", encoding="utf-8") as log:
        return BackgroundStart(log).run(command, cwd, env).pid


def _start_review_agent(prompt: str, checkout: Path) -> None:
    """A headless Claude Code session in checkout, allowed only to read screenshots and record verdicts."""
    if os.environ.get(AGENT_RUNS_OFF):
        return
    from harness.mcp.claude_plugins import ClaudePlugins

    claude = ClaudePlugins().claude_cli
    if claude is None:
        raise E2eReviewRefused("no Claude Code command line to start the review agent with")
    log = checkout / ".sessions" / ScheduledReview.RELEASE / RESULTS_FOLDER / "review-agent.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    _start_in_background([claude, "-p", prompt, "--allowedTools", REVIEW_AGENT_TOOLS], checkout, dict(os.environ), log)
