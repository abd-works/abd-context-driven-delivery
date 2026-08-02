"""
# @toolset-manifest python -m tools manifest agent_bdd.agent_bdd:AgentBdd
"""
# @agent-spec-manifest python -m tools agent-spec context_tools/agent_bdd/examples/generate-action.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: context_tools/agent_bdd/.agent_bdd_sessions/generate-action-example.json
"""Example — helpers: read → run_toolset → follow → ai_judge."""
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
from mamba import context, description, it

_REPO_ROOT = repo_root_from(__file__, parents=3)
_SESSIONS = sessions_dir(__file__)

with description("a CarChronicle generator"):
    with context("with agent and generate action"):
        with it("drives generate then judges the log"):
            with agent(_REPO_ROOT, _SESSIONS / "generate-action-example.json"):
                read_workspace(
                    "context_tools/create_context_tool/examples/car_chronicle/car_chronicle.py"
                )

                response = run_toolset(
                    toolset=(
                        "context_tools.create_context_tool.examples."
                        "car_chronicle.car_chronicle:CarChronicle"
                    ),
                    action="generate",
                    timeout_seconds=120,
                )
                expect_ok_action(response, "generate")
                expect_instructions_contain(response, "use-driving-voice")

                chronicle = follow_instructions(
                    "Follow the generate instructions and write a driving chronicle entry "
                    "for one trip from the Hazzard County garage to the courthouse.",
                    timeout_seconds=300,
                ).text
                ai_judge(
                    chronicle,
                    "The chronicle is a first-person driving log with a named route, "
                    "mileage or odometer numbers, and the car's personality.",
                )
