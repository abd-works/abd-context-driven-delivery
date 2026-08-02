# @agent-spec-manifest python -m tools agent-spec context_tools/create_context_tool/create_context_tool_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/create_context_tool/.context/.agent_bdd_sessions/car-chronicle.json
"""BDD agent spec for create_context_tool — generate and repair via shared helpers."""

from expects import be_true, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    expect_instructions_contain,
    expect_instructions_contain_any,
    expect_ok_action,
    expect_tools_include,
    follow_instructions,
    read_workspace,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_CAR_ROOT = "context_tools/create_context_tool/examples/car_chronicle"
_OUTPUT_DIR = _REPO_ROOT / _CAR_ROOT / "output"
_CAR_CHRONICLE_PY = f"{_CAR_ROOT}/car_chronicle.py"
_CAR_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
)

with description("a CarChronicle generator"):
    with context("with agent and generate action"):
        with it("drives generate then judges the chronicle"):
            with agent(_REPO_ROOT, _SESSIONS / "car-chronicle.json"):
                read_workspace(_CAR_CHRONICLE_PY)

                response = run_toolset(
                    toolset=_CAR_TOOLSET,
                    action="generate",
                    timeout_seconds=120,
                )
                expect_ok_action(response, "generate")
                expect_tools_include(response, ["read_context_index", "record_context_root"])
                expect_instructions_contain_any(
                    response, "driving voice", "use-driving-voice"
                )

                chronicle_result = follow_instructions(
                    "Follow the generate instructions and write a driving chronicle entry "
                    "for one trip from the Hazzard County garage to the courthouse.",
                    timeout_seconds=600,
                )
                chronicle_files = list(_OUTPUT_DIR.glob("*.md")) if _OUTPUT_DIR.is_dir() else []
                wrote_file = len(chronicle_files) > 0
                mentioned = (
                    f"{_CAR_ROOT}/output" in chronicle_result.text.lower() or wrote_file
                )
                expect(mentioned).to(be_true)

                chronicle_text = (
                    chronicle_files[0].read_text(encoding="utf-8")
                    if wrote_file
                    else chronicle_result.text
                )
                ai_judge(
                    chronicle_text,
                    "The chronicle is a first-person driving log with a named route, "
                    "mileage or odometer numbers, and the car's personality.",
                )

    with context("with agent and repair action"):
        with it("drives repair and asserts instruction expansion"):
            with agent(_REPO_ROOT, _SESSIONS / "car-chronicle-repair.json"):
                read_workspace(_CAR_CHRONICLE_PY)

                response = run_toolset(
                    toolset=_CAR_TOOLSET,
                    action="repair",
                    arguments={
                        "asset": f"{_CAR_ROOT}/output/driving-log.md",
                        "violation": (
                            "Scanner use-driving-voice - chronicle reads like a spec sheet"
                        ),
                    },
                    timeout_seconds=120,
                )
                expect_ok_action(response, "repair")
                expect_tools_include(response, ["scan"])
                expect_instructions_contain(
                    response,
                    "fix the generator",
                    "descriptive-folder",
                    "delete `runs/`",
                    "do not hand-edit",
                    f"{_CAR_ROOT}/output/driving-log.md",
                    "use-driving-voice",
                )
