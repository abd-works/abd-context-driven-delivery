"""In-chat agent BDD harness — fulfills instruct steps via inbox response files."""
from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import agent_bdd.conf  # noqa: F401 — secrets + import paths

from agent_bdd.agent_bdd_common import (
    AgentHarnessError,
    AgentJudgeError,
    AgentResult,
    ChatInboxPending,
    INBOX_POLL_SECONDS,
    JUDGE_LAUNCH,
    JUDGE_TASK,
    JudgeResult,
    RUN_PROMPT_SUFFIX,
    RunResponse,
    ShellCapture,
    fenced_yaml_from_text,
    cli_output_matches_prompt,
    log_harness,
    parse_judge_result,
    run_yaml_request,
    yaml_from_prompt,
)
from agent_bdd import yaml_fence


class ChatAgentBlock:
    """Agent session backed by inbox files for Cursor chat subagents."""

    def __init__(self, workspace: Path, session_file: Path) -> None:
        self._workspace = workspace.resolve()
        self._session_file = session_file
        self._yaml = yaml_fence
        self._log_dir = session_file.parent / "logs" / session_file.stem
        self._instruct_count = 0
        self.last_shell_captures: list[ShellCapture] = []
        self.session_shell_captures: list[ShellCapture] = []

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
        return None

    def instruct(self, prompt: str, *, timeout_seconds: int = 300) -> AgentResult:
        prefix = self._next_instruct_prefix("setup")
        log_harness("agent_chat_bdd", f"{prefix} prompt: {prompt[:120]}{'…' if len(prompt) > 120 else ''}")
        self._write_artifact(f"{prefix}-prompt.txt", prompt)
        stdout = self._wait_for_inbox(prefix, prompt, timeout_seconds=timeout_seconds)
        self._write_artifact(f"{prefix}-response.txt", stdout)
        return AgentResult(exit_code=0, text=stdout, stderr="", elapsed_seconds=0.0)

    def instruct_use_tool(self, prompt: str, *, timeout_seconds: int = 300) -> RunResponse:
        full_prompt = prompt.rstrip() + RUN_PROMPT_SUFFIX
        prefix = self._next_instruct_prefix("run")
        log_harness("agent_chat_bdd", f"{prefix} prompt: {full_prompt[:120]}{'…' if len(full_prompt) > 120 else ''}")
        self._write_artifact(f"{prefix}-prompt.txt", full_prompt)
        stdout = self._wait_for_inbox(prefix, full_prompt, timeout_seconds=timeout_seconds)
        self._write_artifact(f"{prefix}-response.txt", stdout)
        cli_output = fenced_yaml_from_text(stdout)
        if cli_output is not None and not cli_output_matches_prompt(cli_output, full_prompt):
            cli_output = None
        if cli_output is None:
            yaml_body = yaml_from_prompt(full_prompt)
            if yaml_body:
                cli_output = run_yaml_request(yaml_body, self._workspace, prefix=prefix)
        if cli_output is None:
            raise AgentHarnessError(
                "no python -m tools run output — chat runner must return fenced YAML",
                prefix=prefix,
                stdout=stdout,
                log_dir=self._log_dir,
            )
        return self._finalize_run_response(prefix, cli_output)

    def instruct_run(self, prompt: str, *, timeout_seconds: int = 300) -> RunResponse:
        """Back-compat alias for ``instruct_use_tool``."""
        return self.instruct_use_tool(prompt, timeout_seconds=timeout_seconds)

    def ai_judge(self, output: str, rubric: str, *, timeout_seconds: int = 60) -> JudgeResult:
        log_harness("agent_chat_bdd", "judge rubric:")
        sys.__stdout__.write(rubric + "\n")
        sys.__stdout__.flush()
        self._write_artifact("judge-rubric.txt", rubric)
        self._write_artifact("judge-output.txt", output)
        task_text = JUDGE_TASK.format(rubric=rubric, output=output)
        task_path = self._write_artifact("judge-prompt.txt", task_text)
        launch_prompt = JUDGE_LAUNCH.format(path=task_path.relative_to(self._workspace).as_posix())
        self._write_artifact("judge-launch.txt", launch_prompt)
        judge_session = self._session_file.with_name(f"{self._session_file.stem}-judge.json")
        judge_block = ChatAgentBlock(self._workspace, judge_session)
        judge_stdout = judge_block._wait_for_inbox("judge", launch_prompt, timeout_seconds=timeout_seconds)
        self._write_artifact("judge-response.txt", judge_stdout)
        verdict, reason = parse_judge_result(judge_stdout)
        self._write_artifact("judge-verdict.txt", f"{verdict}\n\n{reason}\n")
        if verdict == "ERROR":
            raise AgentJudgeError(
                f"judge returned no parseable JSON verdict: {reason}",
                prefix="judge",
                stdout=judge_stdout,
                log_dir=self._log_dir,
            )
        log_harness("agent_chat_bdd", f"judge verdict: {verdict} — {reason}")
        return JudgeResult(verdict=verdict, reason=reason, elapsed_seconds=0.0)

    def _finalize_run_response(self, prefix: str, cli_output: str) -> RunResponse:
        self._write_artifact(f"{prefix}-cli-output.yaml", cli_output)
        ai_response = RunResponse.from_cli_output(cli_output)
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

    def _wait_for_inbox(self, prefix: str, prompt: str, *, timeout_seconds: int) -> str:
        inbox_dir = self._log_dir / "inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        slug = prefix.replace("/", "-")
        prompt_path = inbox_dir / f"{slug}-prompt.txt"
        response_path = inbox_dir / f"{slug}-response.txt"
        ready_path = inbox_dir / f"{slug}-ready.txt"
        prompt_path.write_text(prompt, encoding="utf-8")
        if response_path.is_file():
            response_path.unlink()
        ready_path.write_text(
            f"Write agent response to:\n{response_path}\n",
            encoding="utf-8",
        )
        log_harness("agent_chat_bdd", f"inbox ready: {ready_path}")
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if response_path.is_file():
                text = response_path.read_text(encoding="utf-8").strip()
                if text:
                    return text
            time.sleep(INBOX_POLL_SECONDS)
        raise ChatInboxPending(
            f"timed out waiting for inbox response at {response_path}",
            prefix=prefix,
            log_dir=self._log_dir,
        )


@contextmanager
def agent(workspace: Path, session_file: Path) -> Iterator[ChatAgentBlock]:
    """Establish one in-chat agent session backed by inbox files."""
    block = ChatAgentBlock(workspace, session_file)
    yield block
