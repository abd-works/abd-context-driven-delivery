"""How a story map writes itself onto the practice that holds Stories in a graph.

Each story object is its own graph node: the epic, story, background, scenario, step, and example the map read are
added to the graph as they are, each by its own ``record``, so rules read the scenario, its steps, and its story
straight from them. A node keeps as its own facts only what the object does not know, such as the exports of the file
its story was read from. Where each node sits is read from the text of the files the map was read from, which the map
keeps; nothing is read from disk again.
"""

from __future__ import annotations

import re
import zlib
from functools import cached_property
from typing import TYPE_CHECKING, Callable, Optional
from pathlib import Path, PurePosixPath

from harness.graph.graph import Node

from cdd_guidance.practices.stories.model.story_map_files import source_at

if TYPE_CHECKING:
    from harness.graph.graph import Source

    from cdd_guidance.practices.stories.model.story_model import StoryModel

_EXPORT_CONST = re.compile(r"export const (\w+)")
_DOMAIN_CLASS = re.compile(r"\bclass\s+([A-Z]\w*)\b")
_NAMED_IMPORT = re.compile(r"import\s*(?:type\s*)?\{(?P<names>[^}]+)\}\s*from\s*['\"](?P<module>[^'\"]+)['\"]")
# Python `from .examples.customers_examples import valid_customer, (a as b)`.
_PYTHON_FROM_IMPORT = re.compile(r"^\s*from\s+(?P<module>\.*[\w.]*)\s+import\s+(?P<names>\([^)]*\)|[^#\r\n]+)", re.M)
# Java `import static shop.onboard.examples.CustomersExamples.validCustomer;` or `import shop.onboard.examples.CustomersExamples;`.
_JAVA_IMPORT = re.compile(r"^\s*import\s+(?P<static>static\s+)?(?P<path>[\w.]+)\s*;", re.M)


def _imported_modules(text: str) -> dict[str, str]:
    """Each name the story file imports, mapped to the module it comes from, written as a path without its extension
    the way the story test's language names it: TypeScript and JavaScript as the import says, Python and Java with
    their dots turned into folders."""
    imported: dict[str, str] = {}
    for name, module in [*_script_imports(text), *_python_imports(text), *_java_imports(text)]:
        if name and name != "*":
            imported.setdefault(name, module)
    return imported


def _script_imports(text: str) -> list[tuple[str, str]]:
    return [
        (part.strip().split(" as ")[-1].removeprefix("type ").strip(), match.group("module"))
        for match in _NAMED_IMPORT.finditer(text)
        for part in match.group("names").split(",")
    ]


def _python_imports(text: str) -> list[tuple[str, str]]:
    found = []
    for match in _PYTHON_FROM_IMPORT.finditer(text):
        dotted = match.group("module")
        level = len(dotted) - len(dotted.lstrip("."))
        folders = dotted.lstrip(".").replace(".", "/")
        module = folders if level == 0 else ("./" if level == 1 else "../" * (level - 1)) + folders
        for part in match.group("names").strip("()").split(","):
            found.append((part.strip().split(" as ")[-1].strip(), module))
    return found


def _java_imports(text: str) -> list[tuple[str, str]]:
    """A static import names a member of a class file; any other import names the class file itself."""
    found = []
    for match in _JAVA_IMPORT.finditer(text):
        parts = match.group("path").split(".")
        file_parts = parts[:-1] if match.group("static") else parts
        found.append((parts[-1], "/".join(file_parts)))
    return found


# What each language declares an example as, by the suffix of the file: a TypeScript or JavaScript function or constant,
# a Python module-level function or constant, a Java static method or field (of an `*Examples` class).
_SCRIPT_DECLARATION = re.compile(r"\bfunction\s+([\w$]+)\b|\b(?:const|let|var)\s+([\w$]+)\s*[:=]")
_EXAMPLE_DECLARATIONS = {
    ".ts": _SCRIPT_DECLARATION,
    ".tsx": _SCRIPT_DECLARATION,
    ".js": _SCRIPT_DECLARATION,
    ".jsx": _SCRIPT_DECLARATION,
    ".mjs": _SCRIPT_DECLARATION,
    ".py": re.compile(r"^(?:async\s+)?def\s+(\w+)|^([A-Za-z_]\w*)\s*(?::[^=\n]+)?=(?!=)", re.M),
    ".java": re.compile(r"\bstatic\s+(?:final\s+)?[\w<>\[\],.?]+(?:\s*<[^>]*>)?\s+(\w+)\s*[(=;]"),
}
_IDENTIFIER = re.compile(r"\w+")
_MEMBER_READ = re.compile(r"\.(\w+)")

_EVIDENCE_LINE = re.compile(r"\*\s*Evidence:\s*([A-Za-z][A-Za-z ,-]*)")


