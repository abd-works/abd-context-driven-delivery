"""BDD spec for agents/agent/agent.py — Agent backlog orchestration.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_agents = str(_REPO_ROOT / "agents")
for _cat in ("utilities", "primitives", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
if _agents not in sys.path:
    sys.path.insert(0, _agents)

from expects import be_false, be_true, contain, equal, expect, raise_error
from mamba import before, context, description, it

import json
import os
import subprocess
import threading
import time
import uuid
from typing import Optional

from agent.agent import (
    Agent,
    AgentFault,
    AgentParticipant,
    AgentSession,
    AgentTask,
    AgentTaskTemplate,
    AIChatFault,
    AIChatInstance,
    AgentRuntimeTranscriptWatcher,
    ChatAgent,
    ChatAgentKit,
    CliAgent,
    CliAgentParticipant,
    CursorChatInstance,
    InMemoryRepo,
    MultiRepoSessionError,
    Project,
    Repo,
    SubAgent,
    ToolCall,
    _AssistantText,
    _JsonlTranscript,
    _SubAgentMailbox,
    _TranscriptPath,
    Workspace,
    _ChatAgentPersistence,
)
from agent.sub_agent_kit import SubAgentKit
from agent.tools_cli import assert_tools_response, ToolsCliRunner
from agent.healer import Healer, HealerFailure, HealerRunContext, format_healer_fix_handoff
from agent.workflow import WorkTicket, Workflow, WorkflowConfig
from primitives.tools.repo_paths import repo_python, repo_root


def _bare_session(name: str = "agent-spec") -> AgentSession:
    folder = Path(tempfile.mkdtemp()) / ".agent_sessions" / name
    return AgentSession(name=name, folder=folder, context_root=folder.parent)


def _doer_task(prompt: str = "/echo fence hello") -> AgentTask:
    doer = AgentParticipant(type="doer", prompt=prompt)
    return AgentTask(prompt=prompt, doer=doer)


def _judged_task(
    prompt: str = "/echo fence hello",
    judge_prompt: str = "/validate",
) -> AgentTask:
    doer = AgentParticipant(type="doer", prompt=prompt)
    judge = AgentParticipant(type="judge", prompt=judge_prompt)
    return AgentTask(prompt=prompt, doer=doer, judge=judge)


def _log_kinds(log_or_session) -> list[str]:
    log = log_or_session.log if hasattr(log_or_session, "log") else log_or_session
    return [record["kind"] for record in log._records]


def _verdict_results(log_or_session) -> list[str]:
    log = log_or_session.log if hasattr(log_or_session, "log") else log_or_session
    results: list[str] = []
    for record in log._records:
        if record["kind"] != "verdict":
            continue
        results.append(record["result"])
    return results


def _verdicts(session) -> list[str]:
    return _verdict_results(session)


def _script_verdicts(agent, items: list[str]) -> None:
    remaining = list(items)

    def _await_verdict(participant) -> str:
        participant.state = "awaiting_verdict"
        result = remaining.pop(0) if remaining else "PASS"
        participant.state = "done"
        return result

    agent._await_verdict = _await_verdict


def _script_human_feedback(agent, items: list[str]) -> None:
    remaining = list(items)

    def _next_human_feedback() -> str:
        return remaining.pop(0) if remaining else ""

    agent._next_human_feedback = _next_human_feedback


def _raise_on_next_cycle(agent, kind: str) -> None:
    real = agent._run_current_task_cycle

    def _once() -> None:
        agent._run_current_task_cycle = real
        agent._raise(AgentFault(kind=kind, detail=kind))

    agent._run_current_task_cycle = _once


def _open_workspace_session(
    name: str = "sub-agent",
    *,
    prefix: str = "sub_agent_",
) -> AgentSession:
    root = Path(tempfile.mkdtemp(prefix=prefix))
    repo = InMemoryRepo(root, Repo.Worktree(root, "main"))
    workspace = Workspace(path=root, repos=[repo], primary_repo=repo)
    return workspace.open(name=name, context_root=root)


def _judged_echo_task() -> AgentTask:
    prompt = (
        "/echo fence one-judged-job-55. Finish the Turn. "
        "Do not contact the judge or drain a backlog."
    )
    return _judged_task(
        prompt=prompt,
        judge_prompt=(
            "/validate. PASS when the doer used Echo and finished the Turn. "
            "FAIL only if the doer contacted the judge or edited the queue."
        ),
    )


def _cli_judged_echo_task() -> AgentTask:
    return _judged_task(
        prompt="/echo fence cli-echo-job-55",
        judge_prompt="PASS when echo fence was used.",
    )


def _sub_queue_judged_task(label: str) -> AgentTask:
    prompt = (
        f"/echo fence sub-queue-{label}-55. Finish the Turn. "
        "Do not contact the judge or drain a backlog."
    )
    return _judged_task(
        prompt=prompt,
        judge_prompt=(
            "/validate. PASS when the doer used Echo and finished the Turn "
            "for this queue item. FAIL only if the doer skipped echo or edited the queue."
        ),
    )


def _workflow_fixture():
    parent = Path(tempfile.mkdtemp(prefix="start_fin55_"))
    root = parent / "abd-context-driven-delivery"
    root.mkdir()
    repo = InMemoryRepo(root, Repo.Worktree(root, "main"))
    repo._issue_shelf.attach_project(Project())
    workspace = Workspace(path=root, repos=[repo], primary_repo=repo)
    workflow = Workflow(
        workspace=workspace,
        repo=repo,
        config=WorkflowConfig(),
    )
    return root, repo, workflow


with description("Complete Agent Task"):
    with context("with an Agent bound to an open AgentSession"):
        with before.each:
            self.session = _bare_session("inc1")
            self.agent = SubAgent(session=self.session)

        with context("with a current task"):
            with before.each:
                self.task = _doer_task()
                self.agent.add_tasks([self.task])

            with context("with a doer prompt"):
                with it("should run the doer prompt on the doer agent runtime"):
                    self.agent.run_next_task()
                    expect(self.task.doer.state).to(equal("done"))

                with it("should append session log lines with kind send"):
                    self.agent.run_next_task()
                    expect(_log_kinds(self.session.log)).to(contain("send"))

                with it("should append session log lines with kind accepted"):
                    self.agent.run_next_task()
                    expect(_log_kinds(self.session.log)).to(contain("accepted"))

                with it("should append session log lines with kind done"):
                    self.agent.run_next_task()
                    expect(_log_kinds(self.session.log)).to(contain("done"))

                with it("should mark the task Done when no judge is configured"):
                    self.agent.run_next_task()
                    expect(self.task.state).to(equal("Done"))
                    expect(self.agent.completed_tasks).to(contain(self.task))
                    expect(self.agent.current_task).to(equal(None))

                with it("should record complete_task on the session log"):
                    self.agent.run_next_task()
                    expect(_log_kinds(self.session.log)).to(contain("complete_task"))

                with it("should record launch_next before send"):
                    self.agent.run_next_task()
                    kinds = _log_kinds(self.session.log)
                    launch_idx = kinds.index("launch_next")
                    send_idx = kinds.index("send")
                    expect(launch_idx < send_idx).to(be_true)


with description("Complete Agent Task With Judge and Human"):
    with context("with an Agent bound to an open AgentSession"):
        with before.each:
            self.session = _bare_session("inc2")
            self.agent = SubAgent(session=self.session)

        with context("with a current task"):
            with context("with a judge prompt"):
                with before.each:
                    self.task = _judged_task()
                    self.agent.add_tasks([self.task])

                with it("should run the judge prompt on the judge agent runtime"):
                    self.agent.run_next_task()
                    expect(self.task.judge.state).to(equal("done"))

                with it("should work within the same session as the doer"):
                    self.agent.run_next_task()
                    expect(self.agent.session).to(equal(self.session))

                with it("should write session log lines under session.folder"):
                    self.agent.run_next_task()
                    expect(str(self.session.log.path)).to(
                        contain(str(self.session.folder))
                    )

                with context("with default validation instructions"):
                    with it("should record the verdict on the session log"):
                        self.agent.run_next_task()
                        expect(_log_kinds(self.session.log)).to(contain("verdict"))
                        expect(_verdict_results(self.session.log)).to(contain("PASS"))

                with context("with a passing verdict"):
                    with it("should mark the agent task as complete"):
                        self.agent.run_next_task()
                        expect(self.task.state).to(equal("Done"))
                        expect(self.agent.completed_tasks).to(contain(self.task))

                    with it("should record that the task completed on the session log"):
                        self.agent.run_next_task()
                        expect(_log_kinds(self.session.log)).to(contain("complete_task"))

                with context("with a failing verdict"):
                    with before.each:
                        self.agent.max_fails = 1
                        self.agent._healer_tried = True
                        _script_verdicts(self.agent, ["FAIL"])

                    with it("should skip the task after one try"):
                        self.agent.run_next_task()
                        expect(self.task.state).to(equal("Done"))
                        expect(_log_kinds(self.session.log)).not_to(contain("kick"))
                        outcomes = [
                            record["outcome"]
                            for record in self.session.log._records
                            if record["kind"] == "complete_task"
                        ]
                        expect(outcomes).to(contain("skip"))

                    with it("should not rerun the doer"):
                        self.agent.run_next_task()
                        send_doer = [
                            record
                            for record in self.session.log._records
                            if record["kind"] == "send"
                            and record["participant"] == "doer"
                        ]
                        expect(len(send_doer)).to(equal(1))
                        expect(_verdict_results(self.session.log)).to(equal(["FAIL"]))

            with context("with no judge prompt"):
                with before.each:
                    self.task = AgentTask(
                        prompt="/echo fence",
                        doer=AgentParticipant(type="doer", prompt="/echo fence"),
                    )
                    self.agent.add_tasks([self.task])

                with it("should automatically pass once the doer is done"):
                    self.agent.run_next_task()
                    expect(self.task.state).to(equal("Done"))
                    expect(_log_kinds(self.session.log)).not_to(contain("verdict"))

            with context("with a Human participant"):
                with before.each:
                    self.task = _judged_task()
                    self.task.human = AgentParticipant(
                        type="human", prompt="review please"
                    )
                    self.agent.add_tasks([self.task])

                with it("should wait for the human to finish"):
                    self.agent.run_next_task()
                    expect(self.task.human.state).to(equal("done"))
                    expect(self.task.state).to(equal("Done"))

                with context("with human feedback"):
                    with before.each:
                        _script_human_feedback(self.agent, ["please fix"])

                    with it("should record the feedback on the session log"):
                        self.agent.run_next_task()
                        expect(_log_kinds(self.session.log)).to(
                            contain("human_feedback")
                        )

                    with it("should kick the doer agent or tell it to retry"):
                        self.agent.run_next_task()
                        expect(_log_kinds(self.session.log)).to(contain("kick"))
                        expect(self.task.state).to(equal("Done"))

                with context("with a validation error from the judge"):
                    with before.each:
                        _raise_on_next_cycle(self.agent, "validation_error")

                    with it("should record the validation error on the session log"):
                        self.agent.run_next_task()
                        expect(_log_kinds(self.session.log)).to(
                            contain("validation_error")
                        )

            with context("with a workflow fault on the current task"):
                with before.each:
                    self.task = _doer_task()
                    self.agent.add_tasks([self.task])
                    _raise_on_next_cycle(self.agent, "invariant")

                with it("should stop and raise an invariant fault"):
                    expect(self.agent.run_next_task).to(raise_error(AgentFault))

            with context("that is being rerun after human feedback"):
                with before.each:
                    self.task = _judged_task()
                    self.task.human = AgentParticipant(
                        type="human", prompt="review please"
                    )
                    self.agent.add_tasks([self.task])
                    _script_human_feedback(self.agent, ["please fix"])

                with it("should mint a new turn id on retry"):
                    self.agent.run_next_task()
                    turn_ids = [turn.name for turn in self.session.turns]
                    expect(len(turn_ids) >= 2).to(be_true)
                    expect(len(set(turn_ids)) >= 2).to(be_true)


def _workspace_fixture(prefix: str = "ws_"):
    root = Path(tempfile.mkdtemp(prefix=prefix))
    repo = InMemoryRepo(root, Repo.Worktree(root, "main"))
    workspace = Workspace(path=root, repos=[repo], primary_repo=repo)
    return root, repo, workspace


with description("Add Agent Tasks To Backlog"):
    with context("with an Agent that has an open session"):
        with before.each:
            self.session = _bare_session("add-tasks")
            self.agent = SubAgent(session=self.session)

        with context("with one or more AgentTasks"):
            with it("should append AgentTasks with state Backlog"):
                tasks = [_doer_task("/echo a"), _doer_task("/echo b")]
                self.agent.add_tasks(tasks)
                expect(self.agent.backlog).to(equal(tasks))
                expect(all(task.state == "Backlog" for task in tasks)).to(be_true)

            with it("should log add_tasks"):
                tasks = [_doer_task("/echo a")]
                self.agent.add_tasks(tasks)
                expect(_log_kinds(self.session.log)).to(contain("add_tasks"))

        with it("should clear the backlog without touching completed tasks"):
            done = _doer_task("/echo done")
            self.agent.completed_tasks = [done]
            self.agent.add_tasks([_doer_task("/echo queued")])
            self.agent.clear_backlog()
            expect(self.agent.backlog).to(equal([]))
            expect(self.agent.completed_tasks).to(equal([done]))
            expect(_log_kinds(self.session.log)).to(contain("clear_backlog"))


with description("Load Agent Tasks From Template"):
    with context("with an Agent that has an open session"):
        with before.each:
            self.session = _bare_session("load-template")
            self.agent = SubAgent(session=self.session)
            self.agent.template_store.add(
                AgentTaskTemplate(
                    name="two-step",
                    tasks=["/echo one", "/echo two"],
                    description="pair",
                )
            )

        with context("with a template name provided to the agent"):
            with it("should load the template from the template store"):
                self.agent.load_task_backlog_template("two-step")
                expect(len(self.agent.backlog)).to(equal(2))

            with it("should create an agent task for each task in the template"):
                self.agent.load_task_backlog_template("two-step")
                expect(self.agent.backlog[0].prompt).to(equal("/echo one"))
                expect(self.agent.backlog[1].prompt).to(equal("/echo two"))

            with it("should add those agent tasks to the agent backlog with state Backlog"):
                self.agent.load_task_backlog_template("two-step")
                expect(all(task.state == "Backlog" for task in self.agent.backlog)).to(
                    be_true
                )

            with it("should log add_tasks"):
                self.agent.load_task_backlog_template("two-step")
                expect(_log_kinds(self.session.log)).to(contain("add_tasks"))

            with it("should raise when the template name is unknown"):
                expect(lambda: self.agent.load_task_backlog_template("missing")).to(
                    raise_error(KeyError)
                )


with description("Launch Next Task As Current"):
    with context("with an Agent that has an open session"):
        with before.each:
            self.session = _bare_session("launch-next")
            self.agent = SubAgent(session=self.session)

        with context("with no participant still in flight on the current task"):
            with before.each:
                self.task = _doer_task("/echo launch")
                self.agent.add_tasks([self.task])

            with it("should take the next agent task from the backlog and make it current"):
                self.agent._launch_next()
                expect(self.agent.current_task).to(equal(self.task))
                expect(self.agent.backlog).to(equal([]))

            with it("should mark that task In Progress"):
                self.agent._launch_next()
                expect(self.task.state).to(equal("In Progress"))

            with it("should record launch_next on the session log before send"):
                self.agent.run_next_task()
                kinds = _log_kinds(self.session.log)
                expect(kinds.index("launch_next") < kinds.index("send")).to(be_true)

        with context("with a doer still in flight on the current task"):
            with it("should refuse to take another task from the backlog"):
                self.agent.current_task = _doer_task("/echo running")
                self.agent.current_task.doer.state = "running"
                self.agent.add_tasks([_doer_task("/echo queued")])
                expect(lambda: self.agent._launch_next()).to(raise_error(RuntimeError))

        with context("with a judge still in flight"):
            with it("should refuse to take another task from the backlog"):
                self.task = _judged_task()
                self.agent.current_task = self.task
                self.task.judge.state = "running"
                self.agent.add_tasks([_doer_task("/echo queued")])
                expect(lambda: self.agent._launch_next()).to(raise_error(RuntimeError))

        with context("with a human still in flight"):
            with it("should refuse to take another task from the backlog"):
                self.task = _judged_task()
                self.task.human = AgentParticipant(type="human", prompt="review")
                self.agent.current_task = self.task
                self.task.human.state = "running"
                self.agent.add_tasks([_doer_task("/echo queued")])
                expect(lambda: self.agent._launch_next()).to(raise_error(RuntimeError))


with description("Open Default Agent Session"):
    with context("with a Workspace that has a primary Repo"):
        with before.each:
            self.root, self.repo, self.workspace = _workspace_fixture("open_def_")

        with context("with no AgentSession name given"):
            with it("should create session.folder at repo root agent_sessions default"):
                session = self.workspace.open()
                expected = self.root / ".agent_sessions" / "default"
                expect(session.folder).to(equal(expected))

            with it("should include that session in Repo.agent_sessions"):
                session = self.workspace.open()
                expect(self.repo.agent_sessions).to(contain(session))

            with it("should record session.log line with kind open"):
                session = self.workspace.open()
                expect(_log_kinds(session.log)).to(contain("open"))

            with it("should correlate AgentSession.branch to that Branch"):
                session = self.workspace.open(name="branch-bind")
                expect(session.branch).not_to(equal(None))
                expect(session.branch.agent_session).to(equal(session))

        with context("with an explicit contextRoot override"):
            with it("should set contextRoot to that resolved path"):
                docs = self.root / "docs"
                docs.mkdir()
                self.workspace.upsert_path("agent", "contextRoot", docs)
                session = self.workspace.open(name="ctx-override")
                expect(session.context_root).to(equal(docs))

        with context("with no explicit path override"):
            with it("should resolve contextRoot from workspace defaults"):
                session = self.workspace.open(name="default-root")
                expect(session.context_root).to(equal(self.root))


with description("Open New Agent Session"):
    with context("with a Workspace that has a primary Repo"):
        with before.each:
            self.root, self.repo, self.workspace = _workspace_fixture("open_new_")

        with it("should place session.folder at repo agent_sessions name"):
            session = self.workspace.open(name="feature-a")
            expect(session.folder).to(equal(self.root / ".agent_sessions" / "feature-a"))

        with it("should resolve contextRoot independently of session.folder"):
            docs = self.root / "docs"
            docs.mkdir()
            session = self.workspace.open(name="feature-b", context_root=docs)
            expect(session.context_root).to(equal(docs))
            expect(session.folder).not_to(equal(docs))

        with it("should check out or create the branch worktree and attach it to the session"):
            session = self.workspace.open(name="feature-c")
            expect(session.branch).not_to(equal(None))
            expect(session.worktree).not_to(equal(None))
            expect(session.branch.name).to(equal("session/feature-c"))

        with it("should link the branch to that session"):
            session = self.workspace.open(name="feature-link")
            expect(session.branch).not_to(equal(None))
            expect(session.branch.agent_session).to(equal(session))

        with it("should append a session log line with kind open name and branch"):
            session = self.workspace.open(name="feature-d")
            open_rows = [r for r in session.log._records if r["kind"] == "open"]
            expect(len(open_rows)).to(equal(1))
            expect(open_rows[0]["name"]).to(equal("feature-d"))
            expect("branch" in open_rows[0]).to(be_true)


with description("Open Existing Agent Session"):
    with context("with a Workspace that has a primary Repo"):
        with before.each:
            self.root, self.repo, self.workspace = _workspace_fixture("open_exist_")

        with context("with session data on disk"):
            with before.each:
                self.first = self.workspace.open(name="resume-me", context_root=self.root / "ctx")
                self.first.goal = "remember this"
                self.first.close()
                self.folder = self.first.folder

            with it("should restore contextRoot from what the session recorded"):
                session = AgentSession(
                    name="resume-me",
                    folder=self.folder,
                    context_root=self.root / "ctx",
                    repo=self.repo,
                )
                session.open_existing()
                expect(str(session.context_root)).to(contain("ctx"))

            with it("should record session.log line with kind open on resume"):
                session = AgentSession(
                    name="resume-me",
                    folder=self.folder,
                    context_root=self.root / "ctx",
                    repo=self.repo,
                )
                session.open_existing()
                expect(_log_kinds(session.log)).to(contain("open"))

            with it("should bind AgentSession.branch.worktree to that path"):
                session = AgentSession(
                    name="resume-me",
                    folder=self.folder,
                    context_root=self.root / "ctx",
                    repo=self.repo,
                )
                session.open_existing()
                expect(session.worktree).not_to(equal(None))
                expect(session.worktree.path).to(equal(session.branch.worktree.path))

        with context("with no session data on disk yet"):
            with it("should recreate session.folder scaffolding under the same name"):
                session = self.workspace.open(name="fresh-name", open_existing=True)
                expect(session.folder.is_dir()).to(be_true)
                expect(_log_kinds(session.log)).to(contain("open"))


with description("Close Agent Session"):
    with context("with someone closing the agent session"):
        with before.each:
            self.session = _bare_session("close-agent")
            self.session.open()
            self.agent = SubAgent(session=self.session)
            self.session.agent = self.agent

        with it("should stop live participants without finishing the session folder"):
            task = _doer_task()
            self.agent.add_tasks([task])
            self.agent.current_task = task
            task.doer.state = "running"
            folder_before = self.session.folder
            self.session.close()
            expect(self.session.folder).to(equal(folder_before))
            expect(folder_before.is_dir()).to(be_true)

        with it("should append a session log line with kind close"):
            self.session.close()
            expect(_log_kinds(self.session.log)).to(contain("close"))

        with it("should clear the live agent link from the session"):
            self.session.close()
            expect(self.session.agent is self.agent).to(be_false)

        with it("should not attach or persist chats on close"):
            self.session.close()
            branch = self.session.branch
            if branch is not None:
                expect(branch.chats).to(equal([]))
            else:
                expect(branch).to(equal(None))


with description("AgentSession CDD seam"):
    with context("with a bare AgentSession"):
        with before.each:
            self.session = _bare_session("cdd-seam")
            self.session.open()

        with it("should expose path as context_root"):
            expect(self.session.path).to(equal(self.session.context_root))

        with it("should compose RecordDecisions on decisions"):
            from record_decisions.record_decisions import RecordDecisions

            expect(isinstance(self.session.decisions, RecordDecisions)).to(be_true)

        with it("should hang turn on open_turn"):
            turn = self.session.turn
            expect(self.session.open_turn).to(equal(turn))
            expect(turn.hanging).to(be_true)
            expect(_log_kinds(self.session.log)).to(contain("open_turn"))

        with it("should resolve eval_log_dir under folder/logs"):
            expect(self.session.eval_log_dir).to(equal(self.session.folder / "logs"))

    with context("with a hanging turn"):
        with before.each:
            self.session = _bare_session("finish-turn-alias")
            self.turn = self.session.mint_turn(action="/echo test")

        with it("should finish via finish_turn alias"):
            self.turn.finish_turn(subject="done")
            expect(self.turn.hanging).to(be_false)
            expect(self.session.open_turn).to(equal(None))
            expect(_log_kinds(self.session.log)).to(contain("finish_turn"))


with description("Healer eval orchestration"):
    with before.each:
        self.healer = Healer()

    with it("should keep eval guidance self-contained in the prompt"):
        report = self.healer.eval([], phase="manual", trigger="manual")
        expect(report.healer_prompt).to(contain("You are the Healer"))
        expect(report.healer_prompt).to(contain("Improve doer_prompt"))
        expect("one-judged-job.md" in report.healer_prompt).to(equal(False))
        expect("README" in report.healer_prompt).to(equal(False))

    with it("should forward exceptions as mistakes and recommend fix"):
        report = self.healer.eval(
            ["open"],
            phase="run_doer",
            trigger="exception",
            error=RuntimeError("tools run failed"),
        )
        expect(report.mistakes[0]).to(contain("RuntimeError"))
        expect(report.fix_recommended).to(be_true)
        expect(report.stop_recommended).to(equal(False))
        expect(report.summary()).to(contain("error:"))

    with it("should format healer fix handoff with fix permission"):
        from agent.healer import format_healer_fix_handoff

        report = self.healer.eval(
            [],
            phase="run_judge",
            trigger="exception",
            error=RuntimeError("no current task"),
        )
        handoff = format_healer_fix_handoff(report)
        expect(handoff).to(contain("healer_fix:"))
        expect(handoff).to(contain("improve the prompts"))
        expect(handoff).to(contain("run_judge"))

    with it("should say no heal needed on success with only pass verdicts"):
        report = self.healer.eval(
            ["verdict"],
            phase="task_complete",
            trigger="success",
            log_records=[{"kind": "verdict", "result": "PASS"}],
            last_phase_result="PASS. Task complete.",
        )
        expect(report.healer_prompt).to(contain("no heal needed"))
        expect(report.summary()).to(contain("no problem"))

    with it("should recommend prompt improvement when judge fail retries to pass"):
        records = [
            {"kind": "verdict", "result": "FAIL"},
            {"kind": "kick", "participant": "doer"},
            {"kind": "send", "participant": "doer"},
            {"kind": "verdict", "result": "PASS"},
            {"kind": "complete_task", "outcome": "PASS"},
        ]
        context = HealerRunContext(
            current_task={
                "doer_prompt": "Compute 18 / 3. Reply with the number only.",
                "judge_prompt": "PASS only if the answer is 6.",
            }
        )
        report = self.healer.eval(
            [row["kind"] for row in records],
            phase="task_complete",
            trigger="success",
            log_records=records,
            run_context=context,
            last_phase_result="PASS. Task complete.",
        )
        expect(report.healer_prompt).to(contain("improve doer_prompt"))
        expect(report.healer_prompt).to(contain("Compute 18 / 3"))

    with it("should foreground forwarded exceptions in the problem section"):
        report = self.healer.eval(
            ["open"],
            phase="run_doer",
            trigger="exception",
            error=RuntimeError("tools run failed"),
        )
        expect(report.healer_prompt).to(contain("Exception"))
        expect(report.healer_prompt).to(contain("tools run failed"))

    with it("should record fixes and mistakes from later eval calls"):
        self.healer.record_fixes(["added repo_paths_spec subprocess test"])
        self.healer.record_mistakes(["wrong venv python under mamba"])
        report = self.healer.eval([], phase="manual", trigger="manual")
        expect(len(report.fixes)).to(equal(1))
        expect(len(report.mistakes)).to(equal(1))

    with it("should embed run metadata and log records in the eval prompt"):
        from agent.healer import HealerRunContext

        records = [
            {"kind": "send", "participant": "doer", "prompt": "/echo fence test"},
            {"kind": "verdict", "result": "PASS"},
        ]
        context = HealerRunContext(
            agent_type="ChatAgent",
            session_name="chat55-one",
            log_path="/tmp/agent-session.jsonl",
            backlog_prompts=["/echo fence test"],
        )
        report = self.healer.eval(
            ["send", "verdict"],
            phase="run_judge",
            trigger="success",
            log_records=records,
            run_context=context,
            last_phase_result="verdict: PASS",
        )
        expect(report.healer_prompt).to(contain("ChatAgent"))
        expect(report.healer_prompt).to(contain("chat55-one"))
        expect(report.healer_prompt).to(contain("verdict: PASS"))
        expect(report.healer_prompt).to(contain("/echo fence test"))
        expect(report.healer_prompt).to(contain('"result": "PASS"'))

    with it("should eval on exception even when the agent has no session"):
        from agent.agent import SubAgent

        agent = SubAgent()
        agent.healer = Healer()
        report = agent._healer_eval(
            phase="run_doer",
            trigger="exception",
            error=RuntimeError("need session name"),
        )
        expect(report is not None).to(be_true)
        expect(report.error).to(contain("need session name"))
        expect(report.fix_recommended).to(be_true)

    with it("should hard stop when the agent has no healer"):
        from agent.agent import SubAgent

        agent = SubAgent()
        agent.healer = None
        expect(
            lambda: agent._healer_eval(
                phase="run_doer",
                trigger="exception",
                error=RuntimeError("boom"),
            )
        ).to(raise_error(HealerFailure))

    with it("should send healer on the same Agent runtime as doer and judge"):
        session = _bare_session("heal-runtime")
        agent = Agent(session=session)
        agent.add_tasks([_judged_task("Compute 6 + 2.", "PASS if 8")])
        agent.run_backlog()
        healer = agent._healer_role
        expect(healer is not None).to(be_true)
        expect(healer.chat is not None).to(be_true)
        expect(healer.type).to(equal("healer"))
        expect(healer.chat.runs[-1]).to(contain("You are the Healer"))
        expect(healer.chat.chat_id.startswith("healer-")).to(be_true)


with description("Tools CLI response handling"):
    with it("should treat ok false as a hard failure"):
        expect(
            lambda: assert_tools_response("ok: false\nerror: need session name\n")
        ).to(raise_error(RuntimeError))

    with it("should accept ok true responses"):
        text = assert_tools_response("ok: true\ntool: fence\n")
        expect("ok: true" in text).to(be_true)




_CHAT = "agent.agent:ChatAgentKit"
_SUB = "agent.sub_agent_kit:SubAgentKit"
_DOER = "/echo fence chat-persist-55. Finish the Turn. Do not contact the judge."
_JUDGE = "PASS when echo fence was used and the Turn finished."


def _fresh_kit(root: Path, session: str) -> ChatAgentKit:
    """New toolset instance — simulates a separate ``python -m tools run`` call."""
    return ChatAgentKit(workspace=str(root), session=session)


def _chat_log_kinds(engine: ChatAgent) -> list[str]:
    return [row["kind"] for row in engine.session.log._records]

def _tools_run(repo_root: Path, yaml_body: str) -> str:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    completed = subprocess.run(
        [repo_python(_REPO_ROOT), "-m", "tools", "run", "-"],
        input=yaml_body,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=_REPO_ROOT,
        check=False,
        env=env,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"tools run failed ({completed.returncode}): {completed.stderr or completed.stdout}"
        )
    return completed.stdout

def _kit_yaml(
    repo_root: Path,
    *,
    toolset: str,
    workspace: Path,
    session: str,
    tool: str,
    arguments: dict | None = None,
) -> str:
    ws = str(workspace).replace("\\", "/")
    lines = [
        f"toolset: {toolset}",
        "context:",
        f"  workspace: {ws}",
        f"  session: {session}",
        f"tool: {tool}",
    ]
    if arguments:
        lines.append("arguments:")
        for key, value in arguments.items():
            if isinstance(value, (list, dict)):
                lines.append(f"  {key}: {json.dumps(value)}")
            else:
                text = str(value).replace("'", "''")
                lines.append(f"  {key}: '{text}'")
    return "\n".join(lines) + "\n"

def _chat_yaml(
    repo_root: Path,
    *,
    workspace: Path,
    session: str,
    tool: str,
    arguments: dict | None = None,
) -> str:
    return _kit_yaml(
        repo_root,
        toolset=_CHAT,
        workspace=workspace,
        session=session,
        tool=tool,
        arguments=arguments,
    )

def _sub_yaml(
    repo_root: Path,
    *,
    workspace: Path,
    session: str,
    tool: str,
    arguments: dict | None = None,
) -> str:
    return _kit_yaml(
        repo_root,
        toolset=_SUB,
        workspace=workspace,
        session=session,
        tool=tool,
        arguments=arguments,
    )

with description("Complete Agent Task Using Chat Agent"):
    with context("with the tools CLI runner"):
        with before.each:
            self.root = Path(tempfile.mkdtemp(prefix="chat_spec_"))
            self.runner = ToolsCliRunner(self.root)

        with it("should invoke echo fence via real tools run for /echo in prompt"):
            from agent.agent import AgentSession, InMemoryRepo, Repo, Workspace

            repo = InMemoryRepo(self.root, Repo.Worktree(self.root, "main"))
            workspace = Workspace(path=self.root, repos=[repo], primary_repo=repo)
            session = workspace.open(name="echo-cli", context_root=self.root)
            guidance = self.runner.run_for_prompt(
                session,
                "/echo fence chat-spec-body. Finish the Turn.",
            )
            expect(guidance is not None).to(be_true)
            kinds = [row["kind"] for row in session.log._records]
            expect(kinds).to(contain("open_turn"))
            expect(kinds).to(contain("finish_turn"))

        with it("should invoke bdd development via real tools run for /bdd.development"):
            from agent.agent import AgentSession, InMemoryRepo, Repo, Workspace

            repo = InMemoryRepo(self.root, Repo.Worktree(self.root, "main"))
            workspace = Workspace(path=self.root, repos=[repo], primary_repo=repo)
            session = workspace.open(name="bdd-cli", context_root=self.root)
            guidance = self.runner.run_for_prompt(
                session,
                "/bdd.development agents Finish the Turn.",
            )
            expect(guidance is not None).to(be_true)
            kinds = [row["kind"] for row in session.log._records]
            expect(kinds).to(contain("open_turn"))
            expect(kinds).to(contain("finish_turn"))

    with context("with one judged job in-process"):
        with before.each:
            self.root = Path(tempfile.mkdtemp(prefix="chat_eng_"))
            self.engine = ChatAgent(_workspace=self.root)
            self.engine.open_session("chat-eng", goal="spec")
            self.engine.add_tasks_from_specs(
                [
                    {
                        "doer_prompt": "/echo fence chat-eng-echo. Finish the Turn.",
                        "judge_prompt": "PASS when echo fence was used.",
                    }
                ]
            )

        with it("should open session before work"):
            expect(self.engine.session.name).to(equal("chat-eng"))
            kinds = _chat_log_kinds(self.engine)
            expect(kinds).to(contain("open"))

        with it("should dispatch doer without kit turns when run_backlog drains"):
            self.engine.run_backlog()
            kinds = _chat_log_kinds(self.engine)
            expect(kinds).to(contain("send"))
            expect(kinds).to(contain("accepted"))
            expect(kinds).to(contain("done"))
            expect("open_turn" in kinds).to(equal(False))
            expect("finish_turn" in kinds).to(equal(False))

        with it("should record PASS verdict and complete the task via run_backlog"):
            self.engine.run_backlog()
            kinds = _chat_log_kinds(self.engine)
            expect(kinds).to(contain("verdict"))
            expect(self.engine.completed_tasks[0].state).to(equal("Done"))

    with context("with the unified toolset"):
        with before.each:
            self.root = Path(tempfile.mkdtemp(prefix="chat_kit_"))
            self.kit = ChatAgentKit(workspace=str(self.root), session="chat-kit")

        with it("should document tool agent on the slash guide"):
            doc = ChatAgentKit.run_judged_job.__doc__ or ""
            expect("agent" in doc.lower()).to(be_true)
            expect("in progress" in doc.lower()).to(be_true)

        with it("should document backlog list add remove on agent_backlog"):
            doc = ChatAgentKit.agent_backlog.__doc__ or ""
            expect("backlog" in doc.lower()).to(be_true)

    with context("with persistence across separate tool instances"):
        """Regression: /agent tools must survive separate tools CLI invocations."""

        with before.each:
            self.root = Path(tempfile.mkdtemp(prefix="chat_persist_"))
            self.session = "persist-55"

        with it("should write chat-agent-state.json after agent"):
            _fresh_kit(self.root, self.session).agent(
                session_name=self.session,
                goal="persistence spec",
                doer_prompt=_DOER,
                judge_prompt=_JUDGE,
            )
            state_path = _ChatAgentPersistence.path_for(self.root, self.session)
            expect(state_path.is_file()).to(be_true)

        with it("should finish a judged job across three fresh instances"):
            first = _fresh_kit(self.root, self.session).agent(
                session_name=self.session,
                doer_prompt=_DOER,
                judge_prompt=_JUDGE,
            )
            expect("Next: do this work" in first).to(be_true)
            second = _fresh_kit(self.root, self.session).agent()
            expect("Next: judge" in second).to(be_true)
            third = _fresh_kit(self.root, self.session).agent(verdict="PASS")
            expect("healer" in third.lower()).to(be_true)

        with it("should load persisted work from session_name on a default kit"):
            ChatAgentKit(workspace=str(self.root)).agent(
                session_name=self.session,
                doer_prompt=_DOER,
                judge_prompt=_JUDGE,
            )
            second = ChatAgentKit(workspace=str(self.root)).agent(
                session_name=self.session
            )
            expect("Next: judge" in second).to(be_true)

    with context("with subprocess tools run"):
        with before.each:
            self.root = Path(tempfile.mkdtemp(prefix="chat_subproc_"))
            self.session = "subproc-55"
            self.ctx = {"workspace": self.root, "session": self.session}

        with it("should complete judged job across three subprocess tools run calls"):
            first = _tools_run(
                _REPO_ROOT,
                _chat_yaml(
                    _REPO_ROOT,
                    workspace=self.root,
                    session=self.session,
                    tool="agent",
                    arguments={
                        "session_name": self.session,
                        "goal": "subprocess spec",
                        "doer_prompt": _DOER,
                        "judge_prompt": _JUDGE,
                    },
                ),
            )
            expect("Next: do this work" in first).to(be_true)
            second = _tools_run(
                _REPO_ROOT,
                _chat_yaml(
                    _REPO_ROOT,
                    workspace=self.root,
                    session=self.session,
                    tool="agent",
                ),
            )
            expect("Next: judge" in second).to(be_true)
            third = _tools_run(
                _REPO_ROOT,
                _chat_yaml(
                    _REPO_ROOT,
                    workspace=self.root,
                    session=self.session,
                    tool="agent",
                    arguments={"verdict": "PASS"},
                ),
            )
            expect("healer" in third.lower()).to(be_true)

    with context("with a two-item judged backlog"):
        with before.each:
            self.root = Path(tempfile.mkdtemp(prefix="chat_queue_"))
            self.engine = ChatAgent(_workspace=self.root)
            self.engine.open_session("chat-queue", goal="two-item drain")
            self._doer_a = "/echo fence chat-queue-a. Finish the Turn."
            self._doer_b = "/echo fence chat-queue-b. Finish the Turn."
            self._judge = "PASS when echo fence was used."
            self.engine.add_tasks_from_specs(
                [
                    {"doer_prompt": self._doer_a, "judge_prompt": self._judge},
                    {"doer_prompt": self._doer_b, "judge_prompt": self._judge},
                ]
            )

        with it("should drain both tasks in order when run_backlog runs"):
            self.engine.run_backlog()
            expect(len(self.engine.completed_tasks)).to(equal(2))
            expect(self.engine.backlog).to(equal([]))
            expect(self.engine.current_task).to(equal(None))
            expect(self.engine.completed_tasks[0].prompt).to(equal(self._doer_a))
            expect(self.engine.completed_tasks[1].prompt).to(equal(self._doer_b))

        with it("should log launch_next once per task"):
            self.engine.run_backlog()
            kinds = _chat_log_kinds(self.engine)
            expect(kinds.count("launch_next")).to(equal(2))
            expect(kinds.count("complete_task")).to(equal(2))
            expect(kinds.count("verdict")).to(equal(2))

    with context("with ticket-linked enqueue"):
        with before.each:
            self.root = Path(tempfile.mkdtemp(prefix="chat_ticket_"))
            from agent.agent import Project

            repo = InMemoryRepo(self.root, Repo.Worktree(self.root, "main"))
            repo._issue_shelf.attach_project(Project())
            self.engine = ChatAgent(_workspace=self.root)
            self.engine._repo_ref = repo
            self.work = WorkTicket(repo, None).create(
                "Drain backlog in order",
                "enqueue from ticket then drain",
            )
            self.engine.open_session("chat-ticket", goal="ticket-linked enqueue")

        with it("should link the WorkTicket and forward issue body into the doer prompt"):
            task = self.engine.add_tasks_from_specs(
                [
                    {
                        "ticket_number": self.work.issue.number,
                        "judge_prompt": "PASS when ticket requirements were followed.",
                    }
                ]
            )[0]
            expect(len(task.tickets)).to(equal(1))
            expect(task.tickets[0].issue.number).to(equal(1))
            expect(task.doer.prompt).to(contain("# Ticket #1: Drain backlog in order"))
            expect(task.doer.prompt).to(contain("enqueue from ticket then drain"))

        with it("should persist ticket numbers across separate tool instances"):
            self.engine.add_tasks_from_specs(
                [
                    {
                        "ticket_number": self.work.issue.number,
                        "judge_prompt": "PASS when ticket requirements were followed.",
                    }
                ]
            )
            _ChatAgentPersistence.save(self.engine, session_name="chat-ticket")
            loaded = _ChatAgentPersistence.load(self.root, "chat-ticket")
            expect(loaded is not None).to(be_true)
            expect(len(loaded.backlog)).to(equal(1))
            expect(len(loaded.backlog[0].tickets)).to(equal(1))
            expect(loaded.backlog[0].tickets[0].issue.title).to(
                equal("Drain backlog in order")
            )

    with context("with agent and backlog tools"):
        with before.each:
            self.root = Path(tempfile.mkdtemp(prefix="chat_drain_"))
            self.session = "drain-55"
            self.ctx = {"workspace": self.root, "session": self.session}
            self._doer_a = "/echo fence drain-a. Finish the Turn."
            self._doer_b = "/echo fence drain-b. Finish the Turn."

        with it("should list added jobs then step the first doer via agent"):
            listed = _tools_run(
                _REPO_ROOT,
                _chat_yaml(
                    _REPO_ROOT,
                    workspace=self.root,
                    session=self.session,
                    tool="backlog",
                    arguments={
                        "action": "add",
                        "tasks": [
                            {"doer_prompt": self._doer_a, "judge_prompt": _JUDGE},
                            {"doer_prompt": self._doer_b, "judge_prompt": _JUDGE},
                        ],
                    },
                ),
            )
            expect("Left:" in listed).to(be_true)
            expect("drain-a" in listed).to(be_true)
            out = _tools_run(
                _REPO_ROOT,
                _chat_yaml(
                    _REPO_ROOT,
                    workspace=self.root,
                    session=self.session,
                    tool="agent",
                    arguments={"session_name": self.session},
                ),
            )
            expect("drain-a" in out).to(be_true)
            expect("Next: do this work" in out).to(be_true)


with description("SubAgentKit tools via subprocess"):
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="sub_kit_"))
        self.session = "sub-drain-55"
        self._doer_a = "/echo fence sub-a. Finish the Turn."
        self._doer_b = "/echo fence sub-b. Finish the Turn."

    with it("should drain two judged tasks with one run_backlog call"):
        out = _tools_run(
            _REPO_ROOT,
            _sub_yaml(
                _REPO_ROOT,
                workspace=self.root,
                session=self.session,
                tool="run",
                arguments={
                    "session_name": self.session,
                    "goal": "sub kit drain",
                    "tasks": [
                        {"doer_prompt": self._doer_a, "judge_prompt": _JUDGE},
                        {"doer_prompt": self._doer_b, "judge_prompt": _JUDGE},
                    ],
                },
            ),
        )
        expect("sub-a" in out).to(be_true)
        expect("sub-b" in out).to(be_true)
        expect("(none)" in out.split("Left:")[-1]).to(be_true)

    with it("should document Agent.run on the slash guide"):
        doc = SubAgentKit.run.__doc__ or ""
        expect("run_backlog" in doc).to(be_true)


with description("SubAgent mailbox wait while a child is in flight"):
    with it("should not raise no output while inbox still holds the prompt"):
        root = Path(tempfile.mkdtemp(prefix="mbox_hold_"))
        box = _SubAgentMailbox(root)
        box.send("doer", "Compute 1.")

        def _reply() -> None:
            time.sleep(0.45)
            (root / "doer.out").write_text("1\n", encoding="utf-8")

        threading.Thread(target=_reply, daemon=True).start()
        text = box.wait("doer", timeout_s=0.2)
        expect(text).to(equal("1"))

    with it("should raise when inbox is empty and outbox stays empty"):
        root = Path(tempfile.mkdtemp(prefix="mbox_empty_"))
        box = _SubAgentMailbox(root)

        def _wait() -> None:
            box.wait("doer", timeout_s=0.25)

        expect(_wait).to(raise_error(RuntimeError, contain("produced no output")))


def _pump_live_mailbox(runtime: Path, replies: dict[str, list[str]], seen: dict) -> None:
    """Answer each new inbox payload once. Do not re-answer while .in still holds the prompt."""
    indexes = {role: 0 for role in replies}
    last = {role: "" for role in replies}
    deadline = time.time() + 10
    while time.time() < deadline:
        for role, answers in replies.items():
            inbox = runtime / f"{role}.in"
            if not inbox.is_file():
                continue
            text = inbox.read_text(encoding="utf-8").strip()
            if text == "STOP":
                seen.setdefault("stop_at", []).append(
                    (indexes.get("doer", 0), indexes.get("judge", 0))
                )
                return
            if (
                text
                and text != last[role]
                and indexes[role] < len(answers)
            ):
                seen.setdefault("prompts", {}).setdefault(role, []).append(text)
                (runtime / f"{role}.out").write_text(
                    answers[indexes[role]] + "\n", encoding="utf-8"
                )
                last[role] = text
                indexes[role] += 1
        time.sleep(0.05)


with description("SubAgent close after live drain"):
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="sub_stop_"))
        self.engine = SubAgent(_workspace=self.root)
        self.engine.open_session("stop-kids")
        self.runtime = self.root / ".agent_sessions" / "stop-kids" / "runtime"
        self.runtime.mkdir(parents=True, exist_ok=True)
        (self.runtime / "enabled").write_text("", encoding="utf-8")

    with it("should stop doer and judge runtimes when run_backlog finishes"):
        seen: dict = {}
        worker = threading.Thread(
            target=_pump_live_mailbox,
            args=(
                self.runtime,
                {"doer": ["8"], "judge": ["PASS"], "healer": ["no heal needed"]},
                seen,
            ),
            daemon=True,
        )
        worker.start()
        self.engine.add_tasks_from_specs(
            [
                {
                    "doer_prompt": "Compute 6 + 2.",
                    "judge_prompt": "PASS if 8",
                }
            ]
        )
        self.engine.run_backlog()
        expect(len(self.engine.completed_tasks)).to(equal(1))
        expect((self.runtime / "doer.in").read_text(encoding="utf-8").strip()).to(
            equal("STOP")
        )
        expect((self.runtime / "judge.in").read_text(encoding="utf-8").strip()).to(
            equal("STOP")
        )
        expect((self.runtime / "healer.in").read_text(encoding="utf-8").strip()).to(
            equal("STOP")
        )

    with it("should not write STOP until both judged mailbox tasks complete"):
        seen: dict = {}
        worker = threading.Thread(
            target=_pump_live_mailbox,
            args=(
                self.runtime,
                {"doer": ["8", "7"], "judge": ["PASS", "PASS"], "healer": ["no heal needed", "no heal needed"]},
                seen,
            ),
            daemon=True,
        )
        worker.start()
        self.engine.add_tasks_from_specs(
            [
                {
                    "doer_prompt": "Compute 6 + 2.",
                    "judge_prompt": "PASS if 8",
                },
                {
                    "doer_prompt": "Compute 10 - 3.",
                    "judge_prompt": "PASS if 7",
                },
            ]
        )
        self.engine.run_backlog()
        expect(len(self.engine.completed_tasks)).to(equal(2))
        expect(self.engine.backlog).to(equal([]))
        expect(len(seen.get("prompts", {}).get("doer", []))).to(equal(2))
        expect(len(seen.get("prompts", {}).get("judge", []))).to(equal(2))
        early = seen.get("stop_at") or []
        expect(any(d < 2 or j < 2 for d, j in early)).to(equal(False))
        expect((self.runtime / "doer.in").read_text(encoding="utf-8").strip()).to(
            equal("STOP")
        )

    with it("should not treat child runtime stop as waiter STOP mid-queue"):
        inbox = self.runtime / "doer.in"
        inbox.write_text("Compute 10 - 3. Reply with the number only.\n", encoding="utf-8")
        from agent.agent import AgentParticipant, SubAgentChatInstance

        participant = AgentParticipant(type="doer", prompt="held")
        chat = SubAgentChatInstance.mint(participant, self.engine.session)
        chat.stop()
        expect(inbox.read_text(encoding="utf-8").strip()).to(
            equal("Compute 10 - 3. Reply with the number only.")
        )
        expect(chat.alive).to(be_false)


with description("Complete Task And Advance Backlog"):
    with context("with an Agent bound to an open AgentSession"):
        with before.each:
            self.session = _bare_session("queue-advance")
            self.agent = SubAgent(session=self.session)

        with context("with two tasks on the backlog"):
            with before.each:
                self.agent.add_tasks(
                    [_doer_task("/echo one"), _doer_task("/echo two")]
                )

            with it("should drain both tasks when run_backlog is called"):
                self.agent.run_backlog()
                expect(len(self.agent.completed_tasks)).to(equal(2))
                expect(self.agent.backlog).to(equal([]))
                expect(self.agent.current_task).to(equal(None))

            with it("should skip an unhealed FAIL and continue the backlog"):
                first = _judged_task("/echo one", "/validate")
                second = _judged_task("/echo two", "/validate")
                self.agent.clear_backlog()
                self.agent.add_tasks([first, second])
                self.agent.max_fails = 1
                self.agent._healer_tried = True
                _script_verdicts(self.agent, ["FAIL", "PASS"])
                self.agent.run_backlog()
                expect(len(self.agent.completed_tasks)).to(equal(2))
                outcomes = [
                    record["outcome"]
                    for record in self.session.log._records
                    if record["kind"] == "complete_task"
                ]
                expect(outcomes).to(equal(["skip", "PASS"]))
                expect(_verdict_results(self.session.log)).to(equal(["FAIL", "PASS"]))

            with it("should log launch_next once per task with the correct prompts"):
                self.agent.run_backlog()
                kinds = _log_kinds(self.session)
                expect(kinds.count("launch_next")).to(equal(2))
                launch_records = [
                    row for row in self.session.log._records if row["kind"] == "launch_next"
                ]
                expect(launch_records[0]["prompt"]).to(equal("/echo one"))
                expect(launch_records[1]["prompt"]).to(equal("/echo two"))

        with context("with the current agent task complete and more on the backlog"):
            with it("should launch the next task after the first finishes"):
                first = _doer_task("/echo first")
                second = _doer_task("/echo second")
                self.agent.add_tasks([first, second])
                self.agent.run_backlog()
                expect(len(self.agent.completed_tasks)).to(equal(2))
                expect(self.agent.completed_tasks[1].prompt).to(equal("/echo second"))

        with it("should leave currentTask empty when no tasks remain"):
            expect(self.agent.current_task).to(equal(None))

        with context("with a validation error on the first task"):
            with before.each:
                first = _doer_task("/echo first")
                second = _doer_task("/echo second")
                self.agent.add_tasks([first, second])
                _raise_on_next_cycle(self.agent, "validation_error")

            with it("should skip the failed task and advance to the next backlog item"):
                self.agent.run_backlog()
                expect(len(self.agent.completed_tasks)).to(equal(2))
                expect(_log_kinds(self.session)).to(contain("validation_error"))
                expect(self.agent.backlog).to(equal([]))

        with context("with a broken workflow fault on the first task"):
            with before.each:
                first = _judged_task()
                second = _doer_task("/echo second")
                self.agent.add_tasks([first, second])
                _raise_on_next_cycle(self.agent, "invariant")

            with it("should stop the whole process and leave the second task on the backlog"):
                expect(self.agent.run_backlog).to(raise_error(AgentFault))
                expect(self.agent.completed_tasks).to(equal([]))
                expect(len(self.agent.backlog)).to(equal(1))
                expect(self.agent.backlog[0].prompt).to(equal("/echo second"))


with description("Complete Agent Task Using Sub Agent"):
    with context("with an Agent that is a SubAgent"):
        with context("with a current task"):
            with before.each:
                self.session = _open_workspace_session("complete-sub")
                self.agent = SubAgent(session=self.session)
                self.task = _doer_task()
                self.agent.add_tasks([self.task])

            with it("should launch a non-blocking child for the doer"):
                self.agent.run_next_task()
                expect(self.task.doer.chat is not None).to(be_true)
                expect(self.task.doer.chat.alive).to(be_true)
                expect(self.task.doer.state).to(equal("done"))
                expect(self.task.state).to(equal("Done"))

            with it("should complete the agent task"):
                self.agent.run_next_task()
                expect(_log_kinds(self.session)).to(
                    contain("send", "accepted", "done", "complete_task")
                )
                expect(self.agent.completed_tasks).to(equal([self.task]))

            with context("with a judge"):
                with before.each:
                    self.session = _open_workspace_session("judged-sub")
                    self.agent = SubAgent(session=self.session)
                    self.task = _judged_task()
                    self.agent.add_tasks([self.task])

                with it("should also launch a non-blocking child for the judge"):
                    self.agent.run_next_task()
                    expect(self.task.doer.chat is not None).to(be_true)
                    expect(self.task.judge.chat is not None).to(be_true)
                    expect(self.task.doer.state).to(equal("done"))
                    expect(self.task.judge.state).to(equal("done"))

                with it(
                    "should complete the agent task with judging on the same "
                    "session and contextRoot"
                ):
                    self.agent.run_next_task()
                    expect(_verdicts(self.session)).to(equal(["PASS"]))
                    expect(self.task.state).to(equal("Done"))
                    doer_chat = self.task.doer.chat
                    judge_chat = self.task.judge.chat
                    expect(doer_chat is not None).to(be_true)
                    expect(judge_chat is not None).to(be_true)
                    expect(doer_chat.session_name).to(equal(self.session.name))
                    expect(judge_chat.session_name).to(equal(self.session.name))
                    expect(doer_chat.context_root).to(
                        equal(str(self.session.context_root))
                    )
                    expect(judge_chat.context_root).to(
                        equal(str(self.session.context_root))
                    )
                    expect(doer_chat.pid != judge_chat.pid).to(be_true)

    with context("with a judged echo job"):
        with before.each:
            self.session = _open_workspace_session(
                "one-judged-job-55", prefix="sub55_"
            )
            self.agent = SubAgent(session=self.session)
            self.task = _judged_echo_task()
            self.agent.add_tasks([self.task])

        with it("should open the AgentSession before running the judged task"):
            self.agent.run_next_task()
            expect(_log_kinds(self.session)).to(contain("open"))
            expect(self.session.name).to(equal("one-judged-job-55"))

        with it("should coordinate doer then judge runtime prompt roles on one task"):
            self.agent.run_next_task()
            kinds = _log_kinds(self.session)
            expect(kinds.count("send") >= 2).to(be_true)
            expect(kinds).to(contain("verdict"))
            expect(self.task.doer.state).to(equal("done"))
            expect(self.task.judge.state).to(equal("done"))

        with it("should open and finish kit Turns for slash work during the run"):
            self.agent.run_next_task()
            kinds = _log_kinds(self.session)
            expect(kinds).to(contain("open_turn"))
            expect(kinds).to(contain("finish_turn"))
            expect(kinds.index("open_turn") < kinds.index("finish_turn")).to(be_true)
            expect(any(not turn.hanging for turn in self.session.turns)).to(be_true)

        with it("should record a single PASS verdict for the judged job"):
            self.agent.run_next_task()
            expect(_verdicts(self.session)).to(equal(["PASS"]))
            expect(self.task.state).to(equal("Done"))

        with it("should close the AgentSession after the run"):
            self.agent.run_next_task()
            self.session.close()
            expect(_log_kinds(self.session)).to(contain("close"))

    with context("with a two-item judged backlog"):
        with before.each:
            self.session = _open_workspace_session(
                "sub-two-item-queue-55", prefix="sub55q_"
            )
            self.agent = SubAgent(session=self.session)
            self.first = _sub_queue_judged_task("a")
            self.second = _sub_queue_judged_task("b")
            self.agent.add_tasks([self.first, self.second])

        with it("should drain both tasks in order when run_backlog runs"):
            self.agent.run_backlog()
            expect(len(self.agent.completed_tasks)).to(equal(2))
            expect(self.agent.backlog).to(equal([]))
            expect(self.agent.current_task).to(equal(None))
            expect(self.agent.completed_tasks[0].prompt).to(contain("sub-queue-a"))
            expect(self.agent.completed_tasks[1].prompt).to(contain("sub-queue-b"))

        with it("should launch doer and judge children for each queued task"):
            self.agent.run_backlog()
            kinds = _log_kinds(self.session)
            expect(kinds.count("send") >= 4).to(be_true)
            expect(self.first.doer.state).to(equal("done"))
            expect(self.first.judge.state).to(equal("done"))
            expect(self.second.doer.state).to(equal("done"))
            expect(self.second.judge.state).to(equal("done"))

        with it("should record two PASS verdicts and two complete_task lines"):
            self.agent.run_backlog()
            expect(_verdicts(self.session)).to(equal(["PASS", "PASS"]))
            kinds = _log_kinds(self.session)
            expect(kinds.count("complete_task")).to(equal(2))
            expect(kinds.count("launch_next")).to(equal(2))


with description("Close Agent Session Using Sub Agent"):
    with context("with someone closing the agent session"):
        with before.each:
            self.session = _open_workspace_session("close-sub")
            self.agent = SubAgent(session=self.session)
            self.task = _judged_task()
            self.agent.add_tasks([self.task])
            self.agent.run_next_task()

        with it("should close the agent session"):
            self.session.close()
            expect(_log_kinds(self.session)).to(contain("close"))

        with it("should tear down non-blocking doer and judge children"):
            doer_chat = self.task.doer.chat
            judge_chat = self.task.judge.chat
            expect(doer_chat is not None).to(be_true)
            expect(judge_chat is not None).to(be_true)
            expect(doer_chat.alive).to(be_true)
            expect(judge_chat.alive).to(be_true)
            self.session.close()
            expect(doer_chat.alive).to(be_false)
            expect(judge_chat.alive).to(be_false)




def _fixture(prefix: str = "wf55_") -> tuple[Path, InMemoryRepo, Workspace, Workflow]:
    parent = Path(tempfile.mkdtemp(prefix=f"{prefix}parent_"))
    root = parent / "abd-context-driven-delivery"
    root.mkdir()
    repo = InMemoryRepo(root, Repo.Worktree(root, "main"))
    repo._issue_shelf.attach_project(Project())
    workspace = Workspace(path=root, repos=[repo], primary_repo=repo)
    workflow = Workflow(
        workspace=workspace,
        repo=repo,
        config=WorkflowConfig(),
    )
    return root, repo, workspace, workflow

with description("Create Work Ticket On Project Backlog"):
    with before.each:
        self.root, self.repo, self.workspace, self.workflow = _fixture("create_")

    with context("with a Workflow"):
        with context("with a title and body"):
            with it("should create an Issue via WorkTicket.create"):
                work = WorkTicket(self.repo, self.workflow).create(
                    "Add workflow package",
                    "forward requirements from issue",
                )
                expect(work.issue.number).to(equal(1))
                expect(work.issue.title).to(equal("Add workflow package"))
                expect(work.issue.body).to(
                    equal("forward requirements from issue")
                )

            with it("should set_status Backlog"):
                work = WorkTicket(self.repo, self.workflow).create(
                    "Add workflow package",
                    "body",
                )
                expect(work.as_dict()["project_status"]).to(equal("Backlog"))

            with it("should expose number title body through the WorkTicket"):
                work = self.workflow.create_ticket(
                    "Sketch grill skips a turn",
                    "mistakes in grill",
                )
                expect(work.as_dict()["number"]).to(equal(1))
                expect(work.as_dict()["title"]).to(equal("Sketch grill skips a turn"))
                expect(work.as_dict()["body"]).to(equal("mistakes in grill"))
                expect(work.as_dict()["project_status"]).to(equal("Backlog"))


with description("Start Ticket Moves Issue In Progress"):
    with before.each:
        self.root, self.repo, self.workspace, self.workflow = _fixture("start_")
        self.work = self.workflow.create_ticket(
            "Add workflow package",
            "forward requirements from issue",
        )

    with context("with tickets on Backlog"):
        with context("with someone starting that ticket"):
            with it("should set_status In Progress on the Issue"):
                self.workflow.start(self.work.issue.number)
                expect(self.work.as_dict()["project_status"]).to(
                    equal("In Progress")
                )

            with it("should create one agent task for the work"):
                self.workflow.start(self.work.issue.number)
                agent = self.workflow.agent
                expect(agent).not_to(equal(None))
                expect(len(agent.completed_tasks)).to(equal(1))
                expect(agent.backlog).to(equal([]))
                expect(agent.current_task).to(equal(None))

            with it("should link that agent task to the WorkTicket"):
                self.workflow.start(self.work.issue.number)
                task = self.workflow.agent.completed_tasks[0]
                expect(len(task.tickets)).to(equal(1))
                expect(task.tickets[0].issue.number).to(
                    equal(self.work.issue.number)
                )

            with it(
                "should pass ticket number, title, and body into that task doer prompt"
            ):
                self.workflow.start(self.work.issue.number)
                prompt = self.workflow.agent.completed_tasks[0].doer.prompt
                expect(prompt).to(contain("# Ticket #1: Add workflow package"))
                expect(prompt).to(contain("forward requirements from issue"))


with description("Start Ticket Opens Agent Session And Branch"):
    with before.each:
        self.root, self.repo, self.workspace, self.workflow = _fixture("session_")
        self.work = self.workflow.create_ticket(
            "Add workflow package",
            "forward requirements from issue",
        )

    with context("with an agent type selection"):
        with it("should continue under SubAgent by default"):
            result = self.workflow.start(self.work.issue.number)
            expect(result.agent_type).to(equal("SubAgent"))
            expect(isinstance(self.workflow.agent, SubAgent)).to(be_true)

        with it("should use CliAgent when agent type says so"):
            from agent.agent import CliAgent

            session = self.work.open_session()
            agent = self.workflow._bind_agent(session, "CliAgent")
            expect(isinstance(agent, CliAgent)).to(be_true)
            expect(type(agent).__name__).to(equal("CliAgent"))

    with it("should open a session via WorkTicket.openSession"):
        session = self.work.open_session()
        expect(session.name).to(equal(self.work.session_name))
        expect(session.folder.is_dir()).to(be_true)

    with it("should set session.name from WorkTicket.sessionName"):
        expect(self.work.session_name).to(equal("add-workflow-package-1"))
        self.workflow.start(self.work.issue.number)
        expect(self.workflow.session.name).to(equal("add-workflow-package-1"))

    with it("should check out or create session.branch"):
        self.workflow.start(self.work.issue.number)
        branch = self.workflow.session.branch
        expect(branch).not_to(equal(None))
        expect(branch.name).to(equal("session/add-workflow-package-1"))

    with it(
        "should create a sibling worktree next to the primary clone, never inside it"
    ):
        self.workflow.start(self.work.issue.number)
        worktree = self.workflow.session.worktree
        expect(worktree).not_to(equal(None))
        sibling = self.root.parent / "abd-cdd-1"
        expect(str(worktree.path)).to(equal(str(sibling)))
        expect(sibling.is_dir()).to(be_true)
        expect(
            lambda: self.workflow.session.branch.worktree.create_sibling(
                self.root / "nested-wt"
            )
        ).to(raise_error(ValueError))

    with it("should write the GitHub issue body to issue-body.md under contextRoot"):
        docs = self.root / "docs"
        docs.mkdir()
        self.workspace.upsert_path("agent", "contextRoot", docs)
        self.workflow.start(self.work.issue.number)
        body_path = docs / "issue-body.md"
        expect(body_path.is_file()).to(be_true)
        expect(body_path.read_text(encoding="utf-8")).to(
            equal("forward requirements from issue")
        )
        expect(str(self.workflow.session.context_root)).to(equal(str(docs)))

    with it(
        "should set the session goal from the ticket title or any start instructions provided"
    ):
        self.workflow.start(
            self.work.issue.number, instructions="land the package"
        )
        expect(self.workflow.session.goal).to(equal("land the package"))
        other_root, other_repo, other_ws, other_wf = _fixture("goal_")
        other = other_wf.create_ticket("Other ticket", "body text")
        other_wf.start(other.issue.number)
        expect(other_wf.session.goal).to(equal("Other ticket"))


with description("WorkTicket.create and start without Workflow.run"):
    with before.each:
        self.root, self.repo, self.workspace, self.workflow = _fixture("unit_")

    with it("should kebab-case sessionName from title and issue number"):
        work = self.workflow.create_ticket("Fix Job 1 Session Bind", "body")
        expect(work.session_name).to(equal("fix-job-1-session-bind-1"))

    with it("should load an existing issue via from_ref"):
        created = self.workflow.create_ticket("Existing", "seed body")
        loaded = WorkTicket.from_ref(self.repo, created.issue.number, self.workflow)
        expect(loaded.issue.title).to(equal("Existing"))
        expect(loaded.issue.body).to(equal("seed body"))

    with it("should openSession without draining the agent backlog"):
        work = self.workflow.create_ticket("Open only", "body")
        agent = SubAgent(session=None)
        self.workflow.agent = agent
        session = work.open_session()
        expect(session.name).to(equal(work.session_name))
        expect(agent.backlog).to(equal([]))
        expect(agent.completed_tasks).to(equal([]))




def _fixture(prefix: str = "fin55_") -> tuple[Path, InMemoryRepo, Workspace, Workflow]:
    parent = Path(tempfile.mkdtemp(prefix=f"{prefix}parent_"))
    root = parent / "abd-context-driven-delivery"
    root.mkdir()
    repo = InMemoryRepo(root, Repo.Worktree(root, "main"))
    from agent.agent import Project

    repo._issue_shelf.attach_project(Project())
    workspace = Workspace(path=root, repos=[repo], primary_repo=repo)
    workflow = Workflow(
        workspace=workspace,
        repo=repo,
        config=WorkflowConfig(),
    )
    return root, repo, workspace, workflow

def _open_session(name: str = "finish-work") -> AgentSession:
    root = Path(tempfile.mkdtemp(prefix="fin_sess_"))
    repo = InMemoryRepo(root, Repo.Worktree(root, "main"))
    workspace = Workspace(path=root, repos=[repo], primary_repo=repo)
    return workspace.open(name=name, context_root=root)

def _task_with_chat(chat_id: str, workspace: Path) -> AgentTask:
    prompt = "/echo finish"
    doer = AgentParticipant(type="doer", prompt=prompt)
    doer.chat = AIChatInstance(
        chat_id=chat_id,
        workspace_path=str(workspace),
        session_name="finish-work",
        context_root=str(workspace),
    )
    return AgentTask(prompt=prompt, doer=doer)

with description("Finish Work Session"):
    with context("with an AgentSession that is finishing its work"):
        with before.each:
            self.session = _open_session("finish-work")
            self.agent = SubAgent(session=self.session)
            self.session.agent = self.agent
            self.hanging = self.session.mint_turn(action="/echo hang")

        with it("should finish any hanging turns first"):
            expect(self.hanging.hanging).to(be_true)
            self.session.finish("landed")
            expect(self.hanging.hanging).to(equal(False))
            expect(self.hanging.subject).to(equal("landed"))

        with context("with one or more agent runtimes used during the session"):
            with before.each:
                self.task = _task_with_chat("doer-1", self.session.context_root)
                self.agent.add_tasks([self.task])
                self.agent.run_next_task()
                self.expected_chat = str(
                    Path(self.session.context_root)
                    / "agent-transcripts"
                    / "doer-1.jsonl"
                )
                self.close_commit = self.session.finish("landed")

            with it(
                "should gather transcript paths from participants "
                "and the orchestrator chat"
            ):
                expect(self.session.branch.chats).to(contain(self.expected_chat))

            with it("should commit session close paths on the branch"):
                expect(self.close_commit).not_to(equal(None))
                expect(self.close_commit.subject).to(equal("landed"))
                expect(self.session.branch.head).to(equal(self.close_commit))

            with it(
                "should attach each path to that close commit via refs/notes/chats"
            ):
                notes = self.close_commit.read_notes("refs/notes/chats")
                expect(notes).to(contain(self.expected_chat))

            with it("should append each path to branch.chats"):
                expect(self.session.branch.chats).to(contain(self.expected_chat))

            with it("should record on AnnotatedTag chat/{branch.name}"):
                tag = self.session.repo._tags.read(
                    f"chat/{self.session.branch.name}"
                )
                expect(tag).to(contain(self.expected_chat))


with description("Finish Ticket Closes Issue And Session"):
    with before.each:
        self.root, self.repo, self.workspace, self.workflow = _fixture("ticket_")
        self.work = self.workflow.create_ticket(
            "Land finish paths",
            "close the ticket after the run",
        )
        self.workflow.start(self.work.issue.number)
        self.sibling = self.root.parent / "abd-cdd-1"

    with context("with a ticket that is being closed"):
        with it("should finish the work session"):
            self.workflow.finish(outcome="ticket done")
            expect(self.workflow.session.branch.head).not_to(equal(None))
            expect(self.workflow.session.branch.head.subject).to(
                equal("ticket done")
            )
            expect(self.workflow.session.branch.pushed).to(be_true)

        with it("should set_status Done then close the Issue"):
            self.workflow.finish(outcome="ticket done")
            expect(self.work.as_dict()["project_status"]).to(equal("Done"))
            expect(self.work.issue.closed).to(be_true)

        with it("should close the AgentSession"):
            self.workflow.finish(outcome="ticket done")
            kinds = [row["kind"] for row in self.workflow.session.log._records]
            expect(kinds).to(contain("close"))

        with it("should remove the sibling worktree after push"):
            expect(self.sibling.is_dir()).to(be_true)
            self.workflow.finish(outcome="ticket done")
            trees = self.repo._worktrees.as_list()
            expect(
                any(Path(tree.path) == self.sibling for tree in trees)
            ).to(equal(False))

    with context("with a capstone start-through-finish journey"):
        with before.each:
            self.root, self.repo, self.workflow = _workflow_fixture()
            self.work = self.workflow.create_ticket(
                "Capstone finish",
                "prove start through finish",
            )
            self.workflow.start(self.work.issue.number)
            agent = self.workflow.agent
            completed = agent.completed_tasks[0]
            completed.doer.chat = AIChatInstance(
                chat_id="ticket-doer",
                workspace_path=str(self.workflow.session.context_root),
                session_name=self.workflow.session.name,
                context_root=str(self.workflow.session.context_root),
            )
            self.expected_chat = str(
                Path(self.workflow.session.context_root)
                / "agent-transcripts"
                / "ticket-doer.jsonl"
            )
            self.workflow.finish(outcome="capstone done")

        with it("should open a session and branch before finish"):
            session = self.workflow.session
            expect(session.name).to(equal(self.work.session_name))
            expect(session.branch.name).to(
                equal(f"session/{self.work.session_name}")
            )
            kinds = [row["kind"] for row in session.log._records]
            expect(kinds).to(contain("open"))

        with it("should finish the work session with a close commit and chat note"):
            session = self.workflow.session
            expect(session.branch.head).not_to(equal(None))
            expect(session.branch.head.subject).to(equal("capstone done"))
            expect(session.branch.chats).to(contain(self.expected_chat))
            notes = session.branch.head.read_notes("refs/notes/chats")
            expect(notes).to(contain(self.expected_chat))

        with it("should set the issue Done and closed"):
            expect(self.work.as_dict()["project_status"]).to(equal("Done"))
            expect(self.work.issue.closed).to(be_true)

        with it("should close the AgentSession after finish"):
            kinds = [row["kind"] for row in self.workflow.session.log._records]
            expect(kinds).to(contain("close"))


with description("Reject Multi Repo Session Span on finish workspace"):
    with it("should still refuse multi-repo open without a primary"):
        parent = Path(tempfile.mkdtemp(prefix="multi_fin_"))
        a = parent / "a"
        b = parent / "b"
        a.mkdir()
        b.mkdir()
        repos = [
            InMemoryRepo(a, Repo.Worktree(a, "main")),
            InMemoryRepo(b, Repo.Worktree(b, "main")),
        ]
        workspace = Workspace(path=parent, repos=repos, primary_repo=None)
        expect(lambda: workspace.open("spanning")).to(
            raise_error(MultiRepoSessionError)
        )




class _FakeClock:
    """Deterministic clock/sleep for transcript polling."""

    def __init__(self) -> None:
        self._now = 0.0
        self._hooks: list = []

    @property
    def now(self) -> float:
        return float(self._now)

    def time(self) -> float:
        return float(self._now)

    def sleep(self, seconds: float) -> None:
        self._now += seconds
        for hook in list(self._hooks):
            hook(float(self._now))

    def on_sleep(self, hook) -> None:
        self._hooks.append(hook)


def _transcript_location(chat: AIChatInstance) -> Path:
    home = Path(chat.workspace_path) if chat.workspace_path else None
    return _TranscriptPath(home=home).under_chat(chat)

def _ensure_transcript_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")

def _transcript_path(chat: AIChatInstance) -> Path:
    path = _transcript_location(chat)
    _ensure_transcript_file(path)
    return path


class _TranscriptScript:
    """Shared transcript file helpers for sleep-hook scripts."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def _jsonl_line(self, row: dict) -> str:
        return json.dumps(row) + "\n"

    def _append_jsonl(self, path: Path, row: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(self._jsonl_line(row))

    def _read_if_present(self, path: Path) -> str:
        if not path.is_file():
            return ""
        return path.read_text(encoding="utf-8")

    def _text_lacks_role(self, text: str, role: str) -> bool:
        needle = f'"role": "{role}"'
        return needle not in text

    def _write_row_when_present(self, path: Path, row: Optional[dict]) -> None:
        if row is None:
            return
        self._append_jsonl(path, row)


class _DoerReplyScript(_TranscriptScript):
    """Sleep hook: user turn then assistant reply (default did it)."""

    def __init__(self, path: Path, *, reply: str = "did it") -> None:
        super().__init__(path)
        self._reply = reply

    def __call__(self, _ignored: float) -> None:
        text = self._read_if_present(self._path)
        if self._text_lacks_role(text, "user"):
            self._append_jsonl(self._path, {"role": "user", "content": "go"})
            return
        if self._text_lacks_role(text, "assistant"):
            self._append_jsonl(
                self._path, {"role": "assistant", "content": self._reply}
            )


class _GrowScript(_TranscriptScript):
    """Sleep hook: user turn then assistant turn for accept + done."""

    def __call__(self, _ignored: float) -> None:
        row = self._next_grow_row(self._read_if_present(self._path))
        self._write_row_when_present(self._path, row)

    def _next_grow_row(self, text: str) -> Optional[dict]:
        if self._text_lacks_role(text, "user"):
            return {"role": "user", "content": "go"}
        if self._text_lacks_role(text, "assistant"):
            return {"role": "assistant", "content": "working"}
        return None


class _AcceptOnlyScript(_TranscriptScript):
    """Sleep hook: user turn only (stall on missing growth)."""

    def __call__(self, _ignored: float) -> None:
        row = self._next_accept_row(self._read_if_present(self._path))
        self._write_row_when_present(self._path, row)

    def _next_accept_row(self, text: str) -> Optional[dict]:
        if self._text_lacks_role(text, "user"):
            return {"role": "user", "content": "go"}
        return None


class _RolePairScript(_TranscriptScript):
    """Sleep hook: grow doer then judge transcripts based on tracked path."""

    def __init__(self, agent: CliAgent, doer_path: Path, judge_path: Path) -> None:
        super().__init__(doer_path)
        self._agent = agent
        self._doer_path = doer_path
        self._judge_path = judge_path

    def __call__(self, _ignored: float) -> None:
        tracked = self._agent.watch.path
        if tracked is None:
            return
        if tracked.resolve() == self._doer_path.resolve():
            self._grow_path(self._doer_path, "go", "did it")
            return
        if tracked.resolve() == self._judge_path.resolve():
            self._grow_path(self._judge_path, "judge", "Verdict: PASS")
            return
        _GrowScript(tracked)(_ignored)

    def _grow_path(self, path: Path, user_content: str, assistant_content: str) -> None:
        text = self._read_if_present(path)
        if self._text_lacks_role(text, "user"):
            self._append_jsonl(path, {"role": "user", "content": user_content})
            return
        if self._text_lacks_role(text, "assistant"):
            self._append_jsonl(
                path, {"role": "assistant", "content": assistant_content}
            )
            return
        users = text.count('"role": "user"')
        assistants = text.count('"role": "assistant"')
        if users <= assistants:
            self._append_jsonl(path, {"role": "user", "content": user_content})
            return
        self._append_jsonl(
            path, {"role": "assistant", "content": assistant_content}
        )


class _FailVerdictScript(_RolePairScript):
    """Sleep hook: doer grows; judge transcript ends with FAIL."""

    def __call__(self, _ignored: float) -> None:
        tracked = self._agent.watch.path
        if tracked is None:
            return
        if tracked.resolve() == self._doer_path.resolve():
            self._grow_path(self._doer_path, "go", "did it")
            return
        if tracked.resolve() == self._judge_path.resolve():
            self._grow_path(self._judge_path, "judge", "Verdict: FAIL")
            return
        _GrowScript(tracked)(_ignored)


class _FailThenPassScript(_RolePairScript):
    """Sleep hook: first judge verdict FAIL, then PASS after fail_count advances."""

    def __call__(self, _ignored: float) -> None:
        tracked = self._agent.watch.path
        if tracked is None:
            return
        if tracked.resolve() == self._doer_path.resolve():
            self._grow_path(self._doer_path, "go", "did it")
            return
        if tracked.resolve() == self._judge_path.resolve():
            verdict = (
                "Verdict: FAIL" if self._agent.fail_count < 1 else "Verdict: PASS"
            )
            self._grow_path(self._judge_path, "judge", verdict)
            return
        _GrowScript(tracked)(_ignored)


class _ToolUseOnlyScript(_RolePairScript):
    """Sleep hook: judge transcript ends with tool_use only (no PASS/FAIL)."""

    def __call__(self, _ignored: float) -> None:
        tracked = self._agent.watch.path
        if tracked is None:
            return
        if tracked.resolve() == self._doer_path.resolve():
            self._grow_path(self._doer_path, "go", "did it")
            return
        if tracked.resolve() == self._judge_path.resolve():
            text = self._read_if_present(self._judge_path)
            if self._text_lacks_role(text, "user"):
                self._append_jsonl(
                    self._judge_path, {"role": "user", "content": "judge"}
                )
                return
            if self._text_lacks_role(text, "assistant"):
                self._append_jsonl(
                    self._judge_path,
                    {
                        "role": "assistant",
                        "message": {
                            "content": [{"type": "tool_use", "name": "grep"}]
                        },
                    },
                )
            return
        _GrowScript(tracked)(_ignored)


def _bind_records(session) -> list[dict]:
    return [
        record
        for record in session.log._records
        if record["kind"] == "bind_chat_context"
    ]

with description("Set Chat Context From Session Worktree"):
    with context("with an open AgentSession that has a branch worktree"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "bind-worktree", prefix="cli_bind_"
            )
            self.agent = _cli_agent(self.session, self.clock)
            self.task = _doer_task()
            self.path_holder = {"path": None}

            def _grow(_now: float) -> None:
                tracked = self.agent.watch.path
                if tracked is None:
                    return
                if self.path_holder["path"] is None:
                    self.path_holder["path"] = tracked
                    _ensure_transcript_file(tracked)
                _GrowScript(tracked)(_now)

            self.clock.on_sleep(_grow)
            self.agent.add_tasks([self.task])

        with it(
            "should bind workspace root to session.branch.worktree.path before running tasks"
        ):
            self.agent.run_next_task()
            expect(self.agent._workspace_root).to(
                equal(str(self.session.worktree.path))
            )
            expect(self.task.doer.chat.workspace_path).to(
                equal(str(self.session.worktree.path))
            )

    with context("with no branch worktree yet"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "pending-main", prefix="cli_pending_"
            )
            self.session.branch = None
            self.agent = _cli_agent(self.session, self.clock)
            self.agent.add_tasks([_doer_task()])

        with it("should not open a durable CliAgent session on main"):
            self.agent._ensure_session()
            expect(self.agent._pending_session).to(be_true)
            expect(self.agent._workspace_root).to(equal(""))
            expect(self.agent.run_next_task).to(raise_error(RuntimeError))

    with context("with a current task"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "bind-chat", prefix="cli_chat_"
            )
            self.agent = _cli_agent(self.session, self.clock)
            self.task = _doer_task()
            self.agent.add_tasks([self.task])
            self.clock.on_sleep(
                lambda _n: _GrowScript(self.agent.watch.path)(_n)
                if self.agent.watch.path is not None
                else None
            )

        with it("should ensure one AI chat runtime per CliAgentParticipant"):
            expect(issubclass(CliAgentParticipant, AgentParticipant)).to(be_true)
            expect(self.task.doer.chat).to(equal(None))
            self.agent.run_next_task()
            expect(self.task.doer.chat).not_to(equal(None))
            expect(self.task.doer.chat.chat_id).not_to(equal(""))
            expect(self.task.doer.chat.list_chats()).to(
                contain(self.task.doer.chat.chat_id)
            )

        with it("should set chat.workspacePath to session.branch.worktree.path"):
            self.agent.run_next_task()
            expect(self.task.doer.chat.workspace_path).to(
                equal(str(self.session.worktree.path))
            )

        with it("should set chat.sessionName to session.name"):
            self.agent.run_next_task()
            expect(self.task.doer.chat.session_name).to(equal(self.session.name))

        with it(
            "should append a JSONL line to the session log under session.folder "
            "with the participant, chat id, process id, worktree path, and agent session name"
        ):
            self.agent.run_next_task()
            binds = _bind_records(self.session)
            expect(len(binds) > 0).to(be_true)
            row = binds[0]
            expect(row["participant"]).to(equal("doer"))
            expect(row["chatId"]).to(equal(self.task.doer.chat.chat_id))
            expect(row["pid"]).to(equal(self.task.doer.chat.pid))
            expect(row["workspacePath"]).to(
                equal(str(self.session.worktree.path))
            )
            expect(row["sessionName"]).to(equal(self.session.name))


with description("Launch Doer On Agent Runtime"):
    with context("with a doer prompt"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "launch-doer", prefix="cli_launch_"
            )
            self.agent = _cli_agent(self.session, self.clock)
            self.task = _doer_task("/echo fence doer")
            self.agent.add_tasks([self.task])
            self.clock.on_sleep(
                lambda _n: _GrowScript(self.agent.watch.path)(_n)
                if self.agent.watch.path is not None
                else None
            )

        with it(
            "should persist the prompt to a task file under session.contextRoot "
            "when argv would be too long"
        ):
            long_prompt = "/echo " + ("x" * 8000)
            self.task.doer.prompt = long_prompt
            self.task.prompt = long_prompt
            self.agent.run_next_task()
            task_file = Path(self.session.context_root) / ".context" / "cli-agent-task.txt"
            expect(task_file.is_file()).to(be_true)
            expect(task_file.read_text(encoding="utf-8")).to(equal(long_prompt))

        with it("should run the doer prompt on the doer agent runtime"):
            self.agent.run_next_task()
            expect(self.task.doer.chat.runs).to(contain(self.task.doer.prompt))

        with it(
            "should append a session log line that the doer agent runtime was run "
            "and the prompt was sent"
        ):
            self.agent.run_next_task()
            expect(_log_kinds(self.session)).to(contain("run", "send", "accepted"))


with description("Launch Judge On Agent Runtime"):
    with context("with a judge prompt"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "launch-judge", prefix="cli_judge_"
            )
            self.agent = _cli_agent(self.session, self.clock)
            self.task = _judged_task()
            self.agent.add_tasks([self.task])

            def _grow(_now: float) -> None:
                tracked = self.agent.watch.path
                if tracked is None:
                    return
                doer = self.task.doer.chat
                if doer is None:
                    return
                doer_path = _transcript_path(doer)
                judge = self.task.judge.chat
                if judge is None:
                    _DoerReplyScript(doer_path)(_now)
                    return
                judge_path = _transcript_path(judge)
                _RolePairScript(self.agent, doer_path, judge_path)(_now)

            self.clock.on_sleep(_grow)

        with it("should ensure a separate AI chat runtime for the judge"):
            self.agent.run_next_task()
            expect(self.task.judge.chat).not_to(equal(None))
            expect(self.task.judge.chat.chat_id).not_to(
                equal(self.task.doer.chat.chat_id)
            )

        with it("should set the same workspacePath and sessionName as the doer"):
            self.agent.run_next_task()
            expect(self.task.judge.chat.workspace_path).to(
                equal(self.task.doer.chat.workspace_path)
            )
            expect(self.task.judge.chat.session_name).to(
                equal(self.task.doer.chat.session_name)
            )

        with it("should run the judge prompt on the judge agent runtime"):
            self.agent.run_next_task()
            sent = self.task.judge.chat.runs[-1]
            expect(sent).to(contain(self.task.judge.prompt))
            expect(sent).to(contain("The doer answered:"))

        with it("should forward the doer transcript answer into the judge prompt"):
            self.agent.run_next_task()
            doer_path = _transcript_path(self.task.doer.chat)
            transcript = _JsonlTranscript(doer_path)
            answer = _AssistantText()
            doer_reply = ""
            for row in transcript.rows_newest_first():
                if row.get("role") != "assistant":
                    continue
                doer_reply = answer.from_row(row).strip()
                if doer_reply:
                    break
            sent = self.task.judge.chat.runs[-1]
            expect(sent).to(contain(f"The doer answered: {doer_reply}"))
            expect(sent).to(contain(self.task.judge.prompt))

        with it("should append a session log line that the judge prompt was sent"):
            self.agent.run_next_task()
            expect(_log_kinds(self.session)).to(
                contain("launch_judge", "send", "verdict")
            )


with description("Kick Stalled Doer"):
    with context(
        "with a doer that finished its job but the backlog did not advance"
    ):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "auto-kick", prefix="cli_kick_"
            )
            self.agent = _cli_agent(self.session, self.clock)
            self.agent._ensure_session()
            self.task = _doer_task()
            self.task.state = "In Progress"
            self.task.doer.state = "done"
            self.task.doer.chat = AIChatInstance(chat_id="stuck-doer", pid=9)
            self.agent.current_task = self.task

        with it(
            "should automatically kick the doer agent runtime without user intervention"
        ):
            self.agent._auto_kick_stalled_doer()
            expect(self.task.doer.state).to(equal("idle"))
            expect(self.task.doer.chat.continue_count).to(equal(1))

        with it("should append a session log line that the participant was kicked"):
            self.agent._auto_kick_stalled_doer()
            expect(_log_kinds(self.session)).to(contain("kick"))


