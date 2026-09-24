"""Shared agent BDD types, helpers, session management, and runbook building."""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypedDict

from agent_bdd.yaml_fence import YamlFence

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

_TOOLS_RUN = re.compile(
    r"(?:toolset:\s*\S|action:\s*\w|tool:\s*\w)",
    re.IGNORECASE,
)

JUDGE_TASK = """\
You are an AI judge.
Evaluate OUTPUT against RUBRIC.
Reply with ONLY one JSON object on one line - no markdown, no code fences, no commentary.
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

AGENT_DEFERRAL_PHRASES = (
    "paste the",
    "paste the full",
    "paste the exact",
    "didn't come through",
    "did not come through",
    "missing from your message",
    "nothing after the colon",
    "command itself is missing",
    "didn't come through after the colon",
)

CMDLINE_SAFE = 4096

INBOX_POLL_SECONDS = 0.25


class AgentHarnessError(RuntimeError):
    """Agent or CLI step failed - carries artifacts for debugging."""

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

    @property
    def stdout(self) -> str:
        """Alias for text — the agent's captured stdout."""
        return self.text

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

    @classmethod
    def from_stdout(cls, stdout: str, elapsed_seconds: float = 0.0) -> JudgeResult:
        parsed = cls(verdict="ERROR", reason="")._parsed(stdout)
        return cls(
            verdict=parsed.verdict,
            reason=parsed.reason,
            elapsed_seconds=elapsed_seconds,
        )

    def _parsed(self, stdout: str) -> JudgeResult:
        line_verdict = self._verdict_from_json_lines(stdout)
        if line_verdict is not None:
            return JudgeResult(verdict=line_verdict[0], reason=line_verdict[1])
        embedded = self._preferred_embedded_verdict(stdout)
        if embedded is not None:
            return JudgeResult(verdict=embedded[0], reason=embedded[1])
        return JudgeResult(
            verdict="ERROR",
            reason=f"no parseable verdict in output:\n{stdout[:500]}",
        )

    def _verdict_from_json_lines(self, stdout: str) -> tuple[str, str] | None:
        last_fail: tuple[str, str] | None = None
        for line in reversed(stdout.splitlines()):
            parsed = self._parse_judge_json(line.strip())
            if parsed is None:
                continue
            verdict, reason = parsed
            if verdict == "PASS":
                return verdict, reason
            if verdict == "FAIL":
                last_fail = (verdict, reason)
        return last_fail

    def _preferred_embedded_verdict(self, stdout: str) -> tuple[str, str] | None:
        embedded = self._embedded_judge_verdicts(stdout)
        for verdict, reason in reversed(embedded):
            if verdict == "PASS":
                return verdict, reason
        for verdict, reason in reversed(embedded):
            if verdict == "FAIL":
                return verdict, reason
        return None

    def _parse_judge_json(self, text: str) -> tuple[str, str] | None:
        if not text.startswith("{"):
            return None
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

    def _embedded_judge_verdicts(self, text: str) -> list[tuple[str, str]]:
        self._judge_text = text
        self._decoder = json.JSONDecoder()
        found: list[tuple[str, str]] = []
        index = 0
        while index < len(self._judge_text):
            start = self._next_verdict_start(index)
            if start < 0:
                break
            parsed, index = self._decode_embedded_verdict(start)
            if parsed is not None:
                found.append(parsed)
        return found

    def _next_verdict_start(self, index: int) -> int:
        start = self._judge_text.find('{"verdict"', index)
        if start >= 0:
            return start
        return self._judge_text.find('{"Verdict"', index)

    def _decode_embedded_verdict(self, start: int) -> tuple[tuple[str, str] | None, int]:
        try:
            obj, end = self._decoder.raw_decode(self._judge_text, start)
        except json.JSONDecodeError:
            return None, start + 1
        return self._parse_judge_json(json.dumps(obj)), end


