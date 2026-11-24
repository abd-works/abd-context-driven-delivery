"""The tools that take Clean Engineering's code measures, each behind one question: this measure, of this node.

A project names a tool for each measure no fact on the node already gives, in each language (``ChosenTools``): a
function's lines and parameters, a class's methods, and a module's import loops and imported modules are facts the
reader keeps on every read, and no tool repeats them. Lizard and radon are outside programs, each imported when first
asked, so a project that never checks code does not need them; a tool that is chosen and not installed is reported by
name, with how to install it, because a measure silently left out reads as code within its limits. The reader is the
practice's own reading of the code: a measure the graph's nodes and edges give is counted from them."""

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
    AVERAGE_CLASS_COMPLEXITY,
    CLASSES_DEPENDED_ON,
    INSTABILITY,
    LEAST_MAINTAINABILITY,
    LONGEST_FILE_LINES,
    METHODS_SET_OFF,
    MODULES_IMPORTING,
    MeasureNotTaken,
    PATHS_THROUGH,
    READABILITY_SCORE,
    READER,
    TOTAL_COMPLEXITY,
    UNSHARED_METHOD_GROUPS,
    CodeMeasure,
)
from cdd_guidance.practices.clean_engineering.measures.read_facts import IMPORTED_MODULES_FACT, IMPORTING_MODULES_FACT, is_under

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.measures.read_facts import MeasuredReading

# How the optional dependency group that holds the outside tools is installed, after the tool's own requirement.
_INSTALL = '   (or, from a CDD checkout: pip install -e ".[measures]")'
# What marks a class as abstract in the code of either language family.
_ABSTRACT = re.compile(r"\bABC\b|\bProtocol\b|@abstractmethod|\babstract\s+class\b|^\s*(?:export\s+)?interface\s", re.MULTILINE)
_DECIMALS = 2


class MeasuringToolNotInstalled(MeasureNotTaken):
    """A tool the project chose to take a measure is not installed where the code is read, so the measure cannot be
    taken. Nothing is skipped: the measure's rule reports the tool and how to install it."""

    def __init__(self, tool: str, measure: CodeMeasure, requirement: str) -> None:
        super().__init__(
            f"The tool '{tool}', chosen to measure '{measure.name}' ({measure.label}), is not installed. "
            f'Fix: install {tool}, the tool .context/config.json names for this measure, with: pip install "{requirement}"{_INSTALL}'
        )
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
    reading: "MeasuredReading"
    files: tuple[Path, ...]

    @property
    def file(self) -> Path:
        return self.files[0]

    @property
    def lines(self) -> tuple[int, int]:
        return self.node.source.start_line, self.node.source.end_line

    def keep_file(self, measure: CodeMeasure, file: Path) -> None:
        """Keep on the node, beside measure, the file of the module it was taken of, from the source root, for the
        measure's rule to name."""
        root = Path(self.reading.in_graph.source_root).resolve()
        resolved = file.resolve()
        self.node.set_fact(measure.file_fact, resolved.relative_to(root).as_posix() if root in resolved.parents else resolved.name)


class MeasuringTool:
    """One tool: its name in the config, and the measures it takes, each by the operation that reads it."""

    name = ""
    # What pip installs the tool from, which the failure for a tool that is not installed names.
    requirement = ""

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
            raise MeasuringToolNotInstalled(self.name, measure, self.requirement) from missing