with description("Close Cli Agent Session"):
    with context("with someone closing the agent session"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "close-cli", prefix="cli_close_"
            )
            self.agent = _cli_agent(self.session, self.clock)
            self.agent._ensure_session()
            self.task = _judged_task()
            self.doer_chat = AIChatInstance(
                chat_id="close-doer",
                pid=101,
                alive=True,
                workspace_path=str(self.session.worktree.path),
                session_name=self.session.name,
            )
            self.judge_chat = AIChatInstance(
                chat_id="close-judge",
                pid=202,
                alive=True,
                workspace_path=str(self.session.worktree.path),
                session_name=self.session.name,
            )
            self.task.doer.chat = self.doer_chat
            self.task.judge.chat = self.judge_chat
            self.agent.current_task = self.task
            self.ctx = Path(self.session.context_root) / ".context"
            self.ctx.mkdir(parents=True, exist_ok=True)
            self.temp_task = self.ctx / "cli-agent-task.txt"
            self.temp_task.write_text("/echo long", encoding="utf-8")
            self.durable = self.ctx / "story-map.md"
            self.durable.write_text("# keep\n", encoding="utf-8")
            self.session_log = self.session.folder / "agent-session.jsonl"
            self.session_log.parent.mkdir(parents=True, exist_ok=True)
            if not self.session_log.is_file():
                self.session_log.write_text("", encoding="utf-8")

        with it("should stop live doer and judge agent runtime processes"):
            self.agent.close()
            expect(self.doer_chat.alive).to(be_false)
            expect(self.judge_chat.alive).to(be_false)
            expect(self.doer_chat.pid).to(equal(None))
            expect(self.judge_chat.pid).to(equal(None))

        with it("should clear doer and judge chat bindings on the agent session"):
            self.agent.close()
            expect(self.task.doer.chat).to(equal(None))
            expect(self.task.judge.chat).to(equal(None))
            expect(self.agent._workspace_root).to(equal(""))

        with it(
            "should remove orchestration temps without deleting durable session artifacts"
        ):
            self.agent.close()
            expect(self.temp_task.exists()).to(be_false)
            expect(self.durable.is_file()).to(be_true)
            expect(self.session.folder.is_dir()).to(be_true)
            expect(self.session_log.is_file()).to(be_true)

        with context("with the agent session closed successfully"):
            with it("should leave no live CLI processes or stale chat bindings"):
                self.session.close()
                expect(self.doer_chat.alive).to(be_false)
                expect(self.judge_chat.alive).to(be_false)
                expect(self.task.doer.chat).to(equal(None))
                expect(self.task.judge.chat).to(equal(None))
                expect(self.agent._workspace_root).to(equal(""))
                expect(self.temp_task.exists()).to(be_false)

            with it("should close the agent session"):
                self.session.close()
                expect(_log_kinds(self.session)).to(contain("close"))
                expect(self.session.folder.is_dir()).to(be_true)
                expect(self.durable.is_file()).to(be_true)

        with it("should expose close_agents cleanup and close_cli_session"):
            self.agent.close_agents()
            expect(self.doer_chat.alive).to(be_false)
            expect(self.task.doer.chat).to(equal(None))
            self.agent.cleanup()
            expect(self.temp_task.exists()).to(be_false)
            expect(self.durable.is_file()).to(be_true)
            self.agent.close_cli_session()
            expect(_log_kinds(self.session)).to(contain("close"))


