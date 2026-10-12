"""GraphStoryModel accepts a loaded story model and records it on a practice graph.

Any format model is a StoryModel. This walks that tree into the explorer tuples.
"""

from __future__ import annotations

from pathlib import Path

from practices.stories.model.story_model import Epic, Story, StoryModel


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
        file = self._file_under(epic)
        folder = self._folder(file, up=1 if top and epic.epics else 0)
        semantic = "Epic" if top else "SubEpic"
        node_id = f"stories:{semantic}:{folder}:{epic.name}"
        nodes.append([node_id, epic.name, semantic, "stories", folder or ".", 1, 1])
        edges.append([parent_id, node_id, "decomposedInto", 1, "direct"])
        for child in epic.epics:
            self._epic(root, node_id, child, False, nodes, edges)
        for story in epic.stories:
            self._story(root, node_id, story, nodes, edges)

    def _story(self, root: str, parent_id: str, story: Story, nodes: list, edges: list) -> None:
        file = self._file(story)
        node_id = f"stories:Story:{file}:{story.name}"
        nodes.append([node_id, story.name, "Story", "stories", file or ".", story.sequential_order or 1, story.sequential_order or 1])
        edges.append([parent_id, node_id, "decomposedInto", 1, "direct"])
        for background in story.backgrounds:
            self._background(root, file, node_id, background, nodes, edges)
        for scenario in story.scenarios:
            self._scenario(root, file, node_id, scenario, nodes, edges)

    def _background(self, root: str, file: str, parent_id: str, background, nodes: list, edges: list) -> None:
        label = background.name or "background"
        node_id = f"stories:Background:{file}:{label}"
        nodes.append([node_id, label, "Background", "stories", file or ".", background.sequential_order or 1, background.sequential_order or 1])
        edges.append([parent_id, node_id, "background", 2, "direct"])
        for step in background.steps:
            self._step(root, file, node_id, step, nodes, edges)

    def _scenario(self, root: str, file: str, parent_id: str, scenario, nodes: list, edges: list) -> None:
        node_id = f"stories:Scenario:{file}:{scenario.name}"
        line = scenario.sequential_order or 1
        nodes.append([node_id, scenario.name, "Scenario", "stories", file or ".", line, line])
        edges.append([parent_id, node_id, "scenarios", 3, "direct"])
        for step in scenario.steps:
            self._step(root, file, node_id, step, nodes, edges)
        for name in scenario.examples:
            example_id = f"stories:Example:{file}:{name}"
            nodes.append([example_id, name, "Example", "stories", file or ".", 1, 1])
            edges.append([node_id, example_id, "examples", 5, "direct"])

    def _step(self, root: str, file: str, parent_id: str, step, nodes: list, edges: list) -> None:
        label = f"{step.keyword.lower()} {step.text}".strip()
        line = self._next_line(root, file, step.text)
        node_id = f"stories:Step:{file}:{label}:{line}"
        nodes.append([node_id, label, "Step", "stories", file or ".", line, line])
        edges.append([parent_id, node_id, "steps", 4, "direct"])

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

    def _next_line(self, root: str, file: str, text: str) -> int:
        lines = self._lines.get(file)
        if lines is None:
            path = Path(root, file) if root and file else None
            lines = path.read_text(encoding="utf-8").splitlines() if path is not None and path.is_file() else []
            self._lines[file] = lines
        start = self._cursor.get(file, 0)
        if text:
            for index in range(start, len(lines)):
                if text in lines[index]:
                    self._cursor[file] = index + 1
                    return index + 1
        return 1
