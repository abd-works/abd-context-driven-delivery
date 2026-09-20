# harness: in_chat
# session: installation/.context/.agent_bdd_sessions/harness-invoke.json
"""Installer agent BDD — deployed car skills and commands."""

from pathlib import Path

from expects import be_above, be_true, equal, expect
from mamba import before, context, description, it

from agent_bdd.spec_helpers import (
    expect_ok_action,
    expect_ok_tool,
    invoke_toolset,
    repo_root_from,
)
from installation.installer import Installer
from harness.agent_tools.agent_tools import AgentToolSet

CAR = "practices.car.car:Car"
CAR_CTX = {
    "fidelity": "road_story",
    "make": "Dodge",
    "model": "Charger",
    "year": 1969,
    "personality": "General Lee",
}
CAR_ROAD_STORY = ".cursor/skills/context_tools/car/car-road-story/SKILL.md"
CAR_START = ".cursor/skills/context_tools/car/car-start/SKILL.md"
TRAVEL_TO = ".cursor/skills/actions/travel-to/SKILL.md"
CAR_INSPECT = ".cursor/skills/actions/car-inspect/SKILL.md"
_staged_roots: set[str] = set()


def car_tool_argument() -> dict:
    return {"toolset": CAR, "context": dict(CAR_CTX)}


def invoke_request_for_path(command: str | Path, *, repo_root: Path) -> dict:
    path = Path(command)
    key = str(path.as_posix()).replace("\\", "/")
    if not path.is_file():
        candidate = (repo_root / path).resolve()
        key = str(candidate.relative_to(repo_root.resolve()).as_posix()).replace("\\", "/")
    mapping = {
        CAR_ROAD_STORY.replace("\\", "/"): {
            "toolset": CAR,
            "action": "generate",
            "context": dict(CAR_CTX),
        },
        CAR_START.replace("\\", "/"): {
            "toolset": CAR,
            "tool": "start",
            "context": dict(CAR_CTX),
        },
        TRAVEL_TO.replace("\\", "/"): {
            "toolset": "actions.examples.car_story.car_story:CarStory",
            "action": "travelTo",
            "arguments": {
                "guidance": [car_tool_argument()],
                "destination": "town",
                "conditions": "dry",
            },
        },
        CAR_INSPECT.replace("\\", "/"): {
            "toolset": "actions.examples.car_story.car_story:CarStory",
            "action": "inspect_trip",
            "arguments": {
                "guidance": [car_tool_argument()],
                "plan": "Night run to Atlanta.",
            },
        },
    }
    if key not in mapping:
        raise KeyError(f"No invoke mapping for deployed path {key!r}")
    return dict(mapping[key])


def stage_invoke_commands(repo_root: Path) -> None:
    car = AgentToolSet.instantiate(CAR)
    car_story = AgentToolSet.instantiate("actions.examples.car_story.car_story:CarStory")
    Installer("Cursor", path=repo_root / ".cursor").install([car, car_story])


def ensure_invoke_staged(repo_root: Path) -> None:
    key = str(repo_root.resolve())
    if key in _staged_roots:
        return
    stage_invoke_commands(repo_root)
    _staged_roots.add(key)


_REPO_ROOT = repo_root_from(__file__, parents=1)


with description("harness invoke in-process"):
    with before.all:
        ensure_invoke_staged(_REPO_ROOT)

    with context("deployed car paths"):
        with it("should invoke car-road_story generate"):
            request = invoke_request_for_path(CAR_ROAD_STORY, repo_root=_REPO_ROOT)
            response = invoke_toolset(
                toolset=request["toolset"],
                action=request["action"],
                context=request.get("context"),
            )
            expect_ok_action(response, "generate", require_instructions=False)
            expect(response.toolset).to(equal(CAR))

        with it("should invoke car-start start tool"):
            request = invoke_request_for_path(CAR_START, repo_root=_REPO_ROOT)
            response = invoke_toolset(
                toolset=request["toolset"],
                tool=request["tool"],
                context=request.get("context"),
            )
            expect_ok_tool(response, "start")

        with it("should invoke travel-to with start in response.tools"):
            request = invoke_request_for_path(TRAVEL_TO, repo_root=_REPO_ROOT)
            response = invoke_toolset(
                toolset=request["toolset"],
                action=request["action"],
                arguments=request["arguments"],
            )
            expect_ok_action(response, "travelTo")
            expect("start" in [str(t).lower() for t in (response.tools or [])]).to(be_true)

        with it("should invoke travel-to with many tools listed"):
            response = invoke_toolset(
                toolset="actions.examples.car_story.car_story:CarStory",
                action="travelTo",
                arguments={
                    "guidance": [car_tool_argument()],
                    "destination": "courthouse",
                    "conditions": "muddy",
                },
            )
            expect_ok_action(response, "travelTo")
            tools = [str(t).lower() for t in (response.tools or [])]
            expect("start" in tools).to(be_true)
            expect("speak" in tools).to(be_true)
            expect("stop" in tools).to(be_true)
            expect(len(tools)).to(be_above(3))

        with it("should invoke car-inspect with wrap_story in response.tools"):
            request = invoke_request_for_path(CAR_INSPECT, repo_root=_REPO_ROOT)
            response = invoke_toolset(
                toolset=request["toolset"],
                action=request["action"],
                arguments=request["arguments"],
            )
            expect_ok_action(response, "inspect_trip")
            expect(
                "wrap_story" in [str(t).lower() for t in (response.tools or [])]
            ).to(be_true)

        with it("should invoke car-start reliably across repeated calls"):
            request = invoke_request_for_path(CAR_START, repo_root=_REPO_ROOT)
            for _ in range(3):
                response = invoke_toolset(
                    toolset=request["toolset"],
                    tool=request["tool"],
                    context=dict(CAR_CTX),
                )
                expect_ok_tool(response, "start")