with description("Complete Agent Task Using Cli Agent"):
    with context("with a current task"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "complete-cli", prefix="cli_complete_"
            )
            self.workspace = Path(self.session.context_root)
            self.agent = _cli_agent(self.session, self.clock)
            self.task = _doer_task()
            self.chat = _bind_chat(
                self.task.doer, workspace=self.workspace, chat_id="complete-1"
            )
            self.path = _transcript_path(self.chat)
            self.clock.on_sleep(_GrowScript(self.path))
            self.agent.add_tasks([self.task])

        with it("should complete the agent task"):
            self.agent.run_next_task()
            expect(self.agent.completed_tasks).to(equal([self.task]))
            expect(self.task.state).to(equal("Done"))
            expect(self.chat.runs).to(contain(self.task.doer.prompt))

        with it("should finish with done in the result"):
            result = self.agent.run()
            expect(self.task.state).to(equal("Done"))
            expect(result).to(contain("Done:"))
            expect(result).to(contain(self.task.prompt))

        with context("with max fails reached on the current task"):
            with context("with a validation error"):
                with before.each:
                    self.clock = _FakeClock()
                    self.session = _open_workspace_session(
                        "cli-val-err", prefix="cli_val_"
                    )
                    self.agent = _cli_agent(self.session, self.clock)
                    self.agent.max_fails = 2
                    first = _doer_task("/echo first")
                    second = _doer_task("/echo second")
                    self.agent.add_tasks([first, second])
                    _raise_on_next_cycle(self.agent, "validation_error")
                    self.clock.on_sleep(
                        lambda _n: _GrowScript(self.agent.watch.path)(_n)
                        if self.agent.watch.path is not None
                        else None
                    )

                with it(
                    "should stop this task and move on to the next item in the backlog"
                ):
                    self.agent.run_backlog()
                    expect(len(self.agent.completed_tasks)).to(equal(2))
                    expect(self.agent.completed_tasks[0].prompt).to(
                        equal("/echo first")
                    )
                    expect(self.agent.backlog).to(equal([]))

            with context("with a broken workflow fault"):
                with before.each:
                    self.clock = _FakeClock()
                    self.session = _open_workspace_session(
                        "cli-fail-limit", prefix="cli_limit_"
                    )
                    self.agent = _cli_agent(self.session, self.clock)
                    self.agent.max_fails = 2
                    self.task = _judged_task()
                    self.agent.add_tasks([self.task])

                    def _grow(_now: float) -> None:
                        doer = self.task.doer.chat
                        if doer is None:
                            return
                        doer_path = _transcript_path(doer)
                        judge = self.task.judge.chat
                        if judge is None:
                            _GrowScript(doer_path)(_now)
                            return
                        _FailVerdictScript(
                            self.agent,
                            doer_path,
                            _transcript_path(judge),
                        )(_now)

                    self.clock.on_sleep(_grow)

                with it("should stop with AgentFault judge_fail_limit"):
                    expect(self.agent.run_next_task).to(raise_error(AgentFault))

        with context("with a broken workflow fault on the first task"):
            with before.each:
                self.clock = _FakeClock()
                self.session = _open_workspace_session(
                    "cli-invariant", prefix="cli_inv_"
                )
                self.agent = _cli_agent(self.session, self.clock)
                first = _judged_task()
                second = _doer_task("/echo second")
                self.agent.add_tasks([first, second])
                _raise_on_next_cycle(self.agent, "invariant")
                self.clock.on_sleep(
                    lambda _n: _GrowScript(self.agent.watch.path)(_n)
                    if self.agent.watch.path is not None
                    else None
                )

            with it(
                "should stop the whole process and leave the second task on the backlog"
            ):
                expect(self.agent.run_backlog).to(raise_error(AgentFault))
                expect(self.agent.completed_tasks).to(equal([]))
                expect(len(self.agent.backlog)).to(equal(1))
                expect(self.agent.backlog[0].prompt).to(equal("/echo second"))
                expect(_log_kinds(self.session)).to(contain("error", "run_stopped"))

            with context("under maxFails with a later PASS"):
                with before.each:
                    self.clock = _FakeClock()
                    self.session = _open_workspace_session(
                        "cli-retry-pass", prefix="cli_retry_"
                    )
                    self.agent = _cli_agent(self.session, self.clock)
                    self.agent.max_fails = 2
                    self.task = _judged_task()
                    self.agent.add_tasks([self.task])

                    def _grow(_now: float) -> None:
                        doer = self.task.doer.chat
                        if doer is None:
                            return
                        doer_path = _transcript_path(doer)
                        judge = self.task.judge.chat
                        if judge is None:
                            _GrowScript(doer_path)(_now)
                            return
                        _FailThenPassScript(
                            self.agent,
                            doer_path,
                            _transcript_path(judge),
                        )(_now)

                    self.clock.on_sleep(_grow)

                with it("should kick the doer and complete on pass"):
                    self.agent.run_next_task()
                    expect(self.task.state).to(equal("Done"))
                    expect(_verdicts(self.session)).to(contain("FAIL", "PASS"))
                    expect(_log_kinds(self.session)).to(contain("kick"))


