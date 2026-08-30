# @agent-spec-manifest python -m tools agent-spec utilities/cli_agent/cli_agent_44_finish_worktree_agent_spec.py
# Agent reading this file: run via agent BDD CLI harness (cursor-agent).
# harness: cli
# session: utilities/cli_agent/.context/.agent_bdd_sessions/run-backlog-44-finish.json
"""#44 step 3 — finish_work_session alone removes the worktree.

No doer/judge/run_backlog here. Step 2 already proved judged PASS.
Run alone after one-judged-job is green.
"""
from expects import be_none, be_true, expect
from mamba import description, it, _it

from agent_bdd import agent
from agent_bdd.spec_helpers import (
    expect_ok_tool,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

from cli_agent._agent_bdd_support import HOP_S, WS, commit_all, ctx, init_git_repo, worktree

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("#44 finish worktree"):
    with _it("should remove the worktree on finish_work_session"):
        with agent(_REPO_ROOT, _SESSIONS / "run-backlog-44-finish.json"):
            primary = init_git_repo("cli44_fin_")
            session = "finish-44"
            expect_ok_tool(
                run_toolset(
                    toolset=WS,
                    tool="start_work_session",
                    context=ctx(primary, session),
                    arguments={"name": session, "goal": "finish-only"},
                    timeout_seconds=HOP_S,
                ),
                "start_work_session",
            )
            tree = worktree(primary, session)
            expect(tree is not None).to(be_true)
            assert tree is not None
            c = ctx(tree, session)
            commit_all(tree, "touch so finish has a commit path")
            expect_ok_tool(
                run_toolset(
                    toolset=WS,
                    tool="finish_work_session",
                    context=c,
                    arguments={"outcome": "finish-only done"},
                    timeout_seconds=HOP_S,
                ),
                "finish_work_session",
            )
