"""Review end-to-end screens step by step: walk a sub-epic by hand, run its browser story tests, list the steps whose
screen changed against the accepted run, record a verdict on each, and accept a reviewed run as the next baseline.

A run folder is `<project>/.sessions/<release>/e2e-test-results/<epic>/<sub-epic>/<run>/`: its `results.json` holds one
row per step (written by the step capture hook, or by `record_walked_step` on a walk), `screens/` its screenshots,
`review.json` its verdicts, and `changed.json` its summary. The one model of a run, its pixel check, its verdict rules,
and the reports are `harness/e2e_review/report/`, run through Node, which keeps each run's summary beside it after every
command; Python reads only that summary, so the health report never starts Node. This toolset is the seam an agent and
the cdd server call."""
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
BASELINE_FILE = "baseline.json"
# A run's summary, which the review's every command keeps beside the run, so reading the health report never runs Node.
SUMMARY_FILE = "changed.json"
STORY_TESTS = "story_tests"
# The board's Playwright config runs every browser story test under story_tests/ as its story-ui project.
PLAYWRIGHT_APP = Path("space") / "kanban" / "app"
REPORT_TOOL = Path(__file__).resolve().parent / "report"
WALK_VERDICTS = ("meets the intent", "misses the intent")
REVIEW_VERDICTS = ("intended", "regression caught", "missed by the tests", "noise")
# What the daily review's agent may do: read the screenshots, list the changed pairs, and record a verdict on each.
REVIEW_AGENT_TOOLS = "Read,mcp__plugin_cdd_cdd__e2e-review_changed_pairs,mcp__plugin_cdd_cdd__e2e-review_record_verdict"
AGENT_RUNS_OFF = "CDD_AGENT_RUNS_OFF"
# A run's folder is named for when it started, to the second: `run-` or `walk-` and this.
RUN_STAMP_FORMAT = "%Y-%m-%d-%H-%M-%S"


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
        self._install_packages()
        done = self._command([npx, "tsx", script, *args])
        if done.returncode != 0:
            raise E2eReviewRefused(self._reason(done, f"{script} failed"))
        return done.stdout

    def _install_packages(self) -> None:
        """Install the tool's packages from its package-lock the first time it runs in a folder that holds none, as a
        runtime pinned from a checkout does, since git keeps no node_modules; refused, naming the folder, when npm fails."""
        if (self.folder / "node_modules").is_dir():
            return
        npm = shutil.which("npm")
        if npm is None:
            raise E2eReviewRefused(f"npm is not on PATH, so the e2e review tool's packages cannot be installed in {self.folder}")
        done = self._command([npm, "ci", "--no-audit", "--no-fund"])
        if done.returncode != 0:
            raise E2eReviewRefused(f"the e2e review tool's packages did not install in {self.folder}: {self._reason(done, 'npm ci failed')}; run npm ci there")

    def _command(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, cwd=self.folder, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

    def _reason(self, done: subprocess.CompletedProcess[str], otherwise: str) -> str:
        """The line of the command's output that names its error, such as Node's ERR_MODULE_NOT_FOUND, rather than the
        last line, which for a crash of Node is only its version."""
        lines = [line.strip() for line in (done.stderr or done.stdout or "").splitlines() if line.strip()]
        named = next((line for line in lines if "Error" in line or "error" in line), None)
        return named or (lines[-1] if lines else otherwise)


class E2eRun:
    """One run of a sub-epic, walked by hand or run by its browser story tests, as its summary says it stands: the
    review's commands keep the summary beside the run, and this reads it once."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self._summary: dict | None = None

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
        return int(self.summary.get("steps", 0))

    @property
    @data_field
    def changed_steps(self) -> list[str]:
        """The steps whose screen changed against the accepted run, as the review last listed them."""
        return list(self.summary.get("changed_steps", []))

    @property
    @data_field
    def unjudged_steps(self) -> list[str]:
        """The changed steps with no verdict yet."""
        return list(self.summary.get("unjudged_steps", []))

    @property
    @data_field
    def review_id(self) -> str:
        """Names the run's review, so the chat raises each missed step's toast once."""
        return f"{self.sub_epic}/{self.name}"

    @property
    @data_field
    def missed_steps(self) -> list[str]:
        """The steps judged missed by the tests, and the walked or judged steps that miss the intent."""
        return list(self.summary.get("missed_steps", []))

    @property
    @data_field
    def report(self) -> Path:
        compare = self.folder / "compare.html"
        return compare if compare.exists() else self.folder / "report.html"

    @property
    def summary(self) -> dict:
        """The summary the review last kept beside the run, read once; empty before any command kept one."""
        if self._summary is None:
            file = self.folder / SUMMARY_FILE
            read = json.loads(file.read_text(encoding="utf-8")) if file.exists() else {}
            # A run reviewed before the summary was kept there holds only the keys of its changed steps.
            self._summary = read if isinstance(read, dict) else {"changed_steps": list(read)}
        return self._summary


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
        screenshot under the run folder's screens/ and call record_walked_step with the step's key (`Story › Scenario ›
        <number> <step text>`), its text, the screenshot, and meets the intent or misses the intent with the reason."""
        folder = self.sub_epic_folder(target) / f"walk-{self._stamp()}"
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
        name = f"run-{self._stamp()}"
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
        base = self.run_of(against).folder if against else self.baseline_of(found.folder.parent)
        for pair in pairs:
            pair["ours"] = str(found.folder / pair["ours"]) if pair.get("ours") else ""
            pair["theirs"] = str(base / pair["theirs"]) if pair.get("theirs") and base else ""
        return pairs

    @mcp
    @agent_tool
    def record_verdict(self, run: str, step: str, verdict: str, reason: str, cites: str = "", against: str = "") -> E2eRun:
        """Record the verdict on one step of run whose screen changed against the accepted run (or against, another run
        folder), with its reason: intended (cites the story or code change), regression caught (cites the failing
        test), missed by the tests, or noise."""
        if verdict not in REVIEW_VERDICTS:
            raise E2eReviewRefused(f"no review verdict {verdict!r}: give one of {', '.join(REVIEW_VERDICTS)}")
        found = self.run_of(run)
        args = ["verdict", str(found.folder), step, verdict, reason] + (["--cites", cites] if cites else [])
        args += ["--against", str(self.run_of(against).folder)] if against else []
        self._tool.run("review.ts", *args)
        return found

    @mcp
    @agent_tool
    def judge_step(self, run: str, step: str, verdict: str, reason: str) -> E2eRun:
        """The judge's verdict on one step a test ran, with its reason: meets the intent or misses the intent, as its
        screen shows what the step says or not. Judging it again replaces it."""
        return self._step_verdict("judge", run, verdict, "judge", step, verdict, reason)

    @mcp
    @agent_tool
    def record_walked_step(self, run: str, step: str, step_text: str, screenshot: str, verdict: str, reason: str) -> E2eRun:
        """Record one step of a walk by hand: its key, its Given, When or Then text, its screenshot (saved first, relative
        to the run folder), and meets the intent or misses the intent with the reason. Walking it again replaces it."""
        return self._step_verdict("walk", run, verdict, "walk-step", step, step_text, screenshot, verdict, reason)

    def _step_verdict(self, given_by: str, run: str, verdict: str, command: str, *arguments: str) -> E2eRun:
        """Write a meets-or-misses verdict on one step of run through review.ts's command, refused when verdict is not
        one of the walk verdicts; given_by names who gave it (the judge, or a walk by hand) in that refusal."""
        if verdict not in WALK_VERDICTS:
            raise E2eReviewRefused(f"no {given_by} verdict {verdict!r}: give one of {', '.join(WALK_VERDICTS)}")
        found = self.run_of(run)
        self._tool.run("review.ts", command, str(found.folder), *arguments)
        return found

    @mcp
    @agent_tool
    def accept(self, run: str, by: str) -> E2eRun:
        """The person accepts run as its sub-epic's baseline: refused while a changed step is not judged intended. Only the
        person accepts, so by names them."""
        found = self.run_of(run)
        self._tool.run("review.ts", "accept", str(found.folder), "--by", by)
        self.write_report(found)
        return found

    def latest(self) -> E2eRunReview | None:
        """The newest run under this project's results, each sub-epic it ran together; none before any run."""
        folders = [file.parent for file in self.results_root.glob(f"*/*/*/{RESULTS_FILE}")] if self.results_root.is_dir() else []
        if not folders:
            return None
        # Run names carry their start time, so a later name breaks a tie between runs written in the same instant.
        newest = max(folders, key=lambda folder: ((folder / RESULTS_FILE).stat().st_mtime, folder.name)).name
        return E2eRunReview(newest, [E2eRun(folder) for folder in sorted(folders) if folder.name == newest], self.results_root / "story-map.html")

    def baseline_of(self, sub_epic: Path) -> Path | None:
        """The folder of the run accepted as sub_epic's baseline; none before any run was accepted."""
        file = sub_epic / BASELINE_FILE
        return sub_epic / json.loads(file.read_text(encoding="utf-8"))["run"] if file.exists() else None

    def write_report(self, run: E2eRun, against: Path | None = None) -> None:
        """Write run's report pages, comparing its screens with the run in against when one is given."""
        self._tool.run("report.ts", str(run.folder), *(["--against", str(against)] if against else []))

    def _stamp(self) -> str:
        return datetime.now(timezone.utc).strftime(RUN_STAMP_FORMAT)


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
            baseline = self.review.baseline_of(run.folder.parent)
            if baseline is None:
                self.review.write_report(run)
                done.append(f"{run.sub_epic}: no accepted run yet, so nothing to compare; accept {run.name} to start")
                continue
            changed = self.review.changed_pairs(str(run.folder))
            self.review.write_report(run, baseline)
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
