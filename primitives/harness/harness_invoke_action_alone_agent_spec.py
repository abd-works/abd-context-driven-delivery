# @agent-spec-manifest python -m tools agent-spec primitives/harness/harness_invoke_action_alone_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: primitives/harness/.context/.agent_bdd_sessions/invoke-action-alone.json
"""Strict agent BDD — Car skill + car.road_story fidelity command (generate)."""

from pathlib import Path

from expects import equal, expect
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
    CAR_CTX,
    CAR_ROAD_STORY,
    CAR_SKILL,
    stage_invoke_commands,
)

_REPO = repo_root_from(__file__, parents=2)
stage_invoke_commands(_REPO)
_SESSIONS = sessions_dir(__file__)


def _session(name: str) -> Path:
    path = _SESSIONS / f"invoke-action-alone-{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    return path


with description("invoke context tool fidelity command (strict)"):
    with it("reads car skill and runs car.road_story.md with shell capture"):
        with agent(_REPO, _session("road-story")) as block:
            read_workspace(CAR_SKILL)
            read_workspace(CAR_ROAD_STORY)
            response = run_skill(
                CAR_ROAD_STORY,
                repo_root=_REPO,
                context=CAR_CTX,
                timeout_seconds=180,
                require_agent_shell=True,
            )
            expect_agent_invoked_shell(block)
            expect_ok_action(response, "generate")
            expect(response.toolset).to(equal("context_tools.car.car:Car"))
