"""How a story map writes itself onto the practice that holds Stories in a graph.

Each story object is its own graph node: the epic, story, background, scenario, step, and example the map read are
added to the graph as they are, each by its own ``record``, so rules read the scenario, its steps, and its story
straight from them. A node keeps as its own facts only what the object does not know, such as the exports of the file
its story was read from. Where each node sits is read from the files the map was read from (its *StorySources*), which
the map keeps; nothing is read from disk again.
"""

from __future__ import annotations

import re
from functools import cached_property
from typing import TYPE_CHECKING, Callable, Iterator, Optional
from pathlib import Path, PurePosixPath

from harness.graph.graph import Node, as_code_writes
from harness.graph.location import Location

from cdd_guidance.practices.stories.model.story_map_files import source_at

if TYPE_CHECKING:
    from harness.graph.graph import Source
    from harness.guidance.guidance import PracticeGuidance

    from cdd_guidance.practices.stories.model.story_map import Background, Step, Story, StoryMap, StoryNode

_EXPORT_CONST = re.compile(r"export const (\w+)")
_DOMAIN_CLASS = re.compile(r"\bclass\s+([A-Z]\w*)\b")
_NAMED_IMPORT = re.compile(r"import\s*(?:type\s*)?\{(?P<names>[^}]+)\}\s*from\s*['\"](?P<module>[^'\"]+)['\"]")
# Python `from .examples.customers_examples import valid_customer, (a as b)`.
_PYTHON_FROM_IMPORT = re.compile(r"^\s*from\s+(?P<module>\.*[\w.]*)\s+import\s+(?P<names>\([^)]*\)|[^#\r\n]+)", re.M)

# What each language declares an example as, by the suffix of the file: a TypeScript or JavaScript function or constant,
# a Python module-level function or constant.
_SCRIPT_DECLARATION = re.compile(r"\bfunction\s+([\w$]+)\b|\b(?:const|let|var)\s+([\w$]+)\s*[:=]")
_EXAMPLE_DECLARATIONS = {
    ".ts": _SCRIPT_DECLARATION,
    ".tsx": _SCRIPT_DECLARATION,
    ".js": _SCRIPT_DECLARATION,
    ".jsx": _SCRIPT_DECLARATION,
    ".mjs": _SCRIPT_DECLARATION,
    ".py": re.compile(r"^(?:async\s+)?def\s+(\w+)|^([A-Za-z_]\w*)\s*(?::[^=\n]+)?=(?!=)", re.M),
}
_IDENTIFIER = re.compile(r"\w+")
_MEMBER_READ = re.compile(r"\.(\w+)")

_EVIDENCE_LINE = re.compile(r"\*\s*Evidence:\s*([A-Za-z][A-Za-z ,-]*)")

def example_source_file(story_test: str, imported_modules: dict[str, str], name: str) -> str:
    """The file the example called name comes from, named from the project like story_test: the module story_test
    imports it from, with story_test's own extension and, for a relative import, resolved against story_test's folder;
    else story_test itself, which declares the example."""
    module = imported_modules.get(name)
    if module is None:
        return story_test
    suffix = PurePosixPath(story_test).suffix
    if not module.startswith("."):
        return _module_file(module, suffix)
    parts: list[str] = list(PurePosixPath(story_test).parent.parts)
    for part in PurePosixPath(module).parts:
        if part == "..":
            parts = parts[:-1]
        elif part != ".":
            parts.append(part)
    return _module_file("/".join(parts), suffix)


def _module_file(module: str, suffix: str) -> str:
    """The file a module's path names: the path with suffix, unless the import already writes it, as a JavaScript
    module's import does (``./order.examples.js``)."""
    return module if module.endswith(suffix) else module + suffix