def _bind_chat(
    participant: AgentParticipant,
    *,
    workspace: Path,
    chat_id: str,
    alive: bool = True,
) -> AIChatInstance:
    chat = AIChatInstance(
        chat_id=chat_id,
        workspace_path=str(workspace),
        alive=alive,
        pid=4242 if alive else None,
    )
    participant.chat = chat
    return chat


class _SpecProc:
    def __init__(self, pid: int = 4242) -> None:
        self.pid = pid

    def terminate(self) -> None:
        return None

    def poll(self):
        return None


class _SpecCursorCli:
    def launcher(self) -> str:
        return "cursor-agent"

    def create_chat(self, workspace: str) -> str:
        return str(uuid.uuid4())

    def spawn(self, argv: list, *, cwd: str):
        return _SpecProc()


def _cli_agent(
    session,
    clock: _FakeClock,
    *,
    accept_seconds: float = 2.0,
    stall_seconds: float = 2.0,
    quiet_seconds: float = 0.3,
) -> CliAgent:
    watch = AgentRuntimeTranscriptWatcher(
        sleep=clock.sleep, clock=clock.time, poll_s=0.1
    )
    home = Path(session.context_root)
    paths = _TranscriptPath(home=home)
    agent = CliAgent(
        session=session,
        watch=watch,
        accept_seconds=accept_seconds,
        stall_seconds=stall_seconds,
        quiet_seconds=quiet_seconds,
        _paths=paths,
        _cli=_SpecCursorCli(),
    )

    def _grow_healer(_now: float) -> None:
        healer = agent._healer_role
        tracked = agent.watch.path
        if tracked is None or healer is None or healer.chat is None:
            return
        healer_path = agent._paths.under_chat(healer.chat)
        if tracked.resolve() != healer_path.resolve():
            return
        _GrowScript(tracked)(_now)

    clock.on_sleep(_grow_healer)
    return agent