def _declared_examples(file: str, text: str) -> list[str]:
    """The names the code of file declares the way its language declares an example; none for a file in no language
    that declares them."""
    declaration = _EXAMPLE_DECLARATIONS.get(PurePosixPath(file).suffix)
    found = declaration.findall(text) if declaration is not None else []
    return [name for match in found for name in (match if isinstance(match, tuple) else (match,)) if name]


def _opening_docblock(lines: list[str]) -> str:
    """The file's first `/** … */` comment, when it comes before any story."""
    text = "\n".join(lines)
    start = text.find("/**")
    end = text.find("*/", start)
    if start == -1 or end == -1 or "Story:" in text[start:end]:
        return ""
    return text[start:end]


def example_source_file(story_test: str, imported_modules: dict[str, str], name: str) -> str:
    """The file the example called name comes from, named from the project like story_test: the module story_test
    imports it from, with story_test's own extension and, for a relative import, resolved against story_test's folder;
    else story_test itself, which declares the example."""
    module = imported_modules.get(name)
    if module is None:
        return story_test
    suffix = PurePosixPath(story_test).suffix
    if not module.startswith("."):
        return module + suffix
    parts: list[str] = list(PurePosixPath(story_test).parent.parts)
    for part in PurePosixPath(module).parts:
        if part == "..":
            parts = parts[:-1]
        elif part != ".":
            parts.append(part)
    return "/".join(parts) + suffix


def imported_example_files(story_test: str, text: str) -> list[str]:
    """The files story_test imports names from, named from the project: where its examples can come from. A relative
    import names one file; a module named from a package root (a Python or Java import) may sit under any folder above
    story_test, so each of those is a place it can be, and only the ones that are there are read."""
    imported = _imported_modules(text)
    relative = {example_source_file(story_test, imported, name) for name, module in imported.items() if module.startswith(".")}
    suffix = PurePosixPath(story_test).suffix
    rooted = {
        (folder / f"{module}{suffix}").as_posix().removeprefix("./")
        for module in set(imported.values()) if not module.startswith(".")
        for folder in PurePosixPath(story_test).parents
    }
    return sorted(relative | rooted)


def step_node_id(kind: str, file: str, line: int, name: str) -> str:
    """A step's graph id: its kind, file, line, and a checksum of its name. A checksum, never ``hash``: Python salts
    ``hash`` per process, and a step must keep its id in the worker that refreshes the graph and in the server."""
    return f"stories:{kind}:{file}:{line}:{zlib.crc32(name.encode('utf-8')) & 0xFFFFFF}"


def story_file_facts(text: str) -> dict:
    """Facts a story file owns, read from its text: they sit on the Story node, and its scenarios, steps, and examples
    read them through get_fact."""
    return {
        "export_names": _EXPORT_CONST.findall(text),
        "domain_class_names": _DOMAIN_CLASS.findall(text),
        "imported_modules": _imported_modules(text),
    }


def declared_evidence(text: str) -> list[str]:
    """The evidence a sub-epic file declares in its opening docblock; none when it declares none."""
    declared = _EVIDENCE_LINE.search(_opening_docblock(text.splitlines()))
    return [part.strip() for part in declared.group(1).split(",") if part.strip()] if declared else []


