# @agent-spec-manifest python -m tools agent-spec utilities/cli_agent/cli_agent_run_backlog_pickup_agent_spec.py
# Agent reading this file: run via agent BDD CLI harness (cursor-agent).
# harness: cli
# session: utilities/cli_agent/.context/.agent_bdd_sessions/run-backlog-pickup-44-life.json
# (queue/dup examples use sibling session files — never share one outer chat/log dir)
"""Agent BDD — full CliAgent lifecycle under outer-agent drive (#44).

Outer agent (AI → tools) must exercise the real use case, not a reply-only drain:

1. Single judged job with **tool + action** (Echo util): create session / branch /
   worktree, mint 1 doer + 1 judge, run doer, judge verdict, finish — worktree gone,
   no stall / spawn storm.
2. Small queue (2–3 steps): same lifecycle per step, **in order**, no stalls /
   spawn storm, then clean finish.
3. Double ``launch_next`` still refuses a second doer spawn (regression).

Each example uses its **own** agent-BDD session file (and thus its own instruct log
dir) so runs cannot overwrite each other. Under-test CliAgent worktrees are also
per-example temp clones. Run **one** agent BDD process at a time.

Assert on session artifacts (jsonl / spawn logs / git worktrees), not chat prose.
"""
import json
import re
import tempfile
from pathlib import Path

from expects import be_false, be_none, be_true, equal, expect
from mamba import context, description, it

from agent_bdd import agent
from agent_bdd.spec_helpers import (
    expect_ok_tool,
    repo_root_from,
    run_toolset,
    sessions_dir,
)
from git.git import GitRepo, Repo

_REPO_ROOT = repo_root_from(__file__, parents=2)
_SESSIONS = sessions_dir(__file__)
_CLI = "cli_agent.cli_agent:CliAgent"
_WS = "workspace.workspace:WorkSession"
_ECHO = "echo.echo:Echo"
_SPAWN_LINE = re.compile(r"^--- spawn\b", re.MULTILINE)
_HOP_S = 120
_BACKLOG_S = 900
_STALL_S = 180.0


def _init_git_repo(prefix: str) -> Path:
    primary = Path(tempfile.mkdtemp(prefix=prefix))
    Repo.git(primary, "init")
    Repo.git(primary, "config", "user.email", "e2e@abd.works")
    Repo.git(primary, "config", "user.name", "e2e")
    Repo.git(primary, "commit", "--allow-empty", "-m", "init")
    Repo.git(primary, "branch", "-M", "main")
    return primary


def _worktree(primary: Path, session: str) -> Path | None:
    found = GitRepo(primary).worktree_for(f"session/{session}")
    return Path(found.path) if found is not None else None


def _session_dir(workspace: Path, session: str) -> Path:
    return workspace / ".context" / "sessions" / session


def _records(workspace: Path, session: str) -> list[dict]:
    path = _session_dir(workspace, session) / "cli-agent-session.jsonl"
    if not path.is_file():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _kinds(workspace: Path, session: str) -> list[str]:
    return [str(r.get("kind") or "") for r in _records(workspace, session)]


def _spawn_count(workspace: Path, session: str, *, role: str = "doer") -> int:
    name = "cli-agent-doer.log" if role == "doer" else "cli-agent-judge.log"
    log = _session_dir(workspace, session) / name
    if not log.is_file():
        return 0
    return len(_SPAWN_LINE.findall(log.read_text(encoding="utf-8", errors="replace")))


def _cli_ids(workspace: Path, session: str) -> tuple[str, str]:
    from workspace.workspace import WorkSession

    work = WorkSession(workspace=str(workspace), session=session)
    work.load_cli_sessions()
    return str(work.cli_doer or ""), str(work.cli_judge or "")


def _commit_all(tree: Path, message: str) -> None:
    if not tree.is_dir():
        return
    Repo.git(tree, "add", "-A")
    status = Repo.git(tree, "status", "--porcelain")
    if status.strip():
        Repo.git(tree, "commit", "-m", message)


def _ctx(workspace: Path, session: str) -> dict:
    return {
        "workspace": str(workspace).replace("\\", "/"),
        "session": session,
    }


def _echo_job(prompt: str, *, with_action: bool = True) -> dict:
    job = {
        "prompt": prompt,
        "tools": [_ECHO],
        "judge": True,
        "judge_criteria": (
            "PASS when the doer used Echo (fence and/or echo_session) and finished "
            "the Turn. FAIL only if the doer contacted the judge or edited the queue."
        ),
    }
    if with_action:
        job["actions"] = [_ECHO]
    return job