def imported_files(file: str, imported_modules: dict[str, str]) -> list[str]:
    """The files the code file at file can import its names from, named from the project like file, with file's own
    extension. A relative import names one file; a module named from a package root (a Python import) may sit
    under any folder above file, so each of those is a place it can be, and a reader keeps the ones that are there."""
    relative = {example_source_file(file, imported_modules, name) for name, module in imported_modules.items() if module.startswith(".")}
    suffix = PurePosixPath(file).suffix
    rooted = {
        (folder / _module_file(module, suffix)).as_posix().removeprefix("./")
        for module in set(imported_modules.values()) if not module.startswith(".")
        for folder in PurePosixPath(file).parents
    }
    return sorted(relative | rooted)


class StorySource:
    """One file a story map was read from: its path from the project and its text, and what the story nodes recorded
    from it read there: its lines, the names it imports and exports, the examples it declares, and the evidence a
    sub-epic file declares. Each is scanned once, since every story of a file asks about the same text."""

    def __init__(self, file: str, text: str) -> None:
        self.file = file
        self.text = text

    @cached_property
    def lines(self) -> list[str]:
        return self.text.splitlines()

    @cached_property
    def imported_modules(self) -> dict[str, str]:
        """Each name the file imports, mapped to the module it comes from, written as a path without its extension the
        way the story test's language names it: TypeScript and JavaScript as the import says, Python with its dots
        turned into folders."""
        imported: dict[str, str] = {}
        for name, module in [*self._script_imports(), *self._python_imports()]:
            if name and name != "*":
                imported.setdefault(name, module)
        return imported

    @cached_property
    def exported_names(self) -> list[str]:
        return _EXPORT_CONST.findall(self.text)

    @property
    def facts(self) -> dict:
        """Facts a story file owns: they sit on the Story node, and its scenarios, steps, and examples read them through
        get_fact."""
        return {
            "export_names": list(self.exported_names),
            "domain_class_names": _DOMAIN_CLASS.findall(self.text),
            "imported_modules": dict(self.imported_modules),
        }

    @cached_property
    def evidence(self) -> list[str]:
        """The evidence a sub-epic file declares in its opening docblock; none when it declares none."""
        declared = _EVIDENCE_LINE.search(self._opening_docblock())
        return [part.strip() for part in declared.group(1).split(",") if part.strip()] if declared else []

    @property
    def declares_examples(self) -> bool:
        """True for a file in a language that declares examples, where an example's export is looked for."""
        return PurePosixPath(self.file).suffix in _EXAMPLE_DECLARATIONS

    @cached_property
    def declared_examples(self) -> list[str]:
        """The names the file declares the way its language declares an example; none for a file in no language that
        declares them."""
        declaration = _EXAMPLE_DECLARATIONS.get(PurePosixPath(self.file).suffix)
        found = declaration.findall(self.text) if declaration is not None else []
        return [name for match in found for name in (match if isinstance(match, tuple) else (match,)) if name]

    def example_source(self, name: str) -> str:
        """The file the example called name comes from: the module this story file imports it from, else this file."""
        return example_source_file(self.file, self.imported_modules, name)

    def imported_example_files(self) -> list[str]:
        """The files this story test imports names from, named from the project: where its examples can come from. A
        relative import names one file; a module named from a package root (a Python import) may sit under any
        folder above the story test, so each of those is a place it can be, and only the ones that are there are read."""
        return imported_files(self.file, self.imported_modules)

    def _script_imports(self) -> list[tuple[str, str]]:
        return [
            (part.strip().split(" as ")[-1].removeprefix("type ").strip(), match.group("module"))
            for match in _NAMED_IMPORT.finditer(self.text)
            for part in match.group("names").split(",")
        ]

    def _python_imports(self) -> list[tuple[str, str]]:
        found = []
        for match in _PYTHON_FROM_IMPORT.finditer(self.text):
            dotted = match.group("module")
            level = len(dotted) - len(dotted.lstrip("."))
            folders = dotted.lstrip(".").replace(".", "/")
            module = folders if level == 0 else ("./" if level == 1 else "../" * (level - 1)) + folders
            for part in match.group("names").strip("()").split(","):
                found.append((part.strip().split(" as ")[-1].strip(), module))
        return found

    def _opening_docblock(self) -> str:
        """The file's first `/** … */` comment, when it comes before any story."""
        start = self.text.find("/**")
        end = self.text.find("*/", start)
        if start == -1 or end == -1 or "Story:" in self.text[start:end]:
            return ""
        return self.text[start:end]