@dataclass(frozen=True)
class RunResponse:
    """Parsed spec invoke response."""

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
    def from_dict(cls, run_mapping: dict[str, Any]) -> RunResponse:
        if not isinstance(run_mapping, dict):
            raise AgentHarnessError(f"run output is not a mapping: {run_mapping!r}")
        if not run_mapping.get("ok"):
            error = str(run_mapping.get("error") or "unknown error")
            raise AgentHarnessError(f"run returned ok: false - {error}")
        tools_field = run_mapping.get("tools")
        result = run_mapping.get("result")
        return cls(
            ok=True,
            toolset=str(run_mapping.get("toolset", "")),
            tool=str(run_mapping["tool"]) if run_mapping.get("tool") else None,
            action=str(run_mapping["action"]) if run_mapping.get("action") else None,
            result=result,
            instructions=str(run_mapping["instructions"]) if run_mapping.get("instructions") else None,
            tools=list(tools_field) if isinstance(tools_field, list) else None,
            arguments=dict(run_mapping["arguments"]) if isinstance(run_mapping.get("arguments"), dict) else None,
            resources=dict(run_mapping.get("resources") or {}),
        )

    @classmethod
    def from_cli_output(cls, text: str) -> RunResponse:
        data = YamlFence().load_fenced(text)
        if not isinstance(data, dict):
            raise AgentHarnessError(f"run output is not a mapping: {text[:200]!r}")
        return cls.from_dict(data)


@dataclass(frozen=True)
class _ShellCapture:
    command: str
    output: str


_CHAT_ID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


class HarnessLog:
    """Write timestamped harness progress to the original stdout stream."""

    def __init__(self, name: str) -> None:
        self._name = name

    def write(self, msg: str) -> None:
        ts = time.strftime("%H:%M:%S")
        sys.__stdout__.write(f"[{self._name} {ts}] {msg}\n")
        sys.__stdout__.flush()


