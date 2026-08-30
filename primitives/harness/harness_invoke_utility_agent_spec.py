# @agent-spec-manifest python -m tools agent-spec primitives/harness/harness_invoke_utility_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: primitives/harness/.context/.agent_bdd_sessions/invoke-utility.json
"""Strict agent BDD — Car skill + car-inspect lists wrap_story utility tool."""

from pathlib import Path

from expects import be_true, expect
from mamba import description, it

from agent_bdd import (
    agent,
    expect_ok_action,
    read_workspace,
    repo_root_from,
    run_skill,
    sessions_dir,
)
from agent_bdd.spec_helpers import expect_agent_invoked_shell
from harness.harness_invoke_fixtures import (
    CAR_INSPECT,
    CAR_SKILL,
    car_tool_argument,
    stage_invoke_commands,
)

_REPO = repo_root_from(__file__, parents=2)
stage_invoke_commands(_REPO)
_SESSIONS = sessions_dir(__file__)


def _session(name: str) -> Path:
    path = _SESSIONS / f"invoke-utility-{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    return path


with description("invoke action with utility tool from deployed prompt (strict)"):
    with it("reads car skill and car-inspect.md; lists wrap_story in response.tools"):
        with agent(_REPO, _session("car-inspect")) as block:
            read_workspace(CAR_SKILL)
            read_workspace(CAR_INSPECT)
            response = run_skill(
                CAR_INSPECT,
                repo_root=_REPO,
                arguments={
                    "tools": [car_tool_argument()],
                    "plan": "Drive to town and back.",
                },
                timeout_seconds=180,
                require_agent_shell=True,
            )
            expect_agent_invoked_shell(block)
            expect_ok_action(response, "inspect_trip")
            expect("wrap_story" in [str(t).lower() for t in (response.tools or [])]).to(be_true)
