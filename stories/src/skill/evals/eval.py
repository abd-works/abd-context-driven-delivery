"""Unified evaluation runner for the stories skill.

Three tiers of eval in one entry point:

  1. `rules`     — Rule battery. For every rule with a scanner + evals/pass +
                   evals/fail, verify pass yields 0 violations and fail yields
                   exactly 1. Fast, mechanical, no AI required.

  2. `ai-judge`  — For every rule, invoke cursor-agent as a judge against the
                   fail fixture. The judge reads the rule.md and the fixture,
                   returns PASS/FAIL + reason. Complements the mechanical scanner
                   by catching things a regex or object walk can't see.

  3. `coarse`    — For every case under `stories/evals/<case>/`, invoke the
                   agent on a prompt + context, then run every scanner against
                   the merged workspace. `expected/` defines the **manifest**
                   (which files must exist) and the **golden reference** for
                   the coarse AI judge — there is no byte-for-byte diff today.

  4. Coarse AI judge (runs inside `coarse` unless `--no-coarse-judge`) —
                   cursor-agent compares `expected/` vs `actual/` per case and
                   returns CLOSE / NOT_CLOSE. Scanners alone cannot catch
                   wrong-but-valid-looking output.

Usage:

    # From repo root
    python stories/src/evals/eval.py --mode rules
    python stories/src/evals/eval.py --mode ai-judge --model gpt-5.5-medium
    python stories/src/evals/eval.py --mode coarse
    python stories/src/evals/eval.py --mode all

Reports (overwritten every run — no history is kept):

    stories/evals/last-report.json
    stories/evals/last-report.txt

Coarse-run artifacts:

    stories/evals/<case>/actual/          Manifest-filtered agent outputs.
                                          Harvested from the agent workspace
                                          (stories skill / CLI); never runner-
                                          rendered. Only paths in expected/.

    stories/evals/.last-run/<case>/       Ephemeral scratch, wiped every run.
        workspace/                        Agent's cwd (seeded with context/).
        agent/run.txt                       Prompt + live agent output (one file).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

_THIS_FILE = Path(__file__).resolve()
# stories/src/skill/evals/eval.py -> stories/
_STORIES_ROOT = _THIS_FILE.parents[3]
_REPO_ROOT = _STORIES_ROOT.parent
_RULES_DIR = _STORIES_ROOT / "rules"
_COARSE_DIR = _STORIES_ROOT / "evals"
# Ephemeral scratch for the most recent run only — wiped every invocation.
# Holds the agent's workspace + logs so failures stay debuggable, but no
# timestamped history piles up.
_LAST_RUN_DIR = _COARSE_DIR / ".last-run"
_SESSION_FILE = _LAST_RUN_DIR / "agent-session.json"
_REPORT_JSON = _COARSE_DIR / "last-report.json"
_REPORT_TXT = _COARSE_DIR / "last-report.txt"
_SECRETS_FILE = _STORIES_ROOT / "conf" / ".secrets"

# CLI default --tests-root per format (see stories/cli/README.md). The runner
# never renders artefacts itself — it harvests what the agent produced via
# the stories skill / `stories/cli/main.py`, trying these roots when the flat
# stripped path is missing.
_CLI_TESTS_ROOT_ALIASES: dict[str, tuple[str, ...]] = {
    "drawio": ("diagrams",),
    "md": ("scenarios", "story-context"),
    "ts": ("tests", "scenarios"),
    "tsx": ("tests",),
    "py": ("tests",),
    "js": ("tests",),
    "java": ("tests",),
    "json": ("json",),
}


# ---------------------------------------------------------------------------
# Secrets loading
# ---------------------------------------------------------------------------


def _load_secrets(path: Path = _SECRETS_FILE) -> None:
    """Load KEY=VALUE lines from `path` into os.environ (no overwrite).

    Format matches a minimal `.env` file: comments start with `#`, blank lines
    are skipped, no `export` prefix, no quoting. Whitespace around key and
    value is stripped. Existing env vars are preserved so CI/shell overrides
    still win.
    """
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key and value and not os.environ.get(key):
            os.environ[key] = value


# Load once at import time so both the CLI and any programmatic caller
# (e.g. stories/_run_shaping.py) inherit the same env.
_load_secrets()

_EVAL_DIR = _THIS_FILE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(_EVAL_DIR))

from cursor_agent import AgentSession, get_or_create_session, run_agent  # noqa: E402
from stories.src.skill.skill_trace import (  # noqa: E402
    append_block,
    fetch_assemble_manifest,
    log_agent_artifacts,
    log_runner_coarse_judge,
    log_runner_harvest,
    log_runner_scanners,
    register_manifest,
    set_trace_echo,
    set_trace_file,
)


# ---------------------------------------------------------------------------
# Agent run log — one file: prompt then streamed response
# ---------------------------------------------------------------------------

_RUN_INPUT_MARKER = "=== PROMPT ==="


class _AgentRunLog:
    """Single file per coarse case — structured sections appended as events occur."""

    def __init__(self, log_dir: Path, *, echo: bool) -> None:
        log_dir.mkdir(parents=True, exist_ok=True)
        self.path = log_dir / "run.txt"
        self.echo = echo
        self._file = self.path.open("w", encoding="utf-8")
        self._lock = threading.Lock()

    def write_prompt(self, prompt: str) -> None:
        block = (
            "=== RUN LOG ===\n"
            "Sections: ASSEMBLE | READ | STORIES CLI | WRITE | GENERATED | "
            "EVAL SCANNERS | EVAL JUDGE\n\n"
            f"{_RUN_INPUT_MARKER}\n{prompt.rstrip()}\n"
        )
        with self._lock:
            self._file.write(block)
            self._file.flush()
        if self.echo:
            sys.stdout.write(block)
            sys.stdout.flush()

    def append_section(self, title: str, body: str) -> None:
        append_block(title, body, path=self.path)

    def close_agent(self, exit_code: int, elapsed_seconds: float) -> None:
        with self._lock:
            self._file.write(
                f"\n=== AGENT DONE exit={exit_code} ({elapsed_seconds:.1f}s) ===\n"
            )
            self._file.flush()
            self._file.close()

    def close(self, exit_code: int, elapsed_seconds: float) -> None:
        self.close_agent(exit_code, elapsed_seconds)


@dataclass
class RuleResult:
    rule: str
    pass_ok: bool
    fail_ok: bool
    pass_exit: int
    fail_exit: int
    pass_violations: int
    fail_violations: int
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.pass_ok and self.fail_ok


@dataclass
class AiJudgeResult:
    rule: str
    fixture: str  # "pass" or "fail"
    verdict: str  # "PASS", "FAIL", "ERROR"
    reason: str
    elapsed_seconds: float


@dataclass
class CoarseResult:
    case: str
    agent_exit: int
    scanners_clean: bool
    missing_expected_files: list[str]
    extra_actual_files: list[str]
    violations: list[dict] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    ai_judge_verdict: str = ""  # CLOSE, NOT_CLOSE, SKIP, ERROR
    ai_judge_reason: str = ""

    @property
    def ok(self) -> bool:
        judge_ok = self.ai_judge_verdict in ("CLOSE", "SKIP", "")
        return (
            self.agent_exit == 0
            and self.scanners_clean
            and not self.missing_expected_files
            and judge_ok
        )


@dataclass
class Report:
    started_at: str
    mode: str
    rule_results: list[RuleResult] = field(default_factory=list)
    ai_judge_results: list[AiJudgeResult] = field(default_factory=list)
    coarse_results: list[CoarseResult] = field(default_factory=list)

    def to_json_dict(self) -> dict:
        return {
            "started_at": self.started_at,
            "mode": self.mode,
            "rule_results": [asdict(r) for r in self.rule_results],
            "ai_judge_results": [asdict(r) for r in self.ai_judge_results],
            "coarse_results": [asdict(r) for r in self.coarse_results],
        }


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def discover_rules() -> list[Path]:
    """Return every rule directory that has a scanner + pass + fail fixtures."""
    rules: list[Path] = []
    if not _RULES_DIR.exists():
        return rules
    for rule_dir in sorted(_RULES_DIR.iterdir()):
        if not rule_dir.is_dir():
            continue
        scanner = rule_dir / f"{rule_dir.name}-scanner.py"
        pass_ws = rule_dir / "evals" / "pass"
        fail_ws = rule_dir / "evals" / "fail"
        if scanner.exists() and pass_ws.exists() and fail_ws.exists():
            rules.append(rule_dir)
    return rules


def discover_coarse_cases() -> list[Path]:
    """Return every coarse-eval case with an `eval.json` descriptor."""
    cases: list[Path] = []
    if not _COARSE_DIR.exists():
        return cases
    for case_dir in sorted(_COARSE_DIR.iterdir()):
        if not case_dir.is_dir() or case_dir.name.startswith("_"):
            continue
        if (case_dir / "eval.json").exists():
            cases.append(case_dir)
    return cases


# ---------------------------------------------------------------------------
# Scanner invocation (shared)
# ---------------------------------------------------------------------------


def _run_scanner(scanner: Path, workspace: Path) -> tuple[int, list[dict], str]:
    """Run a scanner and return (exit_code, violations, stderr)."""
    proc = subprocess.run(
        [sys.executable, str(scanner), "--workspace", str(workspace)],
        capture_output=True,
        text=True,
    )
    violations: list[dict] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            violations.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return proc.returncode, violations, proc.stderr


# ---------------------------------------------------------------------------
# Mode: rules — mechanical rule battery
# ---------------------------------------------------------------------------


_REPAIR_LOOP_REF = "stories/behavior/agentic-repair-loop.md"

_RULES_ROOT = Path(__file__).resolve().parents[4] / "rules"


def _diagnose_rule_failure(rule: str, result: "RuleResult") -> str:
    """Return a concise root-cause + recommended action for a failed battery rule."""
    lines: list[str] = []

    rule_dir = _RULES_ROOT / rule
    scanner_path = rule_dir / f"{rule}-scanner.py"
    rule_md_path = rule_dir / f"{rule}.md"
    pass_ws = rule_dir / "evals" / "pass"
    fail_ws = rule_dir / "evals" / "fail"

    # --- Error: scanner crashed ---
    if result.error:
        lines.append(f"  Root cause : scanner crashed — {result.error}")
        lines.append(f"  Location   : {scanner_path}")
        lines.append(f"  Quick fix  : open the scanner, fix the error, re-run the battery")
        return "\n".join(lines)

    # --- Diagnose pass-case failure (scanner flags on known-good fixture) ---
    if not result.pass_ok:
        if result.pass_exit != 0:
            # Scanner raised violations on the pass fixture
            lines.append(f"  Root cause : scanner emits violations on the PASS fixture")
            lines.append(f"  Location   : {pass_ws}")
            lines.append(
                f"  Quick fix  : run `python {scanner_path} --workspace {pass_ws}` "
                f"to see the exact violations, then either (a) fix the pass fixture "
                f"to satisfy the rule, or (b) tighten the scanner so it only fires "
                f"on genuine violations"
            )
        else:
            lines.append(f"  Root cause : pass fixture exited 0 but had unexpected violations count")

    # --- Diagnose fail-case failure (scanner lets known-bad fixture pass) ---
    if not result.fail_ok:
        if result.fail_exit == 0:
            lines.append(f"  Root cause : scanner does not detect the violation in the FAIL fixture")
            lines.append(f"  Location   : {fail_ws}")

            # Check if the scanner is a pure applicability gate (never yields)
            scanner_text = scanner_path.read_text(encoding="utf-8") if scanner_path.exists() else ""
            if "yield  # pragma: no cover" in scanner_text or "yield Violation" not in scanner_text:
                lines.append(
                    f"  Quick fix  : scanner is an applicability gate with no mechanical violations. "
                    f"Add a minimal mechanical check (e.g. missing required file, empty required "
                    f"section) so the fail fixture can trigger exit=1. "
                    f"Then update the fail fixture to exercise that check."
                )
            else:
                lines.append(
                    f"  Quick fix  : update the FAIL fixture so it contains a clear rule "
                    f"violation, OR tighten the scanner's detection logic. "
                    f"Run `python {scanner_path} --workspace {fail_ws}` to verify."
                )
        elif result.fail_violations == 0:
            lines.append(
                f"  Root cause : scanner exited {result.fail_exit} on FAIL fixture "
                f"but no violations were parsed from stdout — scanner may be crashing silently"
            )
            lines.append(
                f"  Quick fix  : run `python {scanner_path} --workspace {fail_ws}` "
                f"and inspect stderr for the real error"
            )
        else:
            lines.append(
                f"  Root cause : fail fixture needs exactly 1 violation (got {result.fail_violations})"
            )
            lines.append(f"  Quick fix  : trim the fail fixture to a single clear violation case")

    # --- Suggest repair loop for anything complex ---
    if not lines:
        lines.append(f"  Root cause : unknown — both pass_ok={result.pass_ok} fail_ok={result.fail_ok}")

    if rule_md_path.exists():
        lines.append(f"  Rule doc   : {rule_md_path}")

    lines.append(
        f"  Complex?   : see @{_REPAIR_LOOP_REF} for the full agentic repair loop"
    )
    return "\n".join(lines)


def run_rule_battery(verbose: bool = True) -> list[RuleResult]:
    results: list[RuleResult] = []
    rules = discover_rules()
    if verbose:
        print(f"[rules] Discovered {len(rules)} rule(s) with scanner + fixtures")

    for rule_dir in rules:
        rule = rule_dir.name
        scanner = rule_dir / f"{rule}-scanner.py"
        pass_ws = rule_dir / "evals" / "pass"
        fail_ws = rule_dir / "evals" / "fail"

        try:
            exit_pass, v_pass, _ = _run_scanner(scanner, pass_ws)
            exit_fail, v_fail, _ = _run_scanner(scanner, fail_ws)
        except Exception as exc:
            result = RuleResult(
                rule=rule,
                pass_ok=False,
                fail_ok=False,
                pass_exit=-1,
                fail_exit=-1,
                pass_violations=0,
                fail_violations=0,
                error=str(exc),
            )
            results.append(result)
            if verbose:
                print(f"  [ERR ] {rule}   {exc}")
            continue

        pass_ok = exit_pass == 0 and len(v_pass) == 0
        fail_ok = exit_fail == 1 and len(v_fail) == 1
        result = RuleResult(
            rule=rule,
            pass_ok=pass_ok,
            fail_ok=fail_ok,
            pass_exit=exit_pass,
            fail_exit=exit_fail,
            pass_violations=len(v_pass),
            fail_violations=len(v_fail),
        )
        results.append(result)
        if verbose:
            tag = "PASS" if result.ok else "FAIL"
            print(
                f"  [{tag}] {rule}   "
                f"pass=exit{exit_pass}/v{len(v_pass)}   "
                f"fail=exit{exit_fail}/v{len(v_fail)}"
            )
            if not result.ok:
                print(_diagnose_rule_failure(rule, result))
    return results


# ---------------------------------------------------------------------------
# Mode: ai-judge — cursor-agent evaluates each rule against its fixture
# ---------------------------------------------------------------------------


_JUDGE_PROMPT = """You are an AI judge for a rule-based validator.

