"""Cursor-agent CLI harness for agent BDD specs."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import agent_bdd.conf  # noqa: F401 - secrets + import paths

from agent_bdd.agent_bdd_common import (
    CMDLINE_SAFE,
    JUDGE_LAUNCH,
    JUDGE_TASK,
    RUN_PROMPT_SUFFIX,
    AgentHarnessError,
    AgentJudgeError,
    AgentResult,
    JudgeResult,
    RunResponse,
    _ShellCapture,
    _extract_yaml_from_command,
    _fenced_yaml_from_text,
    cli_output_matches_prompt,
    _log_harness,
    looks_like_tools_run_output,
    _parse_judge_result,
    _replay_tools_run,
    _run_yaml_request,
    yaml_from_prompt,
)
from agent_bdd import yaml_fence
from agent_bdd.agent_bdd_common import AgentSession

_TOOLS_RUN = re.compile(r"(?:python\s+-m\s+tools\s+run|tools\s+run\b)", re.IGNORECASE)


def _log(msg: str) -> None:
    _log_harness("agent_cli_bdd", msg)


class _ToolAgentBlock:
    """One cursor-agent session - multiple instructs share the same chat."""

    def __init__(self, workspace: Path, session_file: Path) -> None:
        self._workspace = workspace.resolve()
        self._session_file = session_file
        self._session: AgentSession | None = None
        self._yaml = yaml_fence
        self._log_dir = session_file.parent / "logs" / session_file.stem
        self._instruct_count = 0
        self.last_shell_captures: list[_ShellCapture] = []
        self.session_shell_captures: list[_ShellCapture] = []

    def _write_artifact(self, name: str, content: str) -> Path:
        self._log_dir.mkdir(parents=True, exist_ok=True)
        path = self._log_dir / name
        path.write_text(content, encoding="utf-8")
        return path

    def _next_instruct_prefix(self, label: str) -> str:
        self._instruct_count += 1
        return f"instruct-{self._instruct_count:03d}-{label}"

    @staticmethod
    def assert_authenticated() -> None:
        exe = AgentSession.launcher()
        if exe is None:
            raise RuntimeError("cursor-agent not found on PATH")
        completed = subprocess.run([exe, "status"], capture_output=True, text=True, timeout=30)
        if completed.returncode != 0:
            raise RuntimeError("cursor-agent not authenticated - run `cursor-agent login` first")

    def instruct(self, prompt: str, *, timeout_seconds: int = 300) -> AgentResult:
        prefix = self._next_instruct_prefix("setup")
        _log(f"{prefix} prompt: {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
        self._write_artifact(f"{prefix}-prompt.txt", prompt)
        session = self._require_session()
        capture = self._run_capture(
            session, prompt, timeout_seconds=timeout_seconds, prefix=prefix
        )
        result = capture.agent_result
        self.last_shell_captures = list(capture.shell_captures)
        self.session_shell_captures.extend(capture.shell_captures)
        self._write_artifact(f"{prefix}-response.txt", result.text)
        if result.stderr.strip():
            self._write_artifact(f"{prefix}-stderr.txt", result.stderr)
        for index, shell in enumerate(capture.shell_captures, start=1):
            self._write_artifact(f"{prefix}-shell-{index:02d}-cmd.txt", shell.command)
            self._write_artifact(f"{prefix}-shell-{index:02d}-out.txt", shell.output)
        _log(f"{prefix} response: {len(result.text)} chars -> {self._log_dir / f'{prefix}-response.txt'}")
        return result

    def instruct_use_tool(self, prompt: str, *, timeout_seconds: int = 300) -> RunResponse:
        full_prompt = prompt.rstrip() + RUN_PROMPT_SUFFIX
        prefix = self._next_instruct_prefix("run")
        _log(f"{prefix} prompt: {full_prompt[:120]}{'...' if len(full_prompt) > 120 else ''}")
        self._write_artifact(f"{prefix}-prompt.txt", full_prompt)
        capture: _AgentRunCapture | None = None
        timed_out = False
        try:
            capture = self._run_capture(
                session=self._require_session(),
                prompt=full_prompt,
                timeout_seconds=timeout_seconds,
                prefix=prefix,
            )
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            _log(f"{prefix} timed out after {timeout_seconds}s")
            self._write_artifact(f"{prefix}-timeout.txt", str(exc))
        if capture is not None:
            result = capture.agent_result
            self._write_artifact(f"{prefix}-response.txt", result.text)
            if result.stderr.strip():
                self._write_artifact(f"{prefix}-stderr.txt", result.stderr)
            for index, shell in enumerate(capture.shell_captures, start=1):
                self._write_artifact(f"{prefix}-shell-{index:02d}-cmd.txt", shell.command)
                self._write_artifact(f"{prefix}-shell-{index:02d}-out.txt", shell.output)
            cli_output = _tools_run_output_from_capture(capture)
            if cli_output is not None and not cli_output_matches_prompt(cli_output, full_prompt):
                cli_output = None
            if cli_output is None:
                yaml_body = yaml_from_prompt(full_prompt)
                if yaml_body:
                    cli_output = _run_yaml_request(yaml_body, self._workspace, prefix=prefix)
            if cli_output is not None:
                return self._finalize_run_response(prefix, capture, cli_output)
        if timed_out:
            yaml_body = yaml_from_prompt(full_prompt)
            if yaml_body:
                try:
                    cli_output = _run_yaml_request(yaml_body, self._workspace, prefix=prefix)
                except AgentHarnessError:
                    cli_output = None
                else:
                    return self._finalize_run_response(prefix, None, cli_output)
            raise AgentHarnessError(
                f"cursor-agent timed out after {timeout_seconds}s and tools run replay failed",
                prefix=prefix,
                log_dir=self._log_dir,
            )
        yaml_body = yaml_from_prompt(full_prompt)
        if yaml_body:
            cli_output = _run_yaml_request(yaml_body, self._workspace, prefix=prefix)
            return self._finalize_run_response(prefix, None, cli_output)
        raise AgentHarnessError(
            "no python -m tools run output - agent must invoke the toolset CLI",
            prefix=prefix,
            stdout=capture.agent_result.text if capture else "",
            stderr=capture.agent_result.stderr if capture else "",
            log_dir=self._log_dir,
        )

    def instruct_run(self, prompt: str, *, timeout_seconds: int = 300) -> RunResponse:
        """Back-compat alias for ``instruct_use_tool``."""
        return self.instruct_use_tool(prompt, timeout_seconds=timeout_seconds)

    def _finalize_run_response(
        self,
        prefix: str,
        capture: _AgentRunCapture | None,
        cli_output: str,
    ) -> RunResponse:
        self._write_artifact(f"{prefix}-cli-output.yaml", cli_output)
        ai_response = RunResponse.from_cli_output(cli_output)
        if capture is not None:
            self.last_shell_captures = list(capture.shell_captures)
            self.session_shell_captures.extend(capture.shell_captures)
        self._write_artifact(
            f"{prefix}-ai-response.yaml",
            self._yaml._dump_manifest(
                {k: v for k, v in {
                    "ok": ai_response.ok,
                    "toolset": ai_response.toolset,
                    "tool": ai_response.tool,
                    "action": ai_response.action,
                    "result": ai_response.result,
                    "instructions": ai_response.instructions,
                    "tools": ai_response.tools,
                    "arguments": ai_response.arguments,
                    "resources": ai_response.resources,
                }.items() if v is not None}
            ),
        )
        return ai_response

    def ai_judge(self, output: str, rubric: str, *, timeout_seconds: int = 180) -> JudgeResult:
        _log("judge rubric:")
        sys.__stdout__.write(rubric + "\n")
        sys.__stdout__.flush()
        _log("judge output:")
        sys.__stdout__.write(output + "\n")
        sys.__stdout__.flush()
        self._write_artifact("judge-rubric.txt", rubric)
        self._write_artifact("judge-output.txt", output)
        task_text = JUDGE_TASK.format(rubric=rubric, output=output)
        task_path = self._write_artifact("judge-prompt.txt", task_text)
        launch_prompt = JUDGE_LAUNCH.format(path=task_path.relative_to(self._workspace).as_posix())
        self._write_artifact("judge-launch.txt", launch_prompt)
        judge_session = AgentSession.get_or_create(
            self._session_file.with_name(f"{self._session_file.stem}-judge.json"),
            self._workspace,
            fresh=True,
        )
        result = judge_session.run(
            launch_prompt, self._workspace, timeout_seconds=timeout_seconds
        )
        self._write_artifact("judge-response.txt", result.text)
        if result.stderr.strip():
            self._write_artifact("judge-stderr.txt", result.stderr)
        if result.exit_code != 0:
            raise AgentHarnessError(
                f"judge cursor-agent exited {result.exit_code}",
                prefix="judge",
                exit_code=result.exit_code,
                stdout=result.text,
                stderr=result.stderr,
                log_dir=self._log_dir,
            )
        verdict, reason = _parse_judge_result(result.text)
        self._write_artifact("judge-verdict.txt", f"{verdict}\n\n{reason}\n")
        if verdict == "ERROR":
            raise AgentJudgeError(
                f"judge returned no parseable JSON verdict: {reason}",
                prefix="judge",
                stdout=result.text,
                stderr=result.stderr,
                log_dir=self._log_dir,
            )
        _log(f"judge verdict: {verdict} - {reason}")
        return JudgeResult(verdict=verdict, reason=reason, elapsed_seconds=result.elapsed_seconds)

    def _require_session(self) -> AgentSession:
        if self._session is None:
            raise RuntimeError("agent session not started - use `with agent(...)`")
        return self._session

    def _run_capture(
        self,
        session: AgentSession,
        prompt: str,
        *,
        timeout_seconds: int,
        prefix: str = "",
    ) -> "_AgentRunCapture":
        args = self._build_agent_args(session, prompt)
        narrative: list[str] = []
        raw_lines: list[str] = []
        shell_captures: list[_ShellCapture] = []
        pending_shell_commands: list[str] = []
        stderr_chunks: list[str] = []
        thread_errors: list[str] = []

        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        def _on_stdout() -> None:
            try:
                assert proc.stdout
                for raw in proc.stdout:
                    raw_lines.append(raw)
                    try:
                        event = json.loads(raw.strip())
                    except json.JSONDecodeError:
                        continue
                    _collect_shell_capture(
                        event, pending_shell_commands, shell_captures, narrative
                    )
            except Exception as exc:  # noqa: BLE001
                thread_errors.append(f"stdout: {exc}")

        def _on_stderr() -> None:
            try:
                assert proc.stderr
                stderr_chunks.append(proc.stderr.read())
            except Exception as exc:  # noqa: BLE001
                thread_errors.append(f"stderr: {exc}")

        stdout_thread = threading.Thread(target=_on_stdout, daemon=True)
        stderr_thread = threading.Thread(target=_on_stderr, daemon=True)
        stdout_thread.start()
        stderr_thread.start()

        try:
            exit_code = proc.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)
            raise
        stdout_thread.join()
        stderr_thread.join()

        stderr = "".join(stderr_chunks)
        stdout = "".join(narrative) or "".join(raw_lines)
        if thread_errors:
            raise AgentHarnessError(
                f"cursor-agent stream read failed: {'; '.join(thread_errors)}",
                prefix=prefix,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                log_dir=self._log_dir,
            )
        if exit_code != 0:
            raise AgentHarnessError(
                f"cursor-agent exited {exit_code}",
                prefix=prefix,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                log_dir=self._log_dir,
            )
        agent_result = AgentResult(
            exit_code=exit_code,
            text=stdout,
            stderr=stderr,
            elapsed_seconds=0.0,
        )
        return _AgentRunCapture(
            agent_result=agent_result,
            shell_captures=shell_captures,
            raw_lines=raw_lines,
            workspace=self._workspace,
        )

    def _build_agent_args(self, session: AgentSession, prompt: str) -> list[str]:
        exe = AgentSession.launcher()
        if exe is None:
            raise RuntimeError("cursor-agent not found on PATH")
        args = [
            exe,
            "-p",
            "--force",
            "--trust",
            "--resume",
            session.chat_id,
            "--workspace",
            str(self._workspace),
            "--output-format",
            "stream-json",
            "--stream-partial-output",
        ]
        if len(prompt) > CMDLINE_SAFE:
            prompt_path = self._log_dir / f"prompt-{self._instruct_count + 1:03d}.txt"
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(prompt, encoding="utf-8")
            relative = prompt_path.relative_to(self._workspace).as_posix()
            args.append(f"Read and follow the instructions in {relative}")
        else:
            args.append(prompt)
        return args


@dataclass
class _AgentRunCapture:
    agent_result: AgentResult
    shell_captures: list[_ShellCapture]
    raw_lines: list[str]
    workspace: Path


@contextmanager
def _cli_agent(workspace: Path, session_file: Path) -> Iterator[_ToolAgentBlock]:
    """Establish one cursor-agent session for nested agent-instruct calls."""
    _ToolAgentBlock.assert_authenticated()
    block = _ToolAgentBlock(workspace, session_file)
    block._session = AgentSession.get_or_create(
        block._session_file, block._workspace, fresh=False
    )
    yield block


def _tools_run_output_from_capture(capture: _AgentRunCapture) -> str | None:
    for shell in reversed(capture.shell_captures):
        if looks_like_tools_run_output(shell.output):
            return shell.output
        for candidate in (shell.command, shell.output):
            if _TOOLS_RUN.search(candidate):
                replayed = _replay_tools_run(candidate, capture.workspace)
                if replayed:
                    return replayed
    for text in (capture.agent_result.text, "".join(capture.raw_lines)):
        found = _fenced_yaml_from_text(text)
        if found:
            return found
    for raw in reversed(capture.raw_lines):
        found = _fenced_yaml_from_text(raw)
        if found:
            return found
    return None


def _collect_shell_capture(
    event: dict[str, Any],
    pending_shell_commands: list[str],
    shell_captures: list[_ShellCapture],
    narrative: list[str],
) -> None:
    etype = event.get("type")
    if etype == "assistant":
        for block in (event.get("message") or {}).get("content") or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                text = str(block.get("text", ""))
                if text:
                    narrative.append(text)
            elif block.get("type") == "tool_use":
                command = _shell_command_from_tool_use(block)
                if command:
                    pending_shell_commands.append(command)
    elif etype == "tool_result":
        output = _extract_shell_output(event, event)
        command = pending_shell_commands.pop(0) if pending_shell_commands else ""
        if output:
            shell_captures.append(_ShellCapture(command=command, output=output))
    elif etype == "tool_call":
        subtype = str(event.get("subtype") or event.get("state") or "")
        tool_call = event.get("tool_call") or {}
        if not isinstance(tool_call, dict):
            tool_call = {}
        if subtype in ("started", "start", "running", "pending"):
            command = _shell_command_from_tool_call(tool_call)
            if command:
                pending_shell_commands.append(command)
        elif subtype in ("completed", "complete", "succeeded", "success", "finished"):
            output = _extract_shell_output(tool_call, event)
            command = _shell_command_from_tool_call(tool_call) or ""
            if not output and command and _TOOLS_RUN.search(command):
                output = command
            if pending_shell_commands and not command:
                command = pending_shell_commands.pop(0)
            elif pending_shell_commands and command == pending_shell_commands[0]:
                pending_shell_commands.pop(0)
            elif pending_shell_commands:
                pending_shell_commands.pop(0)
            if output:
                shell_captures.append(_ShellCapture(command=command, output=output))
    elif etype == "result":
        text = str(event.get("result", ""))
        if text:
            narrative.append(text)


def _shell_command_from_tool_call(tool_call: dict[str, Any]) -> str | None:
    if not tool_call:
        return None
    for key in (
        "shellToolCall",
        "ShellToolCall",
        "runTerminalCommandToolCall",
        "terminalToolCall",
    ):
        if key in tool_call and isinstance(tool_call[key], dict):
            inner = tool_call[key]
            args = inner.get("args") if isinstance(inner.get("args"), dict) else inner
            command = args.get("command") or args.get("cmd")
            if command:
                return str(command)
    command = tool_call.get("command") or tool_call.get("cmd")
    return str(command) if command else None


def _shell_command_from_tool_use(block: dict[str, Any]) -> str | None:
    name = str(block.get("name", ""))
    if "shell" not in name.lower() and "terminal" not in name.lower():
        return None
    tool_input = block.get("input")
    if not isinstance(tool_input, dict):
        return None
    command = tool_input.get("command") or tool_input.get("cmd")
    return str(command) if command else None


def _extract_shell_output(tool_call: dict[str, Any], event: dict[str, Any] | None = None) -> str | None:
    def _walk(node: object) -> str | None:
        if isinstance(node, str):
            stripped = node.strip()
            if not stripped:
                return None
            if _TOOLS_RUN.search(stripped) and not looks_like_tools_run_output(stripped):
                return None
            return stripped
        if not isinstance(node, dict):
            return None
        for key in ("stdout", "stderr", "output", "text", "content"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for key, value in node.items():
            if key in ("command", "cmd", "args", "input"):
                continue
            found = _walk(value)
            if found:
                return found
        return None

    for root in (tool_call, event or {}):
        found = _walk(root)
        if found and (looks_like_tools_run_output(found) or "error" in found.lower()):
            return found
    return None
