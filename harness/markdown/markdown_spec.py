"""BDD spec — co-located markdown extract and HTML."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be, be_none, contain, equal, expect, raise_error
from mamba import before, context, description, it

from harness.guidance.fixtures.other_tool.other_tool_host import OtherTool
from harness.guidance.fixtures.sample_tool.sample_tool_host import (
    SamplePracticeGuidance,
    SampleTool,
)
from harness.markdown import HTML, Markdown, MarkdownScope, MarkdownText, MarkdownTypeUnresolved, markdown
from harness.markdown.front_matter import FrontMatter
from harness.markdown.markdown import AssetLocator, heading_anchor  # noqa: F401

_CLEAN_ENGINEERING_DIR = _REPO_ROOT / "cdd_guidance" / "practices" / "clean_engineering"
_STORIES_DIR = _REPO_ROOT / "cdd_guidance" / "practices" / "stories"


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

    with context("with one Markdown read more than once"):
        with before.each:
            self.section = Markdown.from_label(SampleTool(), "guidance")
            self.first = self.section.extract()

        with it("should locate its section once"):
            expect(self.section.location).to(be(self.section.location))

        with it("should keep the document it read the first time"):
            document = self.section.document
            self.section.extract()
            expect(self.section.document).to(be(document))

        with it("should answer the same prose each time"):
            expect(self.section.extract()).to(equal(self.first))


class _MistypedSampleTool(SampleTool):
    @markdown("guidance")
    def mistyped(self) -> "NoSuchShape":  # noqa: F821
        """A section whose return annotation names a type nothing defines."""


with description("a templates folder beside the module"):
    with context("with a produce file named for the domain and a markdown extension"):
        with it("should map the markdown format key not the templates filename stem"):
            instance = SamplePracticeGuidance(format="markdown")
            expect(instance.templates).to(contain("active format template body for sample tool"))


with description("an asset locator"):
    with context("that locates shared examples on a CleanEngineering"):
        with before.each:
            scope = MarkdownScope(_CLEAN_ENGINEERING_DIR, "clean_engineering", format="python", template_name="modules")
            self.location = AssetLocator(scope, "examples").locate()

        with it("should resolve to kind folder"):
            expect(self.location.kind).to(equal("folder"))

        with it("should resolve to practices/clean_engineering/_examples"):
            expect(self.location.folder).to(equal((_CLEAN_ENGINEERING_DIR / "_examples").resolve()))

    with context("that locates overview on a CleanEngineering"):
        with before.each:
            scope = MarkdownScope(_CLEAN_ENGINEERING_DIR, "clean_engineering", format="python")
            self.location = AssetLocator(scope, "overview").locate()

        with it("should resolve to Overview in clean_engineering.md"):
            expect(self.location.kind).to(equal("section"))
            expect(self.location.section_heading).to(equal("Overview"))
            expect(self.location.section_file).to(
                equal((_CLEAN_ENGINEERING_DIR / "clean_engineering.md").resolve())
            )

    with context("that locates shared templates on a CleanEngineering"):
        with before.each:
            scope = MarkdownScope(_CLEAN_ENGINEERING_DIR, "clean_engineering", format="python")
            self.location = AssetLocator(scope, "templates").locate()

        with it("should resolve to the python template file when format is python"):
            expect(self.location.kind).to(equal("file"))
            expect(self.location.path).to(
                equal(
                    (_CLEAN_ENGINEERING_DIR / "templates" / "clean_engineering.py").resolve()
                )
            )

    with context("that locates shared templates on a Stories with markdown format"):
        with before.each:
            scope = MarkdownScope(_STORIES_DIR, "stories", format="markdown", template_name="story_map")
            self.location = AssetLocator(scope, "templates").locate()

        with it("should resolve to the fidelity-named markdown file"):
            expect(self.location.kind).to(equal("file"))
            expect(self.location.path).to(
                equal((_STORIES_DIR / "templates" / "md" / "story-map.md").resolve())
            )

    with context("that locates shared templates on a Stories with no format"):
        with before.each:
            self.location = AssetLocator(MarkdownScope(_STORIES_DIR, "stories"), "templates").locate()

        with it("should resolve to no template when no practice-named file exists"):
            expect(self.location.kind).to(equal("file"))
            expect(self.location.path.is_file()).to(equal(False))

    with context("that resolves a label to a folder"):
        with before.each:
            # clean_engineering/scanners was retired for rules/; rules is the practice's code folder now.
            scope = MarkdownScope(_CLEAN_ENGINEERING_DIR, "clean_engineering", format="python")
            self.location = AssetLocator(scope, "rules").locate()

        with it("should resolve to kind folder"):
            expect(self.location.kind).to(equal("folder"))

        with it("should have a non-None folder path"):
            expect(self.location.folder).not_to(be_none)


with description("a markdown scope"):
    with context("of a class that hands none"):
        with it("should be the markdown beside the class, named by the slug the class declares"):
            scope = MarkdownScope.of(SampleTool())
            expect((scope.folder.name, scope.slug)).to(equal(("sample_tool", "sample_tool")))

    with context("in another format"):
        with it("should keep the folder and the part of the document it reads, and read that format"):
            within = ("Fidelities", "story_map")
            scope = MarkdownScope(_STORIES_DIR, "stories", format="markdown", within=within).at("drawio")
            expect((scope.folder, scope.within, scope.format)).to(equal((_STORIES_DIR, within, "drawio")))

    with context("that names no other format"):
        with it("should keep its own"):
            expect(MarkdownScope(_STORIES_DIR, "stories", format="markdown").at(None).format).to(equal("markdown"))

    with context("of an owner that filters the files of its folders"):
        with before.each:
            kept = lambda label, path: path.stem != "left-out"  # noqa: E731
            self.scope = MarkdownScope(_STORIES_DIR, "stories", reads_file=kept)

        with it("should hand the filter to a folder it locates"):
            location = AssetLocator(self.scope, "examples").locate()
            expect(location.reads_file).to(equal(self.scope.reads_file))


with description("a markdown section containing a yaml fence"):
    with before.each:
        self.text = MarkdownText(
            """```yaml
default_format: python
stage: specification
clean_engineering: model
```
prose
"""
        )

    with it("should answer each setting by its key"):
        expect(self.text.yaml_fields).to(
            equal({"default_format": "python", "stage": "specification", "clean_engineering": "model"})
        )

    with it("should leave the settings out of its prose"):
        expect(self.text.without_yaml).to(equal("prose"))


with description("a markdown file with a settings block"):
    with before.each:
        folder = Path(tempfile.mkdtemp(prefix="markdown-file-"))
        self.path = folder / "agent.md"
        self.path.write_text("---\nname: reviewer\n---\n# Reviewer\n", encoding="utf-8")

    with it("should answer its settings"):
        expect(FrontMatter.of_file(self.path).fields).to(equal({"name": "reviewer"}))

    with it("should answer the content after them"):
        expect(FrontMatter.of_file(self.path).content).to(equal("# Reviewer\n"))


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
            expect(Markdown.from_label(instance, "").expand_docstring("overview")).to(contain("sample preamble"))

    with context("that is ordinary prose"):
        with it("should keep the prose"):
            instance = SamplePracticeGuidance(format="markdown")
            expect(Markdown.from_label(instance, "").expand_docstring("plain install text")).to(
                equal("plain install text")
            )


with description("a markdown property"):
    with context("with a return annotation its module cannot resolve"):
        with it("should fail naming the property instead of reading the annotation as a bare string"):
            expect(lambda: _MistypedSampleTool().mistyped).to(
                raise_error(MarkdownTypeUnresolved, contain("_MistypedSampleTool.mistyped", "NoSuchShape"))
            )


with description("an owner's markdown section"):
    with context("that is read twice in the same scope"):
        with it("should be read from the one Markdown the owner keeps"):
            instance = SampleTool()
            expect(Markdown.held_by(instance, "guidance")).to(be(Markdown.held_by(instance, "guidance")))


with description("a heading a link names by its anchor"):
    with before.each:
        self.text = MarkdownText(
            "# Kanban Model\n\n### Board\n\n- The board shows every ticket.\n\n### FilesPage (`files/files-page.ts`)\n\n- The page.\n"
        )

    with it("should be found by the anchor GitHub writes for it"):
        expect(self.text.anchored_lines("filespage-filesfiles-pagets")).to(equal((7, 9)))

    with it("should run through its last line with text before the next heading as high"):
        expect(self.text.anchored_lines("board")).to(equal((3, 5)))

    with context("that no heading has"):
        with it("should name no lines"):
            expect(self.text.anchored_lines("no-such-heading")).to(be_none)

    with context("that names a heading holding a link, as a story map's story links its scenarios"):
        with it("should be found by the anchor made from the words the heading shows"):
            linked = MarkdownText("# Story Map\n\n### (S) Person --> [Delete Ticket](../story_tests/remove_tickets_story.test.md)\n\nThe Person removes a ticket.\n")
            expect(linked.anchored_lines("s-person----delete-ticket")).to(equal((3, 5)))


with description("a parsed document shared between readers"):
    with before.each:
        self.document = MarkdownText(
            "# Practice\n\n## Fidelities\n\n### story_map\n\nScope the solution.\n\n### scenarios\n\nDefine the behavior.\n"
        )

    with context("that one reader has asked for the block under two headings"):
        with before.each:
            self.kept_before = set(vars(self.document))
            self.document.headings()
            self.block = self.document.block_under("Fidelities", "scenarios")

        with it("should answer that block"):
            expect(self.block).to(equal("Define the behavior."))

        with it("should keep nothing of that reader's question, so a second reader's answer is its own"):
            expect(set(vars(self.document))).to(equal(self.kept_before))


with description("a block under headings"):
    with before.each:
        self.document = MarkdownText(
            "# Practice\n\n## Fidelities\n\n### Story_Map\n\n#### Guidance\n\nScope it.\n\n### scenarios\n\nDefine it.\n"
        )

    with it("should match each heading in any case"):
        expect(self.document.block_under("fidelities", "story_map")).to(equal("#### Guidance\n\nScope it."))

    with it("should follow each heading one level further down"):
        expect(self.document.block_under("Fidelities", "story_map", "guidance")).to(equal("Scope it."))

    with context("that the document does not have"):
        with it("should answer nothing"):
            expect(self.document.block_under("Fidelities", "tactics")).to(equal(""))

    with context("whose first heading the document does not have"):
        with it("should answer nothing"):
            expect(self.document.block_under("Stages", "scenarios")).to(equal(""))
