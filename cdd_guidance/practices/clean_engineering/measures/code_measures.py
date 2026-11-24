"""The measures Clean Engineering holds code to, the fact each is read from, and the tool and limit a project chooses.

A measure is one number about a function, a class, or a module, read from a fact on its node and named in plain English
wherever a person reads it. Most are facts the reader already keeps on every node it reads: an operation's lines and
parameters, a class's methods, a module's import loops and the modules it imports. A measure no such fact gives is
supplied by a tool, kept as a fact when the reader reads a file a read names: the paths through a function, its
readability score, a class's total complexity, the lines of a module's longest file and the maintainability index of
its least maintainable one. The practice's own reader is the tool for what the graph's nodes and edges give, such as
the classes a class depends on, the methods one call into it can set off, and the modules that import a module. A
module is measured over all its files and the packages inside it, so the fact on its node answers for the module as a
whole: its longest file, its least maintainable file, the average of its classes. Which tool supplies one depends on
the language the code is written in, so the choice is a table of measure by language, kept with the limits in the
project's ``.context/config.json`` under ``code_measures``. A project holds its code to the limits once its config has
that section; the section starts from the shipped table, which fills in Python, TypeScript and JavaScript, and lays
its own entries over it. Code in any other language has no tool chosen: the reader keeps why on the node
(``CodeMeasure.not_taken_fact``) and the measure's limit rule reports it by name until someone chooses one. A project
whose config has no such section has not chosen to measure its code: no tool is asked, and no limit is held."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Mapping

from harness.installation.context_config import ContextConfig

from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.clean_engineering.measures.read_facts import MODULE_IMPORT_LOOPS_FACT, IMPORTED_MODULES_FACT, counted_parameters, parameters_of

if TYPE_CHECKING:
    from harness.graph.graph import Node

# The section of ``.context/config.json`` that keeps the chosen tools and the limits.
CONFIG_SECTION = "code_measures"
# What a project writes in place of a tool when it has decided a measure is not taken in a language: a decision, where
# a missing entry is a choice nobody has made yet.
NOT_MEASURED = "not measured"
# The tool that is the practice's own reading of the code: a measure the graph's nodes and edges give needs no outside
# tool.
READER = "reader"
FUNCTION, CLASS, MODULE = "function", "class", "module"
# The node types each kind of measure is read on.
# A module is a folder that owns a module card; a folder with no card is a package, a part of its module, and is
# measured with it, never on its own.
NODE_TYPES = {FUNCTION: ("Operation", "Property"), CLASS: ("OoadClass",), MODULE: ("Module",)}


@dataclass(frozen=True)
class CodeMeasure:
    """One measure: its name, which the config chooses a tool and a limit under, what a table calls it in plain
    English, with the name a tool's own report gives it after it in brackets, how a sentence says a value of it, what
    it is a measure of, and where its value is read on a node: the fact of its own name, a fact the reader already
    keeps under another name (``existing``, counted when that fact is a list), or what ``read`` answers."""

    name: str
    label: str
    phrase: str
    of: str
    existing: str = ""
    counted: bool = False
    read: Callable[["Node"], float | int | None] | None = field(default=None, compare=False)
    # True for a measure where higher is better, such as a maintainability index: its limit is the least it may be.
    least: bool = False
    # How the answers for a module written in several languages, each from the tool chosen in that language, make one:
    # the first answer, unless the measure says otherwise, such as the longest of each language's longest files.
    combined: Callable[[list], float | int] | None = field(default=None, compare=False)

    @property
    def file_fact(self) -> str:
        """The fact a module keeps beside a measure taken of one of its files, such as its longest file: that file's
        path from the source root, which the measure's rule names."""
        return f"{self.name}_file"

    def is_past(self, value: float | int, limit: float | int) -> bool:
        """Whether value is past limit: above it, or below it for a measure where higher is better."""
        return value < limit if self.least else value > limit

    @property
    def past_said(self) -> str:
        """How a sentence says a value is past the limit: over it, or under it for a measure where higher is better."""
        return "under the limit of" if self.least else "over the limit of"

    def combine(self, answers: list) -> float | int:
        """One value from the answers of each language a module's files are written in."""
        return self.combined(answers) if self.combined is not None else answers[0]

    @property
    def not_taken_fact(self) -> str:
        """The fact a node keeps in place of the measure when no tool could take it, holding why: no tool chosen for
        its language, or a chosen tool that is not installed or does not take it. The measure's rule reports it."""
        return f"{self.name}_not_taken"

    def value_on(self, node: "Node") -> float | int | None:
        """The measure as node holds it; none when node holds no fact that gives it, and for the holder the class
        model gathers a file's own functions under, which is no class a person wrote."""
        if node.name == MODULE_FUNCTION_HOLDER and self.of == CLASS:
            return None
        if self.read is not None:
            return self.read(node)
        fact = self.existing or self.name
        if not node.has_fact(fact):
            return None
        value = node.get_fact(fact)
        return len(value or []) if self.counted else value

    def said_of(self, value: float | int) -> str:
        """The measure with its value, as a sentence says it: ``14 paths through it (cyclomatic complexity)``."""
        return self.phrase.format(value=f"{value:g}")


