"""GraphStoryModel accepts a loaded story model and records it on a practice graph.

Each story object is its own graph node: the epic, story, background, scenario, and step the model read are added to
the practice graph as they are, so rules read the scenario, its steps, and its story straight from them. A node keeps
as its own facts only what the object does not know, such as the exports of the file its story was read from.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Optional

from harness.graph.graph import Node, Source

from cdd_guidance.practices.stories.model.source_location import SourceLocation
from cdd_guidance.practices.stories.model.story_model import Background, Epic, Scenario, Step, Story, StoryModel

_EXPORT_CONST = re.compile(r"export const (\w+)")
_DOMAIN_CLASS = re.compile(r"\bclass\s+([A-Z]\w*)\b")
_ORCHESTRATION_EXPORT = re.compile(r"export function (?:activate|handle|process)\w*\s*\(")
_NAMED_IMPORT = re.compile(r"import\s*(?:type\s*)?\{(?P<names>[^}]+)\}\s*from\s*['\"](?P<module>[^'\"]+)['\"]")


def _imported_modules(text: str) -> dict[str, str]:
    """Each name the story file imports, mapped to the module it comes from."""
    imported: dict[str, str] = {}
    for match in _NAMED_IMPORT.finditer(text):
        for part in match.group("names").split(","):
            name = part.strip().split(" as ")[-1].removeprefix("type ").strip()
            if name:
                imported.setdefault(name, match.group("module"))
    return imported


_EVIDENCE_LINE = re.compile(r"\*\s*Evidence:\s*([A-Za-z][A-Za-z ,-]*)")


def _opening_docblock(lines: list[str]) -> str:
    """The file's first `/** … */` comment, when it comes before any story."""
    text = "\n".join(lines)
    start = text.find("/**")
    end = text.find("*/", start)
    if start == -1 or end == -1 or "Story:" in text[start:end]:
        return ""
    return text[start:end]


class GraphStoryModel:
    """One loaded story model, written as graph nodes and edges."""

    def __init__(self, model: StoryModel) -> None:
        self.model = model
        self._lines: dict[str, list[str]] = {}
        self._cursor: dict[str, int] = {}

    def record(self, practice, *, on_node: Optional[Callable[[str], None]] = None) -> None:
        """Write the model's epics, stories, backgrounds, scenarios, steps, and examples onto *practice*. *on_node*
        hears each story as it is written."""
        recording = _StoryGraphRecording(self, practice, on_node)
        with self.model.batch_schema_sync():
            recording.write()
        practice.loaded = ["nodes", "edges", "rules"]

    def _epic_evidence(self, root: str, story_file: str, epic: Epic, top: bool) -> list[str]:
        """What the epic declares, else the sub-epic file's opening docblock, else the labels its children carry."""
        if epic.evidence:
            return list(epic.evidence)
        if not top and story_file:
            declared = _EVIDENCE_LINE.search(_opening_docblock(self._file_lines(root, story_file)))
            if declared:
                return [part.strip() for part in declared.group(1).split(",") if part.strip()]
        labels: list[str] = []
        for child in epic.epics:
            labels.extend(self._epic_evidence(root, self._file_under(child), child, False))
        for story in epic.stories:
            labels.extend(story.evidence)
        return list(dict.fromkeys(labels))

    def _file_under(self, epic: Epic) -> str:
        """The first file any story under the epic was read from."""
        return next((file for story in epic.every_story() for file in [self._file(story)] if file), "")

    def _file(self, node) -> str:
        """The file the node was read from; empty while it only holds the placeholder a new node starts with."""
        if not getattr(node, "has_source_file", False):
            return ""
        return str(node.source.file).replace("\\", "/")

    def _folder(self, file: str, up: int) -> str:
        parts = [part for part in file.split("/") if part]
        if parts:
            parts = parts[:-1]
        if up and len(parts) >= up:
            parts = parts[:-up]
        return "/".join(parts) or "."

    def _ensure_source(self, node, file: str, line: int, end: int) -> None:
        if self._file(node):
            return
        node.source = SourceLocation(file or ".", line, end)

    def _name_span(self, root: str, file: str, name: str, folder: str) -> tuple[str, int, int]:
        line = self._line_containing(root, file, name) if file and name else None
        if line is not None:
            return file, line, line
        return folder or ".", 0, 0

    def _line_containing(self, root: str, file: str, text: str) -> int | None:
        if not text:
            return None
        for index, line in enumerate(self._file_lines(root, file), start=1):
            if text in line:
                return index
        return None

    def _file_facts(self, root: str, file: str) -> dict:
        """Facts the story file owns. They sit on the Story node; its scenarios, steps, and examples read them through get_fact."""
        text = "\n".join(self._file_lines(root, file)) if file else ""
        return {
            "export_names": _EXPORT_CONST.findall(text),
            "domain_class_names": _DOMAIN_CLASS.findall(text),
            "exports_orchestration": bool(_ORCHESTRATION_EXPORT.search(text)),
            "imported_modules": _imported_modules(text),
        }

    def _file_lines(self, root: str, file: str) -> list[str]:
        lines = self._lines.get(file)
        if lines is None:
            path = Path(root, file) if root and file else None
            lines = path.read_text(encoding="utf-8").splitlines() if path is not None and path.is_file() else []
            self._lines[file] = lines
        return lines

    def _source_span(self, node, root: str, file: str, fallback_text: str = "") -> tuple[int, int]:
        source = getattr(node, "source", None)
        if source is not None and getattr(source, "line", None):
            start = int(source.line or 1)
            end = int(getattr(source, "end_line", None) or start)
            return start, end
        line = self._next_line(root, file, fallback_text or getattr(node, "name", ""))
        return line, line

    def _next_line(self, root: str, file: str, text: str) -> int:
        lines = self._file_lines(root, file)
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


