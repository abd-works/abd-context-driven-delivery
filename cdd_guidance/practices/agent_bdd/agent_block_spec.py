"""BDD spec for the agent a spec drives: the steps every agent block takes, whichever agent answers."""

import os
import shutil
import tempfile
from pathlib import Path

from expects import be_true, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from cdd_guidance.practices.agent_bdd.agent_bdd_common import AgentResult
from cdd_guidance.practices.agent_bdd.agent import agent
from cdd_guidance.practices.agent_bdd.agent_block import AgentBlock
from cdd_guidance.practices.agent_bdd.agent_chat_bdd import ChatAgentBlock
from cdd_guidance.practices.agent_bdd.agent_cli_bdd import AGENT_RUNS_OFF, AgentRunsOff


class ScriptedAgentBlock(AgentBlock):
    """The agent is another process; this one answers every prompt with a fixed reply, and its judge with a verdict."""

    reply = "a driving log for the trip to the courthouse"
    verdict = '{"verdict": "PASS", "reason": "it is a driving log"}'

    def _answer(self, prefix, prompt, timeout_seconds):
        return AgentResult(exit_code=0, text=self.reply, stderr="", elapsed_seconds=0.0)

    def _judge_answer(self, launch_prompt, timeout_seconds):
        return AgentResult(exit_code=0, text=self.verdict, stderr="", elapsed_seconds=0.0)


class RefusingJudgeBlock(ScriptedAgentBlock):
    verdict = '{"verdict": "FAIL", "reason": "it is a spec sheet"}'


with description("an agent a spec drives") as self:
    with before.each:
        self.workspace = Path(tempfile.mkdtemp(prefix="cdd-agent-block-"))
        self.session_file = self.workspace / ".agent_bdd_sessions" / "trip.json"

    with after.each:
        shutil.rmtree(self.workspace, ignore_errors=True)

    with context("that is opened in chat"):
        with it("should be the in-chat agent"):
            with agent(self.workspace, self.session_file, in_chat=True) as run:
                expect(isinstance(run, ChatAgentBlock)).to(be_true)

    with context("that is opened on the agent command line while agent runs are off"):
        with it("should refuse to start, naming the setting that turned agent runs off"):
            previous = os.environ.get(AGENT_RUNS_OFF)
            os.environ[AGENT_RUNS_OFF] = "1"
            try:
                expect(lambda: agent(self.workspace, self.session_file, in_chat=False).__enter__()).to(
                    raise_error(AgentRunsOff, contain(AGENT_RUNS_OFF))
                )
            finally:
                os.environ.pop(AGENT_RUNS_OFF) if previous is None else os.environ.__setitem__(AGENT_RUNS_OFF, previous)

    with context("that is given a step"):
        with before.each:
            with ScriptedAgentBlock.opened(self.workspace, self.session_file) as run:
                self.result = run.instruct("Write a driving log for one trip.")

        with it("should answer with the agent's reply"):
            expect(self.result.text).to(equal(ScriptedAgentBlock.reply))

        with it("should keep the prompt beside the session"):
            prompt = self.session_file.parent / "logs" / "trip" / "instruct-001-setup-prompt.txt"
            expect(prompt.read_text(encoding="utf-8")).to(equal("Write a driving log for one trip."))

    with context("that judges output the judge passes"):
        with it("should return the verdict"):
            with ScriptedAgentBlock.opened(self.workspace, self.session_file) as run:
                expect(run.ai_judge("a driving log", "It is a driving log.").passed()).to(be_true)

    with context("that judges output the judge fails"):
        with it("should fail the spec with the judge's reason"):
            with RefusingJudgeBlock.opened(self.workspace, self.session_file) as run:
                expect(lambda: run.ai_judge("a spec sheet", "It is a driving log.")).to(
                    raise_error(AssertionError, "ai_judge FAIL - it is a spec sheet")
                )

    with context("that generates against a pass fixture"):
        with it("should return the artifact it judged"):
            with ScriptedAgentBlock.opened(self.workspace, self.session_file) as run:
                expect(run.generate_and_judge("examples/driving-log.md")).to(contain("driving log"))
