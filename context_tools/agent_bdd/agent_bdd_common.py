"""Shared agent BDD types, helpers, session management, manifest parsing, and runbook building."""
from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent_bdd.yaml_fence import fenced, load_fenced

_TOOLS_RUN = re.compile(r"(?:python\s+-m\s+tools\s+run|tools\s+run\b)", re.IGNORECASE)

JUDGE_TASK = """\
You are an AI judge.
Evaluate OUTPUT against RUBRIC.
Reply with ONLY one JSON object on one line — no markdown, no code fences, no commentary.
The JSON must have keys verdict (PASS or FAIL) and reason (one sentence).

--- RUBRIC ---
{rubric}

--- OUTPUT ---
{output}
"""

JUDGE_LAUNCH = (
    "Read {path} and follow it exactly. "
    "Reply with only one JSON line as specified in that file."
)

RUN_PROMPT_SUFFIX = (
    "\n\nIMPORTANT: Invoke python -m tools run via shell. "
    "Return the complete fenced YAML stdout from the CLI. Do not summarize."
)

CMDLINE_SAFE = 4096

INBOX_POLL_SECONDS = 0.25


class AgentHarnessError(RuntimeError):
    """Agent or CLI step failed — carries artifacts for debugging."""

    def __init__(
        self,
        message: str,
        *,
        prefix: str = "",
        exit_code: int | None = None,
        stdout: str = "",
        stderr: str = "",
        log_dir: Path | None = None,
    ) -> None:
        super().__init__(message)
        self.prefix = prefix
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.log_dir = log_dir


class AgentJudgeError(AgentHarnessError):
    """Judge did not return a parseable JSON verdict."""


class ChatInboxPending(AgentHarnessError):
    """Chat harness wrote an inbox prompt and waits for a response file."""


@dataclass(frozen=True)
class AgentResult:
    """Outcome of a single agent instruct run."""

    exit_code: int
    text: str
    stderr: str
    elapsed_seconds: float

    def ok(self) -> bool:
        return self.exit_code == 0


@dataclass(frozen=True)
class JudgeResult:
    """Structured outcome from an AI judge run."""

    verdict: str
    reason: str
    elapsed_seconds: float = 0.0

    def passed(self) -> bool:
        return self.verdict == "PASS"

    def failed(self) -> bool:
        return self.verdict == "FAIL"


@dataclass(frozen=True)
class RunResponse:
    """Parsed fenced YAML from ``python -m tools run`` CLI stdout."""

    ok: bool
    toolset: str
    result: Any
    resources: dict[str, Any]
    tool: str | None = None
    action: str | None = None
    instructions: str | None = None
    tools: list[str] | None = None
    arguments: dict[str, Any] | None = None

    @classmethod
    def from_cli_output(cls, text: str) -> RunResponse:
        data = load_fenced(text)
        if not isinstance(data, dict):
            raise AgentHarnessError(f"tools run output is not a mapping: {text[:200]!r}")
        if not data.get("ok"):
            error = str(data.get("error") or "unknown error")
            raise AgentHarnessError(f"tools run returned ok: false — {error}", stdout=text)
        tools_field = data.get("tools")
        return cls(
            ok=True,
            toolset=str(data.get("toolset", "")),
            tool=str(data["tool"]) if data.get("tool") else None,
            action=str(data["action"]) if data.get("action") else None,
            result=data.get("result"),
            instructions=str(data["instructions"]) if data.get("instructions") else None,
            tools=list(tools_field) if isinstance(tools_field, list) else None,
            arguments=dict(data["arguments"]) if isinstance(data.get("arguments"), dict) else None,
            resources=dict(data.get("resources") or {}),
        )


@dataclass(frozen=True)
class ShellCapture:
    command: str
    output: str


_CHAT_ID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


