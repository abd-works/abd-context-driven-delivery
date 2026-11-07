"""In-chat agent BDD harness - the agent answers each step through inbox files a chat subagent fills."""
from __future__ import annotations

import time
from pathlib import Path

from cdd_guidance.practices.agent_bdd.agent_bdd_common import INBOX_POLL_SECONDS, AgentResult, ChatInboxPending
from cdd_guidance.practices.agent_bdd.agent_block import AgentBlock


class ChatAgentBlock(AgentBlock):
    """An agent session backed by inbox files for Cursor chat subagents: each prompt is written to the inbox, and the
    answer is the response file a subagent writes beside it."""

    log_name = "agent_chat_bdd"

    def _answer(self, prefix: str, prompt: str, timeout_seconds: int) -> AgentResult:
        return AgentResult(exit_code=0, text=self._wait_for_inbox(prefix, prompt, timeout_seconds), stderr="", elapsed_seconds=0.0)

    def _judge_answer(self, launch_prompt: str, timeout_seconds: int) -> AgentResult:
        judge = ChatAgentBlock(self._workspace, self._session_file.with_name(f"{self._session_file.stem}-judge.json"))
        return judge._answer("judge", launch_prompt, timeout_seconds)

    def _wait_for_inbox(self, prefix: str, prompt: str, timeout_seconds: int) -> str:
        response_path = self._prepare_inbox(prefix, prompt)
        text = self._poll_inbox_response(response_path, timeout_seconds)
        if text:
            return text
        raise ChatInboxPending(f"timed out waiting for inbox response at {response_path}", prefix=prefix, log_dir=self._log_dir)

    def _prepare_inbox(self, prefix: str, prompt: str) -> Path:
        inbox_dir = self._log_dir / "inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        slug = prefix.replace("/", "-")
        response_path = inbox_dir / f"{slug}-response.txt"
        ready_path = inbox_dir / f"{slug}-ready.txt"
        (inbox_dir / f"{slug}-prompt.txt").write_text(prompt, encoding="utf-8")
        if response_path.is_file():
            response_path.unlink()
        ready_path.write_text(f"Write agent response to:\n{response_path}\n", encoding="utf-8")
        self._log.write(f"inbox ready: {ready_path}")
        return response_path

    def _poll_inbox_response(self, response_path: Path, timeout_seconds: int) -> str:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if response_path.is_file():
                text = response_path.read_text(encoding="utf-8").strip()
                if text:
                    return text
            time.sleep(INBOX_POLL_SECONDS)
        return ""
