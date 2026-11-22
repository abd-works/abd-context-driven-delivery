"""The tools that take Clean Engineering's code measures, each behind one question: this measure, of this node.

A project names a tool for each measure no fact on the node already gives, in each language (``ChosenTools``): a
function's lines and parameters, a class's methods, and a module's import loops and imported modules are facts the
reader keeps on every read, and no tool repeats them. Lizard and radon are outside programs,
imported when first asked, so a project that never checks code needs neither; a tool that is chosen and not installed
is reported by name, with how to install it, because a measure silently left out reads as code within its limits. The
reader is the practice's own reading of the code: a measure the graph's nodes and edges give is counted from them."""

from __future__ import annotations

import ast
import importlib
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from cdd_guidance.practices.clean_engineering.measures.code_measures import (
    ABSTRACTNESS,
    CLASSES_DEPENDED_ON,
    INSTABILITY,
    MAINTAINABILITY_SCORE,
    MODULES_IMPORTING,
    MeasureNotTaken,
    PATHS_THROUGH,
    READABILITY_SCORE,
    READER,
    TOTAL_COMPLEXITY,
    UNSHARED_METHOD_GROUPS,
    CodeMeasure,
)
from cdd_guidance.practices.clean_engineering.reading.folder_facts import is_under
from cdd_guidance.practices.source_code import is_test_code

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.reading.graph_reading import GraphReading

# How the optional dependency group that holds the outside tools is installed.
_INSTALL = 'pip install "lizard>=1.26" "radon>=6"   (or, from a CDD checkout: pip install -e ".[measures]")'
# What marks a class as abstract in the code of either language family.
_ABSTRACT = re.compile(r"\bABC\b|\bProtocol\b|@abstractmethod|\babstract\s+class\b|^\s*(?:export\s+)?interface\s", re.MULTILINE)
_DECIMALS = 2


class MeasuringToolNotInstalled(MeasureNotTaken):
    """A tool the project chose to take a measure is not installed where the code is read, so the measure cannot be
    taken. Nothing is skipped: the measure's rule reports the tool and how to install it."""

    def __init__(self, tool: str, measure: CodeMeasure) -> None:
        super().__init__(f"The tool '{tool}', chosen to measure '{measure.name}' ({measure.label}), is not installed. Install it with: {_INSTALL}")
        self.tool = tool
        self.measure = measure


class ToolDoesNotTakeMeasure(MeasureNotTaken):
    """The project chose a tool for a measure that tool does not take, or a tool nobody has written a reading for."""

    def __init__(self, tool: str, measure: CodeMeasure, taken: list[str]) -> None:
        known = f"it takes {', '.join(sorted(taken))}" if taken else f"the tools are {', '.join(sorted(TOOLS))}"
        super().__init__(f"The tool '{tool}' is chosen to measure '{measure.name}' ({measure.label}), which it does not take: {known}.")
        self.tool = tool
        self.measure = measure


@dataclass(frozen=True)
class MeasuredNode:
    """One node a measure is taken of: the node, the reading that holds it, and, for a function or a class, the file
    it was read from; for a module, each of the checked files it holds that is written in the language asked of."""

    node: "Node"
    reading: "GraphReading"
    files: tuple[Path, ...]

    @property
    def file(self) -> Path:
        return self.files[0]

    @property
    def lines(self) -> tuple[int, int]:
        return self.node.source.start_line, self.node.source.end_line


class MeasuringTool:
    """One tool: its name in the config, and the measures it takes, each by the operation that reads it."""

    name = ""

    def __init__(self) -> None:
        self._takes: dict[str, Callable[[MeasuredNode], float | int | None]] = {}

    def value(self, measure: CodeMeasure, measured: MeasuredNode) -> float | int | None:
        """The measure of the node; none when the tool finds nothing to measure there, such as a class with one method
        for a measure that compares methods. Raises *ToolDoesNotTakeMeasure* for a measure it was wrongly chosen for."""
        take = self._takes.get(measure.name)
        if take is None:
            raise ToolDoesNotTakeMeasure(self.name, measure, list(self._takes))
        return take(measured)

    def _imported(self, module: str, measure: CodeMeasure) -> Any:
        """The outside tool's module, imported now; *MeasuringToolNotInstalled* when it is not there."""
        try:
            return importlib.import_module(module)
        except ImportError as missing:
            raise MeasuringToolNotInstalled(self.name, measure) from missing


