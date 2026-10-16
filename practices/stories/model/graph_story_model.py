"""GraphStoryModel accepts a loaded story model and records it on a practice graph.

Populates schema fields rules depend on: Given/When/Then typing, ``ands`` edges,
step text/concepts/actor, scenario outline + evidence, example links.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from harness.graph.node_data import encode_node_data

from practices.stories.model.source_location import SourceLocation
from practices.stories.model.story_model import Epic, Step, StepType, Story, StoryModel


class GraphStoryModel:
    """One loaded story model, written as graph nodes and edges."""

    def __init__(self, model: StoryModel) -> None:
        self.model = model
        self._lines: dict[str, list[str]] = {}
        self._cursor: dict[str, int] = {}

    def record(self, practice) -> None:
        nodes: list[list] = []
        edges: list[list] = []
        root_id = practice.root_node.node_id
        for epic in self.model.epics:
            self._epic(practice.source_root, root_id, epic, True, nodes, edges)
        practice.apply_nodes(nodes)
        practice.apply_edges(edges)
        practice.loaded = ["nodes", "edges", "rules"]

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
        file = self._file(story)
        node_id = f"stories:Story:{file}:{story.name}"
        line, end = self._call_span(
            root,
            file,
            re.compile(rf"(?:shareStory|story)\(\s*['\"]{re.escape(story.name)}['\"]"),
            story,
        )
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
        line, end = self._call_span(root, file, re.compile(r"\bbackground\s*\("), background)
        self._ensure_source(background, file, line, end)
        background.load_map_facts()
        nodes.append(self._row(node_id, label, "Background", file or ".", line, end, background))
        edges.append([parent_id, node_id, "background", 2, "direct"])
        for step in background.steps:
            self._step(root, file, node_id, step, nodes, edges, edge_kind="steps", order=4)

    def _scenario(self, root: str, file: str, parent_id: str, scenario, nodes: list, edges: list) -> None:
        node_id = f"stories:Scenario:{file}:{scenario.name}"
        line, end = self._call_span(
            root,
            file,
            re.compile(rf"\bscenario\(\s*['\"]{re.escape(scenario.name)}['\"]"),
            scenario,
        )
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
        placed: list[tuple[str, int, int]] = []
        for step in scenario.steps:
            placed.extend(self._step(root, file, node_id, step, nodes, edges, edge_kind="steps", order=4))
        self._examples(root, file or ".", line, end, node_id, scenario.examples, placed, nodes, edges)

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
    ) -> list[tuple[str, int, int]]:
        semantic = _step_semantic(step)
        label = f"{step.keyword.lower()} {step.text}".strip()
        line, end = self._source_span(step, root, file, fallback_text=step.text)
        end = self._through_block(root, file, line, end)
        node_id = f"stories:{semantic}:{file}:{line}:{hash(label) & 0xFFFFFF}"
        payload = encode_node_data(_step_payload(step))
        row = [node_id, label, semantic, "stories", file or ".", line, end]
        if payload:
            row.extend(["", payload])
        nodes.append(row)
        edges.append([parent_id, node_id, edge_kind, order, "direct"])
        placed = [(node_id, line, end)]
        for continuation in step.ands:
            placed.extend(self._step(root, file, node_id, continuation, nodes, edges, edge_kind="ands", order=9))
        return placed

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

    def _examples(
        self,
        root: str,
        file: str,
        line: int,
        end: int,
        scenario_id: str,
        names,
        steps: list[tuple[str, int, int]],
        nodes: list,
        edges: list,
    ) -> None:
        """An example hangs on the step that names it. The scenario keeps one no step names."""
        for name in names:
            example_file, example_line, example_end = self._example_span(root, name, file, line, end)
            example_id = f"stories:Example:{example_file}:{name}"
            nodes.append([example_id, name, "Example", "stories", example_file, example_line, example_end])
            owners = [step_id for step_id, start, stop in steps if self._names(root, file, start, stop, name)]
            if not owners:
                owners = [scenario_id]
            for owner in owners:
                edges.append([owner, example_id, "examples", 5, "direct"])

    def _names(self, root: str, file: str, start: int, end: int, name: str) -> bool:
        if start < 1:
            return False
        lines = self._file_lines(root, file)
        body = "\n".join(lines[start - 1 : end])
        return re.search(rf"\b{re.escape(name)}\b", body) is not None

    def _example_span(self, root: str, name: str, fallback_file: str, line: int, end: int) -> tuple[str, int, int]:
        """The declaration in an examples folder. A story file that uses the name is not the example."""
        pattern = re.compile(rf"\b(?:function|const|let|var)\s+{re.escape(name)}\b")
        root_path = Path(root) if root else None
        if root_path is None or not root_path.is_dir():
            return fallback_file, line, end
        found: list[tuple[str, int, int]] = []
        for file in root_path.rglob("*.ts"):
            relative = file.relative_to(root_path).as_posix()
            parts = relative.lower().split("/")
            if any(part in {"node_modules", ".git", "dist", "coverage"} for part in parts):
                continue
            if "examples" not in parts:
                continue
            lines = self._file_lines(root, relative)
            for index, text in enumerate(lines, start=1):
                if pattern.search(text):
                    found.append((relative, index, _block_end(lines, index)))
                    break
        if not found:
            return fallback_file, line, end
        return _nearest(fallback_file, found)

    def _call_span(self, root: str, file: str, pattern: re.Pattern[str], node) -> tuple[int, int]:
        """The call that names this node, through the brace block it opens."""
        lines = self._file_lines(root, file)
        begin = self._cursor.get(file, 0)
        for index in range(begin, len(lines)):
            if pattern.search(lines[index]):
                self._cursor[file] = index + 1
                start = index + 1
                return start, _block_end(lines, start)
        line, end = self._source_span(node, root, file)
        return line, self._through_block(root, file, line, end)

    def _through_block(self, root: str, file: str, line: int, end: int) -> int:
        if line < 1:
            return end
        return _block_end(self._file_lines(root, file), line)

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


def _nearest(story: str, found: list[tuple[str, int, int]]) -> tuple[str, int, int]:
    """The declaration that shares the longest path with the story that uses it."""
    story_parts = story.replace("\\", "/").split("/")

    def score(relative: str) -> tuple[int, int]:
        shared = 0
        for left, right in zip(story_parts, relative.split("/")):
            if left != right:
                break
            shared += 1
        return shared, -len(relative)

    return max(found, key=lambda item: score(item[0]))


def _block_end(lines: list[str], start: int) -> int:
    """End line of the brace block this call opens, including a brace on a following line."""
    if start < 1 or start > len(lines):
        return max(start, 1)
    depth = 0
    opened = False
    for index in range(start - 1, len(lines)):
        line = lines[index]
        depth += line.count("{") - line.count("}")
        if "{" in line:
            opened = True
        if opened and depth <= 0:
            return index + 1
        if not opened and index >= start and _next_call(line):
            return start
    return start


def _next_call(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith(("shareStory(", "story(", "scenario(", "background(", "given(", "when(", "then("))


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
