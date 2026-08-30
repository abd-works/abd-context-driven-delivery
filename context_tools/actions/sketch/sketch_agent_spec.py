# @agent-spec-manifest python -m tools agent-spec context_tools/actions/sketch/sketch_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/actions/sketch/.context/.agent_bdd_sessions/sketch-owns-tools.json
"""Agent BDD — /sketch runs Sketch.sketch(tools=...) not host sketch; review gate after save."""

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
_SKETCHER = "sketch.sketch:Sketch"
_BDD = "context_tools.bdd.bdd:Bdd"


with description("a sketch action"):
    with context("that is given one context tool"):
        with it("should run Sketch.sketch with that tool, not the host sketch"):
            with agent(_REPO_ROOT, _SESSIONS / "sketch-owns-tools.json"):
                read_workspace(".cursor/commands/sketch.md")
                read_workspace("context_tools/actions/sketch/sketch.py")

                response = run_toolset(
                    toolset=_SKETCHER,
                    action="sketch",
                    arguments={"tools": [_BDD]},
                    timeout_seconds=300,
                )
                expect_ok_action(response, "sketch")
                expect(response.toolset).to(equal(_SKETCHER))
                expect(str(response.arguments)).to(contain("bdd"))

                explanation = follow_instructions(
                    "The user invoked /bdd /sketch. Using the sketch command you read, "
                    "say which toolset owns the run and how the BDD tool is passed. "
                    "Do not invoke host sketch on Bdd.",
                    timeout_seconds=180,
                ).text
                ai_judge(
                    f"{explanation}\n---\ntoolset: {response.toolset}\n"
                    f"action: {response.action}\narguments: {response.arguments}",
                    "PASS only if sketch is owned by sketch.sketch:Sketch and the "
                    "BDD context tool is an argument in tools (one or more context tools). "
                    "FAIL if the run owner is context_tools.bdd.bdd:Bdd with action sketch.",
                )

    with context("that expands sketch instructions for review"):
        with it("should require pause, confirm correctness, correct mistakes before the next question"):
            with agent(_REPO_ROOT, _SESSIONS / "sketch-review-gate.json"):
                response = run_toolset(
                    toolset=_SKETCHER,
                    action="sketch",
                    arguments={"tools": [_BDD]},
                    timeout_seconds=300,
                )
                expect_ok_action(response, "sketch")
                expect_tools_include(response, ["save_sketch", "review_sketch"])
                expect_instructions_contain(
                    response,
                    "review_sketch",
                    "confirm",
                    "mistakes",
                    "next grill question",
                    "Never defer persistence or review",
                    "carried forward",
                    "do not regenerate as if those mistakes never happened",
                )

                summary = follow_instructions(
                    "From the sketch action instructions you just received, list the "
                    "mandatory steps after every save_sketch before asking the next "
                    "grill question. Name the review gate tool if any. Also say what "
                    "must happen to mistakes named in review when regenerating the next sketch.",
                    timeout_seconds=180,
                ).text
                ai_judge(
                    f"{summary}\n---\ninstructions excerpt:\n{response.instructions}",
                    "PASS only if the agent states that after save_sketch they must "
                    "pause for review / call review_sketch, ask whether the sketch is "
                    "correct, correct mistakes when not, and must NOT ask the next "
                    "grill question until confirmed correct; AND that named review "
                    "mistakes must be carried forward into the next sketch (correct "
                    "the model, not regenerate as if they never happened). FAIL if "
                    "they may continue grilling immediately after save_sketch without "
                    "review, or may ignore prior named mistakes on the next draft.",
                )