class StorySources:
    """The files a story map was read from, each once, by its path from the project: recording the map on a graph finds
    each node's lines in them without reading a file again."""

    def __init__(self) -> None:
        self._by_file: dict[str, StorySource] = {}

    def add(self, file: str, text: str) -> None:
        self._by_file[file] = StorySource(file, text)

    def take(self, other: "StorySources") -> None:
        """Hold every file other holds as well."""
        for source in other:
            self._by_file[source.file] = source

    def of(self, file: str) -> StorySource:
        """The file read at file; an empty one for a file the map was not read from."""
        return self._by_file.get(file) or StorySource(file, "")

    def __iter__(self) -> Iterator[StorySource]:
        return iter([self._by_file[file] for file in sorted(self._by_file)])


class StoryRecording:
    """One writing of a story map onto the practice that holds Stories: the practice and graph it writes to, where in
    the map's own files each node sits, and how many stories it has announced. The map makes one per ``record`` and
    each node records itself through it."""

    def __init__(self, story_map: "StoryMap", practice: PracticeGuidance, on_node: Optional[Callable[[str], None]]) -> None:
        self.story_map = story_map
        self.practice = practice
        self.graph = practice.reading.graph
        self._in_graph = practice.reading.in_graph
        self.on_node = on_node
        self.story_at = 0
        self.story_total = len(story_map.descendants.stories())
        self._cursor: dict[str, int] = {}

    def write(self) -> None:
        for epic in self.story_map.epics:
            epic.record(self, self._in_graph.root)
        for story in self.story_map.unplaced_stories:
            story.record(self, None)

    def announce(self, story: "Story") -> None:
        self.story_at += 1
        if self.on_node is not None:
            self.on_node(f"{self.story_at}/{self.story_total} · {story.name}")

    def add(self, story_object: "StoryNode", node_id: str, lines: "Source") -> Node:
        """story_object added as the graph node node_id, called by its recorded name and of its recorded type, at
        lines; the node already called node_id when two objects share it."""
        if not self._in_graph.holds(node_id):
            story_object.name = story_object.recorded_name
            story_object.type = story_object.recorded_type
        node = self._in_graph.add(story_object, node_id, Location(lines.file or ".", lines.start_line, lines.end_line or lines.start_line))
        self._align(node, story_object)
        return node

    def _align(self, node: Node, story_object: "StoryNode") -> None:
        """Move node, story_object's node, onto the lines that declare it, since the map read it by a nearby line: a
        step sits on its label's line; a scenario, story, or background runs to the close of its call; an example sits
        on its export, or on its row of the table a markdown scenarios file declares it in. Where an example is declared is the story object's to say: the graph may answer with a node it
        already held, such as one added for its file, which knows nothing of the example."""
        if node.type in {"Step", "Given", "When", "Then"}:
            node.source.align_to_label(node.name)
        elif node.type in {"Scenario", "Story", "Background"}:
            node.source.widen_to_call_close()
        elif node.type == "Example" and PurePosixPath(node.source.file or "").suffix.lower() == ".md":
            node.source.align_to_table_row(node.name)
        elif node.type == "Example" and story_object.declaration is not None:
            node.source.align_to_declaration(*story_object.declaration)
        elif node.type == "Example":
            node.source.align_to_example_export(node.name, self._example_files)

    def source_of(self, file: str) -> StorySource:
        """The file the map was read from at file; an empty one when it was read from none there."""
        return self.story_map.sources.of(file)

    @cached_property
    def _example_files(self) -> list[Path]:
        """The code files an example's export is looked for in: the ones the story map was read from, so a read of the
        files being edited opens no file it did not read, and nothing outside the folders a read scans."""
        root = self._in_graph.source_root
        if not root:
            return []
        return [Path(root) / source.file for source in self.story_map.sources if source.declares_examples]

    @cached_property
    def _example_declarations(self) -> dict[str, str]:
        """Each example the code the story map was read from declares, in the way its language declares one (a
        function or a constant), mapped to the first file's text that declares it."""
        declarations: dict[str, str] = {}
        for source in self.story_map.sources:
            for name in source.declared_examples:
                declarations.setdefault(name, source.text)
        return declarations

    def example_facts(self, file: str, name: str) -> dict:
        """The facts of the example called name that story file declares or imports. They save with the graph, so a
        reader in any process has them:

        - ``source_names`` and ``source_reads``: every identifier, and every name read as a member (``.name``), in the
          first code file the map was read from that declares name as its language declares an example (a TypeScript or
          JavaScript function or constant, a Python function or constant), so an example
          is linked to the classes it shows and the properties it reads;
        - ``export_names``: the names exported by the file the example comes from, when that is another file the map
          read (an examples module the story test imports); otherwise the story file's own apply."""
        text = self._example_declarations.get(name, "")
        facts = {"source_names": sorted(set(_IDENTIFIER.findall(text))), "source_reads": sorted(set(_MEMBER_READ.findall(text)))}
        origin = self.source_of(self.source_of(file).example_source(name))
        if origin.file != file and origin.text:
            facts["export_names"] = list(origin.exported_names)
        return facts

    def name_span(self, file: str, name: str, folder: str) -> "Source":
        """The line of file that names name; the folder alone when no line of file does."""
        line = next((index for index, text in enumerate(self.source_of(file).lines, start=1) if name and name in text), None)
        return source_at(file, line) if line is not None else source_at(folder or ".")

    def span_of(self, node: "StoryNode", file: str, fallback_text: str = "") -> "Source":
        """The lines of file node was read from, when its reader named them; else the next line of file that holds its
        text."""
        if node.has_source_file and node.source.start_line:
            return source_at(file, node.source.start_line, node.source.end_line or node.source.start_line)
        line = self._next_line(file, fallback_text or node.name)
        return source_at(file, line)

    def background_span(self, background: "Background", file: str) -> "Source":
        """The lines of file background was read from: where its reader named them; else, from its first step's line,
        the nearest line above that names it in whatever case the file writes its heading (``### Background``), or that
        step's line when the map kept no text of file; else the next line that holds its name."""
        first = next((step.source.start_line for step in background.steps if step.source is not None and step.source.start_line), 0)
        if not first or (background.has_source_file and background.source.start_line):
            return self.span_of(background, file)
        name = background.recorded_name.casefold()
        lines = self.source_of(file).lines
        heading = next((line for line in range(min(first, len(lines)) - 1, 0, -1) if name in lines[line - 1].casefold()), first)
        return source_at(file, heading)

    def _next_line(self, file: str, text: str) -> int:
        lines = self.source_of(file).lines
        start = self._cursor.get(file, 0)
        if not text:
            return 1
        # Search on from the last node found first, so a repeated name lands on its own entry; a diagram
        # need not list its cells in the map's order, so search from the top when that finds nothing.
        written = as_code_writes(text)
        for index in [*range(start, len(lines)), *range(0, start)]:
            if any(form in lines[index] for form in written):
                self._cursor[file] = index + 1
                return index + 1
        return 1

    def place(self, node: "StoryNode", lines: "Source") -> None:
        """Name the file and lines on a node that names no file yet."""
        if not file_of(node):
            node.source = source_at(lines.file or ".", lines.start_line, lines.end_line)


def file_of(node: "StoryNode") -> str:
    """The file the node was read from; empty while it only holds the placeholder a new node starts with."""
    if not node.has_source_file:
        return ""
    return str(node.source.file).replace("\\", "/")
