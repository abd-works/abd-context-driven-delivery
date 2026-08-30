# @agent-spec-manifest python -m tools agent-spec utilities/cli_agent/cli_agent_44_ordered_queue_agent_spec.py
# Agent reading this file: run via agent BDD CLI harness (cursor-agent).
# harness: cli
# session: utilities/cli_agent/.context/.agent_bdd_sessions/run-backlog-44-queue.json
"""#44 step 4 — jobs finish in order 0,1,2.

Judged PASS is proven in step 2. This only checks queue order + finish.
No judge. Short reply-only jobs.
"""
from expects import be_true, equal, expect
from mamba import description, it

from agent_bdd import agent
from agent_bdd.spec_helpers import (
    expect_ok_tool,
    repo_root_from,
    run_toolset,
    sessions_dir,
)

from cli_agent._agent_bdd_support import (
    BACKLOG_S,
    CLI,
    HOP_S,
    STALL_S,
    WS,
    commit_all,
    ctx,
    init_git_repo,
    records,
    worktree,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


def _plain(prompt: str) -> dict:
    return {"prompt": prompt, "tools": [], "judge": False}


with description("#44 ordered queue"):
    with it("should finish plain jobs in order 0,1,2 then remove worktree"):
        with agent(_REPO_ROOT, _SESSIONS / "run-backlog-44-queue.json"):
            primary = init_git_repo("cli44_q_")
            session = "queue-44"
            expect_ok_tool(
                run_toolset(
                    toolset=WS,
                    tool="start_work_session",
                    context=ctx(primary, session),
                    arguments={"name": session, "goal": "ordered queue"},
                    timeout_seconds=HOP_S,
                ),
                "start_work_session",
            )
            tree = worktree(primary, session)
            expect(tree is not None).to(be_true)
            assert tree is not None
            c = ctx(tree, session)
            jobs = [
                _plain("Reply exactly ONE and finish the Turn. Nothing else."),
                _plain("Reply exactly TWO and finish the Turn. Nothing else."),
                _plain("Reply exactly THREE and finish the Turn. Nothing else."),
            ]
            expect_ok_tool(
                run_toolset(
                    toolset=CLI,
                    tool="enqueue_jobs",
                    context=c,
                    arguments={"jobs": jobs},
                    timeout_seconds=HOP_S,
                ),
                "enqueue_jobs",
            )
            ran = run_toolset(
                toolset=CLI,
                tool="run_backlog",
                context=c,
                arguments={"stall_s": STALL_S, "max_fail": 1},
                timeout_seconds=BACKLOG_S,
            )
            expect_ok_tool(ran, "run_backlog")
            expect("done" in str(getattr(ran, "result", "") or "").lower()).to(
                be_true
            )
            rec = records(tree, session)
            expect(
                [r.get("index") for r in rec if r.get("kind") == "job_finished"]
            ).to(equal([0, 1, 2]))
            commit_all(tree, "queue artifacts")
            expect_ok_tool(
                run_toolset(
                    toolset=WS,
                    tool="finish_work_session",
                    context=c,
                    arguments={"outcome": "queue done"},
                    timeout_seconds=HOP_S,
                ),
                "finish_work_session",
            )
