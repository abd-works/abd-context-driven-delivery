"""Cursor-agent CLI harness for agent BDD specs."""
from __future__ import annotations

import json
import os
import re
import subprocess
import threading
from pathlib import Path
from typing import Any

from cdd_guidance.practices.agent_bdd.agent_bdd_common import (
    CMDLINE_SAFE,
    AgentHarnessError,
    AgentResult,
    AgentSession,
    ToolsRunYaml,
    _ShellCapture,
)
from cdd_guidance.practices.agent_bdd.agent_block import AgentBlock
from cdd_guidance.practices.agent_bdd.cursor_cli import CursorAgentNotFound, CursorCli

# How long `cursor-agent status` may take to say whether the agent is signed in.
_STATUS_TIMEOUT_SECONDS = 30

# Set by the quick and heavy suites, so no spec in them can start a real agent: a model call is slow, costs money,
# and gives an answer that changes from run to run.
AGENT_RUNS_OFF = "CDD_AGENT_RUNS_OFF"


class AgentRunsOff(AgentHarnessError):
    """A spec opened the agent command line in a suite that turned agent runs off."""

    def __init__(self) -> None:
        super().__init__(f"agent runs are off in this suite ({AGENT_RUNS_OFF} is set); run agent specs with -Suite e2e")

_TOOLS_RUN = re.compile(
    r"(?:python\s+-m\s+tools\s+run|tools\.ps1\s+run|tools\s+run\b)",
    re.IGNORECASE,
)


