"""BDD specs for a draw.io diagram embedded in the catalog."""
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from harness.catalog_generator.drawio_diagram import DrawioDiagram

_EXAMPLES = Path(__file__).resolve().parents[2] / "cdd_guidance" / "practices"


with description("a draw.io diagram in an approach panel"):
    with context("that is a story map"):
        with before.all:
            self.framed = DrawioDiagram.load(_EXAMPLES / "stories" / "catalog-examples" / "story_map.drawio").framed

        with it("should keep every cell"):
            expect("create-unconfirmed-user" in self.framed.xml).to(equal(True))

        with it("should shrink the page to its cells and the frame margin"):
            # Cells span y 120..443 in the source; parked at the 20px margin the page is 323 + 2*20 high.
            expect(self.framed.page_size[1]).to(equal(363))

        with it("should park its cells at the top-left page edge"):
            expect('x="20"' in self.framed.xml and 'y="20"' in self.framed.xml).to(equal(True))

    with context("that is a bounded context map"):
        with it("should embed the original page with the frame margin around it"):
            html = DrawioDiagram.load(_EXAMPLES / "ddd" / "catalog-examples" / "bounded-context.drawio").panel_html
            # 1080x920 page plus the 20px frame margin on each side.
            expect('data-page-w="1120" data-page-h="960"' in html).to(equal(True))

    with context("that is a class model"):
        with it("should size its frame to cover every cell"):
            html = DrawioDiagram.load(_EXAMPLES / "ddd" / "catalog-examples" / "model.drawio").panel_html
            expect('data-page-w="5240" data-page-h="3270"' in html).to(equal(True))

    with context("that is an information architecture"):
        with it("should embed the original page with the frame margin around it"):
            html = DrawioDiagram.load(_EXAMPLES / "ux" / "catalog-examples" / "information-architecture.drawio").panel_html
            # 2400x680 page plus the 20px frame margin on each side.
            expect('data-page-w="2440" data-page-h="720"' in html).to(equal(True))

    with context("that cannot be read as XML"):
        with it("should be drawn on draw.io's default page"):
            expect(DrawioDiagram("not xml").page_size).to(equal((1080, 919)))