Read the rule below and decide whether the accompanying artifact **{fixture_kind}**
satisfies the rule.

- For the `pass` fixture: verdict must be PASS.
- For the `fail` fixture: verdict must be FAIL.

Reply with a single JSON object on one line, no code fences, no commentary:
{{"verdict": "PASS" | "FAIL", "reason": "<one sentence>"}}

--- RULE ---
{rule_md}

--- ARTIFACT ({fixture_kind}) ---
{artifact_text}
"""


def _collect_fixture_text(fixture_root: Path) -> str:
    """Read all fixture files under `fixture_root` and concatenate them."""
    chunks: list[str] = []
    for path in sorted(fixture_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(fixture_root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        chunks.append(f"--- FILE: {rel} ---\n{text}")
    return "\n\n".join(chunks) if chunks else "(empty fixture)"


def _invoke_cursor_agent_headless(
    prompt: str,
    model: str | None,
    timeout: int = 120,
    cwd: Path | None = None,
    *,
    session: AgentSession | None = None,
    run_log: _AgentRunLog | None = None,
    extra_env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """Invoke cursor-agent. Reuses *session* when set (no cold start each call).

    Streams via ``stream-json`` into ``run_log`` (``run.txt``) when provided.
    """
    if session is None:
        raise FileNotFoundError("cursor-agent session required — pass AgentSession")

    workspace = cwd if cwd is not None else _STORIES_ROOT
    extra: dict[str, str] = dict(extra_env or {})
    if run_log is not None:
        extra["STORIES_SKILL_TRACE"] = str(run_log.path.resolve())
        set_trace_file(run_log.path)
    if run_log is not None:
        run_log.write_prompt(prompt)

    started = time.perf_counter()
    try:
        result = run_agent(
            session,
            prompt,
            workspace,
            timeout_seconds=timeout,
            model=model,
            echo=False,
            extra_env=extra or None,
        )
    except subprocess.TimeoutExpired:
        if run_log is not None:
            run_log.close(-1, time.perf_counter() - started)
        raise

    if run_log is not None:
        run_log.close(result.exit_code, result.elapsed_seconds)
    return result.exit_code, result.stdout, result.stderr


def _parse_judge_verdict(stdout: str) -> tuple[str, str]:
    """Extract the last JSON object with verdict/reason from agent stdout."""
    return _parse_json_verdict(stdout, frozenset({"PASS", "FAIL"}))


def _parse_coarse_judge_verdict(stdout: str) -> tuple[str, str]:
    return _parse_json_verdict(stdout, frozenset({"CLOSE", "NOT_CLOSE"}))


def _parse_json_verdict(stdout: str, allowed: frozenset[str]) -> tuple[str, str]:
    # Pass 1: look for a top-level JSON object on its own line.
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        verdict = str(obj.get("verdict", "")).upper()
        reason = str(obj.get("reason", "")).strip()
        if verdict in allowed:
            return verdict, reason

    # Pass 2: the verdict JSON may be embedded as a string inside a stream-json
    # event (e.g. inside an assistant message content block).  Use regex to
    # extract it from anywhere in the raw output.
    pattern = re.compile(
        r'\{"verdict"\s*:\s*"(' + "|".join(re.escape(v) for v in allowed) + r')"'
        r'.*?"reason"\s*:\s*"([^"]*)"',
        re.IGNORECASE | re.DOTALL,
    )
    for m in pattern.finditer(stdout):
        verdict = m.group(1).upper()
        reason = m.group(2).strip()
        if verdict in allowed:
            return verdict, reason

    tail = stdout.strip()[-200:] if stdout.strip() else "(the judge produced no output)"
    return "ERROR", f"AI judge did not return a verdict. Last output: {tail!r}"


# ---------------------------------------------------------------------------
# Coarse AI judge — expected/ vs actual/ semantic comparison per case
# ---------------------------------------------------------------------------

_COARSE_JUDGE_PROMPT = """You are judging a coarse eval for the stories skill.