class _StreamBuckets:
    """Collect stdout narrative, raw lines, and shell captures from a live process."""

    def __init__(self, tools_run_yaml: ToolsRunYaml) -> None:
        self.narrative: list[str] = []
        self.raw_lines: list[str] = []
        self.shell_captures: list[_ShellCapture] = []
        self.pending_shell_commands: list[str] = []
        self.stderr_chunks: list[str] = []
        self.thread_errors: list[str] = []
        self.stdout = ""
        self.stderr = ""
        self.exit_code = 0
        # The block's reader of toolset-run YAML, which tells a run's output from other shell output.
        self._tools_run_yaml = tools_run_yaml

    def drain(self, proc: subprocess.Popen, timeout_seconds: int) -> tuple[str, str, int]:
        self._stdout_thread = threading.Thread(target=lambda: self._read_stdout(proc), daemon=True)
        self._stderr_thread = threading.Thread(target=lambda: self._read_stderr(proc), daemon=True)
        self._stdout_thread.start()
        self._stderr_thread.start()
        exit_code = self._wait_for_process(proc, timeout_seconds)
        self._stdout_thread.join()
        self._stderr_thread.join()
        self.stderr = "".join(self.stderr_chunks)
        self.stdout = "".join(self.narrative) or "".join(self.raw_lines)
        self.exit_code = exit_code
        return self.stdout, self.stderr, self.exit_code

    def raise_if_failed(self, prefix: str, log_dir: Path) -> None:
        if self.thread_errors:
            raise AgentHarnessError(
                f"cursor-agent stream read failed: {'; '.join(self.thread_errors)}",
                prefix=prefix,
                exit_code=self.exit_code,
                stdout=self.stdout,
                stderr=self.stderr,
                log_dir=log_dir,
            )
        if self.exit_code != 0:
            raise AgentHarnessError(
                f"cursor-agent exited {self.exit_code}",
                prefix=prefix,
                exit_code=self.exit_code,
                stdout=self.stdout,
                stderr=self.stderr,
                log_dir=log_dir,
            )

    def _wait_for_process(self, proc: subprocess.Popen, timeout_seconds: int) -> int:
        try:
            return proc.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            self._stdout_thread.join(timeout=5)
            self._stderr_thread.join(timeout=5)
            raise

    def _read_stdout(self, proc: subprocess.Popen) -> None:
        try:
            assert proc.stdout
            for raw in proc.stdout:
                self.raw_lines.append(raw)
                try:
                    event = json.loads(raw.strip())
                except json.JSONDecodeError:
                    continue
                self.collect_shell_capture(event)
        except Exception as exc:  # noqa: BLE001
            self.thread_errors.append(f"stdout: {exc}")

    def _read_stderr(self, proc: subprocess.Popen) -> None:
        try:
            assert proc.stderr
            self.stderr_chunks.append(proc.stderr.read())
        except Exception as exc:  # noqa: BLE001
            self.thread_errors.append(f"stderr: {exc}")

    def collect_shell_capture(self, event: dict[str, Any]) -> None:
        etype = event.get("type")
        if etype == "assistant":
            self._collect_assistant(event)
            return
        if etype == "tool_result":
            self._collect_tool_result(event)
            return
        if etype == "tool_call":
            self._collect_tool_call(event)
            return
        if etype == "result":
            self._collect_result(event)

    def _collect_assistant(self, event: dict[str, Any]) -> None:
        for block in (event.get("message") or {}).get("content") or []:
            if not isinstance(block, dict):
                continue
            self._collect_assistant_block(block)

    def _collect_assistant_block(self, block: dict[str, Any]) -> None:
        if block.get("type") == "text":
            text = str(block.get("text", ""))
            if text:
                self.narrative.append(text)
            return
        if block.get("type") != "tool_use":
            return
        command = self.shell_command_from_tool_use(block)
        if command:
            self.pending_shell_commands.append(command)

    def _collect_tool_result(self, event: dict[str, Any]) -> None:
        output = self.extract_shell_output(event, event)
        command = self.pending_shell_commands.pop(0) if self.pending_shell_commands else ""
        if output:
            self.shell_captures.append(_ShellCapture(command=command, output=output))

    def _collect_tool_call(self, event: dict[str, Any]) -> None:
        subtype = str(event.get("subtype") or event.get("state") or "")
        tool_call = event.get("tool_call") or {}
        if not isinstance(tool_call, dict):
            tool_call = {}
        if subtype in ("started", "start", "running", "pending"):
            self._note_started_command(tool_call)
            return
        if subtype in ("completed", "complete", "succeeded", "success", "finished"):
            self._note_completed_command(tool_call, event)

    def _note_started_command(self, tool_call: dict[str, Any]) -> None:
        command = self.shell_command_from_tool_call(tool_call)
        if command:
            self.pending_shell_commands.append(command)

    def _note_completed_command(self, tool_call: dict[str, Any], event: dict[str, Any]) -> None:
        output = self.extract_shell_output(tool_call, event)
        command = self.shell_command_from_tool_call(tool_call) or ""
        if not output and command and _TOOLS_RUN.search(command):
            output = command
        command = self._resolve_pending_command(command)
        if output:
            self.shell_captures.append(_ShellCapture(command=command, output=output))

    def _resolve_pending_command(self, command: str) -> str:
        if not self.pending_shell_commands:
            return command
        if not command:
            return self.pending_shell_commands.pop(0)
        self.pending_shell_commands.pop(0)
        return command

    def _collect_result(self, event: dict[str, Any]) -> None:
        text = str(event.get("result", ""))
        if text:
            self.narrative.append(text)

    def shell_command_from_tool_call(self, tool_call: dict[str, Any]) -> str | None:
        if not tool_call:
            return None
        nested = self._command_from_nested_tool_call(tool_call)
        if nested:
            return nested
        command = tool_call.get("command") or tool_call.get("cmd")
        return str(command) if command else None

    def _command_from_nested_tool_call(self, tool_call: dict[str, Any]) -> str | None:
        for key in (
            "shellToolCall",
            "ShellToolCall",
            "runTerminalCommandToolCall",
            "terminalToolCall",
        ):
            if key not in tool_call or not isinstance(tool_call[key], dict):
                continue
            inner = tool_call[key]
            args = inner.get("args") if isinstance(inner.get("args"), dict) else inner
            command = args.get("command") or args.get("cmd")
            if command:
                return str(command)
        return None

    def shell_command_from_tool_use(self, block: dict[str, Any]) -> str | None:
        name = str(block.get("name", ""))
        if "shell" not in name.lower() and "terminal" not in name.lower():
            return None
        tool_input = block.get("input")
        if not isinstance(tool_input, dict):
            return None
        command = tool_input.get("command") or tool_input.get("cmd")
        return str(command) if command else None

    def extract_shell_output(self, tool_call: dict[str, Any], event: dict[str, Any] | None = None) -> str | None:
        for root in (tool_call, event or {}):
            found = self._shell_output_in(root)
            if found and (self._tools_run_yaml.looks_like_tools_run_output(found) or "error" in found.lower()):
                return found
        return None

    def _shell_output_in(self, node: object) -> str | None:
        if isinstance(node, str):
            return self._shell_output_from_text(node)
        if not isinstance(node, dict):
            return None
        from_keys = self._shell_output_from_keys(node)
        if from_keys:
            return from_keys
        return self._shell_output_from_nested(node)

    def _shell_output_from_text(self, node: str) -> str | None:
        stripped = node.strip()
        if not stripped:
            return None
        if _TOOLS_RUN.search(stripped) and not self._tools_run_yaml.looks_like_tools_run_output(stripped):
            return None
        return stripped

    def _shell_output_from_keys(self, node: dict[str, Any]) -> str | None:
        for key in ("stdout", "stderr", "output", "text", "content"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _shell_output_from_nested(self, node: dict[str, Any]) -> str | None:
        for key, value in node.items():
            if key in ("command", "cmd", "args", "input"):
                continue
            found = self._shell_output_in(value)
            if found:
                return found
        return None


class CliAgentBlock(AgentBlock):
    """One cursor-agent session: every instruct in the block resumes the same chat, and the judge runs in a fresh one."""

    log_name = "agent_cli_bdd"

    def __init__(self, workspace: Path, session_file: Path) -> None:
        super().__init__(workspace, session_file)
        self._session: AgentSession | None = None
        # The agent command line before any chat: whether it is installed, and the chats it starts.
        self._cli = CursorCli()

    def _open(self) -> None:
        if os.environ.get(AGENT_RUNS_OFF):
            raise AgentRunsOff()
        self._assert_authenticated()
        self._session = AgentSession.from_workspace(self._session_file, self._workspace, self._cli, fresh=False)

    def _assert_authenticated(self) -> None:
        exe = self._cli.launcher
        if exe is None:
            raise CursorAgentNotFound()
        completed = subprocess.run([exe, "status"], capture_output=True, text=True, timeout=_STATUS_TIMEOUT_SECONDS)
        if completed.returncode != 0:
            raise RuntimeError("cursor-agent not authenticated - run `cursor-agent login` first")

    def _answer(self, prefix: str, prompt: str, timeout_seconds: int) -> AgentResult:
        buckets = self._run(prompt, timeout_seconds, prefix)
        self.last_shell_captures = list(buckets.shell_captures)
        self.session_shell_captures.extend(buckets.shell_captures)
        for index, shell in enumerate(buckets.shell_captures, start=1):
            self._write_artifact(f"{prefix}-shell-{index:02d}-cmd.txt", shell.command)
            self._write_artifact(f"{prefix}-shell-{index:02d}-out.txt", shell.output)
        self._log.write(f"{prefix} response: {len(buckets.stdout)} chars -> {self._log_dir / f'{prefix}-response.txt'}")
        return AgentResult(exit_code=buckets.exit_code, text=buckets.stdout, stderr=buckets.stderr, elapsed_seconds=0.0)

    def _judge_answer(self, launch_prompt: str, timeout_seconds: int) -> AgentResult:
        judge_file = self._session_file.with_name(f"{self._session_file.stem}-judge.json")
        judge_session = AgentSession.from_workspace(judge_file, self._workspace, self._cli, fresh=True)
        return judge_session.run(launch_prompt, self._workspace, timeout_seconds=timeout_seconds)

    def _run(self, prompt: str, timeout_seconds: int, prefix: str) -> _StreamBuckets:
        if self._session is None:
            raise RuntimeError("agent session not started - use `with agent(...)`")
        buckets = _StreamBuckets(self._tools_run_yaml)
        proc = subprocess.Popen(
            self._agent_command(self._session, prompt),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        buckets.drain(proc, timeout_seconds)
        buckets.raise_if_failed(prefix, self._log_dir)
        return buckets

    def _agent_command(self, session: AgentSession, prompt: str) -> list[str]:
        if len(prompt) > CMDLINE_SAFE:
            prompt_path = self._log_dir / f"prompt-{self._instruct_count:03d}.txt"
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(prompt, encoding="utf-8")
            prompt = f"Read and follow the instructions in {prompt_path.relative_to(self._workspace).as_posix()}"
        return session.streaming_cli.command(prompt, str(self._workspace))
