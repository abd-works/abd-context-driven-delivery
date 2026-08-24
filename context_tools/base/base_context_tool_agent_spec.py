# @agent-spec-manifest python -m tools agent-spec context_tools/base/base_context_tool_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/base/.context/.agent_bdd_sessions/base-context-tool.json
"""Agent BDD for BaseContextTool — generate instruction surface."""

from agent_bdd import (
    agent,
    expect_instructions_contain,
    expect_ok_action,
    repo_root_from,
    run_toolset,
    sessions_dir,
)
from mamba import context, description, it

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_TOOLSET = "context_tools.base.base_context_tool:BaseContextTool"


with description("a BaseContextTool host"):
    with context("when generate is given a large implied source"):
        with it("should require several turns even if the user asked once"):
            with agent(_REPO_ROOT, _SESSIONS / "base-context-tool.json"):
                response = run_toolset(
                    toolset=_TOOLSET,
                    action="generate",
                    timeout_seconds=300,
                )
                expect_ok_action(response, "generate")
                expect_instructions_contain(
                    response,
                    "several turns",
                    "one slice",
                )
