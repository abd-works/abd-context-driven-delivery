# @agent-spec-manifest python -m tools agent-spec primitives/harness/harness_manifest_alone_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: primitives/harness/.context/.agent_bdd_sessions/manifest-alone-45.json
"""E2E agent BDD for #45 — harness-deployed car skill + command prompts (strict)."""

import os
import subprocess
import time
from pathlib import Path

from expects import be_above, be_below, be_true, equal, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    expect_ok_action,
    expect_ok_tool,
    read_workspace,
    repo_root_from,
    run_skill,
    sessions_dir,
)
from agent_bdd.spec_helpers import expect_agent_invoked_shell, run_yaml_from_command
from agent_bdd.yaml_fence import load_fenced
from harness.harness_invoke_fixtures import (
    CAR_CTX,
    CAR_INSPECT,
    CAR_ROAD_STORY,
    CAR_SKILL,
    CAR_START,
    TRAVEL_TO,
    car_tool_argument,
    stage_invoke_commands,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
stage_invoke_commands(_REPO_ROOT)
_SESSIONS = sessions_dir(__file__)

_AGENT_BUDGET_S = 90.0
_CLI_OVERHEAD_S = 5.0
_STABILITY_RUNS = 3


def _session(name: str) -> Path:
    path = _SESSIONS / f"manifest-alone-45-{name}.json"
    path.write_text("{}", encoding="utf-8")
    return path


def _run_skill_strict(block: object, command: str, **kwargs: object):
    response = run_skill(
        command,
        repo_root=_REPO_ROOT,
        require_agent_shell=True,
        **kwargs,
    )
    expect_agent_invoked_shell(block)
    return response


def _cli_time(run_yaml: str) -> float:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    root = str(_REPO_ROOT)
    env["PYTHONPATH"] = os.pathsep.join(
        [
            root,
            str(_REPO_ROOT / "primitives"),
            str(_REPO_ROOT / "utilities"),
            str(_REPO_ROOT / "context_tools"),
            str(_REPO_ROOT / "context_tools" / "actions"),
        ]
    )
    py = str(_REPO_ROOT / ".venv" / "Scripts" / "python.exe")
    started = time.perf_counter()
    completed = subprocess.run(
        [py, "-m", "tools", "run", "-"],
        input=run_yaml,
        text=True,
        capture_output=True,
        cwd=root,
        env=env,
        timeout=30,
    )
    elapsed = time.perf_counter() - started
    expect(completed.returncode).to(equal(0))
    parsed = load_fenced(completed.stdout)
    expect(parsed.get("ok")).to(equal(True))
    expect(elapsed).to(be_below(_CLI_OVERHEAD_S))
    expect(elapsed).to(be_above(0.0))
    return elapsed


with description("manifest-alone E2E (#45)"):
    with context("CLI overhead (no agent)"):
        with it("invokes harness-deployed fences within CLI-only budget"):
            _cli_time(
                run_yaml_from_command(CAR_ROAD_STORY, repo_root=_REPO_ROOT, context=CAR_CTX)
            )
            _cli_time(run_yaml_from_command(CAR_START, repo_root=_REPO_ROOT, context=CAR_CTX))
            _cli_time(
                run_yaml_from_command(
                    TRAVEL_TO,
                    repo_root=_REPO_ROOT,
                    arguments={
                        "tools": [car_tool_argument()],
                        "destination": "town",
                        "conditions": "dry",
                    },
                )
            )

    with context("with strict agent shell (no harness replay)"):
        with it("reads car skill and runs car.road_story.md"):
            with agent(_REPO_ROOT, _session("fidelity-generate")) as block:
                read_workspace(CAR_SKILL)
                read_workspace(CAR_ROAD_STORY)
                started = time.perf_counter()
                response = _run_skill_strict(
                    block, CAR_ROAD_STORY, context=CAR_CTX, timeout_seconds=180
                )
                expect(time.perf_counter() - started).to(be_below(_AGENT_BUDGET_S))
                expect_ok_action(response, "generate")

        with it("reads car skill and runs car-start.md"):
            with agent(_REPO_ROOT, _session("one-tool")) as block:
                read_workspace(CAR_SKILL)
                read_workspace(CAR_START)
                response = _run_skill_strict(
                    block, CAR_START, context=CAR_CTX, timeout_seconds=180
                )
                expect_ok_tool(response, "start")
                expect((response.resources or {}).get("running")).to(equal(True))

        with it("reads car skill and travel-to.md; names start in response.tools"):
            with agent(_REPO_ROOT, _session("action-one-tool")) as block:
                read_workspace(CAR_SKILL)
                read_workspace(TRAVEL_TO)
                travel = _run_skill_strict(
                    block,
                    TRAVEL_TO,
                    arguments={
                        "tools": [car_tool_argument()],
                        "destination": "town",
                        "conditions": "dry",
                    },
                    timeout_seconds=180,
                )
                expect_ok_action(travel, "travelTo")
                expect("start" in [str(t).lower() for t in (travel.tools or [])]).to(
                    be_true
                )

        with it("reads car skill and travel-to.md; lists many tools"):
            with agent(_REPO_ROOT, _session("action-many-tools")) as block:
                read_workspace(CAR_SKILL)
                read_workspace(TRAVEL_TO)
                travel = _run_skill_strict(
                    block,
                    TRAVEL_TO,
                    arguments={
                        "tools": [car_tool_argument()],
                        "destination": "courthouse",
                        "conditions": "muddy",
                    },
                    timeout_seconds=180,
                )
                expect_ok_action(travel, "travelTo")
                tools = [str(t).lower() for t in (travel.tools or [])]
                expect("start" in tools).to(be_true)
                expect("speak" in tools).to(be_true)
                expect("stop" in tools).to(be_true)
                expect(len(tools)).to(be_above(3))

        with it("reads car skill and car-inspect.md; lists wrap_story"):
            with agent(_REPO_ROOT, _session("utility")) as block:
                read_workspace(CAR_SKILL)
                read_workspace(CAR_INSPECT)
                response = _run_skill_strict(
                    block,
                    CAR_INSPECT,
                    arguments={
                        "tools": [car_tool_argument()],
                        "plan": "Night run to Atlanta.",
                    },
                    timeout_seconds=180,
                )
                expect_ok_action(response, "inspect_trip")
                expect(
                    "wrap_story" in [str(t).lower() for t in (response.tools or [])]
                ).to(be_true)

        with it("invokes car-start.md reliably across three fresh sessions"):
            for attempt in range(_STABILITY_RUNS):
                with agent(_REPO_ROOT, _session(f"stability-{attempt}")) as block:
                    read_workspace(CAR_SKILL)
                    read_workspace(CAR_START)
                    response = _run_skill_strict(
                        block,
                        CAR_START,
                        context=CAR_CTX,
                        timeout_seconds=180,
                    )
                    expect_ok_tool(response, "start")
                    expect((response.resources or {}).get("running")).to(equal(True))
