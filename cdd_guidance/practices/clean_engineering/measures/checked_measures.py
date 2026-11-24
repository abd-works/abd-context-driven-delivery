"""The code measures a tool supplies, which the reader keeps of the files a read names, such as the files a validate
checks: each function, class and module read from them asks the tool its project chose for each such measure in its
language, and keeps the answer as a fact on its node. A measure no tool could take is kept as the reason why, for the
measure's rule to report. A measure a fact on the node already gives, such as a function's lines, is not asked for."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.measures.code_measures import CLASS, FUNCTION, MEASURES, MODULE, ChosenTools, CodeMeasure, MeasureNotTaken
from cdd_guidance.practices.clean_engineering.model import MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.clean_engineering.measures.measuring_tools import MeasuredNode, MeasuringTool, ToolDoesNotTakeMeasure
from cdd_guidance.practices.clean_engineering.measures.read_facts import DESCRIBED_FACT, is_under
from cdd_guidance.practices.source_code import CODE_LANGUAGES

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.measures.read_facts import MeasuredReading

# The language each file extension is written in, as the practice's readers name it.
_LANGUAGE_OF = {suffix: language.name for language in CODE_LANGUAGES for suffix in language.suffixes}


class CheckedCodeMeasures:
    """The measures of the production code among the files a read names. Test code is left out, as every production
    rule leaves it out, and so is the holder the class model gathers a file's own functions under, which is no class a
    person wrote. A measure no tool could take, because none is chosen for the file's language or the chosen one is
    not installed, is kept as its reason on the first function or class of the file it was asked of, and on the
    module, so its rule reports it once for the file and not for every function in it."""

    def __init__(self, reading: "MeasuredReading", files: list[Path], chosen: ChosenTools, tools: dict[str, type[MeasuringTool]]) -> None:
        self._reading = reading
        self._chosen = chosen
        # One of each tool for this taking, made when first asked, so a file a tool reads is read once.
        self._tool_types = tools
        self._tools: dict[str, MeasuringTool] = {}
        # Each measure already kept as not taken, with the files it was asked of, so one node of a file says so.
        self._not_taken: set[tuple[str, tuple[Path, ...]]] = set()
        root = Path(reading.in_graph.source_root).resolve()
        named = {self._from_root(file, root): file.resolve() for file in files}
        # Each checked production code file, by its path from the source root.
        self._files = {relative: file for relative, file in named.items() if relative and file.suffix in _LANGUAGE_OF and not reading.test_code.is_test_code(relative)}

    def take(self) -> None:
        """Keep each measure of each function, class and module read from the checked files on its node."""
        in_graph = self._reading.in_graph
        functions = [node for kind in ("Operation", "Property") for node in in_graph.nodes(kind) if self._is_function(node)]
        classes = [node for node in in_graph.nodes("OoadClass") if not node.get_fact(DESCRIBED_FACT) and node.name != MODULE_FUNCTION_HOLDER]
        for of, nodes in ((FUNCTION, functions), (CLASS, classes)):
            for node in nodes:
                file = self._files.get(node.source.file or "")
                if file is not None:
                    self._measure(node, of, {_LANGUAGE_OF[file.suffix]: (file,)})
        modules = in_graph.nodes("Module")
        for module in modules:
            by_language = self._files_in(module, [other.source.file for other in modules if other is not module])
            if by_language:
                self._measure(module, MODULE, by_language)

    def _is_function(self, node: "Node") -> bool:
        """An operation, or a property a getter backs, whose node holds the getter's code."""
        return node.type == "Operation" or bool(node.get_fact("is_property"))

    def _files_in(self, module: "Node", others: list[str]) -> dict[str, tuple[Path, ...]]:
        """The checked files the module holds, by the language each is written in: those in its folder and in the
        packages inside it, whose folders own no module card, and not those of a module nested in it, which is
        measured on its own."""
        held = module.source.file or ""
        nested = [other for other in others if other and other != held and is_under(other, held)]
        found: dict[str, tuple[Path, ...]] = {}
        for relative, file in self._files.items():
            if is_under(relative, held) and not any(is_under(relative, inner) for inner in nested):
                language = _LANGUAGE_OF[file.suffix]
                found[language] = (*found.get(language, ()), file)
        return found

    def _measure(self, node: "Node", of: str, files: dict[str, tuple[Path, ...]]) -> None:
        """Keep each measure taken of this kind of node: the first answer among the languages its files are written
        in, each asked of the tool chosen for the measure in that language."""
        for measure in (measure for measure in MEASURES if measure.of == of and self._chosen.supplied_by_a_tool(measure)):
            answers = (self._answer(measure, language, MeasuredNode(node, self._reading, held)) for language, held in files.items())
            value = next((answer for answer in answers if answer is not None), None)
            if value is None:
                continue
            if measure.name in node.graph_facts:
                setattr(node, measure.name, value)
            else:
                node.set_fact(measure.name, value)

    def _answer(self, measure: CodeMeasure, language: str, measured: MeasuredNode) -> float | int | None:
        """The measure of the node, from the tool chosen for it in language; none when the project says it is not
        measured there, when the tool finds nothing to measure, and when no tool could take it, which the node keeps."""
        try:
            name = self._chosen.tool_name(measure, language)
            return self._tool(name, measure).value(measure, measured) if name is not None else None
        except MeasureNotTaken as reason:
            if (measure.name, measured.files) not in self._not_taken:
                self._not_taken.add((measure.name, measured.files))
                measured.node.set_fact(measure.not_taken_fact, str(reason))
            return None

    def _tool(self, name: str, measure: CodeMeasure) -> MeasuringTool:
        if name not in self._tools:
            if name not in self._tool_types:
                raise ToolDoesNotTakeMeasure(name, measure, [])
            self._tools[name] = self._tool_types[name]()
        return self._tools[name]

    def _from_root(self, file: Path, root: Path) -> str:
        """file as a node's source names it, from the source root; empty for a file outside it."""
        resolved = file.resolve()
        return resolved.relative_to(root).as_posix() if root in resolved.parents else ""
