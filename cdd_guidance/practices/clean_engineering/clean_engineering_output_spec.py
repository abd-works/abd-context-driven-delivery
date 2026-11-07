"""A Clean Engineering practice writing the artifact for its fidelity."""
from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.model.drawio.drawio import Drawio
from harness.agent_tools.agent_tools import AgentInstructions


def _expanded(practice: CleanEngineering):
    return AgentInstructions.for_callable(CleanEngineering.generate_output, practice).expand({})


with description("a clean engineering practice writing its artifact"):
    with context("that works in markdown"):
        with before.each:
            self.practice = CleanEngineering(fidelity="model", format="markdown")

        with it("should say where the artifact goes"):
            expect(self.practice.generate_output()).to(equal("Artifact written under {session.path}/."))

        with it("should not ask for a draw.io render"):
            expect(_expanded(self.practice).tools).to(equal([]))

    with context("that works in draw.io"):
        with before.each:
            self.practice = CleanEngineering(fidelity="model", format="drawio")

        with it("should ask for the draw.io render"):
            expect(_expanded(self.practice).tools).to(equal(["render"]))

        with it("should render with its own draw.io toolset"):
            expect(isinstance(self.practice.drawio, Drawio)).to(equal(True))
