"""GraphStoryModel accepts a loaded story model and records it on a practice graph.

Populates schema fields rules depend on: Given/When/Then typing, ``ands`` edges,
step text/concepts/actor, scenario outline + evidence, example links.
"""

from __future__ import annotations

import json
from pathlib import Path

from harness.graph.node_data import encode_node_data

from cdd_guidance.practices.stories.model.source_location import SourceLocation
from cdd_guidance.practices.stories.model.story_model import Epic, Step, StepType, Story, StoryModel


class GraphStoryModel:
    """One loaded story model, written as graph nodes and edges."""

    def __init__(self, model: StoryModel) -> None:
        self.model = model
        self._lines: dict[str, list[str]] = {}
        self._cursor: dict[str, int] = {}
        self._on_node = None
        self._node_at = 0
        self._node_total = 0

    def record(self, practice, *, on_node=None) -> None:
        nodes: list[list] = []
        edges: list[list] = []
        root_id = practice.root_node.node_id
        self._on_node = on_node
        self._node_at = 0
        self._node_total = sum(self._story_count(epic) for epic in self.model.epics)
        try:
            with self.model.batch_schema_sync():
                for epic in self.model.epics:
                    self._epic(practice.source_root, root_id, epic, True, nodes, edges)
            practice.apply_nodes(nodes)
            practice.apply_edges(edges)
            practice.loaded = ["nodes", "edges", "rules"]
        finally:
            self._on_node = None

    def _story_count(self, epic: Epic) -> int:
        return len(epic.stories) + sum(self._story_count(child) for child in epic.epics)

    def _epic(self, root: str, parent_id: str, epic: Epic, top: bool, nodes: list, edges: list) -> None:
        story_file = self._file_under(epic)
        folder = self._folder(story_file, up=1 if top and epic.epics else 0)
        semantic = "Epic" if top else "SubEpic"
        node_id = f"stories:{semantic}:{folder}:{epic.name}"
        source_file, line, end = self._name_span(root, story_file, epic.name, folder)
        epic.source = SourceLocation(source_file, line, end)
        epic.load_map_facts()
        nodes.append(self._row(node_id, epic.name, semantic, source_file, line, end, epic))
        edges.append([parent_id, node_id, "decomposedInto", 1, "direct"])
        for child in epic.epics:
            self._epic(root, node_id, child, False, nodes, edges)
        for story in epic.stories:
            self._story(root, node_id, story, nodes, edges)

    def _story(self, root: str, parent_id: str, story: Story, nodes: list, edges: list) -> None:
        self._node_at += 1
        if self._on_node is not None:
            self._on_node(f"{self._node_at}/{self._node_total} · {story.name}")
        file = self._file(story)
        node_id = f"stories:Story:{file}:{story.name}"
        line, end = self._source_span(story, root, file)
        story.load_map_facts()
        nodes.append(self._row(node_id, story.name, "Story", file or ".", line, end, story))
        edges.append([parent_id, node_id, "decomposedInto", 1, "direct"])
        for background in story.backgrounds:
            self._background(root, file, node_id, background, nodes, edges)
        for scenario in story.scenarios:
            self._scenario(root, file, node_id, scenario, nodes, edges)

    def _background(self, root: str, file: str, parent_id: str, background, nodes: list, edges: list) -> None:
        label = background.name or "background"
        node_id = f"stories:Background:{file}:{label}"
        line, end = self._source_span(background, root, file)
        self._ensure_source(background, file, line, end)
        background.load_map_facts()
        nodes.append(self._row(node_id, label, "Background", file or ".", line, end, background))
        edges.append([parent_id, node_id, "background", 2, "direct"])
        for step in background.steps:
            self._step(root, file, node_id, step, nodes, edges, edge_kind="steps", order=4)

    def _scenario(self, root: str, file: str, parent_id: str, scenario, nodes: list, edges: list) -> None:
        node_id = f"stories:Scenario:{file}:{scenario.name}"
        line, end = self._source_span(scenario, root, file)
        self._ensure_source(scenario, file, line, end)
        scenario.load_map_facts()
        nodes.append(
            self._row(
                node_id,
                scenario.name,
                "Scenario",
                file or ".",
                line,
                end,
                scenario,
                {
                    "is_outline": bool(getattr(scenario, "is_outline", False)),
                    "story_name": getattr(scenario, "story_name", "") or "",
                },
            )
        )
        edges.append([parent_id, node_id, "scenarios", 3, "direct"])
        for step in scenario.steps:
            self._step(root, file, node_id, step, nodes, edges, edge_kind="steps", order=4)
        for name in scenario.examples:
            example_id = f"stories:Example:{file}:{name}"
            nodes.append([example_id, name, "Example", "stories", file or ".", line, end])
            edges.append([node_id, example_id, "examples", 5, "direct"])

    def _step(
        self,
        root: str,
        file: str,
        parent_id: str,
        step: Step,
        nodes: list,
        edges: list,
        *,
        edge_kind: str = "steps",
        order: int = 4,
    ) -> None:
        semantic = _step_semantic(step)
        label = f"{step.keyword.lower()} {step.text}".strip()
        line, end = self._source_span(step, root, file, fallback_text=step.text)
        node_id = f"stories:{semantic}:{file}:{line}:{hash(label) & 0xFFFFFF}"
        payload = encode_node_data(_step_payload(step))
        row = [node_id, label, semantic, "stories", file or ".", line, end]
        if payload:
            row.extend(["", payload])
        nodes.append(row)
        edges.append([parent_id, node_id, edge_kind, order, "direct"])
        for continuation in step.ands:
            self._step(root, file, node_id, continuation, nodes, edges, edge_kind="ands", order=9)

    def _row(
        self,
        node_id: str,
        name: str,
        semantic: str,
        file: str,
        line: int,
        end: int,
        node,
        extra: dict | None = None,
    ) -> list:
        facts = {
            "opening_token": getattr(node, "opening_token", ""),
            "opening_class": getattr(node, "opening_class", ""),
            "child_count": getattr(node, "child_count", 0),
            "child_label": getattr(node, "child_label", "children"),
            "child_band": getattr(node, "child_band", ""),
            "near_duplicate": bool(getattr(node, "near_duplicate", False)),
            "generic_handler": bool(getattr(node, "generic_handler", False)),
            "shared_verb": getattr(node, "shared_verb", "") or "",
            "one_time_task": bool(getattr(node, "one_time_task", False)),
            "artifact_name": getattr(node, "artifact_name", "") or "",
            "camel_case_path": bool(getattr(node, "camel_case_path", False)),
            "evidence": list(getattr(node, "evidence", []) or []),
        }
        scenario_count = getattr(node, "scenario_count", None)
        if scenario_count is not None:
            facts["scenario_count"] = scenario_count
        if extra:
            facts.update(extra)
        payload = encode_node_data(facts)
        row = [node_id, name, semantic, "stories", file, line, end]
        if payload:
            row.extend(["", payload])
        return row

    def _file_under(self, epic: Epic) -> str:
        for story in epic.stories:
            file = self._file(story)
            if file:
                return file
        for child in epic.epics:
            file = self._file_under(child)
            if file:
                return file
        return ""

    def _file(self, node) -> str:
        source = getattr(node, "source", None)
        file = getattr(source, "file", "") if source is not None else ""
        return str(file or "").replace("\\", "/")

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
        if text:
            for index in range(start, len(lines)):
                if text in lines[index]:
                    self._cursor[file] = index + 1
                    return index + 1
        return 1


def _step_semantic(step: Step) -> str:
    if step.step_type == StepType.GIVEN:
        return "Given"
    if step.step_type == StepType.WHEN:
        return "When"
    if step.step_type == StepType.THEN:
        return "Then"
    keyword = (step.keyword or "").casefold()
    if keyword == "given":
        return "Given"
    if keyword == "when":
        return "When"
    if keyword == "then":
        return "Then"
    return "Step"


def _step_payload(step: Step) -> dict:
    phase = ""
    if step.step_type is not None:
        phase = step.step_type.value
    return {
        "keyword": step.keyword,
        "text": step.text,
        "phase": phase,
        "concepts": list(step.concepts or []),
        "values": list(step.values or []),
        "actor": step.actor or "",
        "continuation": step.is_continuation,
        "callees": _callees_from_step(step),
    }


def _callees_from_step(step: Step) -> list[str]:
    found: list[str] = []
    for concept in step.concepts or []:
        token = concept.strip()
        if token and token[0].isupper() and token not in found:
            found.append(token)
    return found
