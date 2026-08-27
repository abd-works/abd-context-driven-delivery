# @agent-spec-manifest python -m tools agent-spec context_tools/actions/iterate/iterate_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/actions/iterate/.context/.agent_bdd_sessions/iterate-owns-tools.json
"""Agent BDD — /iterate runs Iterate.iterate(tools=...) not host iterate."""

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

_REPO_ROOT = repo_root_from(__file__, parents=3)
_SESSIONS = sessions_dir(__file__)
_ITERATOR = "iterate.iterate:Iterate"
_BDD = "context_tools.bdd.bdd:Bdd"


with description("an iterate action"):
    with context("that is given one context tool"):
        with it("should run Iterate.iterate with that tool, not the host iterate"):
            with agent(_REPO_ROOT, _SESSIONS / "iterate-owns-tools.json"):
                read_workspace(".cursor/commands/iterate.md")
                read_workspace("context_tools/actions/iterate/iterate.py")

                response = run_toolset(
                    toolset=_ITERATOR,
                    action="iterate",
                    arguments={"tools": [_BDD]},
                    timeout_seconds=300,
                )
                expect_ok_action(response, "iterate")
                expect(response.toolset).to(equal(_ITERATOR))
                expect(str(response.arguments)).to(contain("bdd"))

                explanation = follow_instructions(
                    "The user invoked /bdd /iterate. Using the iterate command you read, "
                    "say which toolset owns the run and how the BDD tool is passed. "
                    "Do not invoke host iterate on Bdd.",
                    timeout_seconds=180,
                ).text
                ai_judge(
                    f"{explanation}\n---\ntoolset: {response.toolset}\n"
                    f"action: {response.action}\narguments: {response.arguments}",
                    "PASS only if iterate is owned by iterate.iterate:Iterate and the "
                    "BDD context tool is an argument in tools (one or more context tools). "
                    "FAIL if the run owner is context_tools.bdd.bdd:Bdd with action iterate.",
                )
