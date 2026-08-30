# @agent-spec-manifest python -m tools agent-spec primitives/harness/harness_invoke_one_tool_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: primitives/harness/.context/.agent_bdd_sessions/invoke-one-tool.json
"""Strict agent BDD — Car context tool, car-start prompt, one tool invoke."""

from pathlib import Path

from expects import equal, expect
from mamba import description, it

from agent_bdd import (
    agent,
    expect_ok_tool,
    read_workspace,
    repo_root_from,
    run_skill,
    sessions_dir,
)
from agent_bdd.spec_helpers import expect_agent_invoked_shell
from harness.harness_invoke_fixtures import (
    CAR_CTX,
    CAR_SKILL,
    CAR_START,
    stage_invoke_commands,
)

_REPO = repo_root_from(__file__, parents=2)
stage_invoke_commands(_REPO)
_SESSIONS = sessions_dir(__file__)


def _session(name: str) -> Path:
    path = _SESSIONS / f"invoke-one-tool-{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    return path


with description("invoke one tool from deployed prompt (strict)"):
    with it("reads car skill and runs car-start.md with shell capture"):
        with agent(_REPO, _session("car-start")) as block:
            read_workspace(CAR_SKILL)
            read_workspace(CAR_START)
            response = run_skill(
                CAR_START,
                repo_root=_REPO,
                context=CAR_CTX,
                timeout_seconds=180,
                require_agent_shell=True,
            )
            expect_agent_invoked_shell(block)
            expect_ok_tool(response, "start")
            expect((response.resources or {}).get("running")).to(equal(True))