def _parameters_taken(node: "Node") -> int | None:
    """The parameters a caller supplies, counted from the function's parameter nodes as ``limit-operation-parameters``
    counts them: its own object is left out, and a packed tuple counts each value it carries. None for a property no
    getter backs, which is a field and takes nothing."""
    if node.type == "Property" and not node.get_fact("is_property"):
        return None
    return counted_parameters([parameter.name for parameter in parameters_of(node)], node.get_fact("packed_parameters", None) or {})


PATHS_THROUGH = CodeMeasure("paths_through", "paths through a function (cyclomatic complexity)", "{value} paths through it (cyclomatic complexity)", FUNCTION)
READABILITY_SCORE = CodeMeasure(
    "readability_score",
    "readability score of a function (cognitive complexity; higher is harder to read)",
    "a readability score of {value} (cognitive complexity; higher is harder to read)",
    FUNCTION,
)
CODE_LINES = CodeMeasure("code_lines", "lines in a function", "{value} lines", FUNCTION, existing="line_count")
PARAMETERS_TAKEN = CodeMeasure("parameters_taken", "parameters a function takes", "{value} parameters", FUNCTION, read=_parameters_taken)
TOTAL_COMPLEXITY = CodeMeasure(
    "total_complexity",
    "total complexity of a class (the paths through all its methods, added up)",
    "a total complexity of {value} (the paths through all its methods, added up)",
    CLASS,
)
METHOD_COUNT = CodeMeasure("method_count", "methods in a class", "{value} methods", CLASS, existing="method_count")
CLASSES_DEPENDED_ON = CodeMeasure("classes_depended_on", "classes a class depends on (coupling between objects)", "{value} classes it depends on (coupling between objects)", CLASS)
METHODS_SET_OFF = CodeMeasure(
    "methods_set_off",
    "methods one call into a class can set off (response for a class)",
    "{value} methods one call into it can set off (response for a class)",
    CLASS,
)
UNSHARED_METHOD_GROUPS = CodeMeasure(
    "unshared_method_groups",
    "groups of methods in a class that share no data with one another (lack of cohesion)",
    "{value} groups of methods that share no data with one another (lack of cohesion)",
    CLASS,
)
# A module's imports are those of its whole folder, the packages inside it included, to other modules
# (``reading/folder_facts.py``, ``ModuleImports``), which every read keeps.
IMPORT_LOOPS = CodeMeasure("import_loops", "loops of modules importing one another that a module is part of", "{value} import loops", MODULE, existing=MODULE_IMPORT_LOOPS_FACT, counted=True)
MODULES_IMPORTED = CodeMeasure("modules_imported", "modules a module imports (outgoing coupling)", "{value} modules it imports", MODULE, existing=IMPORTED_MODULES_FACT, counted=True)
MODULES_IMPORTING = CodeMeasure("modules_importing", "modules that import a module (incoming coupling)", "{value} modules that import it", MODULE)
LONGEST_FILE_LINES = CodeMeasure(
    "longest_file_lines", "lines of code in a module's longest file", "a file of {value} lines of code", MODULE, combined=max,
)
LEAST_MAINTAINABILITY = CodeMeasure(
    "least_maintainability",
    "maintainability index of a module's least maintainable file (0 to 100; higher is easier to change)",
    "a file with a maintainability index of {value} (0 to 100; higher is easier to change)",
    MODULE,
    least=True,
    combined=min,
)
AVERAGE_CLASS_COMPLEXITY = CodeMeasure(
    "average_class_complexity",
    "average total complexity of a module's classes",
    "classes whose total complexity averages {value} (the paths through all a class's methods, added up)",
    MODULE,
)
COPIED_CODE_BLOCKS = CodeMeasure("copied_code_blocks", "blocks of code a module repeats from another file", "{value} blocks of code repeated from another file", MODULE)
ABSTRACTNESS = CodeMeasure("abstractness", "share of a module's classes that are abstract (abstractness, 0 to 1)", "{value} of its classes abstract", MODULE)
INSTABILITY = CodeMeasure("instability", "share of a module's imports that go outward (instability, 0 to 1)", "{value} of its imports going outward", MODULE)

