"""BDD spec for harness/agent_tools/sub_agent."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from harness.agent_tools.sub_agent.fixtures import MarkedActionExample, MarkedToolExample
from harness.agent_tools.agent_tools import AgentToolSet
from harness.agent_tools.sub_agent.mark import SUB_AGENT_CALLER_PREAMBLE, marked_as_sub_agent
from harness.agent_tools.sub_agent.sub_agent import SubAgent
from mamba import context, description, it


with description("SubAgent toolset"):
    with context("with its tools listed"):
        with it("exposes sub_agent as instructions"):
            tool = AgentToolSet.instantiate(SubAgent).tools["sub_agent"]
            expect(tool.kind).to(equal("instructions"))

    with context("sub_agent instructions"):
        with it("tells the caller to launch a non-blocking sub-agent"):
            instructions = "\n".join(AgentToolSet.instantiate(SubAgent).tools["sub_agent"].prompt)
            expect(instructions).to(contain("run_in_background"))
            expect(instructions).to(contain("generalPurpose"))

        with it("includes the delegated instructions placeholder"):
            instructions = "\n".join(AgentToolSet.instantiate(SubAgent).tools["sub_agent"].prompt)
            expect(instructions).to(contain("{{instructions}}"))


with description("@subAgent mark"):
    with context("on @agent_tool"):
        with it("prepends delegation instructions to the tool description"):
            tool = MarkedToolExample().operations["run_check"]
            expect(tool.description).to(contain(SUB_AGENT_CALLER_PREAMBLE))
            expect(tool.description).to(contain("Run the focused check."))

        with it("marks the tool as launched on a sub-agent"):
            tool = MarkedToolExample().operations["run_check"]
            expect(marked_as_sub_agent(tool.callable)).to(equal(True))

    with context("on @agent_instructions"):
        with it("prepends delegation instructions when expanded"):
            expanded = MarkedActionExample().instructions["plan_work"].expand(
                {},
                {"task": "refactor auth"},
            )
            expect(expanded.instructions).to(contain(SUB_AGENT_CALLER_PREAMBLE))
            expect(expanded.instructions).to(contain("Plan work for refactor auth"))
            expect(expanded.instructions).to(contain("Break the task into steps."))

        with it("marks the instructions as launched on a sub-agent"):
            tool = MarkedActionExample().instructions["plan_work"]
            expect(marked_as_sub_agent(tool.callable)).to(equal(True))