class LizardTool(MeasuringTool):
    """Lizard, which reads a file in either language into its functions, each with its paths and its readability
    score (lizard's cognitive complexity extension); a class's total complexity is the paths of its functions added
    up. A file is read once."""

    name = "lizard"

    def __init__(self) -> None:
        super().__init__()
        self._read: dict[Path, list] = {}
        self._takes = {
            PATHS_THROUGH.name: lambda measured: self._of_function(measured, PATHS_THROUGH, lambda found: found.cyclomatic_complexity),
            READABILITY_SCORE.name: lambda measured: self._of_function(measured, READABILITY_SCORE, lambda found: found.cognitive_complexity),
            TOTAL_COMPLEXITY.name: self._total_complexity,
        }

    def _functions(self, file: Path, measure: CodeMeasure) -> list:
        if file not in self._read:
            lizard = self._imported("lizard", measure)
            extensions = lizard.get_extensions(["cognitive"])
            self._read[file] = [found for info in lizard.analyze_files([str(file)], exts=extensions, threads=1) for found in info.function_list]
        return self._read[file]

    def _of_function(self, measured: MeasuredNode, measure: CodeMeasure, read: Callable[[Any], int]) -> int | None:
        """What read answers for the function lizard found for the node: the one of the node's name that starts within
        its lines, else the first that starts there; none when lizard found no function there."""
        first, last = measured.lines
        within = [found for found in self._functions(measured.file, measure) if first <= found.start_line <= last]
        named = [found for found in within if found.name.split(".")[-1].split("::")[-1] == measured.node.name]
        chosen = min(named or within, key=lambda found: found.start_line, default=None)
        return read(chosen) if chosen is not None else None

    def _total_complexity(self, measured: MeasuredNode) -> int | None:
        """The paths through every function that starts within the class's lines, added up."""
        first, last = measured.lines
        within = [found.cyclomatic_complexity for found in self._functions(measured.file, TOTAL_COMPLEXITY) if first <= found.start_line <= last]
        return sum(within) if within else None


class RadonTool(MeasuringTool):
    """Radon, which reads Python: a file's maintainability score, the one measure here nothing else gives."""

    name = "radon"

    def __init__(self) -> None:
        super().__init__()
        self._takes = {MAINTAINABILITY_SCORE.name: self._maintainability}

    def _maintainability(self, measured: MeasuredNode) -> float | None:
        """The lowest score among the module's checked files, since its hardest file is the one a change meets."""
        metrics = self._imported("radon.metrics", MAINTAINABILITY_SCORE)
        scores = [metrics.mi_visit(file.read_text(encoding="utf-8"), multi=True) for file in measured.files]
        return round(min(scores), _DECIMALS) if scores else None


