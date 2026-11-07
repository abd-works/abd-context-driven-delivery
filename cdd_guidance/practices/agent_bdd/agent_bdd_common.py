"""Shared agent BDD types, helpers, session management, and in-process toolset runs."""
from __future__ import annotations

import contextvars
import json
import os
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar

from cdd_guidance.practices.agent_bdd.cursor_cli import CursorCli
from cdd_guidance.practices.agent_bdd.yaml_fence import YamlFence

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


class ToolRunTimedOut(AgentHarnessError):
    """An in-process toolset run outlived its timeout. Python cannot stop its thread, so the run may still finish."""

    def __init__(self, label: str, timeout_seconds: float) -> None:
        super().__init__(f"{label} did not finish within {timeout_seconds} seconds")
        self.timeout_seconds = timeout_seconds


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
        log.write(f"creating new session for {session_file.name} in {workspace} ...")
        chat_id = CursorCli().create_chat(str(workspace.resolve()))
        session = cls(chat_id=chat_id, session_file=session_file)
        session.save()
        log.write(f"session created: {session.chat_id}")
        return session

    def run(self, prompt: str, workspace: Path, *, timeout_seconds: int = 300) -> AgentResult:
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

    def run_request(self, yaml_body: str, timeout_seconds: float | None = None) -> str:
        if yaml is None:
            raise AgentHarnessError("PyYAML required to parse run request", prefix=self._prefix)
        parsed = yaml.safe_load(yaml_body)
        if not isinstance(parsed, dict):
            raise AgentHarnessError("run request must be a mapping", prefix=self._prefix)
        response = invoke_run_request(parsed, timeout_seconds)
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


class ToolsetInvoke:
    """Expand an action or invoke a tool on a live toolset instance."""

    def __init__(self, instance: Any, toolset_path: str, project: Path) -> None:
        self._instance = instance
        self._toolset_path = toolset_path
        self._project = project
        self._arguments: dict[str, Any] = {}
        self._action_name: str | None = None
        self._tool_name: str | None = None

    @classmethod
    def create(cls, request: dict[str, Any]) -> ToolsetInvoke:
        """The run a request names, on the project it names; a request that names none runs on the project the spec
        works on, the one ``CDD_PROJECT`` names, else the current folder."""
        from harness.agent_tools.agent_tools import AgentToolSet

        toolset_path = request.get("toolset")
        if not toolset_path:
            raise AgentHarnessError("request missing toolset")
        project = Path(request.get("project") or os.environ.get("CDD_PROJECT") or Path.cwd())
        context = dict(request.get("context") or {})
        if request.get("session"):
            context["session"] = cls._session_named(str(request["session"]), project)
        arguments = dict(request.get("arguments") or {})
        try:
            instance = AgentToolSet.instantiate({"toolset": str(toolset_path), "context": context})
        except TypeError as exc:
            raise AgentHarnessError(str(exc)) from exc
        invoke = cls(instance, str(toolset_path), project)
        invoke._arguments = arguments
        invoke._action_name = str(request["action"]) if request.get("action") else None
        invoke._tool_name = str(request["tool"]) if request.get("tool") else None
        return invoke

    @classmethod
    def _session_named(cls, name: str, project: Path) -> Any:
        """The project's session a run request names, which the toolset is made for, so the run works in that session
        and not in whichever session the project has open."""
        from space.session.session import MAIN_SESSION_NAME
        from space.session.sessions import Sessions

        sessions = Sessions(project)
        if name == MAIN_SESSION_NAME:
            return sessions.load(sessions.folder_of(name))
        session = sessions.named(name)
        if session is None:
            raise AgentHarnessError(f"request names session {name!r}, which the project does not have")
        return session

    @property
    def toolset(self) -> Any:
        """The toolset the request is run on, made for the session the request names."""
        return self._instance

    def response(self) -> RunResponse:
        if self._action_name:
            return self.expanded_action()
        if not self._tool_name:
            raise AgentHarnessError("request missing tool or action")
        return self.invoked_tool()

    def expanded_action(self) -> RunResponse:
        try:
            expanded = self._instance.instructions[self._action_name].expand(
                self._arguments
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
            return member.invoke(self._arguments, project=self._project)
        return getattr(self._instance, self._tool_name)(**self._arguments)


def invoke_run_request(request: dict[str, Any], timeout_seconds: float | None = None) -> RunResponse:
    """Load a toolset and expand or invoke the named member the same way production does; with a timeout, fail
    the spec when the run outlives it."""
    if timeout_seconds is None:
        return ToolsetInvoke.create(request).response()
    label = str(request.get("toolset") or "toolset run")
    return ToolRunDeadline(timeout_seconds).run(lambda: ToolsetInvoke.create(request).response(), label)


_Outcome = TypeVar("_Outcome")


class ToolRunDeadline:
    """Runs in-process work on a worker thread and fails when it outlives the timeout, so a hung toolset fails its
    spec instead of hanging the whole run."""

    def __init__(self, timeout_seconds: float) -> None:
        self.timeout_seconds = timeout_seconds

    def run(self, work: Callable[[], _Outcome], label: str) -> _Outcome:
        """The work's result or its own error; ToolRunTimedOut when it is still running at the timeout."""
        attempt = _TimedAttempt(work)
        # WHY: the worker runs in a copy of the caller's context, so it acts on the project and session the spec opened.
        worker = threading.Thread(target=contextvars.copy_context().run, args=(attempt.run,), daemon=True)
        worker.start()
        worker.join(self.timeout_seconds)
        if worker.is_alive():
            raise ToolRunTimedOut(label, self.timeout_seconds)
        return attempt.outcome()


class _TimedAttempt(Generic[_Outcome]):
    """One run of the work on the worker thread: what it returned, or the error it raised for the caller to see."""

    def __init__(self, work: Callable[[], _Outcome]) -> None:
        self._work = work
        self._result: _Outcome | None = None
        self._error: BaseException | None = None

    def run(self) -> None:
        try:
            self._result = self._work()
        except BaseException as error:  # noqa: BLE001 - handed to the caller's thread and raised there
            self._error = error

    def outcome(self) -> _Outcome:
        if self._error is not None:
            raise self._error
        return self._result  # type: ignore[return-value]


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
        return self.harness in {"in_chat", "chat"}

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
    command = _marker_command(text) or "agent-spec"
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


def _marker_command(text: str) -> str | None:
    """The command after the manifest marker in the spec's opening comments; None when they name none."""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("#", '"""', "'''")):
            return None
        body = stripped.lstrip("#").strip()
        if stripped.startswith("#") and AGENT_SPEC_MARKER in body:
            return body.split(AGENT_SPEC_MARKER, 1)[1].strip().removeprefix(":").strip() or None
    return None