class LizardTool(MeasuringTool):
    """Lizard, which reads a file in either language into its lines of code and its functions, each with its paths and
    its readability score (lizard's cognitive complexity extension); a class's total complexity is the paths of its
    functions added up, and a module's longest file the one of its files with the most lines of code. A file is read
    once."""

    name = "lizard"
    requirement = "lizard>=1.26"

    def __init__(self) -> None:
        super().__init__()
        self._read: dict[Path, Any] = {}
        self._takes = {
            PATHS_THROUGH.name: lambda measured: self._of_function(measured, PATHS_THROUGH, lambda found: found.cyclomatic_complexity),
            READABILITY_SCORE.name: lambda measured: self._of_function(measured, READABILITY_SCORE, lambda found: found.cognitive_complexity),
            TOTAL_COMPLEXITY.name: self._total_complexity,
            LONGEST_FILE_LINES.name: self._longest_file_lines,
        }

    def _file(self, file: Path, measure: CodeMeasure) -> Any:
        """What lizard reads of file: its lines of code and its functions."""
        if file not in self._read:
            lizard = self._imported("lizard", measure)
            extensions = lizard.get_extensions(["cognitive"])
            self._read[file] = next(iter(lizard.analyze_files([str(file)], exts=extensions, threads=1)))
        return self._read[file]

    def _functions(self, file: Path, measure: CodeMeasure) -> list:
        return list(self._file(file, measure).function_list)

    def _longest_file_lines(self, measured: MeasuredNode) -> int | None:
        """The lines of code, blank lines and comments left out, of the module's file that has the most; the module
        keeps which file that is."""
        counted = {file: self._file(file, LONGEST_FILE_LINES).nloc for file in measured.files}
        if not counted:
            return None
        longest = max(counted, key=lambda file: counted[file])
        measured.keep_file(LONGEST_FILE_LINES, longest)
        return counted[longest]

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
    """Radon, which takes the maintainability index of a Python file: 0 to 100, from its size, the paths through its
    functions, the variety of its names and operators (Halstead volume) and its comments, higher being easier to change.
    A module's measure is its least maintainable file, which the module keeps; a file that does not parse is left out,
    since ``source-parses`` reports it."""

    name = "radon"
    requirement = "radon>=6"

    def __init__(self) -> None:
        super().__init__()
        self._takes = {LEAST_MAINTAINABILITY.name: self._least_maintainability}

    def _least_maintainability(self, measured: MeasuredNode) -> float | None:
        metrics = self._imported("radon.metrics", LEAST_MAINTAINABILITY)
        indexes: dict[Path, float] = {}
        for file in measured.files:
            try:
                indexes[file] = round(metrics.mi_visit(file.read_text(encoding="utf-8"), multi=True), 1)
            except SyntaxError:
                continue
        if not indexes:
            return None
        least = min(indexes, key=lambda file: indexes[file])
        measured.keep_file(LEAST_MAINTAINABILITY, least)
        return indexes[least]


