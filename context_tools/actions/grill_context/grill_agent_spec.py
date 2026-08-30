# @agent-spec-manifest python -m tools agent-spec context_tools/actions/grill_context/grill_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/actions/grill_context/.context/.agent_bdd_sessions/grill-owns-tools.json
"""Agent BDD — /grill runs GrillContext.grill(tools=...); each write_grill_answer finishes a Turn."""

from expects import contain, equal, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    expect_instructions_contain,
    expect_ok_action,
    expect_tools_include,
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

    with context("that expands grill instructions for turn-per-tick"):
        with it("should require complete_tick after every write_grill_answer"):
            with agent(_REPO_ROOT, _SESSIONS / "grill-turn-per-tick.json"):
                response = run_toolset(
                    toolset=_GRILL_CONTEXT,
                    action="grill",
                    arguments={"tools": [_BDD]},
                    timeout_seconds=300,
                )
                expect_ok_action(response, "grill")
                expect_tools_include(response, ["write_grill_answer", "complete_tick"])
                expect_instructions_contain(
                    response,
                    "complete_tick",
                    "One write_grill_answer = one Turn",
                    "Persisting without complete_tick is a defect",
                )

                summary = follow_instructions(
                    "From the grill action instructions, what must happen after every "
                    "write_grill_answer regarding workspace Turns?",
                    timeout_seconds=180,
                ).text
                ai_judge(
                    f"{summary}\n---\ninstructions excerpt:\n{response.instructions}",
                    "PASS only if the agent says each write_grill_answer tick must call "
                    "complete_tick / finish a workspace Turn so session trail matches "
                    "cadence. FAIL if they say one Turn for the whole grill session is "
                    "enough or that write_grill_answer alone is durable.",
                )
