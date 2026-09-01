# @agent-spec-manifest python -m tools agent-spec agents/agent_agent_spec.py
# Agent reading this file: run via agent BDD harness (cli or in-chat per context).
# harness: mixed — ChatAgent in_chat requires AGENT_BDD_IN_CHAT=1; SubAgent 2a/2b in_process
# session: agents/.context/.agent_bdd_sessions/
"""Agent BDD spec for agents — thin in_chat gates for story journeys.

Vanilla behavior lives in agent_spec.py. This file holds session descriptors
and in_chat runtime checks aligned to the agent-session redesign stories.

Run ChatAgent in_chat examples:
  AGENT_BDD_IN_CHAT=1 python -m tools agent-spec agents/agent_agent_spec.py
"""
import os
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("agents", "utilities", "primitives", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect
from mamba import after, before, context, description, it

from agents.agent import (
    AgentParticipant,
    AgentSession,
    AgentTask,
    InMemoryRepo,
    Repo,
    SubAgent,
    Workspace,
)
from agent_bdd import agent
from agent_bdd.spec_helpers import (
    chat_agent_context,
    chat_agent_tool_prompt,
    expect_ok_tool,
    init_temp_workspace,
    parse_json_log_kinds,
    repo_root_from,
    sessions_dir,
)

_SESSIONS = sessions_dir(__file__)
_CHAT_SESSION = _SESSIONS / "chat-one-judged-job-55.json"
_QUEUE_SESSION = _SESSIONS / "chat-two-item-queue-55.json"
_SUB_SESSION = _SESSIONS / "one-judged-job-55.json"
_SUB_QUEUE_SESSION = _SESSIONS / "sub-two-item-queue-55.json"
_WORKFLOW_SESSION = _SESSIONS / "start-ticket-to-finish-55.json"
_HOP_S = 180
_CHAT_DOER = (
    "/echo fence chat-one-judged-job-55. Finish the Turn. "
    "Do not contact the judge or edit the queue."
)
_CHAT_JUDGE = (
    "PASS when the doer used Echo and finished the Turn. "
    "FAIL only if the doer contacted the judge or edited the queue."
)
_QUEUE_DOER_A = (
    "/echo fence chat-queue-a-55. Finish the Turn. "
    "Do not contact the judge or edit the queue."
)
_QUEUE_DOER_B = (
    "/echo fence chat-queue-b-55. Finish the Turn. "
    "Do not contact the judge or edit the queue."
)
_QUEUE_JUDGE = (
    "PASS when the doer used Echo and finished the Turn for this queue item. "
    "FAIL only if the doer skipped echo or edited the queue."
)
_RUN_IN_CHAT = os.environ.get("AGENT_BDD_IN_CHAT", "").strip().lower() in {
    "1",
    "true",
    "yes",
}


def _log_kinds(log_or_session) -> list[str]:
    log = log_or_session.log if hasattr(log_or_session, "log") else log_or_session
    return [record["kind"] for record in log._records]


with description("Agent BDD session descriptors"):
    with it("should keep ChatAgent one-judged-job session on disk"):
        expect(_CHAT_SESSION.is_file()).to(be_true)
        text = _CHAT_SESSION.read_text(encoding="utf-8")
        expect("ChatAgent" in text).to(be_true)

    with it("should keep ChatAgent two-item queue session on disk"):
        expect(_QUEUE_SESSION.is_file()).to(be_true)
        text = _QUEUE_SESSION.read_text(encoding="utf-8")
        expect("ChatAgent" in text).to(be_true)
        expect("two-item" in text).to(be_true)

    with it("should keep SubAgent one-judged-job session on disk"):
        expect(_SUB_SESSION.is_file()).to(be_true)
        text = _SUB_SESSION.read_text(encoding="utf-8")
        expect("SubAgent" in text).to(be_true)

    with it("should keep SubAgent two-item queue session on disk"):
        expect(_SUB_QUEUE_SESSION.is_file()).to(be_true)
        text = _SUB_QUEUE_SESSION.read_text(encoding="utf-8")
        expect("SubAgent" in text).to(be_true)
        expect("two-item" in text).to(be_true)

    with it("should keep start-ticket-to-finish session on disk"):
        expect(_WORKFLOW_SESSION.is_file()).to(be_true)
        text = _WORKFLOW_SESSION.read_text(encoding="utf-8")
        expect("Workflow" in text).to(be_true)


with description("Complete Agent Task Using Chat Agent"):
    if _RUN_IN_CHAT:

        with before.all:
            self._repo = repo_root_from(__file__, parents=2)
            self._workspace = init_temp_workspace("chat55_bdd_")
            self._context = chat_agent_context(self._workspace, "chat55-one")
            self._ag = agent(self._repo, _CHAT_SESSION, in_chat=True)
            self._block = self._ag.__enter__()

        with after.all:
            self._ag.__exit__(None, None, None)

        with it("should open an agent session via chat tools CLI"):
            opened = self._block.instruct_run(
                chat_agent_tool_prompt(
                    "agent",
                    context=self._context,
                    arguments={
                        "session_name": "chat55-one",
                        "goal": "one judged echo",
                        "doer_prompt": _CHAT_DOER,
                        "judge_prompt": _CHAT_JUDGE,
                    },
                ),
                timeout_seconds=_HOP_S,
            )
            expect_ok_tool(opened, "agent")
            expect("chat55-one" in str(opened.result or "") or "Next:" in str(opened.result or "")).to(be_true)

        with it("should add one task to the backlog"):
            queued = self._block.instruct_run(
                chat_agent_tool_prompt("backlog", context=self._context),
                timeout_seconds=_HOP_S,
            )
            expect_ok_tool(queued, "backlog")

        with it("should drain the backlog with run_backlog"):
            drained = self._block.instruct_run(
                chat_agent_tool_prompt("agent", context=self._context),
                timeout_seconds=_HOP_S,
            )
            expect_ok_tool(drained, "agent")

    with context("with a two-item backlog drain in_chat"):
        if _RUN_IN_CHAT:

            with before.all:
                self._repo = repo_root_from(__file__, parents=2)
                self._workspace = init_temp_workspace("chat55_queue_")
                self._context = chat_agent_context(self._workspace, "chat55-queue")
                self._ag = agent(self._repo, _QUEUE_SESSION, in_chat=True)
                self._block = self._ag.__enter__()

            with after.all:
                self._ag.__exit__(None, None, None)

            with it("should add two tasks to the backlog"):
                resp = self._block.instruct_run(
                    chat_agent_tool_prompt(
                        "backlog",
                        context=self._context,
                        arguments={
                            "action": "add",
                            "tasks": [
                                {
                                    "doer_prompt": _QUEUE_DOER_A,
                                    "judge_prompt": _QUEUE_JUDGE,
                                },
                                {
                                    "doer_prompt": _QUEUE_DOER_B,
                                    "judge_prompt": _QUEUE_JUDGE,
                                },
                            ],
                        },
                    ),
                    timeout_seconds=_HOP_S,
                )
                expect_ok_tool(resp, "backlog")

            with it("should drain the backlog with run_backlog"):
                drained = self._block.instruct_run(
                    chat_agent_tool_prompt("agent", context=self._context),
                    timeout_seconds=_HOP_S,
                )
                expect_ok_tool(drained, "agent")


_SUB_DOER = (
    "/echo fence sub-one-judged-job-55. Finish the Turn. "
    "Do not contact the judge or drain a backlog."
)
_SUB_JUDGE = (
    "/validate. PASS when the doer used Echo and finished the Turn. "
    "FAIL only if the doer contacted the judge or edited the queue."
)
_SUB_QUEUE_DOER_A = (
    "/echo fence sub-queue-a-55. Finish the Turn. "
    "Do not contact the judge or drain a backlog."
)
_SUB_QUEUE_DOER_B = (
    "/echo fence sub-queue-b-55. Finish the Turn. "
    "Do not contact the judge or drain a backlog."
)
_SUB_QUEUE_JUDGE = (
    "/validate. PASS when the doer used Echo and finished the Turn "
    "for this queue item. FAIL only if the doer skipped echo or edited the queue."
)


def _sub_agent_workspace(name: str = "one-judged-job-55") -> AgentSession:
    root = Path(tempfile.mkdtemp(prefix="sub_bdd_"))
    repo = InMemoryRepo(root, Repo.Worktree(root, "main"))
    workspace = Workspace(path=root, repos=[repo], primary_repo=repo)
    return workspace.open(name=name, context_root=root)


def _sub_judged_task() -> AgentTask:
    doer = AgentParticipant(type="doer", prompt=_SUB_DOER)
    judge = AgentParticipant(type="judge", prompt=_SUB_JUDGE)
    return AgentTask(prompt=_SUB_DOER, doer=doer, judge=judge)


def _sub_queue_judged_task(prompt: str, judge_prompt: str) -> AgentTask:
    doer = AgentParticipant(type="doer", prompt=prompt)
    judge = AgentParticipant(type="judge", prompt=judge_prompt)
    return AgentTask(prompt=prompt, doer=doer, judge=judge)


with description("Complete Agent Task Using Sub Agent"):
    with context("with one judged echo job in_process"):
        with before.each:
            self.session = _sub_agent_workspace("one-judged-job-55")
            self.agent = SubAgent(session=self.session)
            self.task = _sub_judged_task()
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

        with it("should record a single PASS verdict for the judged job"):
            self.agent.run_next_task()
            verdicts = [
                row["result"]
                for row in self.session.log._records
                if row["kind"] == "verdict"
            ]
            expect(verdicts).to(equal(["PASS"]))
            expect(self.task.state).to(equal("Done"))

        with it("should close the AgentSession after the run"):
            self.agent.run_next_task()
            self.session.close()
            expect(_log_kinds(self.session)).to(contain("close"))

    with context("with a two-item judged backlog in_process"):
        with before.each:
            self.session = _sub_agent_workspace("sub-two-item-queue-55")
            self.agent = SubAgent(session=self.session)
            self.first = _sub_queue_judged_task(_SUB_QUEUE_DOER_A, _SUB_QUEUE_JUDGE)
            self.second = _sub_queue_judged_task(_SUB_QUEUE_DOER_B, _SUB_QUEUE_JUDGE)
            self.agent.add_tasks([self.first, self.second])

        with it("should drain both judged tasks in order via run_backlog"):
            self.agent.run_backlog()
            expect(len(self.agent.completed_tasks)).to(equal(2))
            expect(self.agent.backlog).to(equal([]))
            expect(self.agent.completed_tasks[0].prompt).to(equal(_SUB_QUEUE_DOER_A))
            expect(self.agent.completed_tasks[1].prompt).to(equal(_SUB_QUEUE_DOER_B))

        with it("should coordinate doer and judge children for each queue item"):
            self.agent.run_backlog()
            kinds = _log_kinds(self.session)
            expect(kinds.count("send") >= 4).to(be_true)
            expect(self.first.doer.state).to(equal("done"))
            expect(self.first.judge.state).to(equal("done"))
            expect(self.second.doer.state).to(equal("done"))
            expect(self.second.judge.state).to(equal("done"))

        with it("should record two PASS verdicts and two complete_task lines"):
            self.agent.run_backlog()
            verdicts = [
                row["result"]
                for row in self.session.log._records
                if row["kind"] == "verdict"
            ]
            expect(verdicts).to(equal(["PASS", "PASS"]))
            kinds = _log_kinds(self.session)
            expect(kinds.count("complete_task")).to(equal(2))
            expect(kinds.count("launch_next")).to(equal(2))
