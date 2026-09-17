"""Unit spec for agent_bdd.spec_helpers — no live agent."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "practices", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect, raise_error
from mamba import context, description, it

from agent_bdd.spec_helpers import (
    command_fence_yaml,
    dump_run_yaml,
    generate_similar_prompt,
    generate_similar_rubric,
    parse_command_fence,
    repo_root_from,
    run_yaml_from_command,
    sessions_dir,
    tools_run_prompt,
    tools_run_prompt_from_command,
)
from harness.harness_invoke_fixtures import (
    CAR,
    CAR_ROAD_STORY,
    CAR_START,
    stage_invoke_commands,
)


with description("spec_helpers"):
    with context("dump_run_yaml"):
        with it("should serialize an action request"):
            body = dump_run_yaml(
                toolset="pkg:Tool",
                action="generate",
                context={"format": "python"},
            )
            expect("toolset: pkg:Tool" in body).to(equal(True))
            expect("action: generate" in body).to(equal(True))
            expect("format: python" in body).to(equal(True))

        with it("should serialize a tool request with arguments"):
            body = dump_run_yaml(
                toolset="pkg:Tool",
                tool="scan",
                arguments={"paths": ["a.py"]},
            )
            expect("tool: scan" in body).to(equal(True))
            expect("paths" in body).to(equal(True))

        with it("should reject missing tool and action"):
            expect(lambda: dump_run_yaml(toolset="pkg:Tool")).to(raise_error(ValueError))

        with it("should reject both tool and action"):
            expect(
                lambda: dump_run_yaml(toolset="pkg:Tool", tool="scan", action="generate")
            ).to(raise_error(ValueError))

    with context("tools_run_prompt"):
        with it("should wrap YAML for stdin tools run via tools.ps1 (#45)"):
            prompt = tools_run_prompt("toolset: X\naction: generate\n")
            expect("tools.ps1 run -" in prompt).to(equal(True))
            expect("action: generate" in prompt).to(equal(True))
            expect("python -m harness manifest" in prompt).to(equal(False))

        with it("should round-trip yaml via yaml_from_prompt"):
            from agent_bdd.agent_bdd_common import yaml_from_prompt

            yaml = dump_run_yaml(toolset="agent_tools.examples.car:Car", tool="start")
            prompt = tools_run_prompt(yaml)
            body = yaml_from_prompt(prompt)
            expect(body.strip()).to(equal(yaml.strip()))

    with context("deployed command fences"):
        with it("should parse car.road_story.md invoke fence"):
            root = repo_root_from(__file__, parents=2)
            stage_invoke_commands(root)
            payload = parse_command_fence(CAR_ROAD_STORY, repo_root=root)
            expect(payload.get("toolset")).to(equal(CAR))
            expect(payload.get("action")).to(equal("generate"))

        with it("should build run yaml from travel-to.md with tools argument"):
            root = repo_root_from(__file__, parents=2)
            stage_invoke_commands(root)
            from harness.harness_invoke_fixtures import TRAVEL_TO, car_tool_argument

            body = run_yaml_from_command(
                TRAVEL_TO,
                repo_root=root,
                arguments={
                    "tools": [car_tool_argument()],
                    "destination": "town",
                    "conditions": "dry",
                },
            )
            expect("action: travelTo" in body).to(equal(True))
            expect("destination: town" in body).to(equal(True))

        with it("should build tools run prompt from deployed car-start fence"):
            root = repo_root_from(__file__, parents=2)
            stage_invoke_commands(root)
            prompt = tools_run_prompt_from_command(CAR_START, repo_root=root)
            expect("tool: start" in prompt).to(equal(True))
            expect("tools.ps1 run -" in prompt).to(equal(True))

        with it("should return the exact fence body from car-start.md"):
            root = repo_root_from(__file__, parents=2)
            stage_invoke_commands(root)
            fence = command_fence_yaml(CAR_START, repo_root=root)
            expect("tool: start" in fence).to(equal(True))
            expect("toolset: practices.car.car:Car" in fence).to(equal(True))

    with context("path helpers"):
        with it("should resolve sessions beside the spec file"):
            fake = Path(__file__).resolve()
            expect(sessions_dir(fake)).to(
                equal(fake.parent / ".context" / ".agent_bdd_sessions")
            )

        with it("should resolve repo root from this package"):
            root = repo_root_from(__file__, parents=2)
            expect((root / "practices" / "agent_bdd").is_dir()).to(equal(True))


    with context("a pass fixture handed to generate"):
        with it("should ask the agent to generate something similar"):
            prompt = generate_similar_prompt(Path("repairedAsset.md"))
            expect("similar" in prompt.lower()).to(equal(True))
            expect("repairedAsset.md" in prompt.replace("\\", "/")).to(equal(True))

        with it("should judge the generate against that pass file"):
            rubric = generate_similar_rubric(Path("repairedAsset.md"))
            expect("repairedAsset.md" in rubric.replace("\\", "/")).to(equal(True))
            expect("similar" in rubric.lower()).to(equal(True))
