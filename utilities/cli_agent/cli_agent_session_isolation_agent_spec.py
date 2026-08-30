# @agent-spec-manifest python -m tools agent-spec utilities/cli_agent/cli_agent_session_isolation_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: utilities/cli_agent/.context/.agent_bdd_sessions/session-isolation-rebind.json
"""Agent BDD — work session isolation for CliAgent, SubAgent, and no-agent.

Captures the prompt/AI half of the isolation defect: every new work session must
bind session/<name> + own worktree before jobs; after start-ticket, rebind the
workspace root to that worktree. Must hold beyond CLI spawn alone.
"""
from pathlib import Path

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import agent, repo_root_from, sessions_dir

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("work session branch/worktree isolation"):
    with context("when the agent reads defect-fix, cli_agent module context, and workspace context"):
        with it(
            "should require session==branch==worktree before jobs and rebind after start-ticket for CliAgent SubAgent and no-agent"
        ):
            with agent(
                _REPO_ROOT,
                _SESSIONS / "session-isolation-rebind.json",
            ):
                roots = [
                    _REPO_ROOT
                    / "utilities"
                    / "cli_agent"
                    / "job-templates"
                    / "defect-fix.json",
                    _REPO_ROOT
                    / "utilities"
                    / "cli_agent"
                    / ".context"
                    / "module-context.md",
                    _REPO_ROOT
                    / "utilities"
                    / "workspace"
                    / ".context"
                    / "module-context.md",
                ]
                text = "\n".join(
                    p.read_text(encoding="utf-8").lower()
                    for p in roots
                    if p.is_file()
                )
                expect("worktree" in text).to(be_true)
                expect("rebind" in text or "rebind" in text).to(be_true)
                expect(
                    "session/" in text
                    or "session/<" in text
                    or "session/<ticket>" in text
                    or "session/<name>" in text
                ).to(be_true)
                expect(
                    "subagent" in text.replace("-", "").replace("_", "")
                    or "sub agent" in text
                    or "no-agent" in text
                    or "no agent" in text
                ).to(be_true)
