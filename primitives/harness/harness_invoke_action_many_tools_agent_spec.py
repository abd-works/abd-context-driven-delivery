# @agent-spec-manifest python -m tools agent-spec primitives/harness/harness_invoke_action_many_tools_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: primitives/harness/.context/.agent_bdd_sessions/invoke-action-many-tools.json
"""Strict agent BDD — Car skill + travel-to lists many Car tools (one pipe)."""

from pathlib import Path

from expects import be_above, be_true, expect
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
    CAR_SKILL,
    TRAVEL_TO,
    car_tool_argument,
    stage_invoke_commands,
)

_REPO = repo_root_from(__file__, parents=2)
stage_invoke_commands(_REPO)
_SESSIONS = sessions_dir(__file__)


def _session(name: str) -> Path:
    path = _SESSIONS / f"invoke-action-many-tools-{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    return path


with description("invoke CarStory action many tools (strict)"):
    with it("reads car skill and travel-to.md; lists start speak stop in response.tools"):
        with agent(_REPO, _session("car-many")) as block:
            read_workspace(CAR_SKILL)
            read_workspace(TRAVEL_TO)
            response = run_skill(
                TRAVEL_TO,
                repo_root=_REPO,
                arguments={
                    "tools": [car_tool_argument()],
                    "destination": "courthouse",
                    "conditions": "muddy",
                },
                timeout_seconds=180,
                require_agent_shell=True,
            )
            expect_agent_invoked_shell(block)
            expect_ok_action(response, "travelTo")
            tools = [str(t).lower() for t in (response.tools or [])]
            expect("start" in tools).to(be_true)
            expect("speak" in tools).to(be_true)
            expect("stop" in tools).to(be_true)
            expect(len(tools)).to(be_above(3))
