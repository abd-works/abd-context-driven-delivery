"""What the measures read of the nodes the graph reading builds: the facts it keeps by name, the parameters an
operation takes and how many of them a caller supplies, and whether a path lies under a folder.

They are named here, below the reading, so the dependencies run one way: the graph reading records these facts and
keeps the code measures through ``GraphReading.keep_code_measures``, the measures read the facts, and nothing in this
package imports the reading back."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from harness.graph.graph import Graph, Node, PracticeNodes

    from cdd_guidance.practices.source_code import ProjectTestCode

# The fact a class keeps when a model document describes it: the design, read from the
# document, standing in for code not written yet.
DESCRIBED_FACT = "described_by_model_document"
# The facts a module keeps of its imports (``ModuleImports`` in ``reading/folder_facts.py``): the paths of the modules
# it imports, of the modules that import it, and the modules it imports that close a loop of modules, with its size.
IMPORTED_MODULES_FACT = "imported_modules"
IMPORTING_MODULES_FACT = "importing_modules"
MODULE_IMPORT_LOOPS_FACT = "module_import_loops"
# The parameter a method takes for its own object, which is no parameter a caller supplies.
_PARAMETER_NAMES_EXCLUDED_FROM_COUNT = frozenset({"self", "cls"})


class MeasuredReading(Protocol):
    """What the measures ask of the practice's reading of the code, which ``GraphReading`` answers: the graph, the
    practice's nodes in it, and the project's test code, which no measure is taken of."""

    @property
    def graph(self) -> "Graph": ...

    @property
    def in_graph(self) -> "PracticeNodes": ...

    @property
    def test_code(self) -> "ProjectTestCode": ...


def is_under(path: str | None, folder: str | None) -> bool:
    """True for a path at or below folder, both from the source root."""
    if not path or not folder:
        return False
    return path == folder or path.startswith(folder.rstrip("/") + "/")


def parameters_of(operation: "Node") -> list["Node"]:
    """The parameters an operation takes, in the order it declares them: the nodes its hasParameter edges lead to, which
    a graph read back from its saved file keeps too."""
    return [edge.child for edge in operation.graph.edges.from_parent("hasParameter", operation)]


def counted_parameters(names: list[str], packed: dict[str, int] | None = None) -> int:
    """Each named parameter counts once, except a packed tuple or ``*args``, which counts each value it carries."""
    packed = packed or {}
    named = [name for name in names if name not in _PARAMETER_NAMES_EXCLUDED_FROM_COUNT]
    unnamed = [values for name, values in packed.items() if name not in named]
    return sum(packed.get(name, 1) for name in named) + sum(unnamed)