Case: **{case}**
Prompt given to the agent:
{prompt}

Compare **EXPECTED** (golden reference under `expected/`) with **ACTUAL** (what the agent produced, copied to `actual/`).

Verdict **CLOSE** when actual is semantically aligned with expected for this fidelity:
- Same story names, epic/sub-epic structure, and thin-slice increments (where applicable)
- `story-graph.json` must include an `"increments"` array when the fidelity includes thin-slicing; each increment must have `name`, `sequentialOrder`, `stories` (list of story names), `outcome`, and `decisionPrompt`
- Draw.io files may differ in layout/XML formatting if the same nodes and labels are present
- `thin-slicing.drawio` must show epic column headers, sub-epic headers, and horizontal increment swim-lane rows with story cells positioned in their epic column

Verdict **NOT_CLOSE** when actual is materially wrong: wrong fidelity, missing stories/increments, extra invented scope, empty placeholders, or broken diagrams that do not reflect the markdown/json model.

Reply with a single JSON object on one line, no code fences, no commentary:
{{"verdict": "CLOSE" | "NOT_CLOSE", "reason": "<one or two sentences>"}}

--- EXPECTED ---
{expected_text}

--- ACTUAL ---
{actual_text}
"""

_MAX_JUDGE_FILE_CHARS = 12_000
_MAX_JUDGE_TOTAL_CHARS = 80_000


def _collect_case_tree_text(root: Path, label: str) -> str:
    """Concatenate all text files under a case sub-tree for the AI judge."""
    if not root.exists():
        return f"({label} tree missing)"
    chunks: list[str] = []
    total = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if len(text) > _MAX_JUDGE_FILE_CHARS:
            text = text[:_MAX_JUDGE_FILE_CHARS] + "\n... [truncated]"
        block = f"--- {label}/{rel} ---\n{text}"
        if total + len(block) > _MAX_JUDGE_TOTAL_CHARS:
            chunks.append(f"... [{label} truncated — remaining files omitted]")
            break
        chunks.append(block)
        total += len(block)
    return "\n\n".join(chunks) if chunks else f"({label} tree empty)"


def _judge_coarse_case(
    case: str,
    case_dir: Path,
    prompt: str,
    model: str | None,
    timeout: int,
    session: AgentSession,
) -> tuple[str, str]:
    """Compare expected/ vs actual/ with cursor-agent. Returns (verdict, reason)."""
    expected_text = _collect_case_tree_text(case_dir / "expected", "expected")
    actual_text = _collect_case_tree_text(case_dir / "actual", "actual")
    judge_prompt = _COARSE_JUDGE_PROMPT.format(
        case=case,
        prompt=prompt.strip() or "(no prompt.md)",
        expected_text=expected_text,
        actual_text=actual_text,
    )
    try:
        exit_code, stdout, stderr = _invoke_cursor_agent_headless(
            judge_prompt,
            model=model,
            timeout=timeout,
            cwd=case_dir,
            session=session,
        )
    except FileNotFoundError:
        return "SKIP", "cursor-agent not on PATH — coarse AI judge skipped"
    except subprocess.TimeoutExpired:
        return "ERROR", "coarse AI judge timed out"
    verdict, reason = _parse_coarse_judge_verdict(stdout)
    if verdict == "ERROR":
        tail = stderr.strip()[-300:] if stderr.strip() else "(no stderr)"
        reason = (
            f"AI judge exited {exit_code} with no parseable verdict.\n"
            f"stdout={stdout.strip()[-200:]!r}\n"
            f"stderr={tail!r}"
        )
    return verdict, reason


def run_ai_judge(
    model: str | None = None,
    verbose: bool = True,
    session: AgentSession | None = None,
) -> list[AiJudgeResult]:
    results: list[AiJudgeResult] = []
    rules = discover_rules()
    if verbose:
        print(f"[ai-judge] Discovered {len(rules)} rule(s); model={model or 'default'}")

    for rule_dir in rules:
        rule = rule_dir.name
        rule_md_path = rule_dir / f"{rule}.md"
        if not rule_md_path.exists():
            if verbose:
                print(f"  [SKIP] {rule}   no {rule}.md alongside scanner")
            continue
        rule_md = rule_md_path.read_text(encoding="utf-8")

        for fixture_kind in ("pass", "fail"):
            fixture_root = rule_dir / "evals" / fixture_kind
            artifact_text = _collect_fixture_text(fixture_root)
            prompt = _JUDGE_PROMPT.format(
                rule_md=rule_md,
                fixture_kind=fixture_kind,
                artifact_text=artifact_text,
            )
            started = time.perf_counter()
            try:
                exit_code, stdout, stderr = _invoke_cursor_agent_headless(
                    prompt, model=model, session=session,
                )
            except FileNotFoundError:
                results.append(AiJudgeResult(
                    rule=rule,
                    fixture=fixture_kind,
                    verdict="ERROR",
                    reason="cursor-agent CLI not found on PATH",
                    elapsed_seconds=0.0,
                ))
                if verbose:
                    print(f"  [ERR ] {rule}/{fixture_kind}   cursor-agent not on PATH")
                continue
            except subprocess.TimeoutExpired:
                results.append(AiJudgeResult(
                    rule=rule,
                    fixture=fixture_kind,
                    verdict="ERROR",
                    reason="cursor-agent timed out",
                    elapsed_seconds=time.perf_counter() - started,
                ))
                if verbose:
                    print(f"  [ERR ] {rule}/{fixture_kind}   timeout")
                continue

            elapsed = time.perf_counter() - started
            if exit_code != 0:
                verdict, reason = "ERROR", f"agent exit {exit_code}: {stderr.strip()[-160:]}"
            else:
                verdict, reason = _parse_judge_verdict(stdout)

            expected = "PASS" if fixture_kind == "pass" else "FAIL"
            correct = verdict == expected
            results.append(AiJudgeResult(
                rule=rule,
                fixture=fixture_kind,
                verdict=verdict,
                reason=reason,
                elapsed_seconds=elapsed,
            ))
            if verbose:
                tag = "PASS" if correct else ("FAIL" if verdict in ("PASS", "FAIL") else "ERR ")
                print(f"  [{tag}] {rule}/{fixture_kind}   verdict={verdict}   {reason[:80]}")
    return results


# ---------------------------------------------------------------------------
# Mode: coarse — run each case in stories/evals/<case>/
# ---------------------------------------------------------------------------


_COARSE_CASE_STRUCTURE = """Each case is:
    stories/evals/<case>/
        eval.json          — descriptor: {fidelity, prompt_file, context_dir, formats}
        prompt.md          — instructions for the agent
        context/           — input files the agent gets to read
        expected/          — golden output tree
        actual/            — populated by this runner (wiped every run)
