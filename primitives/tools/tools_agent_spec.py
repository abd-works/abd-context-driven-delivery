# @agent-spec-manifest python -m tools agent-spec primitives/tools/tools_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: primitives/tools/.context/.agent_bdd_sessions/general-lee.json
"""BDD agent spec for tools-behavior.md — construct resources, then multi-tool CLI use."""

from expects import be_true, equal, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    expect_ok_tool,
    read_workspace,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_CAR_PY = "primitives/tools/examples/car/car.py"
_CAR_TOOLSET = "tools.examples.car:Car"
_LEE = {
    "make": "Dodge",
    "model": "Charger",
    "year": 1969,
    "personality": "a rebellious, high-spirited, and loyal country boy",
}

with description("a class"):
    with context("with a toolset applied"):
        with context("with agent"):
            with it("starts, speaks, and judges General Lee personality"):
                with agent(_REPO_ROOT, _SESSIONS / "general-lee.json"):
                    read_workspace(_CAR_PY)

                    started = run_toolset(
                        toolset=_CAR_TOOLSET,
                        tool="start",
                        context=_LEE,
                        timeout_seconds=120,
                    )
                    expect_ok_tool(started, "start")
                    expect(started.resources.get("running")).to(be_true)
                    expect("Dodge" in str(started.resources.get("make", ""))).to(be_true)
                    expect("Charger" in str(started.resources.get("model", ""))).to(be_true)
                    expect(started.resources.get("year")).to(equal(1969))

                    spoken = run_toolset(
                        toolset=_CAR_TOOLSET,
                        tool="speak",
                        context=_LEE,
                        arguments={"line": "Yee-haw! Hazzard County or bust!"},
                        timeout_seconds=120,
                    )
                    expect_ok_tool(spoken, "speak")
                    expect("says" in str(spoken.result).lower()).to(be_true)

                    ai_judge(
                        str(started.resources.get("personality", "")),
                        "The car personality is a rebellious, high-spirited, and loyal country boy.",
                    )
