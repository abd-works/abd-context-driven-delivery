"""Second registries: a list, tuple, or dict a file assigns that names the same classes another file's collection
already names. Two registries of one set of classes drift, since a class added to one is missing from the other, and
a caller cannot tell which is the one the program trusts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.reading.folder_facts import folders_of, record_fact
from cdd_guidance.practices.source_code import BracketStructure

if TYPE_CHECKING:
    from harness.graph.graph import Node, PracticeNodes

    from cdd_guidance.practices.clean_engineering.reading.production_classes import ProductionClasses

# The fact a folder keeps for each file of it whose collection names classes another file's collection names: the
# file, its collection and how many classes it names, the other file, its collection and its count, and the classes
# both name.
SECOND_REGISTRIES = "second_registries"
# The folder fact that lists each production file a folder holds, by its path from the source root.
_FILES_FACT = "imported_classes_by_file"
# A collection assigned to a name, at a module's top level or on an object: `RULES = (`, `self._kinds = [`,
# `export const KINDS = {`.
_ASSIGNED_COLLECTION = re.compile(
    r"^[ \t]*(?:export\s+)?(?:(?:const|let|var)\s+)?(?:self\.|this\.)?(?P<name>[A-Za-z_$][\w$]*)\s*(?::[^=\n]*)?=\s*(?P<open>[\[\(\{])",
    re.M,
)
_NAME = r"(?<![\w.$])[A-Z][\w$]*(?![\w$])"
# A capitalised name used as a value. A script object's key (`Epic: 'epic'`) is a label, so in a script it is left
# out; a Python dict keyed by classes is a registry, so there it counts.
_VALUE_NAME = {".py": re.compile(_NAME), "script": re.compile(_NAME + r"(?!\s*:)")}
_STRING = re.compile(r"""\"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`""")
# The lists a module exports its names by, which name what a file offers, not a registry it keeps.
_EXPORT_LISTS = frozenset({"__all__"})
_CLOSERS = {"[": "]", "(": ")", "{": "}"}
# A collection must name at least two classes to be a registry worth comparing.
_FEWEST_CLASSES_COMPARED = 2


class SecondRegistries:
    """Each production file's collections that name classes of the graph, compared across files; the folder of each
    file keeps the pairs its files take part in, with the classes they share (``second_registries``)."""

    def __init__(self, in_graph: "PracticeNodes", classes: "ProductionClasses") -> None:
        self._test_code = in_graph.practice.reading.test_code
        self._root = Path(in_graph.source_root) if in_graph.source_root else None
        self._folders = folders_of(in_graph)
        self._class_names = {each.name for each in classes}

    def record(self) -> None:
        pairs = self._pairs([registry for folder in self._folders for file in self._files_of(folder) for registry in self._registries_in(file)])
        for folder in self._folders:
            record_fact(folder, SECOND_REGISTRIES, [pair for file in self._files_of(folder) for pair in pairs.get(file, [])])

    def _pairs(self, registries: list[tuple[str, str, set[str]]]) -> dict[str, list[list]]:
        """Each two collections in different files that name classes in common, by the file that sorts first."""
        pairs: dict[str, list[list]] = {}
        for index, (file, name, named) in enumerate(registries):
            for other_file, other_name, other_named in registries[index + 1 :]:
                shared = sorted(named & other_named)
                if other_file != file and len(shared) >= _FEWEST_CLASSES_COMPARED:
                    first, second = sorted([(file, name, len(named)), (other_file, other_name, len(other_named))])
                    pairs.setdefault(first[0], []).append([*first, *second, shared])
        return pairs

    def _files_of(self, folder: "Node") -> list[str]:
        held = folder.get_fact(_FILES_FACT) if folder.has_fact(_FILES_FACT) else {}
        return sorted(file for file in (held or {}) if not self._test_code.is_test_code(file))

    def _registries_in(self, file: str) -> list[tuple[str, str, set[str]]]:
        """Each collection the file assigns to a name, with the classes of the graph it names."""
        text = self._text_of(file)
        found: list[tuple[str, str, set[str]]] = []
        for assigned in _ASSIGNED_COLLECTION.finditer(text):
            named = self._classes_named(text, assigned.start("open"), _VALUE_NAME[".py" if file.endswith(".py") else "script"])
            if len(named) >= _FEWEST_CLASSES_COMPARED and assigned.group("name") not in _EXPORT_LISTS:
                found.append((file, assigned.group("name"), named))
        return found

    def _classes_named(self, text: str, opened: int, value_name: re.Pattern) -> set[str]:
        """The classes of the graph the collection opened at opened names as values: its strings, which may spell a
        class's name as a label, and an object's keys are left out."""
        closed = BracketStructure(text).closing_bracket(opened, text[opened], _CLOSERS[text[opened]])
        body = _STRING.sub('""', text[opened:closed]) if closed is not None else ""
        return set(value_name.findall(body)) & self._class_names

    def _text_of(self, file: str) -> str:
        """The file's text, which the read has already decoded; empty for a graph with no source root, or a file gone
        from it since the graph was saved."""
        path = self._root / file if self._root is not None else None
        return path.read_text(encoding="utf-8") if path is not None and path.is_file() else ""
