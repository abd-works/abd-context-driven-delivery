"""BDD spec — co-located markdown extract and HTML."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "primitives", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_none, contain, equal, expect
from mamba import before, context, description, it

from primitives.guidance.fixtures.other_tool.other_tool_host import OtherToolHost
from primitives.guidance.fixtures.sample_tool.sample_tool_host import (
    SamplePracticeGuidance,
    SampleToolHost,
)
from primitives.markdown import AssetLocator, HTML, Markdown, canonical_format

_CLEAN_ENGINEERING_DIR = _REPO_ROOT / "practices" / "clean_engineering"
_STORIES_DIR = _REPO_ROOT / "practices" / "stories"


with description("a co-located markdown file beside a host module"):
    with context("with a section heading that matches a property label"):
        with context("with a string property on the host backed by that section"):
            with it("should return the section body when the property is read"):
                host = SampleToolHost()
                text = host.guidance
                expect(text).to(contain("known prose for guidance in sample tool"))
                expect(text).not_to(contain("sample preamble"))

    with context("with known prose written in the module markdown file for that label"):
        with context("with the property read on the host in that module"):
            with it("should return that prose"):
                host = SampleToolHost()
                expect(host.guidance).to(contain("known prose for guidance in sample tool"))

        with context("with an identically named section in a different module folder"):
            with it(
                "should not return prose from the other module file when the host belongs to this module"
            ):
                host = SampleToolHost()
                other = OtherToolHost()
                expect(host.guidance).to(contain("known prose for guidance in sample tool"))
                expect(host.guidance).not_to(contain("prose from the other module only"))
                expect(other.guidance).to(contain("prose from the other module only"))
                expect(other.guidance).not_to(contain("known prose for guidance in sample tool"))

    with context("with a markdown-backed string property"):
        with context("with that property read as HTML"):
            with it("should return HTML formatted from that section body"):
                host = SampleToolHost()
                rendered = Markdown.from_label(host, "guidance").html()
                expect(type(rendered)).to(equal(HTML))
                expect(str(rendered)).to(contain("known prose for guidance in sample tool"))
                expect(str(rendered)).to(contain("<p>"))


with description("a templates folder beside a host module"):
    with context("with a produce file named for the domain and a markdown extension"):
        with it("should map the markdown format key not the templates filename stem"):
            host = SamplePracticeGuidance(format="markdown")
            expect(canonical_format("md")).to(equal("markdown"))
            expect(host.templates.get("markdown")).to(contain("templates/"))


with description("an asset locator"):
    with context("that locates shared examples on a clean-engineering host"):
        with before.each:
            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                fidelity = "modules"
                format = "python"

            self.location = AssetLocator(_Host(), "examples").locate()

        with it("should resolve to kind folder"):
            expect(self.location.kind).to(equal("folder"))

        with it("should resolve to practices/clean_engineering/examples"):
            expect(self.location.folder).to(equal((_CLEAN_ENGINEERING_DIR / "examples").resolve()))

    with context("that locates contexts on a clean-engineering host"):
        with before.each:
            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"
                toolset_name = "clean_engineering"

            self.location = AssetLocator(_Host(), "contexts").locate()

        with it("should resolve to # Contexts in clean_engineering.md"):
            expect(self.location.kind).to(equal("section"))
            expect(self.location.section_heading).to(equal("Contexts"))
            expect(self.location.section_file).to(
                equal((_CLEAN_ENGINEERING_DIR / "clean_engineering.md").resolve())
            )

    with context("that locates shared templates on a clean-engineering host"):
        with before.each:
            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"
                toolset_name = "clean_engineering"

            self.location = AssetLocator(_Host(), "templates").locate()

        with it("should resolve to the python template file when format is python"):
            expect(self.location.kind).to(equal("file"))
            expect(self.location.path).to(
                equal(
                    (
                        _CLEAN_ENGINEERING_DIR / "templates" / "clean_engineering-templates.py"
                    ).resolve()
                )
            )

    with context("that locates shared templates on a stories host with markdown format"):
        with before.each:
            class _Host:
                module_dir = _STORIES_DIR
                format = "markdown"
                fidelity = "story_map"
                toolset_name = "stories"

            self.location = AssetLocator(_Host(), "templates").locate()

        with it("should resolve to the md format folder not the whole templates pack"):
            expect(self.location.kind).to(equal("folder"))
            expect(self.location.folder).to(
                equal((_STORIES_DIR / "templates" / "md").resolve())
            )

        with it("should carry story_map fidelity for filename filtering"):
            expect(self.location.fidelity).to(equal("story_map"))

    with context("that locates shared templates on a stories host with no format"):
        with before.each:
            class _Host:
                module_dir = _STORIES_DIR
                format = None
                toolset_name = "stories"

            self.location = AssetLocator(_Host(), "templates").locate()

        with it("should resolve to the whole templates folder"):
            expect(self.location.kind).to(equal("folder"))
            expect(self.location.folder).to(equal((_STORIES_DIR / "templates").resolve()))

        with it("should not filter by fidelity"):
            expect(self.location.fidelity).to(be_none)

    with context("that resolves a label to a folder"):
        with before.each:
            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"

            self.location = AssetLocator(_Host(), "scanners").locate()

        with it("should resolve to kind folder"):
            expect(self.location.kind).to(equal("folder"))

        with it("should have a non-None folder path"):
            expect(self.location.folder).not_to(be_none)
