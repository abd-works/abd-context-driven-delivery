"""@subAgent mark — prepend non-blocking delegation instructions to agent ops."""
from __future__ import annotations

from harness.marks.mark import Mark

SUB_AGENT_CALLER_PREAMBLE = """Hand work to a background sub-agent and continue without waiting.

Do not perform the delegated work in this conversation. Do not wait for the
sub-agent to finish.

Launch the Task tool with run_in_background true and subagent_type
generalPurpose. Pass the instructions below as the task prompt.

Tell the user you launched a non-blocking sub-agent and summarize what you delegated."""


class SubAgentMark(Mark):
    """Mark an @agent_tool or @agent_instructions member for non-blocking sub-agent launch: its description starts with
    the hand-off to a background sub-agent."""

    flag = "_sub_agent"

    @classmethod
    def with_hand_off(cls, text: str) -> str:
        """text with the hand-off to a background sub-agent in front of it."""
        preamble = SUB_AGENT_CALLER_PREAMBLE.strip()
        body = (text or "").strip()
        return f"{preamble}\n\n{body}" if body else preamble


subAgent = SubAgentMark()