class _StoryGraphRecording:
    """One recording of a story model onto a practice, and how many stories it has announced."""

    def __init__(self, story_graph: GraphStoryModel, practice, on_node: Optional[Callable[[str], None]]) -> None:
        self.story_graph = story_graph
        self.practice = practice
        self.root = practice.source_root
        self.on_node = on_node
        self.story_at = 0
        self.story_total = len(story_graph.model.every_story())

    def write(self) -> None:
        for epic in self.story_graph.model.epics:
            self._epic(self.practice.root_node, epic, True)

    def _epic(self, parent: Node, epic: Epic, top: bool) -> None:
        graph = self.story_graph
        story_file = graph._file_under(epic) or graph._file(epic)
        folder = graph._folder(story_file, up=1 if top and epic.epics else 0)
        semantic = "Epic" if top else "SubEpic"
        node_id = f"stories:{semantic}:{folder}:{epic.name}"
        source_file, line, end = graph._name_span(self.root, story_file, epic.name, folder)
        epic.source = SourceLocation(source_file, line, end)
        epic.load_map_facts()
        epic.evidence = graph._epic_evidence(self.root, story_file, epic, top)
        node = self._add_node(node_id, epic.name, semantic, source_file, line, end, epic)
        self.practice.link("decomposedInto", parent, node)
        for child in epic.epics:
            self._epic(node, child, False)
        for story in epic.stories:
            self._story(node, story)

    def _story(self, parent: Node, story: Story) -> None:
        self._announce(story)
        graph = self.story_graph
        file = graph._file(story)
        node_id = f"stories:Story:{file}:{story.name}"
        line, end = graph._source_span(story, self.root, file)
        story.load_map_facts()
        facts = graph._file_facts(self.root, file)
        node = self._add_node(node_id, story.name, "Story", file or ".", line, end, story, facts)
        self.practice.link("decomposedInto", parent, node)
        for background in story.backgrounds:
            self._background(file, node, background)
        scoped = [name for background in story.backgrounds for name in background.examples]
        for scenario in story.scenarios:
            self._scenario(file, node, scenario, scoped)

    def _announce(self, story: Story) -> None:
        self.story_at += 1
        if self.on_node is not None:
            self.on_node(f"{self.story_at}/{self.story_total} · {story.name}")

    def _background(self, file: str, parent: Node, background: Background) -> None:
        label = background.name or "background"
        node_id = f"stories:Background:{file}:{label}"
        line, end = self.story_graph._source_span(background, self.root, file)
        self.story_graph._ensure_source(background, file, line, end)
        background.load_map_facts()
        node = self._add_node(node_id, label, "Background", file or ".", line, end, background)
        self.practice.link("background", parent, node)
        for step in background.steps:
            self._step(file, node, step, "steps")

    def _scenario(self, file: str, parent: Node, scenario: Scenario, scoped: list[str]) -> None:
        """Record the scenario with its own examples and those its story's Background scopes. A scenario read from a
        story test sits in that file, not in the story map its Story came from."""
        file = self.story_graph._file(scenario) or file
        node_id = f"stories:Scenario:{file}:{scenario.name}"
        line, end = self.story_graph._source_span(scenario, self.root, file)
        self.story_graph._ensure_source(scenario, file, line, end)
        scenario.load_map_facts()
        facts = {"is_outline": bool(scenario.is_outline), "story_name": scenario.story_name or ""}
        node = self._add_node(node_id, scenario.name, "Scenario", file or ".", line, end, scenario, facts)
        self.practice.link("scenarios", parent, node)
        for step in scenario.steps:
            self._step(file, node, step, "steps")
        for name in dict.fromkeys([*scenario.examples, *scoped]):
            source = Source(file or ".", line, end, self.root)
            example = self.practice.add_named("Example", f"stories:Example:{file}:{name}", name, source)
            self.practice.link("examples", node, example)

    def _step(self, file: str, parent: Node, step: Step, edge_kind: str) -> None:
        semantic = _step_semantic(step)
        label = f"{step.keyword.lower()} {step.text}".strip()
        line, end = self.story_graph._source_span(step, self.root, file, fallback_text=step.text)
        node_id = f"stories:{semantic}:{file}:{line}:{hash(label) & 0xFFFFFF}"
        continuations = list(step.ands)
        node = self._add_node(node_id, label, semantic, file or ".", line, end, step)
        self.practice.link(edge_kind, parent, node)
        for continuation in continuations:
            self._step(file, node, continuation, "ands")

    def _add_node(self, node_id: str, name: str, semantic: str, file: str, line: int, end: int, story_object, facts=None) -> Node:
        """The story object added as the graph node node_id, called name, of type semantic, with the facts it does not
        hold itself; the node already called node_id when two objects share it."""
        if node_id not in self.practice.by_id:
            story_object.name = name
            story_object.type = semantic
        node = self.practice.add(story_object, node_id, file, line, end)
        for key, value in (facts or {}).items():
            node.set_fact(key, value)
        return node


def _step_semantic(step: Step) -> str:
    """Given, When, or Then from the step's phase, else from its keyword; a step with neither is a Step."""
    phase = step.phase or (step.keyword or "").casefold()
    return phase.capitalize() if phase in ("given", "when", "then") else "Step"
