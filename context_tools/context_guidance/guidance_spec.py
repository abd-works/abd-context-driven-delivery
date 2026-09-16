"""BDD spec — context / practice / fidelity guidance read."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("context_tools", "primitives", "utilities"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import before, context, description, it

from context_tools.context_guidance.fixtures.sample_tool.sample_tool_host import (
    SampleContextGuidance,
    SamplePracticeGuidance,
    SamplePracticeWithFidelities,
)
from context_tools.context_guidance.fixtures.split_tool.split_tool import SplitPracticeGuidance
from primitives.markdown import HTML, Markdown


with description("context guidance"):
    with context("with the instructions property read"):
        with it(
            "should join context, guidance, formatted rules, and the template for the active format"
        ):
            host = SampleContextGuidance(format="markdown")
            text = host.instructions
            expect(text).to(contain("sample preamble"))
            expect(text).to(contain("known prose for guidance in sample tool"))
            expect(text).to(contain("sample-rule-one"))
            expect(text).to(contain("active format template body for sample tool"))

        with it(
            "should expose instructions as one compound property not as a single markdown label"
        ):
            host = SampleContextGuidance(format="markdown")
            expect(host.instructions).not_to(equal(host.context))
            expect(host.instructions).not_to(equal(host.guidance))
            expect(host.instructions).to(contain(host.context.strip()))
            expect(host.instructions).to(contain(host.guidance.strip()))


with description("a context tool module with one domain markdown file named for the context tool") as self:
    with before.each:
        self.host = SamplePracticeGuidance(format="markdown")

    with context("with the context property read"):
        with it("should return the Contexts preamble"):
            expect(self.host.context).to(contain("sample preamble"))

    with context("with the guidance property read"):
        with it("should return the Guidance section body only"):
            expect(self.host.guidance).to(contain("known prose for guidance in sample tool"))
            expect(self.host.guidance).not_to(contain("sample preamble"))

    with context("with the instructions property read"):
        with it("should join context, guidance, formatted rules, and the template for the active format"):
            text = self.host.instructions
            expect(text).to(contain("sample preamble"))
            expect(text).to(contain("known prose for guidance in sample tool"))
            expect(text).to(contain("active format template body for sample tool"))
            expect(text).not_to(contain("sketch guidance body only"))

    with context("with a templates folder beside the module"):
        with context("with template files such as slug-templates and slug-sketch inside the folder"):
            with context("with the templates property read"):
                with it("should map each format key to a relative path under templates"):
                    expect(self.host.templates.get("markdown")).to(contain("templates/"))

            with context("with one format key selected"):
                with it("should return the file content at the mapped path"):
                    expect(self.host.instructions).to(contain("active format template body for sample tool"))


with description("a context tool module with section files and subsection folders named for the context tool") as self:
    with before.each:
        self.host = SplitPracticeGuidance(format="markdown")

    with context("with the context property read"):
        with it("should return the Contexts preamble"):
            expect(self.host.context).to(contain("split preamble from contexts file"))

    with context("with the guidance property read"):
        with it("should return the Guidance section body only"):
            expect(self.host.guidance).to(contain("split guidance section body only"))

    with context("with a Shared rules section containing scanner bullets"):
        with context("with the rules property read"):
            with it("should parse bullets into a rules collection"):
                expect("split-rule" in self.host.rules.entries).to(equal(True))


with description("a context tool module with one domain markdown file named for the context tool and fidelity sections") as self:
    with before.each:
        self.practice = SamplePracticeWithFidelities(format="markdown")
        self.sketch = self.practice.fidelities.entries["sketch"]
        self.spec = self.practice.fidelities.entries["spec"]

    with context("with the guidance property read on fidelity guidance"):
        with it("should return Guidance under that fidelity name only"):
            expect(self.sketch.guidance).to(contain("sketch guidance body only"))
            expect(self.sketch.guidance).not_to(contain("spec guidance body only"))

    with context("with the rules property read on fidelity guidance"):
        with it("should return a rules collection for that fidelity name only"):
            expect("sketch-rule" in self.sketch.rules.entries).to(equal(True))

        with it("should not include rules from sibling fidelity sections"):
            expect("spec-rule" in self.sketch.rules.entries).to(equal(False))

    with context("with two fidelities declared shallower before deeper in the collection"):
        with context("with the instructions property read on the deeper fidelity guidance"):
            with it("should include prior fidelity sections in context in declaration order"):
                expect(self.spec.context).to(contain("sketch guidance body only"))

            with it("should not include later fidelity sections or sibling templates"):
                expect(self.sketch.context).not_to(contain("spec guidance body only"))

        with context("with a markdown-backed property read as HTML on the deeper fidelity guidance"):
            with it("should return HTML formatted from that fidelity section body"):
                rendered = HTML.from_markdown(self.spec.guidance)
                expect(str(rendered)).to(contain("<p>"))
                expect(str(rendered)).to(contain("spec guidance body only"))

        with context("with the rules property read on the deeper fidelity guidance"):
            with it("should match the same bullets already formatted into fidelity instructions"):
                expect(self.spec.instructions).to(contain("spec-rule"))


with description("a guidance collection of context guidance children") as self:
    with before.each:
        self.practice = SamplePracticeWithFidelities(format="markdown")
        self.collection = self.practice.fidelities

    with context("with the instructions property read on the collection"):
        with it("should join each child instructions string in declaration order"):
            text = self.collection.instructions
            expect(text.index("sketch guidance")).to(equal(text.find("sketch guidance")))
            expect(text).to(contain("sketch guidance body only"))
            expect(text).to(contain("spec guidance body only"))

    with context("with the rules property read on the collection"):
        with it("should return a rules collection keyed by each child key"):
            expect("sketch" in self.collection.rules.entries).to(equal(True))

        with it("should keep each child's rules under that child's key"):
            child_rules = self.collection.rules.entries["sketch"]
            expect("sketch-rule" in child_rules.entries).to(equal(True))

        with it("should return every child rule's validate instructions in one shot"):
            expect(self.collection.rules.validate()).to(contain("sketch-rule"))


with description("practice guidance with fidelities examples and templates beside the module") as self:
    with before.each:
        self.host = SamplePracticeWithFidelities(format="markdown")

    with context("with the instructions property read on practice guidance"):
        with it(
            "should join context guidance instructions with each fidelity instructions in declaration order sketch first"
        ):
            text = self.host.instructions
            expect(text.find("sketch guidance") < text.find("spec guidance")).to(equal(True))

        with it("should not inline examples into instructions"):
            expect(self.host.instructions).not_to(contain("example file not inlined"))

    with context("with the examples property read on practice guidance"):
        with it("should return examples folder content as a separate property not inside instructions"):
            expect(self.host.examples).to(contain("example file not inlined"))

    with context("with a markdown-backed property read as HTML on practice guidance"):
        with it("should return HTML formatted from that property extract"):
            rendered = Markdown.from_label(self.host, "guidance").html()
            expect(str(rendered)).to(contain("<p>"))

    with context("with fidelity set at invoke on practice guidance"):
        with it("should resolve active format from the named fidelity default format"):
            self.host.fidelity = "sketch"
            self.host.format = self.host.fidelities.entries["sketch"].default_format or self.host.format
            expect(self.host.fidelity).to(equal("sketch"))
