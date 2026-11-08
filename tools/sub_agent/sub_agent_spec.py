"""BDD spec for tools/sub_agent and the @subAgent annotation."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from tools.sub_agent.fixtures.annotated_examples import AnnotatedActionExample, AnnotatedToolExample
from harness.agent_tools.agent_tools import AgentToolSet
from harness.agent_tools.agent_tools import SUB_AGENT_CALLER_PREAMBLE, SubAgentAnnotation
from tools.sub_agent.sub_agent import SubAgent
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


with description("@subAgent annotation"):
    with context("on @agent_tool"):
        with it("prepends delegation instructions to the tool description"):
            tool = AnnotatedToolExample().operations["run_check"]
            expect(tool.description).to(contain(SUB_AGENT_CALLER_PREAMBLE))
            expect(tool.description).to(contain("Run the focused check."))

        with it("annotates the tool as launched on a sub-agent"):
            tool = AnnotatedToolExample().operations["run_check"]
            expect(SubAgentAnnotation.annotates(tool.callable)).to(equal(True))

    with context("on @agent_instructions"):
        with it("prepends delegation instructions when expanded"):
            expanded = AnnotatedActionExample().instructions["plan_work"].expand(
                {"task": "refactor auth"},
            )
            expect(expanded.instructions).to(contain(SUB_AGENT_CALLER_PREAMBLE))
            expect(expanded.instructions).to(contain("Plan work for refactor auth"))
            expect(expanded.instructions).to(contain("Break the task into steps."))

        with it("annotates the instructions as launched on a sub-agent"):
            tool = AnnotatedActionExample().instructions["plan_work"]
            expect(SubAgentAnnotation.annotates(tool.callable)).to(equal(True))
