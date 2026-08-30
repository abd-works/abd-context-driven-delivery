# @agent-spec-manifest python -m tools agent-spec utilities/cli_agent/cli_agent_44_one_judged_job_agent_spec.py
# Agent reading this file: run via agent BDD CLI harness (cursor-agent).
# harness: cli
# session: utilities/cli_agent/.context/.agent_bdd_sessions/run-backlog-44-one-job.json
"""#44 step 2 — one judged Echo job through run_backlog → done + PASS.

Run alone after dup is green. No finish / worktree teardown here.
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
from git.git import GitRepo

from cli_agent._agent_bdd_support import (
    BACKLOG_S,
    CLI,
    HOP_S,
    STALL_S,
    WS,
    ctx,
    echo_job,
    init_git_repo,
    records,
    worktree,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


with description("#44 one judged job"):
    with it("should run_backlog one Echo job to a single PASS"):
        with agent(_REPO_ROOT, _SESSIONS / "run-backlog-44-one-job.json"):
            primary = init_git_repo("cli44_one_")
            session = "one-job"
            expect_ok_tool(
                run_toolset(
                    toolset=WS,
                    tool="start_work_session",
                    context=ctx(primary, session),
                    arguments={"name": session, "goal": "one judged Echo job"},
                    timeout_seconds=HOP_S,
                ),
                "start_work_session",
            )
            tree = worktree(primary, session)
            expect(tree is not None).to(be_true)
            assert tree is not None
            expect(GitRepo(tree).current_branch).to(equal(f"session/{session}"))
            c = ctx(tree, session)
            expect_ok_tool(
                run_toolset(
                    toolset=CLI,
                    tool="enqueue_jobs",
                    context=c,
                    arguments={
                        "jobs": [
                            echo_job(
                                "Use the Echo fence tool with body one-job-44. "
                                "Also run the echo_session action with instructions "
                                "one-job-action. Finish the Turn. "
                                "Do not contact the judge or touch the job queue."
                            )
                        ]
                    },
                    timeout_seconds=HOP_S,
                ),
                "enqueue_jobs",
            )
            ran = run_toolset(
                toolset=CLI,
                tool="run_backlog",
                context=c,
                arguments={"stall_s": STALL_S, "max_fail": 2},
                timeout_seconds=BACKLOG_S,
            )
            expect_ok_tool(ran, "run_backlog")
            text = str(getattr(ran, "result", "") or "").lower()
            expect("done" in text).to(be_true)
            verdicts = [
                r.get("result")
                for r in records(tree, session)
                if r.get("kind") == "verdict"
            ]
            expect(verdicts).to(equal(["PASS"]))