def _expect_fault_kind(run, kind: str) -> None:
    raised: list[AIChatFault] = []

    def _capture():
        try:
            run()
        except AIChatFault as fault:
            raised.append(fault)
            raise

    expect(_capture).to(raise_error(AIChatFault))
    expect(raised[0].kind).to(equal(kind))


def _write_verdict_fixture(path: Path, transcript_jsonl: str) -> None:
    path.write_text(transcript_jsonl, encoding="utf-8")


def _flat_pass_jsonl() -> str:
    return (
        json.dumps({"role": "user", "content": "go"})
        + "\n"
        + json.dumps({"role": "assistant", "content": "Verdict: PASS"})
        + "\n"
    )


def _nested_pass_jsonl() -> str:
    return (
        json.dumps(
            {
                "role": "assistant",
                "message": {
                    "content": [
                        {"type": "text", "text": "Evidence ok.\n\nPASS"},
                    ]
                },
            }
        )
        + "\n"
    )


def _fail_jsonl() -> str:
    return json.dumps({"role": "assistant", "content": "Result: FAIL"}) + "\n"


with description("Await Accept On Transcript"):
    with context("with a participant agent runtime that is running"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session("await-accept", prefix="cli_accept_")
            self.workspace = Path(self.session.context_root)
            self.agent = _cli_agent(self.session, self.clock)
            self.task = _doer_task()
            self.chat = _bind_chat(
                self.task.doer, workspace=self.workspace, chat_id="doer-1"
            )
            self.path = _transcript_path(self.chat)
            self.clock.on_sleep(_GrowScript(self.path))
            self.agent.add_tasks([self.task])

        with it("should pick up the prompt before the accept timeout runs out"):
            self.agent.run_next_task()
            expect(self.task.doer.state).to(equal("done"))
            expect(self.chat.runs).to(equal([self.task.doer.prompt]))

        with it(
            "should append a session log line that the participant accepted the prompt"
        ):
            self.agent.run_next_task()
            expect(_log_kinds(self.session)).to(
                contain("send", "accepted", "done", "complete_task")
            )

    with context(
        "with the accept timeout run out and the agent runtime process never ran"
    ):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "not-accepted", prefix="cli_not_acc_"
            )
            self.workspace = Path(self.session.context_root)
            self.agent = _cli_agent(
                self.session, self.clock, accept_seconds=0.5
            )
            self.task = _doer_task()
            self.chat = _bind_chat(
                self.task.doer,
                workspace=self.workspace,
                chat_id="dead-1",
                alive=False,
            )
            _transcript_path(self.chat)
            self.agent.add_tasks([self.task])

        with it("should raise AIChatFault not_accepted"):
            _expect_fault_kind(self.agent.run_next_task, "not_accepted")


