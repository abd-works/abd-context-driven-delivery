# @agent-spec-manifest python -m tools agent-spec context_tools/actions/eval/repair_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/actions/eval/.context/.agent_bdd_sessions/repair-owns-tools.json
"""Agent BDD — /repair runs Improvement.repair(tools=...) not host repair."""

from expects import contain, equal, expect
from mamba import context, description, it

from agent_bdd import (
    agent,
    ai_judge,
    expect_ok_action,
    follow_instructions,
    read_workspace,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_IMPROVEMENT = "improvement.improvement:Improvement"
_BDD = "context_tools.bdd.bdd:Bdd"
_ASSET = "context_tools/bdd/bdd_spec.py"
_VIOLATION = "example scanner violation for agent BDD"


with description("a repair action"):
    with context("that is given one context tool"):
        with it("should run Improvement.repair with that tool, not the host repair"):
            with agent(_REPO_ROOT, _SESSIONS / "repair-owns-tools.json"):
                read_workspace(".cursor/commands/repair.md")
                read_workspace("context_tools/actions/improvement/improvement.py")

                response = run_toolset(
                    toolset=_IMPROVEMENT,
                    action="repair",
                    arguments={
                        "tools": [_BDD],
                        "asset": _ASSET,
                        "violation": _VIOLATION,
                    },
                    timeout_seconds=300,
                )
                expect_ok_action(response, "repair")
                expect(response.toolset).to(equal(_IMPROVEMENT))
                expect(str(response.arguments)).to(contain("bdd"))

                explanation = follow_instructions(
                    "The user invoked /bdd /repair. Using the repair command you read, "
                    "say which toolset owns the run and how the BDD tool is passed. "
                    "Do not invoke host repair on Bdd.",
                    timeout_seconds=180,
                ).text
                ai_judge(
                    f"{explanation}\n---\ntoolset: {response.toolset}\n"
                    f"action: {response.action}\narguments: {response.arguments}",
                    "PASS only if repair is owned by improvement.improvement:Improvement and the "
                    "BDD context tool is an argument in tools (one or more context tools). "
                    "FAIL if the run owner is context_tools.bdd.bdd:Bdd with action repair.",
                )
