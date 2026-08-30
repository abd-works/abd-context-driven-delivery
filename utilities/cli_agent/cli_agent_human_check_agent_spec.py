# @agent-spec-manifest python -m tools agent-spec utilities/cli_agent/cli_agent_human_check_agent_spec.py
# Agent reading this file: run via agent BDD CLI harness (cursor-agent).
# harness: cli
# session: utilities/cli_agent/.context/.agent_bdd_sessions/human-check-53.json
"""#53 — human check gate: real run_backlog wait + file resolve (looks_good).

Starts a work session, enqueues a plain human=true job, runs run_backlog while a
background watcher writes human-check-{index}.json after human_check_needed.
Exercises the real wait/resolve path (not wait_human hook).
"""
import json
import threading
import time
from pathlib import Path

from expects import be_false, be_true, equal, expect
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
    ctx,
    init_git_repo,
    kinds,
    records,
    session_dir,
    worktree,
)

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)


def _watch_and_resolve(
    tree: Path,
    session: str,
    *,
    job_index: int = 0,
    result: str = "looks_good",
    feedback: str = "",
    timeout_s: float = 180.0,
) -> threading.Thread:
    folder = session_dir(tree, session)

    def run() -> None:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            log = folder / "cli-agent-session.jsonl"
            if log.is_file():
                text = log.read_text(encoding="utf-8", errors="replace")
                if '"kind": "human_check_needed"' in text or '"kind":"human_check_needed"' in text:
                    path = folder / f"human-check-{job_index}.json"
                    path.write_text(
                        json.dumps({"result": result, "feedback": feedback}),
                        encoding="utf-8",
                    )
                    return
            time.sleep(0.4)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread


with description("#53 human check"):
    with it("should pause for human then complete on looks_good via session file"):
        with agent(_REPO_ROOT, _SESSIONS / "human-check-53.json"):
            primary = init_git_repo("cli53_human_")
            session = "human-53"
            expect_ok_tool(
                run_toolset(
                    toolset=WS,
                    tool="start_work_session",
                    context=ctx(primary, session),
                    arguments={"name": session, "goal": "human check looks_good"},
                    timeout_seconds=HOP_S,
                ),
                "start_work_session",
            )
            tree = worktree(primary, session)
            expect(tree is not None).to(be_true)
            assert tree is not None
            c = ctx(tree, session)
            expect_ok_tool(
                run_toolset(
                    toolset=CLI,
                    tool="enqueue_jobs",
                    context=c,
                    arguments={
                        "jobs": [
                            {
                                "prompt": (
                                    "Reply exactly HUMAN-OK and finish the Turn. "
                                    "Nothing else. Do not touch the job queue."
                                ),
                                "tools": [],
                                "judge": False,
                                "human": True,
                            }
                        ]
                    },
                    timeout_seconds=HOP_S,
                ),
                "enqueue_jobs",
            )
            _watch_and_resolve(tree, session, job_index=0, result="looks_good")
            ran = run_toolset(
                toolset=CLI,
                tool="run_backlog",
                context=c,
                arguments={"stall_s": STALL_S, "max_fail": 1},
                timeout_seconds=BACKLOG_S,
            )
            expect_ok_tool(ran, "run_backlog")
            text = str(getattr(ran, "result", "") or "").lower()
            expect("done" in text).to(be_true)
            k = kinds(tree, session)
            expect("human_check_needed" in k).to(be_true)
            expect("human_check_resolved" in k).to(be_true)
            expect("judge_started" in k).to(be_false)
            resolved = [
                r.get("result")
                for r in records(tree, session)
                if r.get("kind") == "human_check_resolved"
            ]
            expect(resolved).to(equal(["looks_good"]))
            finished = [r for r in records(tree, session) if r.get("kind") == "job_finished"]
            expect(len(finished)).to(equal(1))
