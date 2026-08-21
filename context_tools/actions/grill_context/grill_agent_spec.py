# @agent-spec-manifest python -m tools agent-spec context_tools/actions/grill_context/grill_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/actions/grill_context/.context/.agent_bdd_sessions/grill-owns-tools.json
"""Agent BDD — /grill runs GrillContext.grill(tools=...) not host grill."""

from expects import contain, equal, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    expect_ok_action,
    follow_instructions,
    read_workspace,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=3)
_SESSIONS = sessions_dir(__file__)
_GRILL_CONTEXT = "grill_context.grill_context:GrillContext"
_BDD = "context_tools.bdd.bdd:Bdd"


with description("a grill action"):
    with context("that is given one context tool"):
        with it("should run GrillContext.grill with that tool, not the host grill"):
            with agent(_REPO_ROOT, _SESSIONS / "grill-owns-tools.json"):
                read_workspace(".cursor/commands/grill.md")
                read_workspace("context_tools/actions/grill_context/grill_context.py")

                response = run_toolset(
                    toolset=_GRILL_CONTEXT,
                    action="grill",
                    arguments={"tools": [_BDD]},
                    timeout_seconds=300,
                )
                expect_ok_action(response, "grill")
                expect(response.toolset).to(equal(_GRILL_CONTEXT))
                expect(str(response.arguments)).to(contain("bdd"))

                explanation = follow_instructions(
                    "The user invoked /bdd /grill. Using the grill command you read, "
                    "say which toolset owns the run and how the BDD tool is passed. "
                    "Do not invoke host grill on Bdd.",
                    timeout_seconds=180,
                ).text
                ai_judge(
                    f"{explanation}\n---\ntoolset: {response.toolset}\n"
                    f"action: {response.action}\narguments: {response.arguments}",
                    "PASS only if grill is owned by grill_context.grill_context:GrillContext and the "
                    "BDD context tool is an argument in tools (one or more context tools). "
                    "FAIL if the run owner is context_tools.bdd.bdd:Bdd with action grill.",
                )