class ReaderTool(MeasuringTool):
    """The practice's own reading of the code: the measures counted from the graph's nodes and edges that no fact
    keeps yet, and the groups of a Python class's methods that share no data, read from the class's own text."""

    name = READER

    def __init__(self) -> None:
        super().__init__()
        self._takes = {
            CLASSES_DEPENDED_ON.name: self._classes_depended_on,
            UNSHARED_METHOD_GROUPS.name: self._unshared_method_groups,
            MODULES_IMPORTING.name: lambda measured: len(self._importing(measured)),
            ABSTRACTNESS.name: self._abstractness,
            INSTABILITY.name: self._instability,
        }

    def _classes_depended_on(self, measured: MeasuredNode) -> int:
        """The other classes an edge of any kind leads to from the class."""
        edges = measured.reading.in_graph.edge_index
        reached = {id(edge.child) for kind in edges.types for edge in measured.reading.graph.edges.from_parent(kind, measured.node) if edge.child.type == "OoadClass"}
        return len(reached - {id(measured.node)})

    def _unshared_method_groups(self, measured: MeasuredNode) -> int | None:
        """The groups a class's methods fall into when two methods are joined by a field both use or by one calling
        the other; none for a class with fewer than two methods to compare, or whose text does not parse."""
        first, last = measured.lines
        written = measured.file.read_text(encoding="utf-8").splitlines()[first - 1 : last]
        try:
            tree = ast.parse(textwrap.dedent("\n".join(written)))
        except SyntaxError:
            return None
        declared = next((found for found in ast.walk(tree) if isinstance(found, ast.ClassDef)), None)
        return MethodGroups(declared).count() if declared is not None else None

    def _imported_by(self, measured: MeasuredNode) -> list["Node"]:
        return [edge.child for edge in measured.reading.graph.edges.from_parent("dependsOn", measured.node)]

    def _importing(self, measured: MeasuredNode) -> list["Node"]:
        return [edge.parent for edge in measured.reading.in_graph.edge_index.of("dependsOn") if edge.child is measured.node]

    def _abstractness(self, measured: MeasuredNode) -> float | None:
        folder = measured.node.source.file
        classes = [node for node in measured.reading.in_graph.nodes("OoadClass") if self._directly_in(node, folder) and not is_test_code(node.source.file)]
        abstract = [node for node in classes if _ABSTRACT.search(node.source.text or "")]
        return round(len(abstract) / len(classes), _DECIMALS) if classes else None

    def _instability(self, measured: MeasuredNode) -> float | None:
        outward, inward = len(self._imported_by(measured)), len(self._importing(measured))
        return round(outward / (outward + inward), _DECIMALS) if outward + inward else None

    def _directly_in(self, node: "Node", folder: str | None) -> bool:
        """Whether node was read from a file that sits in folder itself, not in a folder beneath it."""
        file = node.source.file or ""
        return is_under(file, folder) and "/" not in file[len(folder or "") :].lstrip("/")


class MethodGroups:
    """The methods of one Python class, grouped: two methods are in one group when both use the same field of the
    object, or one calls the other. Constructors and the other double-underscore methods are left out, since a
    constructor assigns every field and would join every method whatever the class does."""

    def __init__(self, declared: ast.ClassDef) -> None:
        written = [item for item in declared.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))]
        self._methods = [method for method in written if not (method.name.startswith("__") and method.name.endswith("__"))]
        self._group = {method.name: method.name for method in self._methods}

    def count(self) -> int | None:
        if len(self._methods) < 2:
            return None
        users: dict[str, list[str]] = {}
        for method in self._methods:
            for used in self._used_by(method):
                if used in self._group:
                    self._join(method.name, used)
                else:
                    users.setdefault(used, []).append(method.name)
        for sharing in users.values():
            for other in sharing[1:]:
                self._join(sharing[0], other)
        return len({self._found(name) for name in self._group})

    def _used_by(self, method: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
        """Each name the method reads on its own object: a field, or a method it calls."""
        receiver = method.args.args[0].arg if method.args.args else None
        reads = (found for found in ast.walk(method) if isinstance(found, ast.Attribute) and isinstance(found.value, ast.Name))
        return {found.attr for found in reads if found.value.id == receiver}

    def _found(self, name: str) -> str:
        while self._group[name] != name:
            self._group[name] = self._group[self._group[name]]
            name = self._group[name]
        return name

    def _join(self, one: str, other: str) -> None:
        self._group[self._found(one)] = self._found(other)


# Each tool a project can choose, by the name its config writes; one of each is made for one taking of measures.
TOOLS: dict[str, type[MeasuringTool]] = {tool.name: tool for tool in (LizardTool, RadonTool, ReaderTool)}