@dataclass
class AgentSession:
    """Persistent cursor-agent chat session backed by a JSON file."""

    chat_id: str
    session_file: Path

    @staticmethod
    def launcher() -> str | None:
        return shutil.which("cursor-agent")

    @classmethod
    def load(cls, session_file: Path) -> AgentSession | None:
        if not session_file.is_file():
            return None
        try:
            data = json.loads(session_file.read_text(encoding="utf-8"))
            chat_id = str(data.get("chat_id", "")).strip()
        except (OSError, json.JSONDecodeError):
            return None
        return cls(chat_id=chat_id, session_file=session_file) if chat_id else None

    def save(self) -> None:
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self.session_file.write_text(
            json.dumps({"chat_id": self.chat_id}, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def get_or_create(
        cls, session_file: Path, workspace: Path, *, fresh: bool = False
    ) -> AgentSession:
        if not fresh:
            existing = cls.load(session_file)
            if existing is not None:
                log_harness("cursor_channel", f"session resumed: {existing.chat_id} ({session_file.name})")
                return existing
        exe = cls.launcher()
        if exe is None:
            raise RuntimeError("cursor-agent not found on PATH")
        log_harness("cursor_channel", f"creating new session for {session_file.name} in {workspace} ...")
        completed = subprocess.run(
            [exe, "create-chat", "--workspace", str(workspace.resolve())],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"cursor-agent create-chat failed (exit {completed.returncode}).\n"
                f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
            )
        match = _CHAT_ID_RE.search(completed.stdout)
        if not match:
            raise RuntimeError(
                f"cursor-agent create-chat returned no chat id.\n"
                f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
            )
        session = cls(chat_id=match.group(0), session_file=session_file)
        session.save()
        log_harness("cursor_channel", f"session created: {session.chat_id}")
        return session

    def run(self, prompt: str, workspace: Path, *, timeout_seconds: int = 300) -> AgentResult:
        exe = self.launcher()
        if exe is None:
            raise RuntimeError("cursor-agent not found on PATH")
        log_harness(
            "cursor_channel",
            f"agent run starting (session={self.chat_id[:8]}…, timeout={timeout_seconds}s)",
        )
        args = [
            exe,
            "-p",
            "--force",
            "--trust",
            "--resume",
            self.chat_id,
            "--workspace",
            str(workspace.resolve()),
            "--output-format",
            "stream-json",
            "--stream-partial-output",
            prompt,
        ]
        narrative: list[str] = []
        raw_lines: list[str] = []
        stderr_buf: list[str] = []
        thread_errors: list[str] = []

        def _on_stdout() -> None:
            try:
                assert proc.stdout
                for raw in proc.stdout:
                    raw_lines.append(raw)
                    try:
                        event = json.loads(raw.strip())
                    except json.JSONDecodeError:
                        sys.__stdout__.write(raw)
                        sys.__stdout__.flush()
                        continue
                    etype = event.get("type", "?")
                    if etype == "assistant":
                        for block in (event.get("message") or {}).get("content") or []:
                            if not isinstance(block, dict):
                                continue
                            btype = block.get("type", "")
                            if btype == "text":
                                text = block.get("text", "")
                                narrative.append(text)
                                sys.__stdout__.write(text)
                                sys.__stdout__.flush()
                            elif btype == "tool_use":
                                name = block.get("name", "?")
                                inp = json.dumps(block.get("input", {}))[:120]
                                log_harness("cursor_channel", f"tool_use: {name}({inp})")
                    elif etype == "result":
                        text = event.get("result", "")
                        narrative.append(text)
                        sys.__stdout__.write(text + "\n")
                        sys.__stdout__.flush()
            except Exception as exc:  # noqa: BLE001
                thread_errors.append(f"stdout thread error: {exc}")

        def _on_stderr() -> None:
            try:
                assert proc.stderr
                for chunk in iter(lambda: proc.stderr.read(4096), ""):
                    stderr_buf.append(chunk)
                    sys.__stderr__.write(chunk)
                    sys.__stderr__.flush()
            except Exception as exc:  # noqa: BLE001
                thread_errors.append(f"stderr thread error: {exc}")

        started = time.perf_counter()
        proc = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )
        threads = [
            threading.Thread(target=_on_stdout, daemon=True),
            threading.Thread(target=_on_stderr, daemon=True),
        ]
        for t in threads:
            t.start()

        try:
            exit_code = proc.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            log_harness("cursor_channel", f"TIMEOUT after {timeout_seconds}s — killing cursor-agent")
            proc.kill()
            proc.wait()
            raise
        for t in threads:
            t.join()

        elapsed = time.perf_counter() - started
        if thread_errors:
            log_harness("cursor_channel", f"stream errors: {'; '.join(thread_errors)}")
        return AgentResult(
            exit_code=exit_code,
            text="".join(narrative) or "".join(raw_lines),
            stderr="".join(stderr_buf),
            elapsed_seconds=elapsed,
        )


def log_harness(name: str, msg: str) -> None:
    import time

    ts = time.strftime("%H:%M:%S")
    sys.__stdout__.write(f"[{name} {ts}] {msg}\n")
    sys.__stdout__.flush()


def looks_like_tools_run_output(text: str) -> bool:
    if "ok:" not in text:
        return False
    return "resources:" in text or "instructions:" in text or "action:" in text


def fenced_yaml_from_text(text: str) -> str | None:
    if "ok:" not in text:
        return None
    for match in re.finditer(r"```(?:yaml)?\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE):
        block = match.group(1)
        if looks_like_tools_run_output(block):
            return fenced(block.strip())
    return None


def extract_yaml_from_command(command: str) -> str | None:
    powershell = re.search(r'@"\s*\r?\n(.*?)\"@', command, re.DOTALL)
    if powershell:
        return powershell.group(1).strip()
    bash = re.search(r"<<-?\s*['\"]?(\w+)['\"]?\s*\r?\n(.*?)^\1", command, re.DOTALL | re.MULTILINE)
    if bash:
        return bash.group(2).strip()
    return None


def yaml_from_prompt(prompt: str) -> str | None:
    marker = re.search(
        r"(?:stdin:|YAML on stdin:)\s*\n+(toolset:.*?)(?:\n\nIMPORTANT:|\Z)",
        prompt,
        re.DOTALL | re.IGNORECASE,
    )
    if marker:
        return _sanitize_yaml_body(marker.group(1))
    if "toolset:" not in prompt:
        return None
    lines: list[str] = []
    collecting = False
    for line in prompt.splitlines():
        stripped = line.strip()
        if stripped.startswith("toolset:"):
            collecting = True
        if collecting:
            if stripped.startswith("IMPORTANT:"):
                break
            if stripped.startswith("Return the complete"):
                break
            lines.append(line)
    body = "\n".join(lines).strip()
    return body or None


def _sanitize_yaml_body(body: str) -> str:
    lines: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("IMPORTANT:"):
            break
        if stripped.startswith("Return the complete"):
            break
        lines.append(line)
    return "\n".join(lines).strip()


def expected_run_fields_from_prompt(prompt: str) -> dict[str, str]:
    body = yaml_from_prompt(prompt)
    if not body:
        return {}
    expected: dict[str, str] = {}
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("action:"):
            expected["action"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("tool:"):
            expected["tool"] = stripped.split(":", 1)[1].strip()
    return expected


def cli_output_matches_prompt(cli_output: str, prompt: str) -> bool:
    expected = expected_run_fields_from_prompt(prompt)
    if not expected:
        return True
    try:
        parsed = RunResponse.from_cli_output(cli_output)
    except AgentHarnessError:
        return False
    if "action" in expected and parsed.action != expected["action"]:
        return False
    if "tool" in expected and parsed.tool != expected["tool"]:
        return False
    return True


def run_yaml_request(yaml_body: str, workspace: Path, *, prefix: str = "") -> str:
    completed = subprocess.run(
        [sys.executable, "-m", "tools", "run", "-"],
        input=yaml_body,
        capture_output=True,
        text=True,
        cwd=workspace,
        check=False,
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if completed.returncode != 0:
        raise AgentHarnessError(
            f"tools run exited {completed.returncode}",
            prefix=prefix,
            exit_code=completed.returncode,
            stdout=stdout,
            stderr=stderr,
        )
    if not stdout or "ok:" not in stdout:
        raise AgentHarnessError(
            "tools run produced no ok: response",
            prefix=prefix,
            stdout=stdout,
            stderr=stderr,
        )
    RunResponse.from_cli_output(stdout)
    return stdout


def replay_tools_run(command: str, workspace: Path) -> str | None:
    if not _TOOLS_RUN.search(command):
        return None
    yaml_body = extract_yaml_from_command(command)
    if not yaml_body:
        return None
    try:
        return run_yaml_request(yaml_body, workspace)
    except AgentHarnessError:
        return None


def parse_judge_result(stdout: str) -> tuple[str, str]:
    last_pass: tuple[str, str] | None = None
    last_fail: tuple[str, str] | None = None
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        parsed = parse_judge_json(line)
        if parsed is None:
            continue
        verdict, reason = parsed
        if verdict == "PASS":
            last_pass = (verdict, reason)
            break
        if verdict == "FAIL":
            last_fail = (verdict, reason)
    if last_pass:
        return last_pass
    if last_fail:
        return last_fail
    embedded = embedded_judge_verdicts(stdout)
    if embedded:
        for verdict, reason in reversed(embedded):
            if verdict == "PASS":
                return verdict, reason
        for verdict, reason in reversed(embedded):
            if verdict == "FAIL":
                return verdict, reason
    return "ERROR", f"no parseable verdict in output:\n{stdout[:500]}"


def parse_judge_json(text: str) -> tuple[str, str] | None:
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    verdict = str(obj.get("verdict", "")).strip().upper()
    reason = str(obj.get("reason", "")).strip()
    if verdict not in {"PASS", "FAIL"}:
        return None
    return verdict, reason


def embedded_judge_verdicts(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    decoder = json.JSONDecoder()
    index = 0
    while index < len(text):
        start = text.find('{"verdict"', index)
        if start < 0:
            start = text.find('{"Verdict"', index)
        if start < 0:
            break
        try:
            obj, end = decoder.raw_decode(text, start)
        except json.JSONDecodeError:
            index = start + 1
            continue
        parsed = parse_judge_json(json.dumps(obj))
        if parsed is not None:
            found.append(parsed)
        index = end
    return found


# ---------------------------------------------------------------------------
# Manifest — @agent-spec-manifest header parsing
# ---------------------------------------------------------------------------

AGENT_SPEC_MARKER = "@agent-spec-manifest"
_HARNESS_RE = re.compile(r"^\s*#\s*harness:\s*(\S+)", re.IGNORECASE | re.MULTILINE)
_SESSION_RE = re.compile(r"^\s*#\s*session:\s*(\S+)", re.IGNORECASE | re.MULTILINE)
_AGENT_READING_RE = re.compile(
    r"^\s*#\s*Agent reading this file:\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class AgentSpecManifest:
    spec_path: Path
    command: str
    harness: str
    session: str | None
    chat_instruction: str | None

    @property
    def in_chat(self) -> bool:
        return self.harness == "in_chat"

    @property
    def judge_session(self) -> str | None:
        if not self.session:
            return None
        path = Path(self.session)
        stem = path.stem
        return path.with_name(f"{stem}-judge.json").as_posix()


def read_manifest(spec_path: Path) -> AgentSpecManifest:
    """Load manifest metadata from comment headers at the top of an agent spec file."""
    text = spec_path.read_text(encoding="utf-8")
    command = _find_marker_command(text)
    if command is None:
        raise ValueError(f"{spec_path}: missing {AGENT_SPEC_MARKER} comment")
    harness = _HARNESS_RE.search(text)
    session = _SESSION_RE.search(text)
    chat = _AGENT_READING_RE.search(text)
    harness_value = harness.group(1).strip().lower() if harness else "cli"
    return AgentSpecManifest(
        spec_path=spec_path.resolve(),
        command=command.strip(),
        harness=harness_value,
        session=session.group(1).strip() if session else None,
        chat_instruction=chat.group(1).strip() if chat else None,
    )


def _find_marker_command(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            if stripped and not stripped.startswith('"""') and not stripped.startswith("'''"):
                break
            continue
        body = stripped.lstrip("#").strip()
        if AGENT_SPEC_MARKER not in body:
            continue
        remainder = body.split(AGENT_SPEC_MARKER, 1)[1].strip()
        if remainder.startswith(":"):
            remainder = remainder[1:].strip()
        if remainder:
            return remainder
    return None


# ---------------------------------------------------------------------------
# Runbook — build chat runbook YAML from an agent spec Python file
# ---------------------------------------------------------------------------

@dataclass
class RunbookStep:
    kind: str
    prompt: str | None = None
    save_as: str | None = None
    timeout_seconds: int | None = None


@dataclass
class RunbookAssertion:
    description: str
    expression: str


@dataclass
class RunbookJudge:
    description: str
    output: str
    rubric: str


@dataclass
class RunbookScenario:
    name: str
    session: str | None
    setup: list[RunbookStep] = field(default_factory=list)
    assertions: list[RunbookAssertion] = field(default_factory=list)
    judges: list[RunbookJudge] = field(default_factory=list)


@dataclass
class AgentSpecRunbook:
    harness: str
    workspace: str
    spec_path: str
    chat_instruction: str | None
    scenarios: list[RunbookScenario]

    def to_dict(self) -> dict[str, Any]:
        return {
            "harness": self.harness,
            "workspace": self.workspace,
            "spec_path": self.spec_path,
            "chat_instruction": self.chat_instruction,
            "scenarios": [
                {
                    "name": scenario.name,
                    "session": scenario.session,
                    "setup": [
                        {
                            "kind": step.kind,
                            "prompt": step.prompt,
                            "save_as": step.save_as,
                            "timeout_seconds": step.timeout_seconds,
                        }
                        for step in scenario.setup
                    ],
                    "assertions": [
                        {"description": item.description, "expression": item.expression}
                        for item in scenario.assertions
                    ],
                    "judges": [
                        {
                            "description": item.description,
                            "output": item.output,
                            "rubric": item.rubric,
                        }
                        for item in scenario.judges
                    ],
                }
                for scenario in self.scenarios
            ],
        }


def _infer_repo_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "primitives").is_dir() and (parent / "contexts").is_dir():
            return parent
    return start.parent.parent


def build_runbook(spec_path: Path, *, workspace: Path | None = None) -> AgentSpecRunbook:
    manifest = read_manifest(spec_path)
    repo_root = workspace or _infer_repo_root(spec_path.resolve().parent)
    source = spec_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    scenarios = _extract_scenarios(tree, manifest, source)
    return AgentSpecRunbook(
        harness=manifest.harness,
        workspace=str(repo_root.resolve()),
        spec_path=str(manifest.spec_path),
        chat_instruction=manifest.chat_instruction,
        scenarios=scenarios,
    )


def _extract_scenarios(
    tree: ast.Module, manifest: AgentSpecManifest, source: str
) -> list[RunbookScenario]:
    scenarios: list[RunbookScenario] = []
    current_name = "default"
    current_session = manifest.session
    setup_steps: list[RunbookStep] = []
    pending_it: str | None = None

    for node in ast.walk(tree):
        if isinstance(node, ast.With):
            context_name = _with_context_name(node)
            if context_name:
                if setup_steps or pending_it:
                    scenarios.append(
                        RunbookScenario(
                            name=current_name,
                            session=current_session,
                            setup=list(setup_steps),
                        )
                    )
                    setup_steps = []
                current_name = context_name
                if "agent" in context_name.lower():
                    current_session = manifest.session

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr in {"instruct", "instruct_use_tool"}:
                prompt = _rb_prompt_arg(source, tree.body, node, 0)
                if prompt:
                    save_as = _rb_assignment_target(tree, node, source)
                    timeout = _rb_keyword_int(node, "timeout_seconds")
                    setup_steps.append(
                        RunbookStep(
                            kind=attr,
                            prompt=prompt,
                            save_as=save_as,
                            timeout_seconds=timeout,
                        )
                    )
            elif attr == "ai_judge":
                output = _rb_expression_source(source, node.args[0]) if node.args else ""
                rubric = _rb_prompt_arg(source, tree.body, node, 1) or ""
                scenarios.append(
                    RunbookScenario(
                        name=current_name,
                        session=current_session,
                        setup=list(setup_steps),
                        judges=[
                            RunbookJudge(
                                description=pending_it or "ai_judge",
                                output=output,
                                rubric=rubric,
                            )
                        ],
                    )
                )
                setup_steps = []
                pending_it = None

        if isinstance(node, ast.Call) and _rb_is_expect_call(node):
            desc = pending_it or "assertion"
            expression = _rb_expression_source(source, node)
            if scenarios and scenarios[-1].name == current_name and not scenarios[-1].setup:
                scenarios[-1].assertions.append(RunbookAssertion(description=desc, expression=expression))
            else:
                scenario = next((s for s in scenarios if s.name == current_name), None)
                if scenario is None:
                    scenario = RunbookScenario(
                        name=current_name,
                        session=current_session,
                        setup=list(setup_steps),
                    )
                    scenarios.append(scenario)
                scenario.assertions.append(RunbookAssertion(description=desc, expression=expression))
            pending_it = None

        if isinstance(node, ast.With):
            it_desc = _rb_it_description(node)
            if it_desc:
                pending_it = it_desc

    if setup_steps:
        scenarios.append(
            RunbookScenario(
                name=current_name,
                session=current_session,
                setup=list(setup_steps),
            )
        )

    merged = _rb_merge_scenarios(scenarios)
    if not merged and manifest.session:
        merged = [
            RunbookScenario(name="default", session=manifest.session, setup=setup_steps),
        ]
    return merged


def _rb_merge_scenarios(scenarios: list[RunbookScenario]) -> list[RunbookScenario]:
    by_name: dict[str, RunbookScenario] = {}
    for scenario in scenarios:
        existing = by_name.get(scenario.name)
        if existing is None:
            by_name[scenario.name] = scenario
            continue
        existing.setup.extend(scenario.setup)
        existing.assertions.extend(scenario.assertions)
        existing.judges.extend(scenario.judges)
        if scenario.session:
            existing.session = scenario.session
    return list(by_name.values())


def _with_context_name(node: ast.With) -> str | None:
    for item in node.items:
        if isinstance(item.context_expr, ast.Call):
            func = item.context_expr.func
            if isinstance(func, ast.Name) and func.id == "context":
                if item.context_expr.args and isinstance(item.context_expr.args[0], ast.Constant):
                    return str(item.context_expr.args[0].value)
            if isinstance(func, ast.Attribute) and func.attr == "context":
                if item.context_expr.args and isinstance(item.context_expr.args[0], ast.Constant):
                    return str(item.context_expr.args[0].value)
    return None


def _rb_it_description(node: ast.With) -> str | None:
    for item in node.items:
        if isinstance(item.context_expr, ast.Call):
            func = item.context_expr.func
            if isinstance(func, ast.Name) and func.id == "it":
                if item.context_expr.args and isinstance(item.context_expr.args[0], ast.Constant):
                    return str(item.context_expr.args[0].value)
    return None


def _rb_string_arg(node: ast.Call, index: int) -> str | None:
    if len(node.args) <= index:
        return None
    arg = node.args[index]
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return arg.value
    return None


def _rb_prompt_arg(source: str, module_body: list[ast.stmt], node: ast.Call, index: int) -> str | None:
    literal = _rb_string_arg(node, index)
    if literal is not None:
        return literal
    if len(node.args) <= index:
        return None
    return _rb_resolve_string_expr(source, module_body, node.args[index])


def _rb_resolve_string_expr(source: str, module_body: list[ast.stmt], arg: ast.AST) -> str | None:
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return arg.value
    if isinstance(arg, ast.JoinedStr):
        parts: list[str] = []
        for piece in arg.values:
            if isinstance(piece, ast.Constant) and isinstance(piece.value, str):
                parts.append(piece.value)
            elif isinstance(piece, ast.FormattedValue):
                resolved = _rb_resolve_formatted_value(source, module_body, piece)
                if resolved is None:
                    return None
                parts.append(resolved)
        return "".join(parts)
    segment = ast.get_source_segment(source, arg)
    if segment is None:
        return None
    if (segment.startswith('"') and segment.endswith('"')) or (
        segment.startswith("'") and segment.endswith("'")
    ):
        return ast.literal_eval(segment)
    if segment.startswith('f"') or segment.startswith("f'"):
        return None
    return segment


def _rb_resolve_formatted_value(
    source: str, module_body: list[ast.stmt], piece: ast.FormattedValue
) -> str | None:
    value = piece.value
    if isinstance(value, ast.Name):
        for stmt in module_body:
            if not isinstance(stmt, ast.Assign):
                continue
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == value.id:
                    if isinstance(stmt.value, ast.Constant):
                        return str(stmt.value.value)
        return None
    if isinstance(value, ast.Constant):
        return str(value.value)
    segment = ast.get_source_segment(source, value)
    return segment


def _rb_keyword_int(node: ast.Call, name: str) -> int | None:
    for keyword in node.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant):
            if isinstance(keyword.value.value, int):
                return keyword.value.value
    return None


def _rb_is_expect_call(node: ast.Call) -> bool:
    func = node.func
    return isinstance(func, ast.Name) and func.id == "expect"


def _rb_expression_source(source: str, node: ast.AST) -> str:
    try:
        return ast.get_source_segment(source, node) or ""
    except (TypeError, ValueError):
        return ""


def _rb_assignment_target(tree: ast.Module, call_node: ast.Call, source: str) -> str | None:
    call_line = getattr(call_node, "lineno", None)
    if call_line is None:
        return None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        if node.value is call_node or (
            getattr(node.value, "lineno", None) == call_line
            and getattr(node.value, "col_offset", None) == getattr(call_node, "col_offset", None)
        ):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Attribute):
                target = node.targets[0]
                if isinstance(target.value, ast.Name):
                    return f"{target.value.id}.{target.attr}"
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                return node.targets[0].id
    prompt = _rb_prompt_arg(source, tree.body, call_node, 0) or ""
    slug = re.sub(r"[^a-z0-9]+", "_", prompt[:40].lower()).strip("_")
    return slug or None