class StoryRecording:
    """One writing of a story map onto the practice that holds Stories: the practice and graph it writes to, where in
    the map's own file texts each node sits, and how many stories it has announced. The map makes one per ``record``
    and each node records itself through it."""

    def __init__(self, story_map: "StoryModel", practice, on_node: Optional[Callable[[str], None]]) -> None:
        self.story_map = story_map
        self.practice = practice
        self.graph = practice.reading.graph
        self.on_node = on_node
        self.story_at = 0
        self.story_total = len(story_map.every_story())
        self._cursor: dict[str, int] = {}

    def write(self) -> None:
        for epic in self.story_map.epics:
            epic.record(self, self.practice.reading.in_graph.root)

    def announce(self, story) -> None:
        self.story_at += 1
        if self.on_node is not None:
            self.on_node(f"{self.story_at}/{self.story_total} · {story.name}")

    def add(self, story_object, node_id: str, at: "Source", facts=None) -> Node:
        """story_object added as the graph node node_id, called by its recorded name and of its recorded type, at the
        lines at names, with the facts it does not hold itself; the node already called node_id when two objects
        share it."""
        if not self.practice.reading.in_graph.holds(node_id):
            story_object.name = story_object.recorded_name
            story_object.type = story_object.recorded_type
        node = self.practice.reading.in_graph.add(story_object, node_id, at.file or ".", at.start_line, at.end_line or at.start_line)
        self._align(node)
        for key, value in (facts or {}).items():
            node.set_fact(key, value)
        return node

    def _align(self, node: Node) -> None:
        """Move node onto the lines that declare it, since the map read it by a nearby line: a step sits on its label's
        line; a scenario, story, or background runs to the close of its call; an example sits on its export."""
        if node.type in {"Step", "Given", "When", "Then"}:
            node.source.align_to_label(node.name)
        elif node.type in {"Scenario", "Story", "Background"}:
            node.source.widen_to_call_close()
        elif node.type == "Example":
            node.source.align_to_example_export(self.practice.reading.in_graph.source_root, node.name, self._example_files)

    def text_of(self, file: str) -> str:
        return self.story_map.source_texts.get(file, "") if file else ""


    @cached_property
    def _example_files(self) -> list[Path]:
        """The code files an example's export is looked for in: the ones the story map was read from, so a read of the
        files being edited opens no file it did not read, and nothing outside the folders a read scans."""
        root = self.practice.reading.in_graph.source_root
        if not root:
            return []
        return [Path(root) / file for file in sorted(self.story_map.source_texts) if PurePosixPath(file).suffix in _EXAMPLE_DECLARATIONS]

    @cached_property
    def _function_sources(self) -> dict[str, str]:
        """Each example the code the story map was read from declares, in the way its language declares one (a
        function or a constant), mapped to the first file's text that declares it."""
        sources: dict[str, str] = {}
        for file, text in sorted(self.story_map.source_texts.items()):
            for name in _declared_examples(file, text):
                sources.setdefault(name, text)
        return sources

    def facts_of(self, file: str) -> dict:
        return story_file_facts(self.text_of(file))

    def example_facts(self, file: str, name: str) -> dict:
        """The facts of the example called name that story file declares or imports. They save with the graph, so a
        reader in any process has them:

        - ``source_names`` and ``source_reads``: every identifier, and every name read as a member (``.name``), in the
          first code file the map was read from that declares name as its language declares an example (a TypeScript or
          JavaScript function or constant, a Python function or constant, a Java static method or field), so an example
          is linked to the classes it shows and the properties it reads;
        - ``export_names``: the names exported by the file the example comes from, when that is another file the map
          read (an examples module the story test imports); otherwise the story file's own apply."""
        text = self._function_sources.get(name, "")
        facts = {"source_names": sorted(set(_IDENTIFIER.findall(text))), "source_reads": sorted(set(_MEMBER_READ.findall(text)))}
        source = example_source_file(file, story_file_facts(self.text_of(file))["imported_modules"], name)
        if source != file and self.text_of(source):
            facts["export_names"] = _EXPORT_CONST.findall(self.text_of(source))
        return facts

    def name_span(self, file: str, name: str, folder: str) -> "Source":
        """The line of file that names name; the folder alone when no line of file does."""
        line = next((index for index, text in enumerate(self.text_of(file).splitlines(), start=1) if name and name in text), None)
        return source_at(file, line) if line is not None else source_at(folder or ".")

    def span_of(self, node, file: str, fallback_text: str = "") -> "Source":
        """The lines of file node was read from, when its reader named them; else the next line of file that holds its
        text."""
        if node.has_source_file and node.source.start_line:
            return source_at(file, node.source.start_line, node.source.end_line or node.source.start_line)
        line = self._next_line(file, fallback_text or node.name)
        return source_at(file, line)

    def _next_line(self, file: str, text: str) -> int:
        lines = self.text_of(file).splitlines()
        start = self._cursor.get(file, 0)
        if not text:
            return 1
        # Search on from the last node found first, so a repeated name lands on its own entry; a diagram
        # need not list its cells in the map's order, so search from the top when that finds nothing.
        for index in [*range(start, len(lines)), *range(0, start)]:
            if text in lines[index]:
                self._cursor[file] = index + 1
                return index + 1
        return 1

    def place(self, node, at: "Source") -> None:
        """Name the file and lines at gives on a node that names no file yet."""
        if not file_of(node):
            node.source = source_at(at.file or ".", at.start_line, at.end_line)


def file_of(node) -> str:
    """The file the node was read from; empty while it only holds the placeholder a new node starts with."""
    if not node.has_source_file:
        return ""
    return str(node.source.file).replace("\\", "/")


def folder_of(file: str, up: int) -> str:
    """The folder file sits in, up more folders above it."""
    parts = [part for part in file.split("/") if part][:-1]
    if up and len(parts) >= up:
        parts = parts[:-up]
    return "/".join(parts) or "."


def step_semantic(step) -> str:
    """Given, When, or Then from the step's phase, else from its keyword; a step with neither is a Step."""
    phase = step.phase or (step.keyword or "").casefold()
    return phase.capitalize() if phase in ("given", "when", "then") else "Step"
