# @agent-spec-manifest python -m tools agent-spec primitives/actions/actions_display_tools_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: primitives/actions/.context/.agent_bdd_sessions/display-agenda-tools.json
"""Agent BDD — agenda expand must tell the agent to display available tools."""

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    expect_instructions_contain,
    expect_ok_action,
    expect_tools_include,
    follow_instructions,
    repo_root_from,
    run_toolset,
    sessions_dir,
    tools_run_captures,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("agenda construction"):
    with context("when expand makes tools available to the chat"):
        with it("should tell the agent to display those tools and the agent should surface them"):
            with agent(_REPO_ROOT, _SESSIONS / "display-agenda-tools.json") as block:
                expanded = run_toolset(
                    toolset="tools.examples.logged_probe:LoggedProbe",
                    action="narrate",
                    arguments={"message": "hello"},
                    timeout_seconds=90,
                    require_agent_shell=True,
                )
                expect_ok_action(expanded, "narrate")
                expect_tools_include(expanded, ["ping"])
                expect_instructions_contain(
                    expanded,
                    "display the tools made available to this chat in your user-visible reply",
                    "Tools made available:",
                    "ping",
                    "Echo a message",
                )

                reply = follow_instructions(
                    "Follow response.instructions. Before calling any tool, "
                    "display the tools made available to this chat — each name and what it is for — "
                    "in your reply. Then stop; do not invoke tools yet.",
                    timeout_seconds=120,
                )
                text = (reply.text or "").lower()
                expect("ping" in text).to(be_true)
                expect("echo" in text).to(be_true)
                expect(len(tools_run_captures(block)) >= 1).to(be_true)
