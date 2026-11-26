"""The Ordering bounded context and its two aggregates, written once in each code language, and the project a spec
creates from one of them: the domain model its code holds, the graph DDD reads from it, and the files a render of it
saves."""

from __future__ import annotations

import tempfile
from pathlib import Path

from cdd_guidance.actions.render.rendered_code import RenderedCode
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from harness.graph.rule_fixture import RuleFixture
from harness.guidance.practice_formats import RenderRequest
from harness.markdown.format import Format

_MARKER = "# Ordering\n\nWhere a customer fills a cart and submits it as an order.\n"

_PYTHON = {
    "ordering/cart/cart.py": '''\
@aggregate_root
@entity
class Cart:
    """Module: Ordering | custom · Cart"""

    def total(self) -> Money:
        raise NotImplementedError


@repository
class CartRepository:
    """Module: Ordering | custom · Cart"""

    def load(self, cart_id: CartId) -> Cart:
        raise NotImplementedError
''',
    "ordering/order/order.py": '''\
@aggregate_root
@entity
class Order:
    """Module: Ordering | custom · Order"""

    def submit(self) -> None:
        raise NotImplementedError
''',
}

_TYPESCRIPT = {
    "ordering/cart/cart.ts": '''\
/**
 * Module: Ordering | custom · Cart
 */
@AggregateRoot()
@Entity()
class Cart {
  total(): Money {
    throw new Error("not implemented");
  }
}

/**
 * Module: Ordering | custom · Cart
 */
@Repository()
class CartRepository {
  load(cartId: CartId): Cart {
    throw new Error("not implemented");
  }
}
''',
    "ordering/order/order.ts": '''\
/**
 * Module: Ordering | custom · Order
 */
@AggregateRoot()
@Entity()
class Order {
  submit(): void {
    throw new Error("not implemented");
  }
}
''',
}

_JAVASCRIPT = {
    "ordering/cart/cart.js": '''\
/** Module: Ordering | custom · Cart
<<Aggregate Root>> <<Entity>> */
class Cart {
  total() {
    throw new Error("not implemented");
  }
}

/** Module: Ordering | custom · Cart
<<Repository>> */
class CartRepository {
  load(cartId) {
    throw new Error("not implemented");
  }
}
''',
    "ordering/order/order.js": '''\
/** Module: Ordering | custom · Order
<<Aggregate Root>> <<Entity>> */
class Order {
  submit() {
    throw new Error("not implemented");
  }
}
''',
}

# Each aggregate's file in each language, at the path the model fidelity declares for it.
ORDERING_FILES = {"python": _PYTHON, "typescript": _TYPESCRIPT, "javascript": _JAVASCRIPT}


class OrderingDomain:
    """A project holding the Ordering context written in one language: what a spec asks of its domain model, of its
    graph, and of a render of its code into a code format."""

    def __init__(self, language: str) -> None:
        self.language = language
        self._code = ORDERING_FILES[language]
        self._fixture = RuleFixture(Ddd, {"ordering/.context/bounded-context.md": _MARKER, **self._code})
        self._fidelity = Ddd(fidelity="model").fidelities.current
        self._saved = tempfile.TemporaryDirectory()

    @property
    def _text(self) -> str:
        """The code of every aggregate, one file after another, as a render of the files reads it."""
        return "\n".join(self._code.values())

    @property
    def _model(self) -> MarkdownBoundedContextMap:
        document = self._fidelity.render("markdown", self._text, self.language).content
        return MarkdownBoundedContextMap().parse(document)

    def context_names(self) -> list[str]:
        return [context.name for context in self._model.contexts]

    def aggregate_names(self) -> list[str]:
        return [aggregate.name for aggregate in self._model.every_aggregate]

    def stereotypes_of(self, aggregate_name: str) -> dict[str, list[str]]:
        """The stereotypes of each class an aggregate holds, by the class's name."""
        aggregate = next(found for found in self._model.every_aggregate if found.name == aggregate_name)
        return {oclass.name: list(oclass.stereotypes) for oclass in aggregate.classes}

    def graph_names(self, node_type: str) -> list[str]:
        """The names of the graph's nodes of one type, such as its bounded contexts."""
        return sorted(node.name for node in self._fixture.practice.reading.in_graph.nodes(node_type))

    def saved_by_render_to(self, format: str) -> list[str]:
        """The files a render of the context's code into format saves, as paths under the folder it saves in."""
        folder = self._fixture.root / "ordering"
        request = RenderRequest(Format(format), self._text, Format(self.language), folder=str(folder), fidelity=self._fidelity)
        rendered = request.render()
        root = Path(self._saved.name) / format
        saved = RenderedCode(root, self._fidelity.declared.placement, Format(format)).save(rendered)
        return sorted(Path(path).relative_to(root).as_posix() for path in saved.paths)

    def declares(self, path: str, format: str) -> bool:
        """Whether path is a file the model fidelity declares for format."""
        return self._fidelity.declared.includes(path, format)
