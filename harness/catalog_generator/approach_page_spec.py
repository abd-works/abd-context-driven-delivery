"""BDD specs for the approach page and the board drawn under its principles."""
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from harness.catalog_generator.approach_copy import APPROACH_MARKDOWN, ApproachCopy
from harness.catalog_generator.approach_page import ApproachGrids, ApproachPage, PrincipleBullets
from harness.catalog_generator.catalog_generator import CatalogPractice
from harness.catalog_generator.hub_board import HubBoard
import cdd_guidance.actions  # noqa: F401 - registers the actions with the action catalogue

_HAND_EDITED_MD = """# Approach

HAND-EDITABLE-SUBHEAD

## Stages

### Discovery

id: discovery
items: ZZ-CHIP

ZZ-PARA

## Context Driven Delivery Practices

### Product Engineering

slug: product-engineering
kind: descriptions

- HAND-EDITABLE-BULLET

## Library

HAND-EDITABLE-LIBRARY
"""


with description("the catalog board's stage columns"):
    with context("with approach copy for its stages"):
        with before.all:
            path = Path(tempfile.mkdtemp()) / "cdd-approach.md"
            path.write_text(_HAND_EDITED_MD, encoding="utf-8")
            self.html = HubBoard([], [], [], ApproachCopy.load(path).board_stages).html()

        with it("should show each stage's chips in its column"):
            expect("ZZ-CHIP" in self.html).to(equal(True))

        with it("should show each stage's paragraphs in its column"):
            expect("ZZ-PARA" in self.html).to(equal(True))

    with context("whose stages name catalog examples"):
        with it("should link each column heading to its stage's example page"):
            html = HubBoard([], [], [], ApproachCopy.load(APPROACH_MARKDOWN).board_stages).html()
            links = ('href="examples/discovery.html"', 'href="examples/specification.html"', 'href="examples/implementation.html"')
            expect(all(link in html for link in links)).to(equal(True))


with description("the approach page"):
    with context("written from hand-edited copy"):
        with before.all:
            path = Path(tempfile.mkdtemp()) / "cdd-approach.md"
            path.write_text(_HAND_EDITED_MD, encoding="utf-8")
            self.html = ApproachPage(ApproachCopy.load(path), [], Path(tempfile.mkdtemp())).body

        with it("should show the stage copy"):
            expect("ZZ-PARA" in self.html).to(equal(True))

        with it("should show the principle's bullets"):
            expect("HAND-EDITABLE-BULLET" in self.html).to(equal(True))

        with it("should show the library heading"):
            expect("HAND-EDITABLE-LIBRARY" in self.html).to(equal(True))

        with it("should load its script from the catalog's shared files"):
            expect('src="commons/catalog-approach.js' in self.html).to(equal(True))

    with context("written from the catalog's own copy"):
        with before.all:
            self.out = Path(tempfile.mkdtemp())
            page = ApproachPage(ApproachCopy.load(APPROACH_MARKDOWN), CatalogPractice.load_all(), self.out)
            page.write_stage_example_pages()
            self.html = page.body

        with it("should open each stage's Stories example under the Iterate and Learn diagram"):
            expect('id="approach-stage-examples"' in self.html and "approach-stage-column" in self.html).to(equal(True))

        with it("should give the Stories fidelity's opening above its example"):
            expect("a simple graph is easier to change, compare, and reorganize" in self.html).to(equal(True))

        with it("should show a diagram that has a picture beside it as the picture"):
            picture = '<img class="catalog-example__image" alt="story_map.png" src="examples/stories/story_map.png">'
            expect(picture in self.html).to(equal(True))

        with it("should not embed the diagrams.net viewer"):
            expect("viewer.diagrams.net" in self.html).to(equal(False))

        with it("should show code in the Monaco viewer with its folds"):
            expect('id="catalog-monaco"' in self.html and "&quot;start&quot;:" in self.html).to(equal(True))

        with it("should copy each stage's example beside its page"):
            expect((self.out / "examples" / "story_map.png").is_file()).to(equal(True))

        with it("should write each stage's example page"):
            expect((self.out / "examples" / "discovery.html").is_file()).to(equal(True))

    with context("with a principle page for each principle"):
        with it("should write a coming-soon page for the practices the catalog does not hold yet"):
            pages = ApproachPage(ApproachCopy.load(APPROACH_MARKDOWN), [], Path(tempfile.mkdtemp())).principle_pages
            expect("customer-discovery.html" in pages and "devops.html" in pages).to(equal(True))


with description("a principle's bullets"):
    with context("written as phrase and so-what"):
        with it("should put each so-what under its phrase"):
            html = PrincipleBullets(("drill down | so the right decisions are made",)).so_what_html()
            expect('<p class="approach-so__why">so the right decisions are made</p>' in html).to(equal(True))

    with context("with emphasis"):
        with it("should write the emphasis in italics"):
            expect(PrincipleBullets(("a *simple* graph",)).list_html).to(
                equal('<ul class="approach-principle__bullets"><li>a <em>simple</em> graph</li></ul>')
            )


with description("the Product Engineering board"):
    with before.all:
        # Practice labels and colour families come from the practices' own catalog cards.
        self.html = ApproachGrids(CatalogPractice.load_all(), (), None).product_engineering

    with it("should give each practice its own refine row"):
        rows = ("refine-row-stories", "refine-row-ddd", "refine-row-ux", "refine-row-clean_engineering", "refine-row-bdd")
        expect(all(f'id="{row}"' in self.html for row in rows)).to(equal(True))

    with it("should give each row rewind and play"):
        expect((self.html.count('data-refine-nav="1"'), self.html.count('data-refine-nav="-1"'))).to(equal((5, 5)))

    with it("should label each row from the practice's card"):
        expect('class="approach-window__context-label">Domain-driven design<' in self.html).to(equal(True))

    with it("should colour each row by the practice's perspective"):
        families = ("sdd", "ddd", "uxd", "arc", "bdd")
        expect(all(f"approach-grid__label--{family}" in self.html for family in families)).to(equal(True))

    with it("should show a practice's picture in place of its diagram"):
        expect('src="examples/ddd/bounded-context.png"' in self.html and "catalog-drawio-frame" not in self.html).to(equal(True))

    with it("should give each code viewer its own element"):
        expect("monaco-ddd-tactics-ts" in self.html).to(equal(True))

    with it("should start with every column closed"):
        expect("is-open" in self.html).to(equal(False))
