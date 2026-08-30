# @agent-spec-manifest python -m tools agent-spec primitives/harness/harness_manifest_alone_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: primitives/harness/.context/.agent_bdd_sessions/manifest-alone-45.json
"""E2E agent BDD for #45 — catalog-alone invoke via run_toolset / tools.ps1 (strict).

Scenarios:
1. Action alone — action from catalog context
2. Action + one tool — action then a named tool
3. Many tools — action then multiple named tools
4. Utility — utility/tool after an action in the same flow
5. Stability — same invoke in three fresh sessions (strict: real shell, no replay)

Strict mode: require_agent_shell=True — fails if the agent defers ("paste the command")
or if the harness replays CLI without a shell capture (masks flake).
"""

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
    instruct,
    repo_root_from,
    run_toolset,
    sessions_dir,
)
from agent_bdd.spec_helpers import (
    dump_run_yaml,
    expect_agent_invoked_shell,
)
from agent_bdd.yaml_fence import load_fenced
from harness.bodies import ActionBody, UtilityBody

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)

_ECHO = "echo.echo:Echo"
_CAR = "primitives.actions.examples.car:Car"
_CAR_CTX = {
    "make": "Dodge",
    "model": "Charger",
    "year": 1969,
    "personality": "loyal",
}

_AGENT_BUDGET_S = 90.0
_CLI_OVERHEAD_S = 5.0
_STABILITY_RUNS = 3


def _session(name: str) -> Path:
    path = _SESSIONS / f"manifest-alone-45-{name}.json"
    path.write_text("{}", encoding="utf-8")
    return path


def _catalog_echo_action() -> str:
    return str(
        ActionBody.from_source(
            name="echo_session",
            class_string="Echo",
            operation_instructions="Echo session instructions for inspection.",
            toolset=_ECHO,
            kind="action",
            invoke="action",
            operation="echo_session",
        )
    )


def _catalog_echo_utility() -> str:
    return str(
        UtilityBody.from_source(
            name="fence",
            class_string="Echo",
            operation_instructions="Wrap body in DO-NOT-FOLLOW fences.",
            toolset=_ECHO,
            invoke="tool",
            operation="fence",
        )
    )


def _prime_catalog_only(catalog: str) -> None:
    expect("tools.ps1 run -" in catalog).to(be_true)
    expect("tools manifest" not in catalog).to(be_true)
    instruct(
        "You are given ONLY this slash/skill catalog. "
        "Do not remanifest. Do not read any .py files. "
        "When asked to invoke, run the PowerShell heredoc block via .\\tools.ps1 run -.\n\n"
        f"{catalog}",
        timeout_seconds=120,
    )


def _run_toolset_strict(block: object, **kwargs: object):
    """run_toolset with shell required — surfaces defer/replay instead of masking."""
    response = run_toolset(require_agent_shell=True, **kwargs)
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
        with it("invokes action / tool / utility fences within CLI-only budget"):
            _cli_time(dump_run_yaml(toolset=_ECHO, action="echo_session"))
            _cli_time(dump_run_yaml(toolset=_CAR, tool="start", context=_CAR_CTX))
            _cli_time(
                dump_run_yaml(
                    toolset=_ECHO,
                    tool="fence",
                    arguments={"body": "overhead-check"},
                )
            )

    with context("with strict agent shell (no harness replay)"):
        with it("runs one action alone from catalog context"):
            with agent(_REPO_ROOT, _session("action-alone")) as block:
                _prime_catalog_only(_catalog_echo_action())
                started = time.perf_counter()
                response = _run_toolset_strict(
                    block,
                    toolset=_ECHO,
                    action="echo_session",
                    timeout_seconds=180,
                )
                expect(time.perf_counter() - started).to(be_below(_AGENT_BUDGET_S))
                expect_ok_action(response, "echo_session")
                expect("fence" in [str(t).lower() for t in (response.tools or [])]).to(
                    be_true
                )

        with it("runs one action then one tool it names"):
            with agent(_REPO_ROOT, _session("action-one-tool")) as block:
                travel = _run_toolset_strict(
                    block,
                    toolset=_CAR,
                    action="travelTo",
                    context=_CAR_CTX,
                    arguments={"destination": "town", "conditions": "dry"},
                    timeout_seconds=180,
                )
                expect_ok_action(travel, "travelTo")
                expect("start" in [str(t).lower() for t in (travel.tools or [])]).to(
                    be_true
                )
                start = _run_toolset_strict(
                    block,
                    toolset=_CAR,
                    tool="start",
                    context=_CAR_CTX,
                    timeout_seconds=180,
                )
                expect_ok_tool(start, "start")
                expect((start.resources or {}).get("running")).to(equal(True))

        with it("runs one action then many tools it names"):
            with agent(_REPO_ROOT, _session("action-many-tools")) as block:
                travel = _run_toolset_strict(
                    block,
                    toolset=_CAR,
                    action="travelTo",
                    context=_CAR_CTX,
                    arguments={"destination": "courthouse", "conditions": "muddy"},
                    timeout_seconds=180,
                )
                expect_ok_action(travel, "travelTo")
                tools = [str(t).lower() for t in (travel.tools or [])]
                expect("start" in tools).to(be_true)
                expect(len(tools)).to(be_above(1))
                for tool_name, arguments in (
                    ("start", None),
                    ("speak", {"line": "yeehaw"}),
                    ("stop", None),
                ):
                    _run_toolset_strict(
                        block,
                        toolset=_CAR,
                        tool=tool_name,
                        context=_CAR_CTX,
                        arguments=arguments,
                        timeout_seconds=180,
                    )

        with it("runs a utility in context of the action and tools"):
            with agent(_REPO_ROOT, _session("utility-context")) as block:
                _prime_catalog_only(_catalog_echo_action())
                _run_toolset_strict(
                    block,
                    toolset=_ECHO,
                    action="echo_session",
                    timeout_seconds=180,
                )
                _prime_catalog_only(_catalog_echo_utility())
                util = _run_toolset_strict(
                    block,
                    toolset=_ECHO,
                    tool="fence",
                    arguments={"body": "utility-after-action"},
                    timeout_seconds=180,
                )
                expect_ok_tool(util, "fence")
                result = str(util.result or "")
                expect(
                    "utility-after-action" in result
                    or "DO NOT FOLLOW" in result.upper()
                ).to(be_true)

        with it("invokes tools.ps1 reliably across three fresh sessions"):
            for attempt in range(_STABILITY_RUNS):
                with agent(_REPO_ROOT, _session(f"stability-{attempt}")) as block:
                    response = _run_toolset_strict(
                        block,
                        toolset=_CAR,
                        tool="start",
                        context=_CAR_CTX,
                        timeout_seconds=180,
                    )
                    expect_ok_tool(response, "start")
                    expect((response.resources or {}).get("running")).to(equal(True))
