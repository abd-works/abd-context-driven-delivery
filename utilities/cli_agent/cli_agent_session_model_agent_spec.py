# @agent-spec-manifest python -m tools agent-spec utilities/cli_agent/cli_agent_session_model_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: utilities/cli_agent/.context/.agent_bdd_sessions/session-model.json
"""Agent BDD — CliAgent reads session model when present.

Covers the cli-agent half of #25: when ``.context/sessions/{session}/model``
is set and IdeCli.model is empty, cursor-agent launches with that --model.
"""
from pathlib import Path

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import agent, repo_root_from, sessions_dir

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("CliAgent session model"):
    with context("when the agent reads cli_agent module context and IdeCli wiring"):
        with it("should require reading sessions/{session}/model when IdeCli.model is empty"):
            with agent(
                _REPO_ROOT,
                _SESSIONS / "session-model.json",
            ):
                roots = [
                    _REPO_ROOT
                    / "utilities"
                    / "cli_agent"
                    / ".context"
                    / "module-context.md",
                    _REPO_ROOT / "utilities" / "cli_agent" / "cli_agent.py",
                ]
                text = "\n".join(
                    p.read_text(encoding="utf-8") for p in roots if p.is_file()
                ).lower()
                expect("resolve_session_model" in text or "session model" in text).to(
                    be_true
                )
                expect("sessions" in text and "model" in text).to(be_true)
                expect("--model" in text or "\"--model\"" in text or "model" in text).to(
                    be_true
                )
