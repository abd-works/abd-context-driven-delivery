# @agent-spec-manifest python -m tools agent-spec utilities/cli_agent/cli_agent_44_dup_spawn_agent_spec.py
# Agent reading this file: run via agent BDD CLI harness (cursor-agent).
# harness: cli
# session: utilities/cli_agent/.context/.agent_bdd_sessions/run-backlog-44-dup.json
"""#44 step 1 — double launch_next must spawn the doer once.

Run this file alone. Do not chain other #44 agent BDDs in the same process.
"""
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import description, it

from agent_bdd import agent
from agent_bdd.spec_helpers import (
    expect_ok_tool,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

from cli_agent._agent_bdd_support import CLI, HOP_S, ctx, kinds, spawn_count

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("#44 dup spawn"):
    with it("should spawn doer only once when launch_next is called twice"):
        with agent(_REPO_ROOT, _SESSIONS / "run-backlog-44-dup.json"):
            workspace = Path(tempfile.mkdtemp(prefix="cli44_dup_"))
            session = "dup-44"
            c = ctx(workspace, session)
            expect_ok_tool(
                run_toolset(
                    toolset=CLI,
                    tool="enqueue_jobs",
                    context=c,
                    arguments={
                        "jobs": [
                            {
                                "prompt": "Reply WAITING and keep this Turn open.",
                                "tools": [],
                                "judge": False,
                            }
                        ]
                    },
                    timeout_seconds=HOP_S,
                ),
                "enqueue_jobs",
            )
            expect_ok_tool(
                run_toolset(
                    toolset=CLI, tool="launch_next", context=c, timeout_seconds=HOP_S
                ),
                "launch_next",
            )
            expect(spawn_count(workspace, session)).to(equal(1))
            expect_ok_tool(
                run_toolset(
                    toolset=CLI, tool="launch_next", context=c, timeout_seconds=HOP_S
                ),
                "launch_next",
            )
            expect(spawn_count(workspace, session)).to(equal(1))
            expect(kinds(workspace, session).count("spawn")).to(equal(1))
