"""BDD spec for harness/agent_tools/sub_agent."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from harness.agent_tools.sub_agent.fixtures import MarkedActionExample, MarkedToolExample
from harness.agent_tools.sub_agent.mark import SUB_AGENT_CALLER_PREAMBLE
from harness.agent_tools.sub_agent.sub_agent import SubAgent
from mamba import context, description, it


with description("SubAgent toolset"):
    with context("manifest signature"):
        with it("exposes sub_agent as an action"):
            entry = SubAgent.manifest.signature["sub_agent"]
            expect(entry["kind"]).to(equal("action"))

    with context("sub_agent instructions"):
        with it("tells the caller to launch a non-blocking sub-agent"):
            instructions = SubAgent.manifest.signature["sub_agent"]["instructions"]
            expect(instructions).to(contain("run_in_background"))
            expect(instructions).to(contain("generalPurpose"))

        with it("includes the delegated instructions placeholder"):
            instructions = SubAgent.manifest.signature["sub_agent"]["instructions"]
            expect(instructions).to(contain("{{instructions}}"))


with description("@subAgent mark"):
    with context("on @agent_tool"):
        with it("prepends delegation instructions to the tool description"):
            tool = MarkedToolExample().operations["run_check"]
            expect(tool.description).to(contain(SUB_AGENT_CALLER_PREAMBLE))
            expect(tool.description).to(contain("Run the focused check."))

        with it("exposes sub_agent kind in the manifest"):
            entry = MarkedToolExample.manifest.signature["run_check"]
            expect(entry["kind"]).to(equal("sub_agent"))
            expect(entry["launch"]).to(equal("non_blocking"))
            expect(entry["returns"]).to(equal("str"))

    with context("on @agent_instructions"):
        with it("prepends delegation instructions when expanded"):
            expanded = MarkedActionExample().instructions["plan_work"].expand(
                {},
                {"task": "refactor auth"},
            )
            expect(expanded.instructions).to(contain(SUB_AGENT_CALLER_PREAMBLE))
            expect(expanded.instructions).to(contain("Plan work for refactor auth"))
            expect(expanded.instructions).to(contain("Break the task into steps."))

        with it("exposes sub_agent kind in the manifest"):
            entry = MarkedActionExample.manifest.signature["plan_work"]
            expect(entry["kind"]).to(equal("sub_agent"))
            expect(entry["launch"]).to(equal("non_blocking"))
