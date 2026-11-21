"""A bounded context's own file, ``.context/bounded-context.md``, names each aggregate as a link to that aggregate's
heading in the domain model, so the Files app opens the aggregate in place.

The domain model is created in whatever format (markdown, or markdown taken through a drawing, a whiteboard, or code
and back), then one common set of examples asks the context's file for its links and the domain model for the headings
they open."""

from pathlib import Path

from expects import be_none, contain, equal, expect
from mamba import before, context, description, included_context, it, shared_context

from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from cdd_guidance.practices.ddd.model.nodes import ContextFile
from harness.markdown.markdown import MarkdownText

_MODEL_LINKED = "../../.context/domain-model.md"
_EXAMPLES = Path(__file__).resolve().parent / "_examples" / "expected"
_DOMAIN_MODEL = """# Domain Model — Bookshop

## Ordering | custom

Where a customer fills a cart and checks out an order.

### Cart

A cart holds one line per book.

#### Cart <<Aggregate Root>> <<Entity>>

------
+ cartId: CartId
----
+ total(): Money

### Order

An order is a cart a customer submitted.

#### Order <<Aggregate Root>> <<Entity>>

------
+ orderId: OrderId
----
+ submit(): void

## Catalogue | custom

### Book

#### Book <<Aggregate Root>> <<Entity>>

------
+ isbn: Isbn
----
+ price(): Money
"""


def _through(format: str) -> str:
    """The domain model as markdown again after it is written in format and read back."""
    ddd = Ddd(fidelity="model")
    written = ddd.render(format, _DOMAIN_MODEL, source="markdown")["content"]
    return ddd.render("markdown", written, source=format, previous=_DOMAIN_MODEL)["content"]


def _ordering(model: str):
    return next(found for found in MarkdownBoundedContextMap().parse(model).contexts if found.name == "Ordering")


with shared_context("the file of the Ordering context"):
    with it("should be titled with the context's name"):
        expect(self.file.splitlines()[0]).to(equal("# Ordering"))

    with it("should name each aggregate as a link to its heading in the domain model"):
        expect(self.file).to(contain(f"- [Cart]({_MODEL_LINKED}#cart)\n- [Order]({_MODEL_LINKED}#order)\n"))

    with it("should link no aggregate of another context"):
        expect(self.file).not_to(contain("[Book]"))

    with it("should link only headings the domain model holds"):
        links = ContextFile(self.file).aggregate_links
        expect([MarkdownText(self.model).anchored_lines(link.anchor) is None for link in links]).to(equal([False, False]))


with description("a bounded context's file") as self:
    with context("written from a domain model in markdown"):
        with before.all:
            self.model = _DOMAIN_MODEL
            self.file = _ordering(self.model).context_file(_MODEL_LINKED)

        with included_context("the file of the Ordering context"):
            pass

        with it("should say what the context is, as the domain model says it"):
            expect(self.file).to(contain("Where a customer fills a cart and checks out an order."))

    with context("written from a domain model taken through a drawing and back"):
        with before.all:
            self.model = _through("drawio")
            self.file = _ordering(self.model).context_file(_MODEL_LINKED)

        with included_context("the file of the Ordering context"):
            pass

    with context("written from a domain model taken through a whiteboard and back"):
        with before.all:
            self.model = _through("whiteboard")
            self.file = _ordering(self.model).context_file(_MODEL_LINKED)

        with included_context("the file of the Ordering context"):
            pass

    with context("written from a domain model taken through Python and back"):
        with before.all:
            self.model = _through("python")
            self.file = _ordering(self.model).context_file(_MODEL_LINKED)

        with included_context("the file of the Ordering context"):
            pass

    with context("written from a domain model taken through TypeScript and back"):
        with before.all:
            self.model = _through("typescript")
            self.file = _ordering(self.model).context_file(_MODEL_LINKED)

        with included_context("the file of the Ordering context"):
            pass

    with context("written from a domain model taken through JavaScript and back"):
        with before.all:
            self.model = _through("javascript")
            self.file = _ordering(self.model).context_file(_MODEL_LINKED)

        with included_context("the file of the Ordering context"):
            pass

    with context("written over a file a person already wrote, which names its aggregates in plain words"):
        with before.all:
            self.model = _DOMAIN_MODEL
            written = "# Ordering\n\nOwner: custom. The shop's own checkout.\n\nAggregates:\n- Cart\n- Order\n\nCart → Catalogue · Book\n"
            self.file = _ordering(self.model).context_file(_MODEL_LINKED, written)

        with included_context("the file of the Ordering context"):
            pass

        with it("should keep the words the person wrote"):
            expect(self.file).to(contain("Owner: custom. The shop's own checkout."))

        with it("should keep each context mapping the file lists"):
            expect(self.file).to(contain("\nCart → Catalogue · Book\n"))

        with it("should name each aggregate once"):
            expect(self.file.count("Order]")).to(equal(1))

    with context("read back"):
        with before.all:
            self.links = ContextFile(_ordering(_DOMAIN_MODEL).context_file(_MODEL_LINKED)).aggregate_links

        with it("should give each aggregate's link: its name, the file it opens, and the heading's anchor"):
            expect([(link.name, link.file, link.anchor) for link in self.links]).to(equal([("Cart", _MODEL_LINKED, "cart"), ("Order", _MODEL_LINKED, "order")]))

        with it("should give the line each link is written on"):
            expect([link.line for link in self.links]).to(equal([6, 7]))

    with context("kept among the practice's examples, beside the domain model it links"):
        with before.all:
            self.model = MarkdownBoundedContextMap().parse((_EXAMPLES / "domain-model.md").read_text(encoding="utf-8"))

        with it("should be the file the example domain model writes for each of its contexts"):
            kept = {found.name: (_EXAMPLES / found.name.lower() / ".context" / "bounded-context.md").read_text(encoding="utf-8") for found in self.model.contexts}
            expect(kept).to(equal({found.name: found.context_file("../../domain-model.md") for found in self.model.contexts}))

    with context("that names its aggregates in plain words"):
        with it("should hold no link"):
            expect(ContextFile("# Ordering\n\nAggregates:\n- Cart\n").aggregate_links).to(equal([]))

    with context("whose link opens a whole file, with no heading"):
        with it("should hold no aggregate link, since a sentence's reference names no aggregate"):
            links = ContextFile("# Ordering\n\nSee [the map](../../.context/bounded-context-map.md).\n").aggregate_links
            expect(next(iter(links), None)).to(be_none)
