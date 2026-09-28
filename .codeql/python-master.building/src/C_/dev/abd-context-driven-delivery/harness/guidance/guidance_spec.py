"""BDD spec — context / practice / fidelity guidance read."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
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
            guidance = SampleGuidance(format="markdown")
            text = guidance.instructions
            expect(text).to(contain("sample preamble"))
            expect(text).to(contain("known prose for guidance in sample tool"))
            expect(text).to(contain("sample-rule-one"))
            expect(text).to(contain("## Shared rules"))
            expect(text).to(contain("active format template body for sample tool"))

        with it("should use overview as the skill and MCP copy for instructions"):
            guidance = SampleGuidance(format="markdown")
            copy = guidance.tools["instructions"].description
            expect(copy).to(equal(guidance.overview.strip()))
            expect(copy).not_to(contain("known prose for guidance in sample tool"))

        with it(
            "should expose instructions as one compound property not as a single markdown label"
        ):
            guidance = SampleGuidance(format="markdown")
            expect(guidance.instructions).not_to(equal(guidance.overview))
            expect(guidance.instructions).not_to(equal(guidance.guidance))
            expect(guidance.instructions).to(contain(guidance.overview.strip()))
            expect(guidance.instructions).to(contain(guidance.guidance.strip()))

    with context("with the rules collection and the rules markdown read"):
        with it("should keep parsed rules on rules and the section text on rules.markdown"):
            guidance = SampleGuidance(format="markdown")
            expect("sample-rule-one" in guidance.rules.entries).to(equal(True))
            expect(guidance.rules.markdown).to(contain("sample rule one"))

        with it("should inject rules markdown when the agent writes a matching path"):
            guidance = SampleGuidance(format="markdown")
            result = guidance.rules.inject_rules(
                {
                    "tool_name": "Write",
                    "tool_input": {"path": "pkg/foo_sample_bar.py"},
                }
            )
            expect(result.get("additional_context")).to(contain("sample rule one"))
            inject = type(guidance.rules).inject_rules
            expect(getattr(inject, "_echo", False)).to(equal(True))
            expect(getattr(inject, "_hook", False)).to(equal(True))
            expect(getattr(inject, "_hook_name", "")).to(equal("postToolUse"))
            from prompt_echo.prompt_echo import TOAST_NOTICE

            notice = (_REPO_ROOT / TOAST_NOTICE).read_text(encoding="utf-8")
            expect(notice).to(contain("chat edit"))
            expect(notice).to(contain("rules :"))
            expect(notice).to(contain("SampleGuidance"))

        with it("should list inject_rules on tools so hook install can enroll it"):
            guidance = SampleGuidance(format="markdown")
            expect("inject_rules" in guidance.tools).to(equal(True))
            expect(guidance.tools["inject_rules"].install_to_hook).to(equal(True))
            expect("inject_rules" in guidance.rules.tools).to(equal(True))

        with it("should rehost inject_rules on the practice so install enrolls CleanEngineering"):
            from practices.clean_engineering.clean_engineering import CleanEngineering

            guidance = CleanEngineering()
            expect(type(guidance.tools["inject_rules"].toolset).__name__).to(
                equal("CleanEngineering")
            )

        with it("should inject the matching fidelity rules when a practice file is written"):
            from practices.clean_engineering.clean_engineering import CleanEngineering
            from prompt_echo.prompt_echo import TOAST_NOTICE

            result = CleanEngineering().rules.inject_rules(
                {
                    "tool_name": "Write",
                    "tool_input": {
                        "path": "actions/validate/validate.py",
                    },
                }
            )
            text = result.get("additional_context") or ""
            expect(text).to(contain("keep-operations-small-focused"))
            expect(text).to(contain("hide-inner-details"))
            notice = (_REPO_ROOT / TOAST_NOTICE).read_text(encoding="utf-8")
            expect(notice).to(contain("chat edit"))
            expect(notice).to(contain("code"))
            expect(notice).to(contain("model"))

        with it("should inject after Read using the parented practice rules collection"):
            from practices.clean_engineering.clean_engineering import CleanEngineering

            result = CleanEngineering().rules.inject_rules(
                {
                    "tool_name": "Read",
                    "tool_input": {"path": "actions/validate/validate.py"},
                }
            )
            expect(result.get("additional_context") or "").to(
                contain("keep-operations-small-focused")
            )

        with it("should inject matching code rules for an absolute path in any folder"):
            from practices.clean_engineering.clean_engineering import CleanEngineering

            result = CleanEngineering().rules.inject_rules(
                {
                    "tool_input": {
                        "path": r"C:\dev\other-repo\src\cart.py",
                    }
                }
            )
            expect(result.get("additional_context") or "").to(
                contain("keep-operations-small-focused")
            )

        with it("should not inject rules markdown when the agent writes a non-matching path"):
            guidance = SampleGuidance(format="markdown")
            result = guidance.rules.inject_rules(
                {
                    "tool_name": "Write",
                    "tool_input": {"path": "pkg/other.py"},
                }
            )
            expect(result).to(equal({}))


with description("a context tool module with one domain markdown file named for the context tool") as self:
    with before.each:
        self.guidance = SamplePracticeGuidance(format="markdown")

    with context("with the overview property read"):
        with it("should return the Overview preamble"):
            expect(self.guidance.overview).to(contain("sample preamble"))

    with context("with the guidance property read"):
        with it("should return the Guidance section body only"):
            expect(self.guidance.guidance).to(contain("known prose for guidance in sample tool"))
            expect(self.guidance.guidance).not_to(contain("sample preamble"))

    with context("with the instructions property read"):
        with it("should join context, guidance, formatted rules, and the template for the active format"):
            text = self.guidance.instructions
            expect(text).to(contain("sample preamble"))
            expect(text).to(contain("known prose for guidance in sample tool"))
            expect(text).to(contain("active format template body for sample tool"))
            expect(text).to(contain("sketch guidance body only"))

    with context("with a templates folder beside the module"):
        with context("with template files such as slug-templates and slug-sketch inside the folder"):
            with context("with the templates property read"):
                with it("should return the active format template body"):
                    expect(self.guidance.templates).to(contain("active format template body for sample tool"))

            with context("with one format key selected"):
                with it("should return the file content at the mapped path"):
                    expect(self.guidance.instructions).to(contain("active format template body for sample tool"))


with description("a context tool module with section files and subsection folders named for the context tool") as self:
    with before.each:
        self.guidance = SplitPracticeGuidance(format="markdown")

    with context("with the overview property read"):
        with it("should return the Overview preamble"):
            expect(self.guidance.overview).to(contain("split preamble from contexts file"))

    with context("with the guidance property read"):
        with it("should return the Guidance section body only"):
            expect(self.guidance.guidance).to(contain("split guidance section body only"))

    with context("with a Shared rules section containing scanner bullets"):
        with context("with the rules property read"):
            with it("should parse bullets into a rules collection"):
                expect("split-rule" in self.guidance.rules.entries).to(equal(True))


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

    with context("with the class marked as a toolset collection"):
        with it("should be a ToolSetCollection without subclassing it in the source"):
            from harness.agent_tools.agent_tools import ToolSetCollection

            expect(isinstance(self.collection, ToolSetCollection)).to(equal(True))
            expect(getattr(type(self.collection), "_is_toolset_collection", False)).to(equal(True))
            from harness.markdown import MarkdownCollection

            expect(isinstance(self.collection, MarkdownCollection)).to(equal(True))

    with context("with the instructions property read on the collection"):
        with it("should list instructions on the collection tools"):
            expect("instructions" in self.collection.tools).to(equal(True))
            expect(self.collection.tools["instructions"].install_to_mcp).to(equal(True))

        with it("should join each child instructions string"):
            text = self.collection.instructions
            expect(text).to(contain("sketch guidance body only"))
            expect(text).to(contain("spec guidance body only"))

        with it("should return one child's instructions from that child"):
            text = self.collection["sketch"].instructions
            expect(text).to(contain("sketch guidance body only"))
            expect(text).not_to(contain("spec guidance body only"))

    with context("with the rules property read on the collection"):
        with it("should return a rules collection keyed by each child key"):
            expect("sketch" in self.collection.rules.entries).to(equal(True))

        with it("should keep each child's rules under that child's key"):
            child_rules = self.collection.rules.entries["sketch"]
            expect("sketch-rule" in child_rules.entries).to(equal(True))

        with it("should return every child rule's validate instructions in one shot"):
            expect(self.collection.rules.validate).to(contain("sketch-rule"))


with description("practice guidance with fidelities examples and templates beside the module") as self:
    with before.each:
        self.guidance = SamplePracticeWithFidelities(format="markdown")

    with context("with the instructions property read on practice guidance"):
        with it(
            "should join this practice's own instructions with the fidelities collection instructions"
        ):
            text = self.guidance.instructions
            expect(text).to(contain("sample preamble"))
            expect(text).to(contain("sketch guidance body only"))
            expect(text).to(contain("spec guidance body only"))

        with it("should not inline examples into instructions"):
            expect(self.guidance.instructions).not_to(contain("example file not inlined"))

    with context("with the examples property read on practice guidance"):
        with it("should return examples folder content as a separate property not inside instructions"):
            expect(self.guidance.examples).to(contain("example file not inlined"))

    with context("with a markdown-backed property read as HTML on practice guidance"):
        with it("should return HTML formatted from that property extract"):
            rendered = Markdown.from_label(self.guidance, "guidance").html()
            expect(str(rendered)).to(contain("<p>"))

    with context("with fidelity set at invoke on practice guidance"):
        with it("should resolve active format from the named fidelity default format"):
            first = self.guidance.fidelities
            first.current = first["sketch"]
            self.guidance.format = first["sketch"].default_format or self.guidance.format
            expect(self.guidance.fidelities is first).to(equal(True))
            expect(self.guidance.toolset_collections).to(equal([first]))
            expect(self.guidance.fidelities.current.fidelity).to(equal("sketch"))


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

            text = CleanEngineering(fidelity="model", format="markdown").templates
            expect(text).to(contain("clean_engineering markdown template"))

        with it("should load that same practice-named template for every fidelity"):
            from practices.clean_engineering.clean_engineering import CleanEngineering

            code = CleanEngineering(fidelity="code", format="markdown").templates
            model = CleanEngineering(fidelity="model", format="markdown").templates
            expect(model).to(equal(code))

    with context("with no fidelity-named file and no practice-named template"):
        with it("should return no template"):
            from practices.ddd.ddd import Ddd

            expect(Ddd(fidelity="tactics", format="python").templates).to(equal(""))
            expect(Ddd(fidelity="building_blocks", format="markdown").templates).to(
                equal("")
            )
