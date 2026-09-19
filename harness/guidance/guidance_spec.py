"""BDD spec — context / practice / fidelity guidance read."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_below, contain, equal, expect
from mamba import before, context, description, it

from harness.guidance.fixtures.sample_tool.sample_tool_host import (
    SampleGuidance,
    SamplePracticeGuidance,
    SamplePracticeWithFidelities,
)
from harness.guidance.fixtures.split_tool.split_tool import SplitPracticeGuidance
from harness.markdown import HTML, Markdown


with description("context guidance"):
    with context("with the instructions property read"):
        with it(
            "should join context, guidance, formatted rules, and the template for the active format"
        ):
            host = SampleGuidance(format="markdown")
            text = host.instructions
            expect(text).to(contain("sample preamble"))
            expect(text).to(contain("known prose for guidance in sample tool"))
            expect(text).to(contain("sample-rule-one"))
            expect(text).to(contain("## Shared rules"))
            expect(text).to(contain("active format template body for sample tool"))

        with it("should publish the overview as the prompt message"):
            host = SampleGuidance(format="markdown")
            expect(host.prompt_message).to(equal(host.overview.strip()))
            expect(host.prompt_message).not_to(contain("known prose for guidance in sample tool"))

        with it(
            "should expose instructions as one compound property not as a single markdown label"
        ):
            host = SampleGuidance(format="markdown")
            expect(host.instructions).not_to(equal(host.overview))
            expect(host.instructions).not_to(equal(host.guidance))
            expect(host.instructions).to(contain(host.overview.strip()))
            expect(host.instructions).to(contain(host.guidance.strip()))

    with context("with the rules collection and the rules markdown read"):
        with it("should keep parsed rules on rules and the section text on rules_markdown"):
            host = SampleGuidance(format="markdown")
            expect("sample-rule-one" in host.rules.entries).to(equal(True))
            expect(host.rules_markdown).to(contain("sample rule one"))

        with it("should inject rules markdown when the agent writes a matching path"):
            host = SampleGuidance(format="markdown")
            result = host.inject_rules(
                {
                    "tool_name": "Write",
                    "tool_input": {"path": "pkg/foo_sample_bar.py"},
                }
            )
            expect(result.get("additional_context")).to(contain("sample rule one"))
            expect(getattr(type(host).inject_rules, "_echo", False)).to(equal(True))
            from installation.hooks.prompt_echo.prompt_echo import TOAST_NOTICE

            notice = (_REPO_ROOT / TOAST_NOTICE).read_text(encoding="utf-8")
            expect(notice).to(contain("Rules"))
            expect(notice).to(contain("sample-tool"))

        with it("should not inject rules markdown when the agent writes a non-matching path"):
            host = SampleGuidance(format="markdown")
            result = host.inject_rules(
                {
                    "tool_name": "Write",
                    "tool_input": {"path": "pkg/other.py"},
                }
            )
            expect(result).to(equal({}))


with description("a context tool module with one domain markdown file named for the context tool") as self:
    with before.each:
        self.host = SamplePracticeGuidance(format="markdown")

    with context("with the overview property read"):
        with it("should return the Overview preamble"):
            expect(self.host.overview).to(contain("sample preamble"))

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
                with it("should return the active format template body"):
                    expect(self.host.templates).to(contain("active format template body for sample tool"))

            with context("with one format key selected"):
                with it("should return the file content at the mapped path"):
                    expect(self.host.instructions).to(contain("active format template body for sample tool"))


with description("a context tool module with section files and subsection folders named for the context tool") as self:
    with before.each:
        self.host = SplitPracticeGuidance(format="markdown")

    with context("with the overview property read"):
        with it("should return the Overview preamble"):
            expect(self.host.overview).to(contain("split preamble from contexts file"))

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

    with context("with a Stage attribute on the fidelity markdown"):
        with it("should set stage on that fidelity guidance"):
            expect(self.sketch.stage).to(equal("discovery"))
            expect(self.spec.stage).to(equal("specification"))

    with context("with the guidance property read on fidelity guidance"):
        with it("should return Guidance under that fidelity name only"):
            expect(self.sketch.guidance).to(contain("sketch guidance body only"))
            expect(self.sketch.guidance).not_to(contain("spec guidance body only"))

    with context("with the rules property read on fidelity guidance"):
        with it("should return a rules collection for that fidelity name only"):
            expect("sketch-rule" in self.sketch.rules.entries).to(equal(True))

        with it("should not include rules from sibling fidelity sections"):
            expect("spec-rule" in self.sketch.rules.entries).to(equal(False))

    with context("with the instructions property read on fidelity guidance"):
        with it("should include the parent overview, guidance, and shared rules"):
            text = self.sketch.instructions
            expect(text).to(contain("sample preamble"))
            expect(text).to(contain("known prose for guidance in sample tool"))
            expect(text).to(contain("sample-rule-one"))

        with it("should still include this fidelity's own guidance and rules"):
            expect(self.sketch.instructions).to(contain("sketch guidance body only"))
            expect(self.sketch.instructions).to(contain("sketch-rule"))
            expect(self.sketch.instructions).to(contain("#### Rules"))

        with it("should put the fidelity template under a Template heading"):
            from practices.stories.stories import Stories

            story_map = Stories(fidelity="story_map").fidelities.entries["story_map"]
            text = story_map.instructions
            expect(text).to(contain("#### Template"))
            expect(text.index("#### Template")).to(be_below(text.index("Story Map")))

    with context("with two fidelities declared shallower before deeper in the collection"):
        with context("with the instructions property read on the deeper fidelity guidance"):
            with it("should not include prior fidelity sections in the overview"):
                expect(self.spec.overview).not_to(contain("sketch guidance body only"))
                expect(self.spec.instructions).not_to(contain("sketch guidance body only"))

            with it("should not include later fidelity sections or sibling templates"):
                expect(self.sketch.overview).not_to(contain("spec guidance body only"))

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
            "should join this practice's own context, guidance, rules, and template without inlining fidelity bodies"
        ):
            text = self.host.instructions
            expect(text).to(contain("sample preamble"))
            expect(text).not_to(contain("sketch guidance body only"))
            expect(text).not_to(contain("spec guidance body only"))

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
            self.host.fidelities.current = self.host.fidelities["sketch"]
            self.host.format = self.host.fidelities["sketch"].default_format or self.host.format
            expect(self.host.fidelities.current.fidelity).to(equal("sketch"))


with description("practice and fidelity template files"):
    with context("with a fidelity-named file under templates/{format}"):
        with it("should load that file"):
            from practices.stories.stories import Stories

            text = Stories(fidelity="story_map", format="markdown").templates
            expect(text).to(contain("Story Map"))
            expect(text).not_to(contain("Stories sketch"))

    with context("with no fidelity-named file"):
        with it("should load the practice-named template"):
            from practices.clean_engineering.clean_engineering import CleanEngineering

            text = CleanEngineering(fidelity="modules", format="markdown").templates
            expect(text).to(contain("clean_engineering markdown template"))

        with it("should load that same practice-named template for every fidelity"):
            from practices.clean_engineering.clean_engineering import CleanEngineering

            modules = CleanEngineering(fidelity="modules", format="markdown").templates
            model = CleanEngineering(fidelity="model", format="markdown").templates
            expect(model).to(equal(modules))

    with context("with no fidelity-named file and no practice-named template"):
        with it("should return no template"):
            from practices.ddd.ddd import Ddd

            expect(Ddd(fidelity="tactics", format="python").templates).to(equal(""))
            expect(Ddd(fidelity="building_blocks", format="markdown").templates).to(
                equal("")
            )