with description("Wait For Done On Transcript"):
    with context("with a participant agent runtime that accepted the prompt"):
        with context("with a doer participant"):
            with before.each:
                self.clock = _FakeClock()
                self.session = _open_workspace_session(
                    "wait-done", prefix="cli_done_"
                )
                self.workspace = Path(self.session.context_root)
                self.agent = _cli_agent(
                    self.session,
                    self.clock,
                    stall_seconds=2.0,
                    quiet_seconds=0.3,
                )
                self.task = _doer_task()
                self.chat = _bind_chat(
                    self.task.doer, workspace=self.workspace, chat_id="doer-done"
                )
                self.path = _transcript_path(self.chat)
                self.agent.add_tasks([self.task])

            with context("with new output appearing on the transcript"):
                with before.each:
                    self.clock.on_sleep(_GrowScript(self.path))

                with it(
                    "should wait until the transcript stops changing for quietSeconds"
                ):
                    self.agent.run_next_task()
                    expect(self.task.doer.state).to(equal("done"))
                    expect(self.task.state).to(equal("Done"))

                with it(
                    "should append a session log line that the participant finished producing output"
                ):
                    self.agent.run_next_task()
                    expect(_log_kinds(self.session)).to(
                        contain("accepted", "done", "complete_task")
                    )

            with context("with no new output before the stall timeout runs out"):
                with it("should raise AIChatFault stall"):
                    self.clock.on_sleep(_AcceptOnlyScript(self.path))
                    _expect_fault_kind(self.agent.run_next_task, "stall")