@dataclass
class AgentSession:
    """Persistent cursor-agent chat session backed by a JSON file."""

    chat_id: str
    session_file: Path

    def __post_init__(self) -> None:
        self._log = HarnessLog("cursor_channel")

    @classmethod
    def launcher(cls) -> str | None:
        from cli_agent.cli_agent import CursorCli

        return CursorCli().launcher()

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
    def from_workspace(
        cls, session_file: Path, workspace: Path, *, fresh: bool = False
    ) -> AgentSession:
        log = HarnessLog("cursor_channel")
        if not fresh:
            existing = cls.load(session_file)
            if existing is not None:
                log.write(f"session resumed: {existing.chat_id} ({session_file.name})")
                return existing
        from cli_agent.cli_agent import CursorCli

        log.write(f"creating new session for {session_file.name} in {workspace} ...")
        chat_id = CursorCli().create_chat(str(workspace.resolve()))
        session = cls(chat_id=chat_id, session_file=session_file)
        session.save()
        log.write(f"session created: {session.chat_id}")
        return session

    def run(self, prompt: str, workspace: Path, *, timeout_seconds: int = 300) -> AgentResult:
        from cli_agent.cli_agent import CursorCli

        self._log.write(
            f"agent run starting (session={self.chat_id[:8]}..., timeout={timeout_seconds}s)"
        )
        args = CursorCli(resume=self.chat_id).command(prompt, str(workspace.resolve()))
        started = time.perf_counter()
        completed = self._run_cursor_cli(args, workspace, timeout_seconds)
        elapsed = time.perf_counter() - started
        if completed.stderr:
            sys.__stderr__.write(completed.stderr)
            sys.__stderr__.flush()
        narrative = self._narrative_from_cli_stdout(completed.stdout or "")
        text = narrative or (completed.stdout or "")
        if text:
            sys.__stdout__.write(text if text.endswith("\n") else text + "\n")
            sys.__stdout__.flush()
        return AgentResult(
            exit_code=completed.returncode,
            text=text,
            stderr=completed.stderr or "",
            elapsed_seconds=elapsed,
        )

    def _run_cursor_cli(
        self, args: list[str], workspace: Path, timeout_seconds: int
    ) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                args,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                check=False,
                cwd=str(workspace.resolve()),
            )
        except subprocess.TimeoutExpired as exc:
            raise AgentHarnessError(
                f"cursor-agent timed out after {timeout_seconds}s",
                stdout=str(exc.stdout or ""),
                stderr=str(exc.stderr or ""),
            ) from exc

    def _narrative_from_cli_stdout(self, stdout: str) -> str:
        narrative: list[str] = []
        for raw in (stdout or "").splitlines():
            event = self._json_event(raw)
            if event is None:
                continue
            text = self._narrative_from_event(event)
            if text:
                narrative.append(text)
        return "".join(narrative)

    def _json_event(self, raw: str) -> dict[str, Any] | None:
        try:
            event = json.loads(raw.strip())
        except json.JSONDecodeError:
            return None
        return event if isinstance(event, dict) else None

    def _narrative_from_event(self, event: dict[str, Any]) -> str:
        etype = event.get("type", "")
        if etype == "assistant":
            return self._assistant_text(event)
        if etype == "result":
            return str(event.get("result", "") or "")
        return ""

    def _assistant_text(self, event: dict[str, Any]) -> str:
        parts: list[str] = []
        for block in (event.get("message") or {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "text":
                text = str(block.get("text", ""))
                if text:
                    parts.append(text)
        return "".join(parts)


class ToolsRunYaml:
    """Parse, replay, and fence toolset-run YAML from prompts and shell captures."""

    def __init__(self, workspace: Path | None = None, prefix: str = "") -> None:
        self._workspace = workspace
        self._prefix = prefix
        self._fence = YamlFence()

    def looks_like_tools_run_output(self, text: str) -> bool:
        has_ok_line = any(line.strip().startswith("ok:") for line in text.splitlines())
        if not has_ok_line:
            return False
        return any(
            line.strip().startswith(prefix)
            for line in text.splitlines()
            for prefix in ("resources:", "instructions:", "action:", "tool:")
        )

    def fenced_yaml_from_text(self, text: str) -> str | None:
        if "ok:" not in text:
            return None
        for match in re.finditer(r"```(?:yaml)?\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE):
            block = match.group(1)
            if self.looks_like_tools_run_output(block):
                return self._fence.fenced(block.strip())
        return None

    def extract_yaml_from_command(self, command: str) -> str | None:
        powershell = re.search(r'@"\s*\r?\n(.*?)\"@', command, re.DOTALL)
        if powershell:
            return powershell.group(1).strip()
        bash = re.search(r"<<-?\s*['\"]?(\w+)['\"]?\s*\r?\n(.*?)^\1", command, re.DOTALL | re.MULTILINE)
        if bash:
            return bash.group(2).strip()
        return None

    def yaml_from_prompt(self, prompt: str) -> str | None:
        heredoc = self.extract_yaml_from_command(prompt)
        if heredoc and heredoc.strip().startswith("toolset:"):
            return self._sanitize_yaml_body(heredoc)
        marker = re.search(
            r"(?:stdin:|YAML on stdin:)\s*\n+(toolset:.*?)(?:\n\nIMPORTANT:|\Z)",
            prompt,
            re.DOTALL | re.IGNORECASE,
        )
        if marker:
            return self._sanitize_yaml_body(marker.group(1))
        if "toolset:" not in prompt:
            return None
        return self._toolset_block_from_prompt(prompt)

    def _toolset_block_from_prompt(self, prompt: str) -> str | None:
        lines: list[str] = []
        collecting = False
        for line in prompt.splitlines():
            stripped = line.strip()
            if stripped.startswith("toolset:"):
                collecting = True
            if not collecting:
                continue
            if stripped.startswith("IMPORTANT:") or stripped.startswith("Return the complete"):
                break
            if stripped == '"@' or stripped == '@"':
                break
            lines.append(line)
        return "\n".join(lines).strip() or None

    def _sanitize_yaml_body(self, body: str) -> str:
        lines: list[str] = []
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("IMPORTANT:"):
                break
            if stripped.startswith("Return the complete"):
                break
            lines.append(line)
        return "\n".join(lines).strip()

    def expected_run_fields_from_prompt(self, prompt: str) -> dict[str, str]:
        body = self.yaml_from_prompt(prompt)
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

    def run_request(self, yaml_body: str) -> str:
        if yaml is None:
            raise AgentHarnessError("PyYAML required to parse run request", prefix=self._prefix)
        parsed = yaml.safe_load(yaml_body)
        if not isinstance(parsed, dict):
            raise AgentHarnessError("run request must be a mapping", prefix=self._prefix)
        response = invoke_run_request(parsed)
        return self._fence.fenced(self._fence.dump_manifest(response_to_dict(response)))

    def replay(self, command: str) -> str | None:
        if not _TOOLS_RUN.search(command):
            return None
        yaml_body = self.extract_yaml_from_command(command)
        if not yaml_body:
            return None
        try:
            return self.run_request(yaml_body)
        except AgentHarnessError:
            return None


def looks_like_tools_run_output(text: str) -> bool:
    """True when text looks like a fenced spec invoke response (not arbitrary prose)."""
    return ToolsRunYaml().looks_like_tools_run_output(text)


def yaml_from_prompt(prompt: str) -> str | None:
    return ToolsRunYaml().yaml_from_prompt(prompt)


def cli_output_matches_prompt(cli_output: str, prompt: str) -> bool:
    expected = ToolsRunYaml().expected_run_fields_from_prompt(prompt)
    if not expected:
        return True
    try:
        parsed = RunResponse.from_cli_output(cli_output)
    except Exception:
        # Malformed captures (e.g. Python source mistaken for YAML) must not abort
        # instruct_use_tool — callers fall back to replaying the prompt YAML.
        return False
    if "action" in expected and parsed.action != expected["action"]:
        return False
    if "tool" in expected and parsed.tool != expected["tool"]:
        return False
    return True


def reject_agent_deferral(agent_text: str) -> None:
    """Raise when the agent defers instead of running the embedded invoke block."""
    lowered = (agent_text or "").lower()
    for phrase in AGENT_DEFERRAL_PHRASES:
        if phrase in lowered:
            raise AgentHarnessError(
                f"agent deferred invoke ({phrase!r}) instead of running the request"
            )


class ToolsetInvoke:
    """Expand an action or invoke a tool on a live toolset instance."""

    def __init__(self, instance: Any, toolset_path: str) -> None:
        self._instance = instance
        self._toolset_path = toolset_path
        self._context: dict[str, Any] = {}
        self._arguments: dict[str, Any] = {}
        self._action_name: str | None = None
        self._tool_name: str | None = None

    @classmethod
    def create(cls, request: dict[str, Any]) -> ToolsetInvoke:
        from harness.agent_tools.agent_tools import AgentToolSet

        toolset_path = request.get("toolset")
        if not toolset_path:
            raise AgentHarnessError("request missing toolset")
        session = request.get("session")
        if session is not None:
            from workspace import SessionLog

            SessionLog.instance().set_session(str(session))
        context = dict(request.get("context") or {})
        arguments = dict(request.get("arguments") or {})
        try:
            instance = AgentToolSet.instantiate({"toolset": str(toolset_path), "context": context})
        except TypeError as exc:
            raise AgentHarnessError(str(exc)) from exc
        invoke = cls(instance, str(toolset_path))
        invoke._context = context
        invoke._arguments = arguments
        invoke._action_name = str(request["action"]) if request.get("action") else None
        invoke._tool_name = str(request["tool"]) if request.get("tool") else None
        return invoke

    def response(self) -> RunResponse:
        if self._action_name:
            return self.expanded_action()
        if not self._tool_name:
            raise AgentHarnessError("request missing tool or action")
        return self.invoked_tool()

    def expanded_action(self) -> RunResponse:
        try:
            expanded = self._instance.instructions[self._action_name].expand(
                self._context, self._arguments
            )
        except KeyError as exc:
            raise AgentHarnessError(f"unknown action {self._action_name!r}") from exc
        return RunResponse(
            ok=True,
            toolset=self._toolset_path,
            action=self._action_name,
            result=expanded.result,
            instructions=expanded.instructions,
            tools=list(expanded.tools),
            arguments=self._arguments,
            resources={},
        )

    def invoked_tool(self) -> RunResponse:
        from harness.agent_tools.agent_tools import AgentOperation

        member = self._instance.tools.get(self._tool_name)
        if member is None:
            raise AgentHarnessError(f"unknown tool {self._tool_name!r}")
        try:
            result = self._invoke_member(member)
        except TypeError as exc:
            raise AgentHarnessError(str(exc)) from exc
        return RunResponse(
            ok=True,
            toolset=self._toolset_path,
            tool=self._tool_name,
            result=result,
            resources={},
        )

    def _invoke_member(self, member: Any) -> Any:
        from harness.agent_tools.agent_tools import AgentOperation

        if isinstance(member, AgentOperation):
            return member.invoke(self._arguments)
        return getattr(self._instance, self._tool_name)(**self._arguments)


def invoke_run_request(request: dict[str, Any]) -> RunResponse:
    """Load a toolset and expand or invoke the named member the same way production does."""
    return ToolsetInvoke.create(request).response()


def response_to_dict(response: RunResponse) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": response.ok,
        "toolset": response.toolset,
        "result": response.result,
    }
    if response.tool:
        payload["tool"] = response.tool
    if response.action:
        payload["action"] = response.action
    if response.instructions is not None:
        payload["instructions"] = response.instructions
    if response.tools is not None:
        payload["tools"] = response.tools
    if response.arguments is not None:
        payload["arguments"] = response.arguments
    return payload


# ---------------------------------------------------------------------------
# Manifest - @agent-spec-manifest header parsing
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
        return self.installer == "in_chat"

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
    finder = AgentSpecRunbook()
    finder._source = text
    command = finder._find_marker_command()
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


# ---------------------------------------------------------------------------
# Runbook - build chat runbook YAML from an agent spec Python file
# ---------------------------------------------------------------------------

@dataclass
class _RunbookStep:
    kind: str
    prompt: str | None = None
    save_as: str | None = None
    timeout_seconds: int | None = None


@dataclass
class _RunbookAssertion:
    description: str
    expression: str


@dataclass
class _RunbookJudge:
    description: str
    output: str
    rubric: str


@dataclass
class _RunbookScenario:
    name: str
    session: str | None
    setup: list[_RunbookStep] = field(default_factory=list)
    assertions: list[_RunbookAssertion] = field(default_factory=list)
    judges: list[_RunbookJudge] = field(default_factory=list)


class _AgentSpecRunbookDocument(TypedDict):
    """Serializable agent-spec runbook for CLI / harness consumers."""

    harness: str
    workspace: str
    spec_path: str
    chat_instruction: str | None
    scenarios: list[dict[str, Any]]


@dataclass
class AgentSpecRunbook:
    harness: str = ""
    workspace: str = ""
    spec_path: str = ""
    chat_instruction: str | None = None
    scenarios: list[_RunbookScenario] = field(default_factory=list)

    def to_dict(self) -> _AgentSpecRunbookDocument:
        return {
            "harness": self.harness,
            "workspace": self.workspace,
            "spec_path": self.spec_path,
            "chat_instruction": self.chat_instruction,
            "scenarios": [self._scenario_to_dict(scenario) for scenario in self.scenarios],
        }

    def _scenario_to_dict(self, scenario: _RunbookScenario) -> dict[str, Any]:
        return {
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

    @classmethod
    def from_spec(cls, spec_path: Path, workspace: Path | None = None) -> AgentSpecRunbook:
        runbook = cls()
        runbook._assemble(spec_path, workspace)
        return runbook

    def _assemble(self, spec_path: Path, workspace: Path | None) -> None:
        self._manifest = read_manifest(spec_path)
        self._root_start = spec_path.resolve().parent
        repo_root = workspace or self._infer_repo_root()
        self._source = spec_path.read_text(encoding="utf-8")
        self._tree = ast.parse(self._source)
        self.harness = self._manifest.harness
        self.workspace = str(repo_root.resolve())
        self.spec_path = str(self._manifest.spec_path)
        self.chat_instruction = self._manifest.chat_instruction
        self.scenarios = self._extract_scenarios()

    def _infer_repo_root(self) -> Path:
        for parent in [self._root_start, *self._root_start.parents]:
            if (parent / "harness").is_dir() and (parent / "contexts").is_dir():
                return parent
        return self._root_start.parent.parent

    def _find_marker_command(self) -> str | None:
        for line in self._source.splitlines():
            command = self._marker_command_from_line(line)
            if command is not None:
                return command
            if self._stops_header_scan(line):
                return None
        return None

    def _stops_header_scan(self, line: str) -> bool:
        stripped = line.strip()
        if stripped.startswith("#"):
            return False
        if not stripped or stripped.startswith('"""') or stripped.startswith("'''"):
            return False
        return True

    def _marker_command_from_line(self, line: str) -> str | None:
        stripped = line.strip()
        if not stripped.startswith("#"):
            return None
        body = stripped.lstrip("#").strip()
        if AGENT_SPEC_MARKER not in body:
            return None
        remainder = body.split(AGENT_SPEC_MARKER, 1)[1].strip()
        if remainder.startswith(":"):
            remainder = remainder[1:].strip()
        return remainder or None

    def _extract_scenarios(self) -> list[_RunbookScenario]:
        self._collected: list[_RunbookScenario] = []
        self._current_name = "default"
        self._current_session = self._manifest.session
        self._setup_steps: list[_RunbookStep] = []
        self._pending_it: str | None = None
        for node in ast.walk(self._tree):
            self._ingest_node(node)
        self._append_remaining_setup()
        return self._merged_scenarios()

    def _ingest_node(self, node: ast.AST) -> None:
        if isinstance(node, ast.With):
            self._ingest_with(node)
        if isinstance(node, ast.Call):
            self._ingest_call(node)

    def _ingest_with(self, node: ast.With) -> None:
        context_name = self._with_context_name(node)
        if context_name:
            self._begin_named_context(context_name)
        it_desc = self._it_description(node)
        if it_desc:
            self._pending_it = it_desc

    def _begin_named_context(self, context_name: str) -> None:
        if self._setup_steps or self._pending_it:
            self._collected.append(
                _RunbookScenario(
                    name=self._current_name,
                    session=self._current_session,
                    setup=list(self._setup_steps),
                )
            )
            self._setup_steps = []
        self._current_name = context_name
        if "agent" in context_name.lower():
            self._current_session = self._manifest.session

    def _ingest_call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute):
            self._ingest_attribute_call(node)
        if self._is_expect_call(node):
            self._record_expect(node)

    def _ingest_attribute_call(self, node: ast.Call) -> None:
        attr = node.func.attr
        if attr in {"instruct", "instruct_use_tool"}:
            self._record_instruct(node, attr)
            return
        if attr == "ai_judge":
            self._record_judge(node)

    def _record_instruct(self, node: ast.Call, attr: str) -> None:
        prompt = self._prompt_arg(node, 0)
        if not prompt:
            return
        self._setup_steps.append(
            _RunbookStep(
                kind=attr,
                prompt=prompt,
                save_as=self._assignment_target(node),
                timeout_seconds=self._keyword_int(node, "timeout_seconds"),
            )
        )

    def _record_judge(self, node: ast.Call) -> None:
        output = self._expression_source(node.args[0]) if node.args else ""
        rubric = self._prompt_arg(node, 1) or ""
        self._collected.append(
            _RunbookScenario(
                name=self._current_name,
                session=self._current_session,
                setup=list(self._setup_steps),
                judges=[
                    _RunbookJudge(
                        description=self._pending_it or "ai_judge",
                        output=output,
                        rubric=rubric,
                    )
                ],
            )
        )
        self._setup_steps = []
        self._pending_it = None

    def _record_expect(self, node: ast.Call) -> None:
        desc = self._pending_it or "assertion"
        expression = self._expression_source(node)
        scenario = self._scenario_for_expect()
        scenario.assertions.append(_RunbookAssertion(description=desc, expression=expression))
        self._pending_it = None

    def _scenario_for_expect(self) -> _RunbookScenario:
        if self._collected and self._collected[-1].name == self._current_name and not self._collected[-1].setup:
            return self._collected[-1]
        for scenario in self._collected:
            if scenario.name == self._current_name:
                return scenario
        scenario = _RunbookScenario(
            name=self._current_name,
            session=self._current_session,
            setup=list(self._setup_steps),
        )
        self._collected.append(scenario)
        return scenario

    def _append_remaining_setup(self) -> None:
        if not self._setup_steps:
            return
        self._collected.append(
            _RunbookScenario(
                name=self._current_name,
                session=self._current_session,
                setup=list(self._setup_steps),
            )
        )

    def _merged_scenarios(self) -> list[_RunbookScenario]:
        by_name: dict[str, _RunbookScenario] = {}
        for scenario in self._collected:
            self._merge_named_scenario(by_name, scenario)
        merged = list(by_name.values())
        if merged or not self._manifest.session:
            return merged
        return [
            _RunbookScenario(name="default", session=self._manifest.session, setup=self._setup_steps),
        ]

    def _merge_named_scenario(
        self, by_name: dict[str, _RunbookScenario], scenario: _RunbookScenario
    ) -> None:
        existing = by_name.get(scenario.name)
        if existing is None:
            by_name[scenario.name] = scenario
            return
        existing.setup.extend(scenario.setup)
        existing.assertions.extend(scenario.assertions)
        existing.judges.extend(scenario.judges)
        if scenario.session:
            existing.session = scenario.session

    def _with_context_name(self, node: ast.With) -> str | None:
        for item in node.items:
            name = self._context_call_name(item.context_expr)
            if name is not None:
                return name
        return None

    def _context_call_name(self, expr: ast.AST) -> str | None:
        if not isinstance(expr, ast.Call):
            return None
        func = expr.func
        named = isinstance(func, ast.Name) and func.id == "context"
        attributed = isinstance(func, ast.Attribute) and func.attr == "context"
        if not (named or attributed):
            return None
        if expr.args and isinstance(expr.args[0], ast.Constant):
            return str(expr.args[0].value)
        return None

    def _it_description(self, node: ast.With) -> str | None:
        for item in node.items:
            name = self._it_call_name(item.context_expr)
            if name is not None:
                return name
        return None

    def _it_call_name(self, expr: ast.AST) -> str | None:
        if not isinstance(expr, ast.Call):
            return None
        func = expr.func
        if not (isinstance(func, ast.Name) and func.id == "it"):
            return None
        if expr.args and isinstance(expr.args[0], ast.Constant):
            return str(expr.args[0].value)
        return None

    def _string_arg(self, node: ast.Call, index: int) -> str | None:
        if len(node.args) <= index:
            return None
        arg = node.args[index]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value
        return None

    def _prompt_arg(self, node: ast.Call, index: int) -> str | None:
        literal = self._string_arg(node, index)
        if literal is not None:
            return literal
        if len(node.args) <= index:
            return None
        return self._resolve_string_expr(node.args[index])

    def _resolve_string_expr(self, arg: ast.AST) -> str | None:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value
        if isinstance(arg, ast.JoinedStr):
            return self._joined_string(arg)
        segment = ast.get_source_segment(self._source, arg)
        if segment is None:
            return None
        if (segment.startswith('"') and segment.endswith('"')) or (
            segment.startswith("'") and segment.endswith("'")
        ):
            return ast.literal_eval(segment)
        if segment.startswith('f"') or segment.startswith("f'"):
            return None
        return segment

    def _joined_string(self, arg: ast.JoinedStr) -> str | None:
        parts: list[str] = []
        for piece in arg.values:
            if isinstance(piece, ast.Constant) and isinstance(piece.value, str):
                parts.append(piece.value)
                continue
            if not isinstance(piece, ast.FormattedValue):
                return None
            resolved = self._resolve_formatted_value(piece)
            if resolved is None:
                return None
            parts.append(resolved)
        return "".join(parts)

    def _resolve_formatted_value(self, piece: ast.FormattedValue) -> str | None:
        value = piece.value
        if isinstance(value, ast.Name):
            return self._assigned_name_value(value.id)
        if isinstance(value, ast.Constant):
            return str(value.value)
        return ast.get_source_segment(self._source, value)

    def _assigned_name_value(self, name: str) -> str | None:
        for stmt in self._tree.body:
            if not isinstance(stmt, ast.Assign):
                continue
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    if isinstance(stmt.value, ast.Constant):
                        return str(stmt.value.value)
        return None

    def _keyword_int(self, node: ast.Call, name: str) -> int | None:
        for keyword in node.keywords:
            if keyword.arg == name and isinstance(keyword.value, ast.Constant):
                if isinstance(keyword.value.value, int):
                    return keyword.value.value
        return None

    def _is_expect_call(self, node: ast.Call) -> bool:
        func = node.func
        return isinstance(func, ast.Name) and func.id == "expect"

    def _expression_source(self, node: ast.AST) -> str:
        try:
            return ast.get_source_segment(self._source, node) or ""
        except (TypeError, ValueError):
            return ""

    def _assignment_target(self, call_node: ast.Call) -> str | None:
        named = self._assign_name_for_call(call_node)
        if named is not None:
            return named
        prompt = self._prompt_arg(call_node, 0) or ""
        slug = re.sub(r"[^a-z0-9]+", "_", prompt[:40].lower()).strip("_")
        return slug or None

    def _assign_name_for_call(self, call_node: ast.Call) -> str | None:
        self._call_node = call_node
        self._call_line = getattr(call_node, "lineno", None)
        if self._call_line is None:
            return None
        for node in ast.walk(self._tree):
            found = self._target_if_matching_assign(node)
            if found is not None:
                return found
        return None

    def _target_if_matching_assign(self, node: ast.AST) -> str | None:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Call):
            return None
        if not self._assign_matches_call(node.value):
            return None
        if len(node.targets) != 1:
            return None
        return self._name_from_assign_target(node.targets[0])

    def _assign_matches_call(self, value: ast.Call) -> bool:
        if value is self._call_node:
            return True
        return (
            getattr(value, "lineno", None) == self._call_line
            and getattr(value, "col_offset", None) == getattr(self._call_node, "col_offset", None)
        )

    def _name_from_assign_target(self, target: ast.AST) -> str | None:
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
            return f"{target.value.id}.{target.attr}"
        if isinstance(target, ast.Name):
            return target.id
        return None


def build_runbook(spec_path: Path, *, workspace: Path | None = None) -> AgentSpecRunbook:
    return AgentSpecRunbook.from_spec(spec_path, workspace)

