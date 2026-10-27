"""DrawIO bounded-context map — layout uses relative swimlane coordinates."""

from pathlib import Path

from expects import expect, equal, be_true, be_false
from mamba import description, context, it

from cdd_guidance.practices.ddd.model.drawio.drawio_bounded_context_map import DrawIOBoundedContextMap
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap

_EXPECTED = Path(__file__).resolve().parent.parent / "_examples" / "expected" / "bounded-context-map.md"


with description("DrawIOBoundedContextMap"):
    with context("render"):
        with it("should nest compact aggregates with bulleted members"):
            model = MarkdownBoundedContextMap().parse(_EXPECTED.read_text(encoding="utf-8"))
            xml = DrawIOBoundedContextMap().render(model)
            expect("<mxfile" in xml).to(be_true)
            expect("Sales" in xml).to(be_true)
            expect("custom" in xml).to(be_true)
            expect('parent="1"' in xml).to(be_true)
            expect('y="44"' in xml).to(be_true)
            expect("&lt;li" in xml).to(be_true)
            expect("fillColor=#d4e8f8" in xml).to(be_false)
            expect(xml.find("note: a product")).to(equal(-1))
            expect(xml.find("in this channel")).to(equal(-1))

        with it("should draw straight integration edges without waypoints"):
            model = MarkdownBoundedContextMap().parse(_EXPECTED.read_text(encoding="utf-8"))
            xml = DrawIOBoundedContextMap().render(model)
            expect('edge="1"' in xml).to(be_true)
            expect('source="' in xml).to(be_true)
            expect("orthogonalEdgeStyle" in xml).to(be_false)
            expect("<mxPoint" in xml).to(be_false)

        with it("should place the most connected context in the center"):
            model = MarkdownBoundedContextMap().parse(_EXPECTED.read_text(encoding="utf-8"))
            from cdd_guidance.practices.ddd.model.drawio.drawio_bounded_context_map import (
                _context_height,
                _hub_context,
                _integration_graph,
                _layout_context_positions,
            )

            contexts = [item for item in model.contexts if hasattr(item, "name")]
            outgoing, links = _integration_graph(contexts)
            hub = _hub_context(contexts, outgoing)
            positions = _layout_context_positions(contexts, links, hub)
            sales_x, sales_y = positions["Sales"]
            catalog_x, catalog_y = positions["Catalog"]
            expect(catalog_x < sales_x).to(be_true)
            expect(sales_x < catalog_x + 900).to(be_true)
            catalog = next(item for item in contexts if item.name == "Catalog")
            catalog_bottom = catalog_y + _context_height(catalog)
            expect(sales_y >= catalog_y).to(be_true)
            expect(sales_y <= catalog_bottom).to(be_true)


_MODEL = Path(__file__).resolve().parent.parent / "_examples" / "expected" / "domain-model.md"


with description("DrawIOBoundedContextMap at model fidelity"):
    with context("render"):
        with it("should draw each root card with its repository below the domain operations"):
            model = MarkdownBoundedContextMap().parse(_MODEL.read_text(encoding="utf-8"))
            xml = DrawIOBoundedContextMap().render(model)
            card = xml.split('id="card-customerprofile"', 1)[1].split("/>", 1)[0]
            expect(card.find("enterProfileDetails") < card.find("Repository")).to(be_true)
            expect(card.find("CustomerProfileRepository") < card.find("create(accountCredentials)")).to(be_true)
            expect('id="card-customerprofilerepository"' in xml).to(be_false)

        with it("should nest aggregates in their contexts and compose members under the root"):
            model = MarkdownBoundedContextMap().parse(_MODEL.read_text(encoding="utf-8"))
            xml = DrawIOBoundedContextMap().render(model)
            expect('id="ctx-customer"' in xml).to(be_true)
            expect('id="agg-customer-profile"' in xml).to(be_true)
            expect('source="card-customerprofile" target="card-customer-profile-identity"' in xml).to(be_true)
            expect("startArrow=diamondThin" in xml).to(be_true)

        with it("should draw an arrow only where one aggregate needs another"):
            model = MarkdownBoundedContextMap().parse(_MODEL.read_text(encoding="utf-8"))
            xml = DrawIOBoundedContextMap().render(model)
            expect('source="card-customerprofile" target="card-kycinquiry"' in xml).to(be_true)
            expect('source="card-subscription" target="card-customerprofile"' in xml).to(be_true)
            expect('source="card-kycinquiry" target=' in xml).to(be_false)