class ReaderTool(MeasuringTool):
    """The practice's own reading of the code: the measures counted from the graph's nodes and edges that no fact
    keeps yet, and the groups of a Python class's methods that share no data, read from the class's own text."""

    name = READER

    def __init__(self) -> None:
        super().__init__()
        self._takes = {
            CLASSES_DEPENDED_ON.name: self._classes_depended_on,
            METHODS_SET_OFF.name: self._methods_set_off,
            UNSHARED_METHOD_GROUPS.name: self._unshared_method_groups,
            MODULES_IMPORTING.name: lambda measured: len(self._importing(measured)),
            AVERAGE_CLASS_COMPLEXITY.name: self._average_class_complexity,
            ABSTRACTNESS.name: self._abstractness,
            INSTABILITY.name: self._instability,
        }

    def _classes_depended_on(self, measured: MeasuredNode) -> int:
        """The other classes an edge of any kind leads to from the class."""
        edges = measured.reading.in_graph.edge_index
        reached = {id(edge.child) for kind in edges.types for edge in measured.reading.graph.edges.from_parent(kind, measured.node) if edge.child.type == "OoadClass"}
        return len(reached - {id(measured.node)})

    def _methods_set_off(self, measured: MeasuredNode) -> int:
        """The class's own methods, and each method of another class or module function one of them calls (response
        for a class): what one call into the class can set off, one step deep. A getter counts as a method, a plain
        field as none; a call the read could not join to a member is not counted."""
        edges = measured.reading.graph.edges
        own = [edge.child for edge in edges.from_parent("owns", measured.node) if self._is_method(edge.child)]
        held = {id(method) for method in own}
        called = {id(edge.child) for method in own for edge in edges.from_parent("invokes", method) if self._is_method(edge.child)}
        return len(own) + len(called - held)

    def _is_method(self, member: "Node") -> bool:
        return member.type == "Operation" or bool(member.get_fact("is_property"))

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

    def _imported_by(self, measured: MeasuredNode) -> list[str]:
        """The modules the module imports, the packages inside it included, as every read keeps them."""
        return list(measured.node.get_fact(IMPORTED_MODULES_FACT) or []) if measured.node.has_fact(IMPORTED_MODULES_FACT) else []

    def _importing(self, measured: MeasuredNode) -> list[str]:
        """The modules that import the module or a package inside it, as every read keeps them."""
        return list(measured.node.get_fact(IMPORTING_MODULES_FACT) or []) if measured.node.has_fact(IMPORTING_MODULES_FACT) else []

    def _classes_of_module(self, measured: MeasuredNode) -> list["Node"]:
        """The module's production classes: those of its own files and of the packages inside it, not those of a
        module nested in it, which is measured on its own."""
        folder = measured.node.source.file
        nested = [module.source.file for module in measured.reading.in_graph.nodes("Module") if module is not measured.node and is_under(module.source.file, folder)]
        return [
            node for node in measured.reading.in_graph.nodes("OoadClass")
            if is_under(node.source.file, folder) and not any(is_under(node.source.file, inner) for inner in nested) and not measured.reading.test_code.is_test_code(node.source.file)
        ]

    def _abstractness(self, measured: MeasuredNode) -> float | None:
        """The share of the module's classes that are abstract."""
        classes = self._classes_of_module(measured)
        abstract = [node for node in classes if _ABSTRACT.search(node.source.text or "")]
        return round(len(abstract) / len(classes), _DECIMALS) if classes else None

    def _average_class_complexity(self, measured: MeasuredNode) -> float | None:
        """The total complexity of the module's classes, averaged over those a tool measured; none when it measured
        none. The classes are measured before their module, so their total complexity is on their nodes."""
        totals = [total for total in (TOTAL_COMPLEXITY.value_on(node) for node in self._classes_of_module(measured)) if total is not None]
        return round(sum(totals) / len(totals), _DECIMALS) if totals else None

    def _instability(self, measured: MeasuredNode) -> float | None:
        outward, inward = len(self._imported_by(measured)), len(self._importing(measured))
        return round(outward / (outward + inward), _DECIMALS) if outward + inward else None



class MethodGroups:
    """The methods of one Python class, grouped: two methods are in one group when both use the same field of the
    object, or one calls the other. Constructors and the other double-underscore methods are left out, since a
    constructor assigns every field and would join every method whatever the class does. A method that uses no field
    of the object and calls no method of it is left out too: it shares no data because it holds none, so it is no
    second job the class does."""

    def __init__(self, declared: ast.ClassDef) -> None:
        written = [item for item in declared.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))]
        self._methods = [method for method in written if not (method.name.startswith("__") and method.name.endswith("__"))]
        self._group = {method.name: method.name for method in self._methods}

    def count(self) -> int | None:
        """How many groups the methods that use the object fall into; none with fewer than two such methods, which
        leave nothing to compare."""
        users: dict[str, list[str]] = {}
        using_the_object: set[str] = set()
        for method in self._methods:
            for used in self._used_by(method):
                using_the_object.add(method.name)
                if used in self._group:
                    using_the_object.add(used)
                    self._join(method.name, used)
                else:
                    users.setdefault(used, []).append(method.name)
        for sharing in users.values():
            for other in sharing[1:]:
                self._join(sharing[0], other)
        if len(using_the_object) < 2:
            return None
        return len({self._found(name) for name in using_the_object})

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
