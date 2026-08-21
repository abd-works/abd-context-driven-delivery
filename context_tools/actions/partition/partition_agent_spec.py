# @agent-spec-manifest python -m tools agent-spec context_tools/actions/partition/partition_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: cli
# session: context_tools/actions/partition/.context/.agent_bdd_sessions/partition-owns-tools.json
"""Agent BDD — /partition runs Partition.partition(tools=...) not host partition."""

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
_PARTITION = "partition.partition:Partition"
_BDD = "context_tools.bdd.bdd:Bdd"
_CONTEXT = "context_tools/bdd/bdd.py"


with description("a partition action"):
    with context("that is given one context tool"):
        with it("should run Partition.partition with that tool, not the host partition"):
            with agent(_REPO_ROOT, _SESSIONS / "partition-owns-tools.json"):
                read_workspace(".cursor/commands/partition.md")
                read_workspace("context_tools/actions/partition/partition.py")

                response = run_toolset(
                    toolset=_PARTITION,
                    action="partition",
                    arguments={
                        "tools": [_BDD],
                        "context": _CONTEXT,
                        "mode": "one_go",
                    },
                    timeout_seconds=300,
                )
                expect_ok_action(response, "partition")
                expect(response.toolset).to(equal(_PARTITION))
                expect(str(response.arguments)).to(contain("bdd"))

                explanation = follow_instructions(
                    "The user invoked /bdd /partition. Using the partition command you read, "
                    "say which toolset owns the run and how the BDD tool is passed. "
                    "Do not invoke host partition on Bdd.",
                    timeout_seconds=180,
                ).text
                ai_judge(
                    f"{explanation}\n---\ntoolset: {response.toolset}\n"
                    f"action: {response.action}\narguments: {response.arguments}",
                    "PASS only if partition is owned by partition.partition:Partition and the "
                    "BDD context tool is an argument in tools (one or more context tools). "
                    "FAIL if the run owner is context_tools.bdd.bdd:Bdd with action partition.",
                )
