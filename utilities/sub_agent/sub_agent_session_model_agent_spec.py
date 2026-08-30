# @agent-spec-manifest python -m tools agent-spec utilities/sub_agent/sub_agent_session_model_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: utilities/sub_agent/.context/.agent_bdd_sessions/session-model.json
"""Agent BDD — SubAgent reads session model when present.

Covers the sub-agent half of #25: before launch, read
``.context/sessions/{session}/model`` (or sessions/default) and pass it as the
sub-agent model. Never disable-model-invocation.
"""
from pathlib import Path

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import agent, repo_root_from, sessions_dir

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("SubAgent session model"):
    with context("when the agent reads SubAgent.run instructions"):
        with it(
            "should require reading sessions model and passing it on sub-agent launch"
        ):
            with agent(
                _REPO_ROOT,
                _SESSIONS / "session-model.json",
            ):
                path = _REPO_ROOT / "utilities" / "sub_agent" / "sub_agent.py"
                text = path.read_text(encoding="utf-8").lower()
                expect("sessions" in text and "model" in text).to(be_true)
                expect("disable-model-invocation" in text).to(be_true)
                expect("launch" in text or "pass it" in text or "task" in text).to(
                    be_true
                )