with description("Read Verdict From Judge Transcript"):
    with context(
        "with a readable PASS or FAIL on the judge transcript before the stall timeout runs out"
    ):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "read-verdict", prefix="cli_verdict_"
            )
            self.workspace = Path(self.session.context_root)
            self.agent = _cli_agent(self.session, self.clock)
            self.task = _judged_task()
            self.doer_chat = _bind_chat(
                self.task.doer, workspace=self.workspace, chat_id="doer-v"
            )
            self.judge_chat = _bind_chat(
                self.task.judge, workspace=self.workspace, chat_id="judge-v"
            )
            self.doer_path = _transcript_path(self.doer_chat)
            self.judge_path = _transcript_path(self.judge_chat)
            self.agent.add_tasks([self.task])
            self.clock.on_sleep(
                _RolePairScript(self.agent, self.doer_path, self.judge_path)
            )

        with it("should append a session log line with the verdict and result"):
            self.agent.run_next_task()
            expect(_verdicts(self.session)).to(equal(["PASS"]))
            expect(self.task.state).to(equal("Done"))

        with it("should read PASS from flat assistant jsonl via the watcher"):
            watch = AgentRuntimeTranscriptWatcher()
            path = Path(tempfile.mkdtemp(prefix="verdict_flat_")) / "j.jsonl"
            _write_verdict_fixture(path, _flat_pass_jsonl())
            watch.track(path)
            expect(watch._read_verdict()).to(equal("PASS"))

        with it(
            "should read PASS from Cursor message-nested assistant jsonl"
        ):
            watch = AgentRuntimeTranscriptWatcher()
            path = Path(tempfile.mkdtemp(prefix="verdict_nest_")) / "j.jsonl"
            _write_verdict_fixture(path, _nested_pass_jsonl())
            watch.track(path)
            expect(watch._read_verdict()).to(equal("PASS"))

        with it("should read FAIL when the assistant text contains FAIL"):
            watch = AgentRuntimeTranscriptWatcher()
            path = Path(tempfile.mkdtemp(prefix="verdict_fail_")) / "j.jsonl"
            _write_verdict_fixture(path, _fail_jsonl())
            watch.track(path)
            expect(watch._read_verdict()).to(equal("FAIL"))


