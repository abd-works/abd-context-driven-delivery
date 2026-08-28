# @toolset-manifest python -m tools manifest catalog_generator.catalog_generator:CatalogGenerator
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""Acceptance tests for the "Configure Illustrated Examples" epic - one `it`
per sketch story's single main-flow scenario.
"""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("context_tools", "primitives", "utilities"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import before, description, it

from catalog_generator.catalog_generator import (
    extract_comment_tag,
    extract_heading_section,
    extract_whole_file,
    parse_illustrated_examples,
    resolve_illustrated_example,
)

_INDEX_MD = """# Stories examples

Some intro prose.

## Illustrated examples

| Fidelity | Source | Anchor |
|---|---|---|
| story_map | md/story-map.md | whole-file |
| scenarios | py/manage-customer-orders/story_runner.py | ## run_scenario |
| acceptance_tests | py/manage-customer-orders/story_types.py | <!-- Mu --> |

## Other section

Ignored by the table parser.
"""


with description("Configure Illustrated Example Mapping Per Fidelity"):
    with description("given a tool's examples.md index naming a real subfolder file"):
        with before.all:
            self.rows = parse_illustrated_examples(_INDEX_MD)

        with it("resolves each row to its named Fidelity, Source, and Anchor - nothing else"):
            expect(len(self.rows)).to(equal(3))
            expect(self.rows[0].fidelity).to(equal("story_map"))
            expect(self.rows[0].source).to(equal("md/story-map.md"))
            expect(self.rows[0].anchor).to(equal("whole-file"))
            expect(self.rows[1].anchor).to(equal("## run_scenario"))
            expect(self.rows[2].anchor).to(equal("<!-- Mu -->"))


with description("Extract Whole-File Illustrated Example"):
    with description("given an Illustrated examples row with Anchor whole-file"):
        with before.all:
            self.tmp = Path(tempfile.mkdtemp())
            self.source = self.tmp / "story-map.md"
            self.source.write_text("# Story Map\n\nEpic -> Story", encoding="utf-8")

        with it("resolves the entire source file's content as the illustrated-example body"):
            body = extract_whole_file(self.source)
            expect(body).to(equal("# Story Map\n\nEpic -> Story"))


with description("Extract Heading-Anchored Illustrated Example Section"):
    with description("given an Illustrated examples row whose Anchor names a ## heading"):
        with it("resolves only the body under that heading up to the next same-or-higher heading"):
            markdown = "# Title\n\n## keep\n\nkept body\n\n## drop\n\ndropped body\n"
            section = extract_heading_section(markdown, "keep")
            expect(section).to(equal("kept body"))
            expect("dropped body" in section).to(equal(False))


with description("Extract Comment-Tag-Anchored Illustrated Example Block"):
    with description("given an Illustrated examples row whose Anchor names an HTML comment tag"):
        with it("resolves only the lines carrying that comment tag"):
            text = "line one\nline two <!-- Mu -->\nline three\nline four <!-- Mu -->\n"
            body = extract_comment_tag(text, "<!-- Mu -->")
            expect(body).to(equal("line two <!-- Mu -->\nline four <!-- Mu -->"))


with description("resolve_illustrated_example dispatches by anchor shape"):
    with before.all:
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "whole.md").write_text("whole content", encoding="utf-8")
        (self.tmp / "heading.md").write_text("# T\n\n## keep\n\nkept\n", encoding="utf-8")
        (self.tmp / "tagged.md").write_text("a\nb <!-- Mu -->\nc\n", encoding="utf-8")

    with it("dispatches whole-file, heading, and comment-tag rows to their own extractor"):
        from catalog_generator.catalog_generator import IllustratedExampleRow

        whole = resolve_illustrated_example(self.tmp, IllustratedExampleRow("x", "whole.md", "whole-file"))
        expect(whole).to(equal("whole content"))

        heading = resolve_illustrated_example(self.tmp, IllustratedExampleRow("x", "heading.md", "## keep"))
        expect(heading).to(equal("kept"))

        tagged = resolve_illustrated_example(self.tmp, IllustratedExampleRow("x", "tagged.md", "<!-- Mu -->"))
        expect(tagged).to(equal("b <!-- Mu -->"))
