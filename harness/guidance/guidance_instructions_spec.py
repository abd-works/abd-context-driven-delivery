"""A guidance's own instructions tool, and how a guidance's tools are published and installed."""
from pathlib import Path, PurePosixPath

from expects import be_a, be_true, contain, equal, expect
from mamba import before, context, description, it

from harness.agent_tools.agent_tools import InstalledName
from harness.guidance.fixtures.sample_tool.sample_tool_host import SampleMcpGuidance, SamplePracticeWithFidelities
from harness.guidance.guidance_instructions import LISTED_INSTRUCTIONS_NOTE, GuidanceInstructions


class _LongGuidance(SampleMcpGuidance):
    """A guidance whose instructions tool is described by an overview of several paragraphs."""

    @property
    def overview(self) -> str:
        return "## Overview\n\nWhat this guidance is for.\n\nEvery rule the guidance holds."


class _ShortGuidance(SampleMcpGuidance):
    """A guidance whose instructions tool is described by an overview of one paragraph."""

    @property
    def overview(self) -> str:
        return "## Overview\n\nWhat this guidance is for."


with description("a guidance's own instructions tool"):
    with before.each:
        self.tool = _LongGuidance().tools["instructions"]

    with it("should be published as the guidance's whole instructions"):
        expect(self.tool).to(be_a(GuidanceInstructions))

    with it("should keep its whole overview as its description"):
        expect(self.tool.description).to(contain("Every rule the guidance holds."))

    with it("should list its overview's opening paragraph and say a call returns the rest"):
        expect(self.tool.listed_description).to(equal(f"What this guidance is for.\n\n{LISTED_INSTRUCTIONS_NOTE}"))

    with it("should be published under the guidance's slug and its own name"):
        expect(self.tool.mcp_name).to(equal(f"{self.tool.toolset.slug}.instructions"))

    with it("should be installed as the guidance's own, named after the guidance alone"):
        expect(self.tool.toolset.installed_as(self.tool).is_own).to(be_true)

    with context("with an overview of one paragraph"):
        with it("should list that paragraph alone"):
            expect(_ShortGuidance().tools["instructions"].listed_description).to(equal("What this guidance is for."))


with description("a fidelity a practice holds"):
    with before.each:
        self.practice = SamplePracticeWithFidelities(format="markdown")
        self.fidelity = next(iter(self.practice.fidelities))
        self.tool = self.fidelity.tools["instructions"]

    with it("should publish its instructions under its slug alone"):
        expect(self.tool.mcp_name).to(equal(self.fidelity.slug))

    with it("should install its files in its practice's folder, named after its slug"):
        expected = InstalledName(self.practice.install_folder, self.fidelity.slug, is_own=True)
        expect(self.fidelity.installed_as(self.tool)).to(equal(expected))

    with it("should be one of the parts its practice's instructions list"):
        expect(self.practice.listed_parts()).to(contain(self.fidelity))

    with context("and a tool of its other than its instructions"):
        with it("should be installed beside them, not as its own"):
            other = next(tool for tool in self.fidelity.tools.values() if not isinstance(tool, GuidanceInstructions))
            expect(self.fidelity.installed_as(other).is_own).to(equal(False))


with description("a practice"):
    with it("should install its files in its own folder, named after it"):
        practice = SamplePracticeWithFidelities(format="markdown")
        expect(practice.installed_as(practice.tools["instructions"])).to(equal(InstalledName(practice.install_folder, is_own=True)))


with description("where a practice places a declared path under a fidelity's root"):
    with before.each:
        self.practice = SamplePracticeWithFidelities(format="markdown")

    with it("should place it under the root"):
        placed = self.practice.placed_under(PurePosixPath("docs/map.md"), Path("billing"))
        expect(placed).to(equal(Path("billing/docs/map.md")))

    with context("that is a .context document, under a root inside .context"):
        with it("should land in that root itself, not in a .context within it"):
            placed = self.practice.placed_under(PurePosixPath(".context/map.md"), Path("harness/.context/sample"))
            expect(placed).to(equal(Path("harness/.context/sample/map.md")))

    with it("should take every file as production code"):
        expect(self.practice.is_production_code("billing/invoice_spec.py")).to(be_true)