with description("Cli Agent One Judged Echo Job"):
    with context("that enqueues and runs the backlog"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "cli-echo-job", prefix="cli_echo_"
            )
            self.agent = _cli_agent(self.session, self.clock)
            self.task = _cli_judged_echo_task()
            self.agent.add_tasks([self.task])

            def _grow(_now: float) -> None:
                doer = self.task.doer.chat
                if doer is None:
                    return
                doer_path = _transcript_path(doer)
                judge = self.task.judge.chat
                if judge is None:
                    _GrowScript(doer_path)(_now)
                    return
                _RolePairScript(
                    self.agent,
                    doer_path,
                    _transcript_path(judge),
                )(_now)

            self.clock.on_sleep(_grow)

        with it("should finish with done in the result"):
            result = self.agent.run()
            expect(self.task.state).to(equal("Done"))
            expect(result).to(contain("Done:"))
            expect(result).to(contain(self.task.prompt))

        with it("should record exactly one pass verdict on the session log"):
            self.agent.run_next_task()
            expect(_verdicts(self.session)).to(equal(["PASS"]))
            expect(_log_kinds(self.session)).to(contain("run_stopped"))


with description("Cli Agent Session Log Kinds"):
    with context("with a successful CliAgent run"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "cli-log-ok", prefix="cli_log_ok_"
            )
            self.agent = _cli_agent(self.session, self.clock)
            self.task = _doer_task()
            self.agent.add_tasks([self.task])
            self.clock.on_sleep(
                lambda _n: _GrowScript(self.agent.watch.path)(_n)
                if self.agent.watch.path is not None
                else None
            )

        with it("should append run_stopped complete after run_next_task"):
            self.agent.run_next_task()
            stopped = [
                row
                for row in self.session.log._records
                if row["kind"] == "run_stopped"
            ]
            expect(len(stopped) > 0).to(be_true)
            expect(stopped[-1]["reason"]).to(equal("complete"))

    with context("with a transcript fault during run"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "cli-log-fault", prefix="cli_log_fault_"
            )
            self.agent = _cli_agent(
                self.session, self.clock, accept_seconds=0.5
            )
            self.task = _doer_task()
            self.chat = _bind_chat(
                self.task.doer,
                workspace=Path(self.session.context_root),
                chat_id="dead-log",
                alive=False,
            )
            _transcript_path(self.chat)
            self.agent.add_tasks([self.task])

        with it("should append error and run_stopped with the exception name"):
            _expect_fault_kind(self.agent.run_next_task, "not_accepted")
            kinds = _log_kinds(self.session)
            expect(kinds).to(contain("error", "run_stopped"))
            stopped = [
                row
                for row in self.session.log._records
                if row["kind"] == "run_stopped"
            ]
            expect(stopped[-1]["reason"]).to(equal("AIChatFault"))


with description("Cli Agent Tools Cli No Op"):
    with context("with a doer prompt that would invoke tools on Agent"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "cli-no-tools", prefix="cli_no_tools_"
            )
            self.agent = _cli_agent(self.session, self.clock)
            self.task = _doer_task("/echo fence hello")
            self.agent.add_tasks([self.task])
            self.clock.on_sleep(
                lambda _n: _GrowScript(self.agent.watch.path)(_n)
                if self.agent.watch.path is not None
                else None
            )

        with it("should not run the in-process tools CLI stub on CliAgent"):
            self.agent.run_next_task()
            expect(self.agent.last_guidance).to(equal(None))


with description("Cli Agent Empty Judge Verdict"):
    with context("with a judge transcript that has tool_use only"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "cli-empty-verdict", prefix="cli_empty_"
            )
            self.agent = _cli_agent(self.session, self.clock)
            self.task = _judged_task()
            self.agent.add_tasks([self.task])

            def _grow(_now: float) -> None:
                doer = self.task.doer.chat
                if doer is None:
                    return
                doer_path = _transcript_path(doer)
                judge = self.task.judge.chat
                if judge is None:
                    _GrowScript(doer_path)(_now)
                    return
                _ToolUseOnlyScript(
                    self.agent,
                    doer_path,
                    _transcript_path(judge),
                )(_now)

            self.clock.on_sleep(_grow)

        with it("should raise AIChatFault connection when no PASS or FAIL is present"):
            _expect_fault_kind(self.agent.run_next_task, "connection")


with description("Cli Agent Healer Runtime"):
    with context("after a judged task completes on CliAgent"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "cli-healer", prefix="cli_healer_"
            )
            self.agent = _cli_agent(self.session, self.clock)
            self.agent.healer = Healer()
            self.task = _judged_task()
            self.agent.add_tasks([self.task])

            def _grow(_now: float) -> None:
                doer = self.task.doer.chat
                if doer is None:
                    return
                doer_path = _transcript_path(doer)
                judge = self.task.judge.chat
                if judge is None:
                    _GrowScript(doer_path)(_now)
                    return
                _RolePairScript(
                    self.agent,
                    doer_path,
                    _transcript_path(judge),
                )(_now)

            self.clock.on_sleep(_grow)

        with it("should deliver healer on the CLI runtime path"):
            self.agent.run_next_task()
            healer = self.agent._healer_role
            expect(healer is not None).to(be_true)
            expect(healer.chat is not None).to(be_true)
            expect(isinstance(healer.chat, CursorChatInstance)).to(be_true)
            expect(healer.chat.runs[-1]).to(contain("You are the Healer"))


with description("Pending Session Blocks Participant Deliver"):
    with context("with no branch worktree yet"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "cli-pending-deliver", prefix="cli_pending_d_"
            )
            self.session.branch = None
            self.agent = _cli_agent(self.session, self.clock)
            self.task = _judged_task()
            self.agent.add_tasks([self.task])
            self.agent._ensure_session()

        with it("should refuse judge deliver on main before worktree exists"):
            judge = self.task.judge
            expect(self.agent._pending_session).to(be_true)
            expect(
                lambda: self.agent._deliver_to_runtime(judge)
            ).to(raise_error(RuntimeError))


with description("Cli Agent Stall Kick On Run Path"):
    with context("with a doer that accepted but never finished"):
        with before.each:
            self.clock = _FakeClock()
            self.session = _open_workspace_session(
                "cli-stall-kick", prefix="cli_stall_kick_"
            )
            self.workspace = Path(self.session.context_root)
            self.agent = _cli_agent(
                self.session,
                self.clock,
                stall_seconds=2.0,
                quiet_seconds=0.3,
            )
            self.task = _doer_task()
            self.chat = _bind_chat(
                self.task.doer, workspace=self.workspace, chat_id="stall-kick"
            )
            self.path = _transcript_path(self.chat)
            self.agent.add_tasks([self.task])
            self.clock.on_sleep(_AcceptOnlyScript(self.path))

        with it("should log kick before re-raising AIChatFault stall"):
            _expect_fault_kind(self.agent.run_next_task, "stall")
            expect(_log_kinds(self.session)).to(contain("kick"))
