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
if _agents not in sys.path:
    sys.path.insert(0, _agents)

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

from agent.agent import Agent, AgentParticipant, AgentSession, AgentTask


def _open_session(name: str = "agent-spec") -> AgentSession:
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


def _log_kinds(log) -> list[str]:
    return [record["kind"] for record in log._records]


def _verdict_results(log) -> list[str]:
    results: list[str] = []
    for record in log._records:
        if record["kind"] != "verdict":
            continue
        results.append(record["result"])
    return results


with description("Complete Agent Task"):
    with context("with an Agent bound to an open AgentSession"):
        with before.each:
            self.session = _open_session("inc1")
            self.agent = Agent(session=self.session)

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
            self.session = _open_session("inc2")
            self.agent = Agent(session=self.session)

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
                    with context("with fails still under the limit"):
                        with before.each:
                            self.agent._stub_verdicts.replace(["FAIL", "PASS"])

                        with it("should kick the doer agent or tell it to retry"):
                            self.agent.run_next_task()
                            expect(_log_kinds(self.session.log)).to(contain("kick"))

                        with it(
                            "the doer runtime should rerun the task according to the prompt"
                        ):
                            self.agent.run_next_task()
                            send_doer = [
                                record
                                for record in self.session.log._records
                                if record["kind"] == "send"
                                and record["participant"] == "doer"
                            ]
                            expect(len(send_doer) >= 2).to(be_true)
                            expect(self.task.state).to(equal("Done"))
                            expect(_verdict_results(self.session.log)).to(
                                equal(["FAIL", "PASS"])
                            )

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
                        self.agent._stub_human_feedback.replace(["please fix"])
                        self.agent._stub_verdicts.replace(["PASS", "PASS"])

                    with it("should record the feedback on the session log"):
                        self.agent.run_next_task()
                        expect(_log_kinds(self.session.log)).to(
                            contain("human_feedback")
                        )

                    with it("should kick the doer agent or tell it to retry"):
                        self.agent.run_next_task()
                        expect(_log_kinds(self.session.log)).to(contain("kick"))
                        expect(self.task.state).to(equal("Done"))
