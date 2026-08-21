# @agent-spec-manifest python -m tools agent-spec context_tools/actions/sketch/sketch_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/actions/sketch/.context/.agent_bdd_sessions/sketch-owns-tools.json
"""Agent BDD — /sketch runs Sketcher.sketch(tools=...) not host sketch."""

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
_SKETCHER = "sketch.sketch:Sketcher"
_BDD = "context_tools.bdd.bdd:Bdd"


with description("a sketch action"):
    with context("that is given one context tool"):
        with it("should run Sketcher.sketch with that tool, not the host sketch"):
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
                    "PASS only if sketch is owned by sketch.sketch:Sketcher and the "
                    "BDD context tool is an argument in tools (one or more context tools). "
                    "FAIL if the run owner is context_tools.bdd.bdd:Bdd with action sketch.",
                )
