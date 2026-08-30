# @agent-spec-manifest python -m tools agent-spec utilities/workspace/workspace_session_model_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: utilities/workspace/.context/.agent_bdd_sessions/session-model.json
"""Agent BDD — /model persists session model and changes the IDE chat model.

Covers the chat/IDE half of #25: slash /model must AskQuestion when unset,
persist under .context/sessions/{session}/model (default session when none),
and switch the IDE model. Never disable-model-invocation.
"""
from pathlib import Path

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import agent, repo_root_from, sessions_dir

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("session model for chat and IDE"):
    with context("when the agent reads workspace module context and Workspace.model prompt"):
        with it(
            "should require /model to persist under sessions, AskQuestion when unset, and change the IDE model"
        ):
            with agent(
                _REPO_ROOT,
                _SESSIONS / "session-model.json",
            ):
                roots = [
                    _REPO_ROOT
                    / "utilities"
                    / "workspace"
                    / ".context"
                    / "module-context.md",
                    _REPO_ROOT / "utilities" / "workspace" / "workspace.py",
                ]
                text = "\n".join(
                    p.read_text(encoding="utf-8") for p in roots if p.is_file()
                ).lower()
                expect(
                    "sessions" in text
                    and ('name="model"' in text or "@prompt(name=\"model\")" in text or "/model" in text)
                ).to(be_true)
                expect("askquestion" in text).to(be_true)
                expect("disable-model-invocation" in text).to(be_true)
                expect(
                    "ide" in text or "chat model" in text or "model picker" in text
                ).to(be_true)
                expect("default" in text).to(be_true)
