"""Cursor-agent CLI harness for agent BDD specs."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import agent_bdd.conf  # noqa: F401 - secrets + import paths

from agent_bdd.agent_bdd_common import (
    CMDLINE_SAFE,
    JUDGE_LAUNCH,
    JUDGE_TASK,
    AgentHarnessError,
    AgentJudgeError,
    AgentResult,
    AgentSession,
    HarnessLog,
    JudgeResult,
    RunResponse,
    ToolsRunYaml,
    _ShellCapture,
    yaml_from_prompt,
)
from agent_bdd.yaml_fence import YamlFence

_TOOLS_RUN = re.compile(
    r"(?:python\s+-m\s+tools\s+run|tools\.ps1\s+run|tools\s+run\b)",
    re.IGNORECASE,
)


class _StreamBuckets:
    """Collect stdout narrative, raw lines, and shell captures from a live process."""

    def __init__(self) -> None:
        self.narrative: list[str] = []
        self.raw_lines: list[str] = []
        self.shell_captures: list[_ShellCapture] = []
        self.pending_shell_commands: list[str] = []
        self.stderr_chunks: list[str] = []
        self.thread_errors: list[str] = []
        self.stdout = ""
        self.stderr = ""
        self.exit_code = 0
        self._tools_run_yaml = ToolsRunYaml()

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


class _ToolAgentBlock:
    """One cursor-agent session - multiple instructs share the same chat."""

    def __init__(self, workspace: Path, session_file: Path) -> None:
        self._workspace = workspace.resolve()
        self._session_file = session_file
        self._session: AgentSession | None = None
        self._yaml = YamlFence()
        self._log = HarnessLog("agent_cli_bdd")
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

    def assert_authenticated(self) -> None:
        exe = AgentSession.launcher()
        if exe is None:
            raise RuntimeError("cursor-agent not found on PATH")
        completed = subprocess.run([exe, "status"], capture_output=True, text=True, timeout=30)
        if completed.returncode != 0:
            raise RuntimeError("cursor-agent not authenticated - run `cursor-agent login` first")

    def instruct(self, prompt: str, *, timeout_seconds: int = 300) -> AgentResult:
        prefix = self._next_instruct_prefix("setup")
        self._log.write(f"{prefix} prompt: {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
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
        self._log.write(f"{prefix} response: {len(result.text)} chars -> {self._log_dir / f'{prefix}-response.txt'}")
        return result

    def instruct_use_tool(
        self,
        prompt: str,
        *,
        timeout_seconds: int = 300,
        require_agent_shell: bool = False,
    ) -> RunResponse:
        _ = timeout_seconds, require_agent_shell
        request_yaml = yaml_from_prompt(prompt)
        if not request_yaml:
            raise AgentHarnessError(
                "prompt must contain a toolset: run request block",
            )
        prefix = self._next_instruct_prefix("run")
        self._write_artifact(f"{prefix}-prompt.txt", prompt)
        self._write_artifact(f"{prefix}-stdin.yaml", request_yaml)
        cli_output = ToolsRunYaml(self._workspace, prefix).run_request(request_yaml)
        return self._finalize_run_response(prefix, None, cli_output)

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
            self._yaml.dump_manifest(
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
        self._log.write("judge rubric:")
        sys.__stdout__.write(rubric + "\n")
        sys.__stdout__.flush()
        self._log.write("judge output:")
        sys.__stdout__.write(output + "\n")
        sys.__stdout__.flush()
        self._write_artifact("judge-rubric.txt", rubric)
        self._write_artifact("judge-output.txt", output)
        task_text = JUDGE_TASK.format(rubric=rubric, output=output)
        task_path = self._write_artifact("judge-prompt.txt", task_text)
        launch_prompt = JUDGE_LAUNCH.format(path=task_path.relative_to(self._workspace).as_posix())
        self._write_artifact("judge-launch.txt", launch_prompt)
        judge_session = AgentSession.from_workspace(
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
        parsed = JudgeResult.from_stdout(result.text, result.elapsed_seconds)
        self._write_artifact("judge-verdict.txt", f"{parsed.verdict}\n\n{parsed.reason}\n")
        if parsed.verdict == "ERROR":
            raise AgentJudgeError(
                f"judge returned no parseable JSON verdict: {parsed.reason}",
                prefix="judge",
                stdout=result.text,
                stderr=result.stderr,
                log_dir=self._log_dir,
            )
        self._log.write(f"judge verdict: {parsed.verdict} - {parsed.reason}")
        return parsed

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
        buckets = _StreamBuckets()
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        stdout, stderr, exit_code = buckets.drain(proc, timeout_seconds)
        buckets.raise_if_failed(prefix, self._log_dir)
        return _AgentRunCapture(
            agent_result=AgentResult(
                exit_code=exit_code, text=stdout, stderr=stderr, elapsed_seconds=0.0
            ),
            shell_captures=buckets.shell_captures,
            raw_lines=buckets.raw_lines,
            workspace=self._workspace,
        )

    def _build_agent_args(self, session: AgentSession, prompt: str) -> list[str]:
        from cli_agent.cli_agent import CursorCli

        if len(prompt) > CMDLINE_SAFE:
            prompt_path = self._log_dir / f"prompt-{self._instruct_count + 1:03d}.txt"
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(prompt, encoding="utf-8")
            relative = prompt_path.relative_to(self._workspace).as_posix()
            prompt = f"Read and follow the instructions in {relative}"
        return CursorCli(resume=session.chat_id, print_mode=True).command(
            prompt, str(self._workspace)
        )

    @classmethod
    @contextmanager
    def opened(cls, workspace: Path, session_file: Path) -> Iterator["_ToolAgentBlock"]:
        """Establish one cursor-agent session for nested agent-instruct calls."""
        block = cls(workspace, session_file)
        block.assert_authenticated()
        block._session = AgentSession.from_workspace(
            block._session_file, block._workspace, fresh=False
        )
        yield block


@dataclass
class _AgentRunCapture:
    agent_result: AgentResult
    shell_captures: list[_ShellCapture]
    raw_lines: list[str]
    workspace: Path

    def tools_run_output(self) -> str | None:
        from_shell = self._output_from_shell_captures()
        if from_shell:
            return from_shell
        from_text = self._output_from_agent_text()
        if from_text:
            return from_text
        return self._output_from_raw_lines()

    def _output_from_shell_captures(self) -> str | None:
        yaml_run = ToolsRunYaml(self.workspace)
        for shell in reversed(self.shell_captures):
            found = self._output_from_shell(yaml_run, shell)
            if found:
                return found
        return None

    def _output_from_shell(self, yaml_run: ToolsRunYaml, shell: _ShellCapture) -> str | None:
        if yaml_run.looks_like_tools_run_output(shell.output):
            return shell.output
        for candidate in (shell.command, shell.output):
            if not _TOOLS_RUN.search(candidate):
                continue
            replayed = yaml_run.replay(candidate)
            if replayed:
                return replayed
        return None

    def _output_from_agent_text(self) -> str | None:
        yaml_run = ToolsRunYaml(self.workspace)
        for text in (self.agent_result.text, "".join(self.raw_lines)):
            found = yaml_run.fenced_yaml_from_text(text)
            if found:
                return found
        return None

    def _output_from_raw_lines(self) -> str | None:
        yaml_run = ToolsRunYaml(self.workspace)
        for raw in reversed(self.raw_lines):
            found = yaml_run.fenced_yaml_from_text(raw)
            if found:
                return found
        return None

