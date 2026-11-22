"""The Ordering module's two classes, written once in each code language, and the project a spec creates from one of
them: the class model its file holds, the graph Clean Engineering reads from it, and the files a render of it saves."""

from __future__ import annotations

import tempfile
from pathlib import Path

from cdd_guidance.actions.render.rendered_code import RenderedCode
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_files
from harness.guidance.practice_formats import RenderRequest
from harness.markdown.format import Format

_PYTHON = '''\
class CartLine:
    def __init__(self, sku: str, quantity: int) -> None:
        self.sku = sku
        self.quantity = quantity


class Cart:
    def __init__(self) -> None:
        self.lines: list[CartLine] = []

    def add(self, line: CartLine) -> None:
        self.lines.append(line)
'''

_TYPESCRIPT = '''\
export class CartLine {
  sku: string;
  quantity: number;

  constructor(sku: string, quantity: number) {
    this.sku = sku;
    this.quantity = quantity;
  }
}

export class Cart {
  lines: CartLine[] = [];

  add(line: CartLine): void {
    this.lines.push(line);
  }
}
'''

_JAVASCRIPT = '''\
export class CartLine {
  constructor(sku, quantity) {
    this.sku = sku;
    this.quantity = quantity;
  }
}

export class Cart {
  constructor() {
    this.lines = [];
  }

  add(line) {
    this.lines.push(line);
  }
}
'''

# The module's file in each language, at the path the model fidelity declares for it.
ORDERING_FILES = {
    "python": ("ordering/ordering.py", _PYTHON),
    "typescript": ("ordering/ordering.ts", _TYPESCRIPT),
    "javascript": ("ordering/ordering.js", _JAVASCRIPT),
}


class OrderingProject:
    """A project holding the Ordering module written in one language: what a spec asks of its model, of its graph, and
    of a render of its file into a code format."""

    def __init__(self, language: str) -> None:
        self.language = language
        self._relative, self._text = ORDERING_FILES[language]
        self._fixture = practice_from_files({self._relative: self._text})
        self._fidelity = CleanEngineering(fidelity="model").fidelities.current
        self._saved = tempfile.TemporaryDirectory()

    @property
    def _model(self):
        return self._fidelity.practice_guidance.formats.adapter_class(self.language)().parse(self._text)

    def class_names(self) -> list[str]:
        """The classes the file's model holds, in the order the file declares them."""
        return [oclass.name for oclass in self._model.every_class()]

    def operations_of(self, class_name: str) -> list[str]:
        """The operations the model gives a class, its constructor left out."""
        oclass = next(found for found in self._model.every_class() if found.name == class_name)
        return [operation.name for operation in oclass.operations if operation is not oclass.constructor()]

    def graph_classes(self) -> list[str]:
        """The classes the graph holds for the project."""
        return sorted(node.name for node in self._fixture.practice.reading.in_graph.nodes("OoadClass"))

    def owned_by(self, class_name: str) -> list[str]:
        """What the graph says a class owns."""
        edges = self._fixture.practice.reading.in_graph.edge_index.of("owns")
        return sorted(edge.child.name for edge in edges if edge.parent.name == class_name)

    def saved_by_render_to(self, format: str) -> list[str]:
        """The files a render of the module's file into format saves, as paths under the folder it saves in."""
        source = self._fixture.root / self._relative
        request = RenderRequest(Format(format), self._text, Format(self.language), folder=str(source.parent), fidelity=self._fidelity)
        rendered = request.render()
        root = Path(self._saved.name) / format
        saved = RenderedCode(root, self._fidelity.declared.placement, Format(format)).save(rendered)
        return sorted(Path(path).relative_to(root).as_posix() for path in saved.paths)

    def declares(self, path: str, format: str) -> bool:
        """Whether path is a file the model fidelity declares for format."""
        return self._fidelity.declared.includes(path, format)
