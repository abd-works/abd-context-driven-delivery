# @agent-spec-manifest python -m tools agent-spec context_tools/actions/grill_context/grill_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/actions/grill_context/.context/.agent_bdd_sessions/grill-owns-tools.json
"""Agent BDD — /grill runs GrillContext.grill(tools=...); validates sketch; batches questions."""

from expects import contain, equal, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    expect_instructions_contain,
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

    with context("that expands grill instructions for sketch validation and batching"):
        with it("should require thinking questions, sketch validation, and batching similar asks"):
            with agent(_REPO_ROOT, _SESSIONS / "grill-validate-sketch.json"):
                response = run_toolset(
                    toolset=_GRILL_CONTEXT,
                    action="grill",
                    arguments={"tools": [_BDD]},
                    timeout_seconds=300,
                )
                expect_ok_action(response, "grill")
                expect_instructions_contain(
                    response,
                    "thinking/context questions",
                    "Sketch-validation gate",
                    "must not run disconnected",
                    "Batch similar questions",
                    "does not run forever",
                )

                summary = follow_instructions(
                    "From the grill action instructions, explain how grilling should "
                    "relate to an existing sketch, what kind of questions to prefer, "
                    "and when to batch similar questions.",
                    timeout_seconds=180,
                ).text
                ai_judge(
                    f"{summary}\n---\ninstructions excerpt:\n{response.instructions}",
                    "PASS only if the agent says grilling must validate what the sketch "
                    "claimed (not interview as if no sketch), prefers thinking/context "
                    "questions over syntax trivia, and batches similar peer questions "
                    "so the loop does not run forever. FAIL if they describe grill as "
                    "unrelated to the sketch or as one near-identical question forever.",
                )
