"""Mechanical spec — harness deploy produces car skill + command prompts."""
from pathlib import Path

from expects import be_true, equal, expect
from mamba import context, description, it

from agent_bdd.spec_helpers import (
    command_fence_yaml,
    parse_command_fence,
    repo_root_from,
    run_yaml_from_command,
)
from agent_bdd.yaml_fence import load_fenced
from harness.harness_invoke_fixtures import (
    CAR,
    CAR_INSPECT,
    CAR_ROAD_STORY,
    CAR_SKILL,
    CAR_START,
    TRAVEL_TO,
    car_tool_argument,
    stage_invoke_commands,
)

_REPO = repo_root_from(__file__, parents=2)


def _cli_run(run_yaml: str) -> dict:
    import os
    import subprocess

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    root = str(_REPO)
    env["PYTHONPATH"] = os.pathsep.join(
        [
            root,
            str(_REPO / "primitives"),
            str(_REPO / "utilities"),
            str(_REPO / "context_tools"),
            str(_REPO / "context_tools" / "actions"),
        ]
    )
    py = str(_REPO / ".venv" / "Scripts" / "python.exe")
    completed = subprocess.run(
        [py, "-m", "tools", "run", "-"],
        input=run_yaml,
        text=True,
        capture_output=True,
        cwd=root,
        env=env,
        timeout=30,
    )
    expect(completed.returncode).to(equal(0))
    parsed = load_fenced(completed.stdout)
    expect(parsed.get("ok")).to(equal(True))
    return parsed


with description("harness deploy for car invoke BDD"):
    with context("after write_deploy"):
        with it("should write the car context tool skill"):
            stage_invoke_commands(_REPO)
            skill = _REPO / CAR_SKILL
            expect(skill.is_file()).to(be_true)
            body = skill.read_text(encoding="utf-8")
            expect("AskQuestion constrained to these actions" in body).to(be_true)
            expect("trip_outline" in body or "road_story" in body).to(be_true)

        with it("should write fidelity and action command prompts"):
            stage_invoke_commands(_REPO)
            expect((_REPO / CAR_ROAD_STORY).is_file()).to(be_true)
            expect((_REPO / TRAVEL_TO).is_file()).to(be_true)
            expect((_REPO / CAR_START).is_file()).to(be_true)
            expect((_REPO / CAR_INSPECT).is_file()).to(be_true)

        with it("should parse car.road_story.md fence like bdd.behavior.md"):
            stage_invoke_commands(_REPO)
            payload = parse_command_fence(CAR_ROAD_STORY, repo_root=_REPO)
            expect(payload.get("toolset")).to(equal(CAR))
            expect(payload.get("action")).to(equal("generate"))
            expect(payload.get("context", {}).get("fidelity")).to(equal("road_story"))

        with it("should invoke each deployed fence via CLI"):
            stage_invoke_commands(_REPO)
            gen = _cli_run(
                run_yaml_from_command(CAR_ROAD_STORY, repo_root=_REPO, context={"make": "Dodge", "model": "Charger", "year": 1969, "personality": "loyal"})
            )
            expect(gen.get("action")).to(equal("generate"))
            start = _cli_run(
                run_yaml_from_command(CAR_START, repo_root=_REPO, context={"make": "Dodge", "model": "Charger", "year": 1969, "personality": "loyal", "fidelity": "road_story"})
            )
            expect(start.get("tool")).to(equal("start"))
            travel = _cli_run(
                run_yaml_from_command(
                    TRAVEL_TO,
                    repo_root=_REPO,
                    arguments={
                        "tools": [car_tool_argument()],
                        "destination": "town",
                        "conditions": "dry",
                    },
                )
            )
            tools = [str(t).lower() for t in (travel.get("tools") or [])]
            expect("start" in tools).to(be_true)
            inspect = _cli_run(
                run_yaml_from_command(
                    CAR_INSPECT,
                    repo_root=_REPO,
                    arguments={"tools": [car_tool_argument()], "plan": "test"},
                )
            )
            expect("wrap_story" in [str(t).lower() for t in (inspect.get("tools") or [])]).to(
                be_true
            )

        with it("should preserve exact fence text for agent prompts"):
            stage_invoke_commands(_REPO)
            fence = command_fence_yaml(CAR_START, repo_root=_REPO)
            expect("tool: start" in fence).to(equal(True))
            expect("toolset: context_tools.car.car:Car" in fence).to(equal(True))