"""


def _read_case_descriptor(case_dir: Path) -> dict:
    return json.loads((case_dir / "eval.json").read_text(encoding="utf-8"))


def _rmtree_readonly_safe(path: Path) -> None:
    """`shutil.rmtree` that survives Windows ReadOnly attributes.

    Windows `rmtree` raises PermissionError on any entry that carries the
    ReadOnly bit (git checkouts, tooling that hardens outputs, etc.). The
    onerror hook clears the attribute and retries — standard idiom.
    """
    def _on_rm_error(func, target, exc_info):
        try:
            os.chmod(target, 0o777)
            func(target)
        except OSError:
            raise exc_info[1]

    if path.exists():
        shutil.rmtree(path, onerror=_on_rm_error)


def _wipe_and_recreate(path: Path) -> None:
    """Remove `path` and re-create it as an empty directory."""
    _rmtree_readonly_safe(path)
    path.mkdir(parents=True, exist_ok=True)


def _relative_files(root: Path) -> set[str]:
    if not root.exists():
        return set()
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
    }


def _workspace_path(rel: str) -> str:
    """Strip the leading format-folder prefix from an expected/ relative path.

    expected/ uses format sub-folders to avoid name collisions when a case
    produces the same filename in multiple output formats:
        md/story-map.md   → story-map.md   (agent writes flat)
        drawio/story-map.drawio → story-map.drawio

    The first path component is always the format bucket; everything after is
    the canonical workspace-relative path for consolidated layouts.
    """
    parts = Path(rel).parts
    return str(Path(*parts[1:])) if len(parts) > 1 else rel


def _harvest_candidates(expected_rel: str) -> list[str]:
    """Workspace-relative paths to probe when harvesting one manifest entry.

    The agent is expected to produce artefacts via the stories skill (AI edits
    for models, `stories/cli/main.py` for deterministic views). Those files
    may land flat at the workspace root, under the format bucket, or under
    the CLI's default ``--tests-root`` for that format.
    """
    parts = Path(expected_rel).parts
    if len(parts) <= 1:
        return [expected_rel]

    format_bucket, rest = parts[0], Path(*parts[1:]).as_posix()
    candidates = [rest, expected_rel]
    for alias_root in _CLI_TESTS_ROOT_ALIASES.get(format_bucket, ()):
        candidates.append(f"{alias_root}/{rest}")

    seen: set[str] = set()
    ordered: list[str] = []
    for candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            ordered.append(candidate)
    return ordered


def _find_produced_file(workspace_root: Path, expected_rel: str) -> Path | None:
    """Return the first matching file the agent wrote for a manifest path."""
    for rel in _harvest_candidates(expected_rel):
        path = workspace_root / rel
        if path.is_file():
            return path
    return None


_READS_RE = re.compile(r"reads\s*=\s*\(([^)]+)\)")


def _scanner_reads(scanner_path: Path) -> set[str]:
    """Return the set of artifact kinds the scanner declares it reads.

    Falls back to the base-class default `("story_map",)` when unset.
    """
    try:
        text = scanner_path.read_text(encoding="utf-8")
    except OSError:
        return {"story_map"}
    m = _READS_RE.search(text)
    if not m:
        return {"story_map"}
    kinds = set(re.findall(r'"([^"]+)"', m.group(1)))
    return kinds or {"story_map"}


def _detect_workspace_kinds(scan_root: Path) -> set[str]:
    """Return the set of artifact kinds actually present in a workspace tree.

    A scanner is meaningful only when every kind it declares it reads is
    available. We infer presence from canonical file/folder locations rather
    than importing the workspace loader (keeps the runner subprocess-free for
    this check).

    Kinds match the scanner `reads` vocabulary:
    - `story_map`      — story-map.md OR story-graph.json
    - `increments`     — thin-slicing.md (canonical) or legacy names
    - `scenarios`      — scenarios/**/*.md
    - `story_contexts` — story-context.md anywhere under root
    - `test_suites`    — test files under tests/**
    """
    kinds: set[str] = set()
    if (scan_root / "story-map.md").exists() or (scan_root / "story-graph.json").exists():
        kinds.add("story_map")
    if any(
        (scan_root / name).exists()
        for name in ("thin-slicing.md", "thin-slice.md", "thin-slices.md", "increments.md")
    ):
        kinds.add("increments")
    _scenario_dirs = [scan_root / "scenarios", scan_root / "md"]
    if any(d.is_dir() and any(d.rglob("*.md")) for d in _scenario_dirs):
        kinds.add("scenarios")
    if any(scan_root.rglob("story-context.md")):
        kinds.add("story_contexts")
    tests_dir = scan_root / "tests"
    _TEST_STEMS = {".test", ".spec"}
    if tests_dir.is_dir() and any(
        Path(f.stem).suffix in _TEST_STEMS
        for f in tests_dir.rglob("*") if f.is_file()
    ):
        kinds.add("test_suites")
    return kinds


_MERGE_EXCLUDE_NAMES = {"prompt.md", ".stories-skill-trace"}


def _merge_workspace(context_dir: Path, actual_dir: Path, dest: Path) -> Path:
    """Copy context/ then actual/ into `dest` so scanners see a full workspace.

    Files in `actual/` override files in `context/` with the same relative path
    (this is what allows a downstream fidelity to refine an upstream artifact).

    `prompt.md` is excluded — it's an eval-runner concern, not a story artifact,
    and it must not appear in the workspace scanners walk.
    """
    import shutil
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for source in (context_dir, actual_dir):
        if not source.exists():
            continue
        for f in source.rglob("*"):
            if not f.is_file() or f.name in _MERGE_EXCLUDE_NAMES:
                continue
            rel = f.relative_to(source)
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
    return dest


def _case_fidelity(case_name: str) -> str:
    parts = case_name.split("-", 1)
    return parts[1] if len(parts) == 2 else case_name


def _formats_from_expected(expected_dir: Path) -> str:
    buckets: set[str] = set()
    if expected_dir.is_dir():
        for path in expected_dir.rglob("*"):
            if path.is_file():
                rel = path.relative_to(expected_dir)
                if rel.parts:
                    buckets.add(rel.parts[0])
    return ",".join(sorted(buckets)) or "md"


def _prime_read_tags(case: str, expected_dir: Path) -> None:
    """Load generate manifest paths so READ lines can tag assembled files."""
    manifest = fetch_assemble_manifest(
        skill_root=_STORIES_ROOT,
        fidelity=_case_fidelity(case),
        fmt=_formats_from_expected(expected_dir),
        phase="generate",
    )
    if manifest is not None:
        register_manifest(manifest)


def run_coarse_cases(
    model: str | None = None,
    verbose: bool = True,
    run_dir: Path | None = None,
    case_filter: list[str] | None = None,
    coarse_judge: bool = True,
    session: AgentSession | None = None,
) -> list[CoarseResult]:
    """Run every coarse-eval case.

    `case_dir/actual/` holds the live "latest run" tree (wiped per invocation).
    When `run_dir` is provided, a persistent snapshot is also copied into
    `run_dir/<case>/actual/` so historical runs remain browsable. Ephemeral
    scan trees also live under `run_dir` when it's given, otherwise they fall
    back to the case dir (legacy behaviour).
    """
    import shutil

    results: list[CoarseResult] = []
    cases = discover_coarse_cases()
    if case_filter:
        wanted = set(case_filter)
        cases = [c for c in cases if c.name in wanted]
        missing = wanted - {c.name for c in cases}
        if missing:
            raise SystemExit(f"Unknown coarse case(s): {', '.join(sorted(missing))}")
    if verbose:
        print(f"[coarse] Running {len(cases)} coarse-eval case(s)", flush=True)

    if session is None:
        raise RuntimeError("cursor-agent session required for coarse evals")

    rule_dirs = discover_rules()
    scanner_paths = [rule_dir / f"{rule_dir.name}-scanner.py" for rule_dir in rule_dirs]
    scanner_reads = {p: _scanner_reads(p) for p in scanner_paths}

    for case_dir in cases:
        case = case_dir.name
        descriptor = _read_case_descriptor(case_dir)
        context_dir = case_dir / "context"
        prompt_file = context_dir / "prompt.md"
        expected_dir = case_dir / "expected"
        actual_dir = case_dir / "actual"

        _wipe_and_recreate(actual_dir)
        prompt = prompt_file.read_text(encoding="utf-8") if prompt_file.exists() else ""

        case_run_dir = (run_dir / case) if run_dir is not None else None
        if case_run_dir is not None:
            case_run_dir.mkdir(parents=True, exist_ok=True)
        scratch_root = case_run_dir if case_run_dir is not None else case_dir

        # Agent runs in an isolated scratch workspace seeded with context/
        # so prompt-relative paths (e.g. `context/brief.md`) resolve.
        # Use a fresh timestamped workspace so the IDE can keep .last-run
        # files open without causing a PermissionError on the wipe.
        workspace_root = scratch_root / f"workspace-{int(time.time())}"
        workspace_root.mkdir(parents=True, exist_ok=True)
        if context_dir.exists():
            seed_root = workspace_root / "context"
            for src in context_dir.rglob("*"):
                if not src.is_file() or src.name in _MERGE_EXCLUDE_NAMES:
                    continue
                rel = src.relative_to(context_dir)
                dest = seed_root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)

        required = sorted(_relative_files(expected_dir))

        started = time.perf_counter()
        agent_stderr = ""
        agent_stdout = ""
        agent_log_dir = (case_run_dir / "agent") if case_run_dir is not None else None
        run_log = (
            _AgentRunLog(agent_log_dir, echo=verbose)
            if agent_log_dir is not None
            else None
        )
        if verbose:
            stream_hint = (
                run_log.path.relative_to(_REPO_ROOT).as_posix()
                if run_log is not None
                else "(no log dir)"
            )
            print(f"  … {case}   agent running → {stream_hint}", flush=True)
        if run_log is not None:
            _prime_read_tags(case, expected_dir)
            set_trace_file(run_log.path)
            set_trace_echo(verbose)
        try:
            try:
                case_model = model or descriptor.get("model")
                exit_code, agent_stdout, agent_stderr = _invoke_cursor_agent_headless(
                    prompt=prompt,
                    model=case_model,
                    timeout=descriptor.get("timeout_seconds", 180),
                    cwd=workspace_root,
                    session=session,
                    run_log=run_log,
                )
            except FileNotFoundError:
                results.append(CoarseResult(
                    case=case,
                    agent_exit=-1,
                    scanners_clean=False,
                    missing_expected_files=[],
                    extra_actual_files=[],
                    violations=[{"error": "cursor-agent not on PATH"}],
                    elapsed_seconds=0.0,
                ))
                if verbose:
                    print(f"  [ERR ] {case}   cursor-agent not on PATH")
                continue
        finally:
            set_trace_echo(False)
            set_trace_file(None)

        # Re-enable trace for the post-agent sections (harvest, scanners, judge).
        if run_log is not None:
            set_trace_file(run_log.path)
            set_trace_echo(verbose)

        expected_files = _relative_files(expected_dir)

        # Harvest manifest files only — never render. Draw.io, JSON, and code
        # views must come from the agent via the stories skill / CLI.
        harvested: list[tuple[str, str]] = []
        for rel_str in expected_files:
            produced = _find_produced_file(workspace_root, rel_str)
            if produced is None:
                continue
            dest = actual_dir / rel_str
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(produced, dest)
            source_rel = produced.relative_to(workspace_root).as_posix()
            manifest_rel = _workspace_path(rel_str)
            harvested.append((manifest_rel, source_rel))
            if verbose and source_rel != manifest_rel:
                print(f"         harvested {rel_str} from {source_rel}")

        actual_files = _relative_files(actual_dir)
        missing = sorted(expected_files - actual_files)
        extra: list[str] = []

        if run_log is not None:
            artifact_paths: list[tuple[str, Path]] = []
            for rel_str in sorted(expected_files):
                actual_path = actual_dir / rel_str
                if actual_path.is_file():
                    artifact_paths.append((rel_str, actual_path))
                    continue
                produced = _find_produced_file(workspace_root, rel_str)
                if produced is not None:
                    artifact_paths.append((rel_str, produced))
            log_agent_artifacts(artifact_paths, path=run_log.path)

        # Scanners see the full workspace (context flattened to root level).
        # Copy order matters: context/ files go first so the agent's root-level
        # outputs (e.g. story-map.md) overwrite the seeded context versions
        # when both share the same filename.
        scan_root = scratch_root / "_scan"
        _rmtree_readonly_safe(scan_root)
        scan_root.mkdir(parents=True, exist_ok=True)
        context_prefix = Path("context")
        for passes in (True, False):  # True = context pass, False = output pass
            for src in workspace_root.rglob("*"):
                if not src.is_file() or src.name in _MERGE_EXCLUDE_NAMES:
                    continue
                rel = src.relative_to(workspace_root)
                is_context = rel.parts and rel.parts[0] == "context"
                if passes != is_context:
                    continue
                if is_context:
                    rel = Path(*rel.parts[1:])
                    if not rel.parts:
                        continue
                dest = scan_root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
        present_kinds = _detect_workspace_kinds(scan_root)

        all_violations: list[dict] = []
        scanner_results: list[tuple[str, str, int, list[dict]]] = []
        for scanner in scanner_paths:
            reads = scanner_reads[scanner]
            scanner_name = scanner.parent.name
            if not reads.issubset(present_kinds):
                missing_reads = sorted(reads - present_kinds)
                scanner_results.append((
                    scanner_name,
                    f"SKIP (needs {', '.join(missing_reads)})",
                    0,
                    [],
                ))
                continue
            _, v, _ = _run_scanner(scanner, scan_root)
            status = "PASS" if not v else "FAIL"
            scanner_results.append((scanner_name, status, len(v), v))
            all_violations.extend(v)

        if run_log is not None:
            log_runner_harvest(
                harvested=harvested,
                missing=missing,
                path=run_log.path,
            )
            log_runner_scanners(
                results=scanner_results,
                total_violations=len(all_violations),
                path=run_log.path,
            )

        if exit_code != 0:
            tail = (agent_stderr or agent_stdout or "").strip()
            if tail:
                all_violations.insert(0, {
                    "source": "cursor-agent",
                    "exit_code": exit_code,
                    "stderr_tail": tail[-500:],
                })

        ai_verdict = ""
        ai_reason = ""
        scanners_clean = not all_violations
        judge_enabled = coarse_judge and descriptor.get("ai_judge", True)
        if judge_enabled and not missing:
            if verbose:
                print(f"         judging expected vs actual…")
            ai_verdict, ai_reason = _judge_coarse_case(
                case=case,
                case_dir=case_dir,
                prompt=prompt,
                model=case_model,
                timeout=descriptor.get("judge_timeout_seconds", 120),
                session=session,
            )
            if ai_verdict == "NOT_CLOSE":
                all_violations.insert(0, {
                    "source": "coarse-ai-judge",
                    "rule": "expected-vs-actual",
                    "message": ai_reason,
                })
        elif judge_enabled and missing:
            ai_verdict = "NOT_CLOSE"
            ai_reason = f"missing expected files: {', '.join(missing)}"
        elif not judge_enabled:
            ai_verdict = "SKIP"
            ai_reason = "coarse AI judge disabled"

        if run_log is not None:
            log_runner_coarse_judge(
                verdict=ai_verdict or "SKIP",
                reason=ai_reason,
                path=run_log.path,
            )
            set_trace_echo(False)
            set_trace_file(None)

        result = CoarseResult(
            case=case,
            agent_exit=exit_code,
            scanners_clean=scanners_clean,
            missing_expected_files=missing,
            extra_actual_files=extra,
            violations=all_violations,
            elapsed_seconds=time.perf_counter() - started,
            ai_judge_verdict=ai_verdict,
            ai_judge_reason=ai_reason,
        )
        results.append(result)
        if verbose:
            tag = "PASS" if result.ok else "FAIL"
            parts = []
            if exit_code != 0:
                parts.append(f"agent crashed (exit {exit_code})")
            if missing:
                parts.append(f"{len(missing)} expected file(s) missing")
            if all_violations:
                parts.append(f"{len(all_violations)} violation(s)")
            if ai_verdict == "CLOSE":
                parts.append("judge: matches expected")
            elif ai_verdict == "NOT_CLOSE":
                parts.append("judge: does not match expected")
            elif ai_verdict == "ERROR":
                parts.append("judge: failed to run")
            elif ai_verdict == "SKIP":
                parts.append("judge: skipped")
            summary = "  —  ".join(parts) if parts else ("all good" if tag == "PASS" else "unknown failure")
            print(f"  [{tag}] {case}  ({result.elapsed_seconds:.1f}s)  {summary}")
            if ai_reason and ai_verdict in ("NOT_CLOSE", "ERROR"):
                print(f"         {ai_reason}")

    return results


# ---------------------------------------------------------------------------
# Seed-expected — capture first-run agent output as golden files
# ---------------------------------------------------------------------------

_EXT_TO_BUCKET: dict[str, str] = {
    ".md": "md",
    ".ts": "ts",
    ".tsx": "tsx",
    ".py": "py",
    ".js": "js",
    ".java": "java",
    ".json": "json",
    ".drawio": "drawio",
}

# Workspace sub-folders whose prefix is stripped when building the expected/
# manifest path (e.g. scenarios/foo.md → md/foo.md).
# Workspace sub-folders whose prefix is stripped when building the expected/
# manifest path.  Includes the format-bucket names themselves so that agent
# outputs written to e.g. workspace/ts/... or workspace/md/... are not
# double-prefixed as ts/ts/... or md/md/... in expected/.
_SEED_STRIP_DIRS: frozenset[str] = frozenset({
    "scenarios", "diagrams", "tests", "json",
    "md", "ts", "tsx", "py", "js", "java", "drawio",
})


def run_seed_expected(
    model: str | None,
    verbose: bool,
    run_dir: Path,
    case_filter: list[str] | None,
    session: "AgentSession | None",
) -> None:
    """Run each coarse case and write the agent output to ``expected/`` as golden files.

    Wipes the existing ``expected/`` tree for each case before writing so that
    stale artefacts from a previous seed do not linger.
    """
    import shutil

    cases = discover_coarse_cases()
    if case_filter:
        wanted = set(case_filter)
        cases = [c for c in cases if c.name in wanted]
        missing = wanted - {c.name for c in cases}
        if missing:
            raise SystemExit(f"Unknown coarse case(s): {', '.join(sorted(missing))}")

    for case_dir in cases:
        case = case_dir.name
        descriptor = _read_case_descriptor(case_dir)
        context_dir = case_dir / "context"
        expected_dir = case_dir / "expected"
        prompt_file = context_dir / "prompt.md"

        case_run_dir = run_dir / case
        case_run_dir.mkdir(parents=True, exist_ok=True)

        workspace_root = case_run_dir / f"workspace-{int(time.time())}"
        workspace_root.mkdir(parents=True, exist_ok=True)
        if context_dir.exists():
            seed_root = workspace_root / "context"
            for src in context_dir.rglob("*"):
                if not src.is_file() or src.name in _MERGE_EXCLUDE_NAMES:
                    continue
                rel = src.relative_to(context_dir)
                dest = seed_root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)

        prompt = prompt_file.read_text(encoding="utf-8") if prompt_file.exists() else ""
        agent_log_dir = case_run_dir / "agent"
        run_log = _AgentRunLog(agent_log_dir, echo=verbose)
        _prime_read_tags(case, expected_dir)
        set_trace_file(run_log.path)
        set_trace_echo(verbose)

        if verbose:
            stream_hint = run_log.path.relative_to(_REPO_ROOT).as_posix()
            print(f"  … {case}   agent running → {stream_hint}", flush=True)

        try:
            _invoke_cursor_agent_headless(
                prompt=prompt,
                model=model or descriptor.get("model"),
                timeout=descriptor.get("timeout_seconds", 180),
                cwd=workspace_root,
                session=session,
                run_log=run_log,
            )
        finally:
            set_trace_echo(False)
            set_trace_file(None)

        # Wipe old expected/ and reseed from workspace output.
        _rmtree_readonly_safe(expected_dir)
        expected_dir.mkdir(parents=True, exist_ok=True)

        seeded: list[str] = []
        _SEED_SKIP_ROOTS = frozenset({"context", "agent", "_scan_test"})
        for src in workspace_root.rglob("*"):
            if not src.is_file():
                continue
            rel = src.relative_to(workspace_root)
            parts = rel.parts
            if parts[0] in _SEED_SKIP_ROOTS:
                continue
            ext = src.suffix.lower()
            bucket = _EXT_TO_BUCKET.get(ext)
            if bucket is None:
                continue
            # Strip known subdir prefixes so paths are flat under the bucket.
            if len(parts) > 1 and parts[0] in _SEED_STRIP_DIRS:
                filename = Path(*parts[1:])
            else:
                filename = Path(*parts)
            dest = expected_dir / bucket / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            seeded.append(f"{bucket}/{filename.as_posix()}")

        if verbose:
            print(f"  [SEED] {case}   wrote {len(seeded)} file(s) to expected/")
            for s in sorted(seeded):
                print(f"         {s}")


# ---------------------------------------------------------------------------
# Report + CLI
# ---------------------------------------------------------------------------


def _create_run_dir() -> Path:
    """Prepare the single ephemeral scratch dir for this invocation.

    Best-effort wipe of `.last-run/` — skips any sub-tree that Windows
    reports as locked (e.g. IDE has a file open). Fresh workspace dirs
    are timestamped so they never collide with open ones.
    """
    if _LAST_RUN_DIR.exists():
        for child in list(_LAST_RUN_DIR.iterdir()):
            try:
                _rmtree_readonly_safe(child)
            except OSError:
                pass  # locked by IDE — leave it, timestamped workspace avoids collision
    _LAST_RUN_DIR.mkdir(parents=True, exist_ok=True)
    return _LAST_RUN_DIR


def _write_report(report: Report, run_dir: Path) -> Path:
    """Write the run's report to a single overwriting location.

    `run_dir` is accepted for signature compatibility but the report
    always lands at `stories/evals/last-report.{json,txt}` — no
    per-run folders.
    """
    _REPORT_JSON.write_text(
        json.dumps(report.to_json_dict(), indent=2),
        encoding="utf-8",
    )

    summary_lines: list[str] = [f"Eval run  mode={report.mode}  at {report.started_at}", ""]
    if report.rule_results:
        ok = sum(1 for r in report.rule_results if r.ok)
        summary_lines.append(f"Rule battery:  {ok}/{len(report.rule_results)} passed")
        for r in report.rule_results:
            if not r.ok:
                summary_lines.append(
                    f"  FAIL  {r.rule}  "
                    f"pass=exit{r.pass_exit}/v{r.pass_violations}  "
                    f"fail=exit{r.fail_exit}/v{r.fail_violations}"
                )
    if report.ai_judge_results:
        summary_lines.append("")
        correct = sum(
            1 for r in report.ai_judge_results
            if (r.fixture == "pass" and r.verdict == "PASS") or
               (r.fixture == "fail" and r.verdict == "FAIL")
        )
        summary_lines.append(f"AI judge:  {correct}/{len(report.ai_judge_results)} correct")
        for r in report.ai_judge_results:
            expected = "PASS" if r.fixture == "pass" else "FAIL"
            if r.verdict != expected:
                summary_lines.append(f"  {r.verdict}  {r.rule}/{r.fixture}  {r.reason}")
    if report.coarse_results:
        summary_lines.append("")
        ok = sum(1 for r in report.coarse_results if r.ok)
        summary_lines.append(f"Coarse cases:  {ok}/{len(report.coarse_results)} passed")
        for r in report.coarse_results:
            tag = "PASS" if r.ok else "FAIL"
            judge = f"  judge={r.ai_judge_verdict}" if r.ai_judge_verdict else ""
            summary_lines.append(
                f"  {tag}  {r.case}  "
                f"agent=exit{r.agent_exit}  "
                f"missing={len(r.missing_expected_files)}  "
                f"violations={len(r.violations)}{judge}"
            )
            if r.ai_judge_reason and r.ai_judge_verdict in ("NOT_CLOSE", "ERROR"):
                summary_lines.append(f"    judge: {r.ai_judge_reason}")
            for v in r.violations:
                summary_lines.append(
                    f"    - {v.get('rule', v.get('source', '?'))}: "
                    f"{v.get('message', v.get('stderr_tail', v.get('error', '')))}"
                )

    summary = "\n".join(summary_lines) + "\n"
    _REPORT_TXT.write_text(summary, encoding="utf-8")
    return _REPORT_JSON.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Unified eval runner for the stories skill",
    )
    parser.add_argument(
        "--mode",
        choices=("rules", "ai-judge", "coarse", "all", "seed-expected"),
        default="rules",
    )
    parser.add_argument("--model", default=None, help="cursor-agent model slug")
    parser.add_argument(
        "--case",
        action="append",
        dest="cases",
        metavar="NAME",
        help="coarse case folder name under stories/evals/ (repeatable; default: all)",
    )
    parser.add_argument("--quiet", action="store_true", help="suppress per-item log")
    parser.add_argument(
        "--no-coarse-judge",
        action="store_true",
        help="skip expected-vs-actual AI judge during coarse evals",
    )
    parser.add_argument(
        "--fresh-session",
        action="store_true",
        help="start a new cursor-agent chat instead of reusing .last-run/agent-session.json",
    )
    args = parser.parse_args(argv)

    verbose = not args.quiet
    report = Report(
        started_at=datetime.now(timezone.utc).isoformat(),
        mode=args.mode,
    )
    run_dir = _create_run_dir()

    agent_session: AgentSession | None = None
    if args.mode in ("coarse", "all", "ai-judge", "seed-expected"):
        try:
            agent_session = get_or_create_session(
                _SESSION_FILE,
                _STORIES_ROOT,
                fresh=args.fresh_session,
            )
        except FileNotFoundError:
            if args.mode == "coarse":
                raise SystemExit("cursor-agent not on PATH") from None
        if verbose and agent_session is not None:
            print(
                f"[agent] session {agent_session.chat_id[:8]}… "
                f"({'new' if args.fresh_session else 'reused'})",
                flush=True,
            )

    if args.mode in ("rules", "all"):
        report.rule_results = run_rule_battery(verbose=verbose)
    if args.mode in ("ai-judge", "all"):
        report.ai_judge_results = run_ai_judge(
            model=args.model, verbose=verbose, session=agent_session,
        )
    if args.mode in ("coarse", "all"):
        report.coarse_results = run_coarse_cases(
            model=args.model,
            verbose=verbose,
            run_dir=run_dir,
            case_filter=args.cases,
            coarse_judge=not args.no_coarse_judge,
            session=agent_session,
        )
    if args.mode == "seed-expected":
        run_seed_expected(
            model=args.model,
            verbose=verbose,
            run_dir=run_dir,
            case_filter=args.cases,
            session=agent_session,
        )
        return 0

    _write_report(report, run_dir)
    print()
    print(f"Report:   {_REPORT_JSON.relative_to(_REPO_ROOT)}")
    print(f"Summary:  {_REPORT_TXT.relative_to(_REPO_ROOT)}")
    print(f"Scratch:  {_LAST_RUN_DIR.relative_to(_REPO_ROOT)}")

    rule_ok = all(r.ok for r in report.rule_results)
    judge_ok = all(
        (r.fixture == "pass" and r.verdict == "PASS") or
        (r.fixture == "fail" and r.verdict == "FAIL")
        for r in report.ai_judge_results
    )
    coarse_ok = all(r.ok for r in report.coarse_results)
    return 0 if (rule_ok and judge_ok and coarse_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