MEASURES: tuple[CodeMeasure, ...] = (
    PATHS_THROUGH, READABILITY_SCORE, CODE_LINES, PARAMETERS_TAKEN,
    TOTAL_COMPLEXITY, METHOD_COUNT, CLASSES_DEPENDED_ON, METHODS_SET_OFF, UNSHARED_METHOD_GROUPS,
    IMPORT_LOOPS, MODULES_IMPORTED, MODULES_IMPORTING, LONGEST_FILE_LINES, LEAST_MAINTAINABILITY, AVERAGE_CLASS_COMPLEXITY,
    COPIED_CODE_BLOCKS, ABSTRACTNESS, INSTABILITY,
)
MEASURE_NAMED = {measure.name: measure for measure in MEASURES}

# The tool that supplies each measure no fact on the node already gives, by language: what a project that measures
# its code starts with. Its own ``code_measures`` is laid over it, entry by entry. A measure that is not here is read
# from a fact the reader keeps on every node, and no tool is ever asked for it.
SHIPPED_TOOLS: dict[str, dict[str, str]] = {
    PATHS_THROUGH.name: {"python": "lizard", "typescript": "lizard", "javascript": "lizard"},
    READABILITY_SCORE.name: {"python": "lizard", "typescript": "lizard", "javascript": "lizard"},
    TOTAL_COMPLEXITY.name: {"python": "lizard", "typescript": "lizard", "javascript": "lizard"},
    CLASSES_DEPENDED_ON.name: {"python": READER, "typescript": READER, "javascript": READER},
    METHODS_SET_OFF.name: {"python": READER, "typescript": READER, "javascript": READER},
    UNSHARED_METHOD_GROUPS.name: {"python": READER, "typescript": NOT_MEASURED, "javascript": NOT_MEASURED},
    MODULES_IMPORTING.name: {"python": READER, "typescript": READER, "javascript": READER},
    LONGEST_FILE_LINES.name: {"python": "lizard", "typescript": "lizard", "javascript": "lizard"},
    # Radon takes the maintainability index of Python alone; no tool is shipped for it in the brace languages.
    LEAST_MAINTAINABILITY.name: {"python": "radon", "typescript": NOT_MEASURED, "javascript": NOT_MEASURED},
    AVERAGE_CLASS_COMPLEXITY.name: {"python": READER, "typescript": READER, "javascript": READER},
    COPIED_CODE_BLOCKS.name: {"python": NOT_MEASURED, "typescript": NOT_MEASURED, "javascript": NOT_MEASURED},
    ABSTRACTNESS.name: {"python": READER, "typescript": READER, "javascript": READER},
    INSTABILITY.name: {"python": READER, "typescript": READER, "javascript": READER},
}
# The most each measure may be before its rule reports the node, or the least, for a measure where higher is better. A
# measure with no limit is kept for information. ``one-way-deps`` holds a module to no import loop at all.
SHIPPED_LIMITS: dict[str, float] = {
    PATHS_THROUGH.name: 10,
    READABILITY_SCORE.name: 15,
    CODE_LINES.name: 50,
    PARAMETERS_TAKEN.name: 3,
    TOTAL_COMPLEXITY.name: 100,
    METHOD_COUNT.name: 30,
    CLASSES_DEPENDED_ON.name: 14,
    METHODS_SET_OFF.name: 50,
    UNSHARED_METHOD_GROUPS.name: 1,
    IMPORT_LOOPS.name: 0,
    MODULES_IMPORTING.name: 40,
    LONGEST_FILE_LINES.name: 800,
    LEAST_MAINTAINABILITY.name: 20,
    AVERAGE_CLASS_COMPLEXITY.name: 15,
}
# The measures the explorer tree shows under a node for information, with their value and no limit: no rule reads
# them, so none reports them.
SHOWN_WITHOUT_LIMIT: tuple[CodeMeasure, ...] = (MODULES_IMPORTED,)


