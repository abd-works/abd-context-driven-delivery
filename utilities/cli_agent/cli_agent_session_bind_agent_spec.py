# @agent-spec-manifest python -m tools agent-spec utilities/cli_agent/cli_agent_session_bind_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: utilities/cli_agent/.context/.agent_bdd_sessions/session-bind-before-start-ticket.json
"""Agent BDD — defect-fix job 1 must not bind a durable CliAgent session on main before start-ticket.

Captures the prompt/AI half of #41: after start-ticket the session is named for the
ticket on its branch/worktree; CliAgent must not keep a premature ``default`` bind.
"""
from pathlib import Path

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import agent, repo_root_from, sessions_dir

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("defect-fix triage session bind"):
    with context("when the agent reads the defect-fix template and module context"):
        with it("should require deferring durable CliAgent session bind until after start-ticket"):
            with agent(
                _REPO_ROOT,
                _SESSIONS / "session-bind-before-start-ticket.json",
            ):
                template = (
                    _REPO_ROOT
                    / "utilities"
                    / "cli_agent"
                    / "job-templates"
                    / "defect-fix.json"
                )
                module_ctx = (
                    _REPO_ROOT
                    / "utilities"
                    / "cli_agent"
                    / ".context"
                    / "module-context.md"
                )
                text = (
                    template.read_text(encoding="utf-8").lower()
                    + "\n"
                    + module_ctx.read_text(encoding="utf-8").lower()
                )
                expect(
                    ("before start-ticket" in text and "session" in text)
                    or "rebind" in text
                    or "do not bind" in text
                    or "durable" in text
                ).to(be_true)