with description("CliAgent full lifecycle under agent BDD (#44)"):
    with context("when an outer agent runs one judged job with tool + action"):
        with it(
            "should open session/worktree/branch, run doer+judge, verdict, and finish clean"
        ):
            with agent(_REPO_ROOT, _SESSIONS / "run-backlog-pickup-44-life.json"):
                primary = _init_git_repo("cli44_life_")
                session = "life-single"
                primary_ctx = _ctx(primary, session)

                started = run_toolset(
                    toolset=_WS,
                    tool="start_work_session",
                    context=primary_ctx,
                    arguments={
                        "name": session,
                        "goal": "single judged Echo tool+action lifecycle",
                    },
                    timeout_seconds=_HOP_S,
                )
                expect_ok_tool(started, "start_work_session")
                tree = _worktree(primary, session)
                expect(tree is not None).to(be_true)
                assert tree is not None
                expect(GitRepo(tree).current_branch).to(equal(f"session/{session}"))

                ctx = _ctx(tree, session)
                expect_ok_tool(
                    run_toolset(
                        toolset=_CLI,
                        tool="enqueue_jobs",
                        context=ctx,
                        arguments={
                            "jobs": [
                                _echo_job(
                                    "Use the Echo fence tool with body life-single-44. "
                                    "Also run the echo_session action with instructions "
                                    "life-single-action. Finish the Turn. "
                                    "Do not contact the judge or touch the job queue."
                                )
                            ]
                        },
                        timeout_seconds=_HOP_S,
                    ),
                    "enqueue_jobs",
                )
                ran = run_toolset(
                    toolset=_CLI,
                    tool="run_backlog",
                    context=ctx,
                    arguments={"stall_s": _STALL_S, "max_fail": 2},
                    timeout_seconds=_BACKLOG_S,
                )
                expect_ok_tool(ran, "run_backlog")
                result_text = str(getattr(ran, "result", "") or "")
                expect("done" in result_text.lower()).to(be_true)

                kinds = _kinds(tree, session)
                for needed in (
                    "orchestrator_started",
                    "job_started",
                    "spawn",
                    "doer_finished",
                    "judge_started",
                    "verdict",
                    "job_finished",
                    "orchestrator_stopped",
                ):
                    expect(needed in kinds).to(be_true)

                doer_id, judge_id = _cli_ids(tree, session)
                expect(bool(doer_id)).to(be_true)
                expect(bool(judge_id)).to(be_true)
                expect(doer_id == judge_id).to(be_false)
                expect(_spawn_count(tree, session, role="doer") <= 2).to(be_true)
                expect(_spawn_count(tree, session, role="judge") <= 2).to(be_true)
                expect(_spawn_count(tree, session, role="doer") >= 1).to(be_true)
                expect(_spawn_count(tree, session, role="judge") >= 1).to(be_true)

                verdicts = [
                    r.get("result")
                    for r in _records(tree, session)
                    if r.get("kind") == "verdict"
                ]
                expect(verdicts).to(equal(["PASS"]))

                _commit_all(tree, "e2e lifecycle artifacts")
                finished = run_toolset(
                    toolset=_WS,
                    tool="finish_work_session",
                    context=ctx,
                    arguments={"outcome": "lifecycle e2e done"},
                    timeout_seconds=_HOP_S,
                )
                expect_ok_tool(finished, "finish_work_session")
                expect(tree.exists()).to(be_false)
                expect(_worktree(primary, session)).to(be_none)

    with context("when an outer agent runs a 2–3 step judged queue"):
        with it(
            "should run steps in order with doer+judge, without stall or spawn storm"
        ):
            with agent(_REPO_ROOT, _SESSIONS / "run-backlog-pickup-44-queue.json"):
                primary = _init_git_repo("cli44_queue_")
                session = "life-queue"
                primary_ctx = _ctx(primary, session)

                expect_ok_tool(
                    run_toolset(
                        toolset=_WS,
                        tool="start_work_session",
                        context=primary_ctx,
                        arguments={
                            "name": session,
                            "goal": "ordered multi-step CliAgent queue",
                        },
                        timeout_seconds=_HOP_S,
                    ),
                    "start_work_session",
                )
                tree = _worktree(primary, session)
                expect(tree is not None).to(be_true)
                assert tree is not None
                ctx = _ctx(tree, session)

                jobs = [
                    _echo_job(
                        "Step ONE: Echo fence body queue-one-44 and echo_session "
                        "instructions queue-one-action. Finish the Turn. "
                        "Do not contact the judge or touch the job queue."
                    ),
                    _echo_job(
                        "Step TWO: Echo fence body queue-two-44 only (tool). "
                        "Finish the Turn. Do not contact the judge or touch the queue.",
                        with_action=False,
                    ),
                    {
                        "prompt": (
                            "Step THREE: Reply with exactly THREE and finish the Turn. "
                            "Do not contact the judge or touch the job queue."
                        ),
                        "tools": [],
                        "judge": False,
                    },
                ]
                expect_ok_tool(
                    run_toolset(
                        toolset=_CLI,
                        tool="enqueue_jobs",
                        context=ctx,
                        arguments={"jobs": jobs},
                        timeout_seconds=_HOP_S,
                    ),
                    "enqueue_jobs",
                )
                ran = run_toolset(
                    toolset=_CLI,
                    tool="run_backlog",
                    context=ctx,
                    arguments={"stall_s": _STALL_S, "max_fail": 2},
                    timeout_seconds=_BACKLOG_S,
                )
                expect_ok_tool(ran, "run_backlog")
                text = str(getattr(ran, "result", "") or "").lower()
                expect("done" in text).to(be_true)

                records = _records(tree, session)
                kinds = [str(r.get("kind") or "") for r in records]
                expect("orchestrator_started" in kinds).to(be_true)
                expect("orchestrator_stopped" in kinds).to(be_true)

                started_idx = [
                    r.get("index")
                    for r in records
                    if r.get("kind") == "job_started"
                ]
                finished_idx = [
                    r.get("index")
                    for r in records
                    if r.get("kind") == "job_finished"
                ]
                expect(started_idx).to(equal([0, 1, 2]))
                expect(finished_idx).to(equal([0, 1, 2]))

                verdicts = [
                    r.get("result")
                    for r in records
                    if r.get("kind") == "verdict"
                ]
                expect(len(verdicts)).to(equal(2))
                expect(all(v == "PASS" for v in verdicts)).to(be_true)

                doer_id, judge_id = _cli_ids(tree, session)
                expect(bool(doer_id)).to(be_true)
                expect(bool(judge_id)).to(be_true)
                # One durable doer chat + one judge chat; resumes may re-spawn argv.
                expect(_spawn_count(tree, session, role="doer") <= 4).to(be_true)
                expect(_spawn_count(tree, session, role="judge") <= 3).to(be_true)
                expect(_spawn_count(tree, session, role="doer") >= 1).to(be_true)
                expect(_spawn_count(tree, session, role="judge") >= 1).to(be_true)

                _commit_all(tree, "e2e queue artifacts")
                expect_ok_tool(
                    run_toolset(
                        toolset=_WS,
                        tool="finish_work_session",
                        context=ctx,
                        arguments={"outcome": "queue e2e done"},
                        timeout_seconds=_HOP_S,
                    ),
                    "finish_work_session",
                )
                expect(tree.exists()).to(be_false)
                expect(_worktree(primary, session)).to(be_none)

    with context("when an outer agent double-launches the same head job"):
        with it("should spawn the doer CLI only once (ground-truth log)"):
            with agent(_REPO_ROOT, _SESSIONS / "run-backlog-pickup-44-dup.json"):
                workspace = Path(tempfile.mkdtemp(prefix="cli44_dup_"))
                session = "dup-44"
                ctx = _ctx(workspace, session)
                expect_ok_tool(
                    run_toolset(
                        toolset=_CLI,
                        tool="enqueue_jobs",
                        context=ctx,
                        arguments={
                            "jobs": [
                                {
                                    "prompt": "Reply WAITING and keep this Turn open.",
                                    "tools": [],
                                    "judge": False,
                                }
                            ]
                        },
                        timeout_seconds=_HOP_S,
                    ),
                    "enqueue_jobs",
                )
                expect_ok_tool(
                    run_toolset(
                        toolset=_CLI,
                        tool="launch_next",
                        context=ctx,
                        timeout_seconds=_HOP_S,
                    ),
                    "launch_next",
                )
                expect(_spawn_count(workspace, session)).to(equal(1))
                expect_ok_tool(
                    run_toolset(
                        toolset=_CLI,
                        tool="launch_next",
                        context=ctx,
                        timeout_seconds=_HOP_S,
                    ),
                    "launch_next",
                )
                expect(_spawn_count(workspace, session)).to(equal(1))
                expect(_kinds(workspace, session).count("spawn")).to(equal(1))
