"""BDD spec — co-located markdown extract and HTML."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_none, contain, equal, expect
from mamba import before, context, description, it

from harness.guidance.fixtures.other_tool.other_tool_host import OtherTool
from harness.guidance.fixtures.sample_tool.sample_tool_host import (
    SamplePracticeGuidance,
    SampleTool,
)
from harness.markdown import AssetLocator, HTML, Markdown, bind_yaml, canonical_format

_CLEAN_ENGINEERING_DIR = _REPO_ROOT / "practices" / "clean_engineering"
_STORIES_DIR = _REPO_ROOT / "practices" / "stories"


with description("a co-located markdown file beside the module"):
    with context("with a section heading that matches a property label"):
        with context("with a string property on Guidance backed by that section"):
            with it("should return the section body when the property is read"):
                instance = SampleTool()
                text = instance.guidance
                expect(text).to(contain("known prose for guidance in sample tool"))
                expect(text).not_to(contain("sample preamble"))

    with context("with known prose written in the module markdown file for that label"):
        with context("with the property read on Guidance in that module"):
            with it("should return that prose"):
                instance = SampleTool()
                expect(instance.guidance).to(contain("known prose for guidance in sample tool"))

        with context("with an identically named section in a different module folder"):
            with it(
                "should not return prose from the other module file when the class belongs to this module"
            ):
                instance = SampleTool()
                other = OtherTool()
                expect(instance.guidance).to(contain("known prose for guidance in sample tool"))
                expect(instance.guidance).not_to(contain("prose from the other module only"))
                expect(other.guidance).to(contain("prose from the other module only"))
                expect(other.guidance).not_to(contain("known prose for guidance in sample tool"))

    with context("with a markdown-backed string property"):
        with context("with that property read as HTML"):
            with it("should return HTML formatted from that section body"):
                instance = SampleTool()
                rendered = Markdown.from_label(instance, "guidance").html()
                expect(type(rendered)).to(equal(HTML))
                expect(str(rendered)).to(contain("known prose for guidance in sample tool"))
                expect(str(rendered)).to(contain("<p>"))


with description("a templates folder beside the module"):
    with context("with a produce file named for the domain and a markdown extension"):
        with it("should map the markdown format key not the templates filename stem"):
            instance = SamplePracticeGuidance(format="markdown")
            expect(canonical_format("md")).to(equal("markdown"))
            expect(instance.templates).to(contain("active format template body for sample tool"))


with description("an asset locator"):
    with context("that locates shared examples on a CleanEngineering"):
        with before.each:
            class _YamlSubject:
                module_dir = _CLEAN_ENGINEERING_DIR
                fidelity = "modules"
                format = "python"

            self.location = AssetLocator(_YamlSubject(), "examples").locate()

        with it("should resolve to kind folder"):
            expect(self.location.kind).to(equal("folder"))

        with it("should resolve to practices/clean_engineering/examples"):
            expect(self.location.folder).to(equal((_CLEAN_ENGINEERING_DIR / "examples").resolve()))

    with context("that locates overview on a CleanEngineering"):
        with before.each:
            class _YamlSubject:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"
                toolset_name = "clean_engineering"

            self.location = AssetLocator(_YamlSubject(), "overview").locate()

        with it("should resolve to Overview in clean_engineering.md"):
            expect(self.location.kind).to(equal("section"))
            expect(self.location.section_heading).to(equal("Overview"))
            expect(self.location.section_file).to(
                equal((_CLEAN_ENGINEERING_DIR / "clean_engineering.md").resolve())
            )

    with context("that locates shared templates on a CleanEngineering"):
        with before.each:
            class _YamlSubject:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"
                toolset_name = "clean_engineering"

            self.location = AssetLocator(_YamlSubject(), "templates").locate()

        with it("should resolve to the python template file when format is python"):
            expect(self.location.kind).to(equal("file"))
            expect(self.location.path).to(
                equal(
                    (_CLEAN_ENGINEERING_DIR / "templates" / "clean_engineering.py").resolve()
                )
            )

    with context("that locates shared templates on a Stories with markdown format"):
        with before.each:
            class _YamlSubject:
                module_dir = _STORIES_DIR
                format = "markdown"
                fidelity = "story_map"
                toolset_name = "stories"

            self.location = AssetLocator(_YamlSubject(), "templates").locate()

        with it("should resolve to the fidelity-named markdown file"):
            expect(self.location.kind).to(equal("file"))
            expect(self.location.path).to(
                equal((_STORIES_DIR / "templates" / "md" / "story-map.md").resolve())
            )

    with context("that locates shared templates on a Stories with no format"):
        with before.each:
            class _YamlSubject:
                module_dir = _STORIES_DIR
                format = None
                toolset_name = "stories"

            self.location = AssetLocator(_YamlSubject(), "templates").locate()

        with it("should resolve to no template when no practice-named file exists"):
            expect(self.location.kind).to(equal("file"))
            expect(self.location.path.is_file()).to(equal(False))

    with context("that resolves a label to a folder"):
        with before.each:
            class _YamlSubject:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"

            self.location = AssetLocator(_YamlSubject(), "scanners").locate()

        with it("should resolve to kind folder"):
            expect(self.location.kind).to(equal("folder"))

        with it("should have a non-None folder path"):
            expect(self.location.folder).not_to(be_none)


with description("a markdown section containing a yaml fence"):
    with context("with keys that match properties on Guidance"):
        with before.each:
            class _YamlSubject:
                default_format = ""
                stage = ""
                clean_engineering = ""

            self.instance = _YamlSubject()
            bind_yaml(
                self.instance,
                """```yaml
default_format: python
stage: specification
clean_engineering: model
```
prose
""",
            )

        with it("should bind each matching key as a property"):
            expect(self.instance.default_format).to(equal("python"))
            expect(self.instance.stage).to(equal("specification"))
            expect(self.instance.clean_engineering).to(equal("model"))


with description("a markdown collection bound to a guidance"):
    with context("with the member annotated as a markdown collection"):
        with it("should return the same collection when the member is read again"):
            guidance = SamplePracticeGuidance(format="markdown")
            first = guidance.rules
            first.glob = "bound-once"
            expect(guidance.rules is first).to(equal(True))
            expect(guidance.rules.glob).to(equal("bound-once"))
            expect(guidance.rules.parent).to(equal(guidance))


with description("a docstring used as install prose"):
    with context("that is one word naming a markdown section"):
        with it("should extract that section from the Guidance markdown"):
            instance = SamplePracticeGuidance(format="markdown")
            expect(Markdown.expand_docstring(instance, "overview")).to(contain("sample preamble"))

    with context("that is ordinary prose"):
        with it("should keep the prose"):
            instance = SamplePracticeGuidance(format="markdown")
            expect(Markdown.expand_docstring(instance, "plain install text")).to(
                equal("plain install text")
            )
