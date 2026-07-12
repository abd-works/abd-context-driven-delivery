"""Agent BDD harness selection — cli (cursor-agent) or in-chat (inbox subagents)."""
from __future__ import annotations

import agent_bdd.conf  # noqa: F401 — secrets + import paths

import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from agent_bdd.agent_bdd_common import (  # noqa: F401
    AgentResult,
    AgentSession,
    AgentSpecManifest,
    AgentSpecRunbook,
    JudgeResult,
    RunResponse,
    build_runbook,
    read_manifest,
)

__all__ = [
    "agent",
    "instruct",
    "instruct_use_tool",
    "ai_judge",
    "AgentResult",
    "AgentSession",
    "AgentSpecManifest",
    "AgentSpecRunbook",
    "build_runbook",
    "read_manifest",
]

_local = threading.local()


def _current() -> Any:
    block = getattr(_local, "block", None)
    if block is None:
        raise RuntimeError("instruct/instruct_use_tool/ai_judge called outside of `with agent(...)`")
    return block


@contextmanager
def agent(
    workspace: Path,
    session_file: Path,
    *,
    in_chat: bool | None = None,
) -> Iterator[object]:
    """Route to cli or chat harness; pushes block onto thread-local so free functions work."""
    if in_chat is None:
        in_chat = _in_chat_from_env()
    if in_chat:
        from agent_bdd.agent_chat_bdd import agent as chat_agent
        with chat_agent(workspace, session_file) as block:
            _local.block = block
            try:
                yield block
            finally:
                _local.block = None
        return
    from agent_bdd.agent_cli_bdd import cli_agent
    with cli_agent(workspace, session_file) as block:
        _local.block = block
        try:
            yield block
        finally:
            _local.block = None


def instruct(prompt: str, *, timeout_seconds: int = 300) -> AgentResult:
    """Send a natural-language instruct to the current agent block."""
    return _current().instruct(prompt, timeout_seconds=timeout_seconds)


def instruct_use_tool(prompt: str, *, timeout_seconds: int = 300) -> RunResponse:
    """Drive the agent to pipe YAML to `python -m tools run -`; returns parsed RunResponse."""
    return _current().instruct_use_tool(prompt, timeout_seconds=timeout_seconds)


def ai_judge(output: str, rubric: str, *, timeout_seconds: int = 60) -> None:
    """Assert that output passes the rubric; raises AssertionError(reason) if the judge returns FAIL."""
    result = _current().ai_judge(output, rubric, timeout_seconds=timeout_seconds)
    if result.failed():
        raise AssertionError(f"ai_judge FAIL — {result.reason}")


def _in_chat_from_env() -> bool:
    return os.environ.get("AGENT_BDD_IN_CHAT", "").strip().lower() in {"1", "true", "yes"}


def in_chat_for_spec(spec_path: Path) -> bool:
    """Return whether the spec file declares in-chat execution for reading agents."""
    return read_manifest(spec_path).in_chat