class MeasureNotTaken(Exception):
    """A measure could not be taken of code that was read. The reader keeps the reason on the node, and the measure's
    limit rule reports it, so code nobody measured is never read as code within its limits."""


class NoToolChosen(MeasureNotTaken):
    """Code was read in a language the project has chosen no tool for, for one measure."""

    def __init__(self, measure: CodeMeasure, language: str, config: Path) -> None:
        chosen_under = f'"{CONFIG_SECTION}": "tools": "{measure.name}": "{language}"'
        super().__init__(
            f"No tool is chosen to measure '{measure.name}' ({measure.label}) in {language}. "
            f"Fix: choose a tool that takes '{measure.name}' in {language}, record it in {config} under {chosen_under}, "
            f'and install it; or write "{NOT_MEASURED}" there to leave the measure out.'
        )
        self.measure = measure
        self.language = language


class ChosenTools:
    """The tool a project chose for each measure a tool supplies, in each language, and the limit of each measure: the
    shipped choices with the project's own ``code_measures`` laid over them. A project with no ``code_measures`` chose
    none."""

    def __init__(self, chosen: Mapping[str, Any] | None = None, config: Path | None = None) -> None:
        # Whether the project's config holds the section at all: a project that never wrote it measures nothing.
        self.measures_code = isinstance(chosen, Mapping)
        chosen = chosen if isinstance(chosen, Mapping) else {}
        tools = chosen.get("tools") if isinstance(chosen.get("tools"), Mapping) else {}
        limits = chosen.get("limits") if isinstance(chosen.get("limits"), Mapping) else {}
        self._tools = {name: {**languages, **self._entries(tools.get(name))} for name, languages in SHIPPED_TOOLS.items()}
        self._limits = {**SHIPPED_LIMITS, **{str(name): limit for name, limit in limits.items() if isinstance(limit, (int, float))}}
        # The file a failure names as the place to choose a tool.
        self.config = config or Path(".context") / "config.json"

    @classmethod
    def of_project(cls, folder: Path) -> "ChosenTools":
        """The choices of the project whose top folder is folder, read from its ``.context/config.json``; none for a
        folder with no config of its own."""
        config = ContextConfig(folder)
        return cls(config.load().get(CONFIG_SECTION), config.path) if config.exists() else cls(None, config.path)

    def supplied_by_a_tool(self, measure: CodeMeasure) -> bool:
        """Whether a tool supplies measure, so the reader asks one for it; false for a measure read from a fact the
        reader already keeps."""
        return measure.name in self._tools

    def tool_name(self, measure: CodeMeasure, language: str) -> str | None:
        """The name of the tool chosen for measure in language; none when the project decided it is not measured
        there. Raises *NoToolChosen* when nobody has chosen."""
        chosen = self._tools.get(measure.name, {}).get(language)
        if chosen is None:
            raise NoToolChosen(measure, language, self.config)
        return None if chosen == NOT_MEASURED else chosen

    def limit(self, measure: CodeMeasure) -> float | None:
        """The most measure may be; none for a measure kept for information only, and for every measure of a project
        that has not chosen to measure its code."""
        return self._limits.get(measure.name) if self.measures_code else None

    def _entries(self, written: object) -> dict[str, str]:
        return {str(language): str(tool) for language, tool in written.items()} if isinstance(written, Mapping) else {}
