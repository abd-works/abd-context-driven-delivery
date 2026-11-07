"""How Stories takes part in the graph: it reads the story tests (or, when there are none, the story maps) into a
story model and adds its epics, stories, scenarios, steps, and examples to its graph, then links each step to the
operations it calls and each example to the classes and properties it shows."""

from __future__ import annotations

import re
from pathlib import Path

from typing import TYPE_CHECKING

from harness.graph.graph import Graph

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.stories import Stories
from harness.graph.skipped_folders import scanned_files

_MEMBER_CALL = re.compile(r"\.([\w$]+)\s*\(")
_FUNCTION_DECLARATION = re.compile(r"\bfunction\s+([\w$]+)\b")
# A step's own lines and the calls just after it: the lines a step's operations are read from.
_STEP_LINES = 40


def align_story_node(node) -> None:
    """A step sits on its label's line; a scenario, story, or background runs to the close of its call; an example
    sits on its export."""
    if node.type in {"Step", "Given", "When", "Then"}:
        node.source.align_to_label(node.name)
    elif node.type in {"Scenario", "Story", "Background"}:
        node.source.widen_to_call_close()
    elif node.type == "Example":
        node.source.align_to_example_export(node.graph.source_root_of(node.practice), node.name)


def read_stories(practice: Stories) -> None:
    """Read the story tests (or, when there are none, the story maps) into a story model and add its epics, stories,
    scenarios, steps, and examples to the graph that holds Stories."""
    from cdd_guidance.practices.stories.model.graph_story_model import GraphStoryModel

    graph = practice.graph
    model = _typescript_model(practice)
    if not model.epics:
        graph.report_progress("stories · markdown")
        model = _story_map_model(practice)
    graph.report_progress("stories · record")
    GraphStoryModel(model).record(practice, on_node=lambda detail: graph.report_progress(f"stories · record · {detail}"))


def link_steps_and_examples(graph: Graph) -> None:
    """Link each step to the operations it calls and each example to the classes and properties it shows, when the
    graph holds both Stories and Clean Engineering."""
    if "stories" in graph.practices and "clean_engineering" in graph.practices:
        _StoryLinks(graph).link()


def _typescript_model(practice: Stories):
    from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel

    graph = practice.graph
    root = Path(graph.source_root_of(practice))
    sources = _typescript_files(graph, root)
    files: dict[str, str] = {}
    for index, path in enumerate(sources, start=1):
        relative = path.relative_to(root).as_posix()
        graph.report_progress(f"stories · {index}/{len(sources)} · {relative}")
        files[relative] = path.read_text(encoding="utf-8")
    graph.report_progress("stories · parse")
    return TypeScriptStoryModel("tests").load(files, on_file=lambda detail: graph.report_progress(f"stories · parse · {detail}"))


def _story_map_model(practice: Stories):
    """The story maps under the practice's root; with edited files, only the story maps among them."""
    from cdd_guidance.practices.stories.model.story_model import StoryModel

    graph = practice.graph
    root = Path(graph.source_root_of(practice))
    on_file = lambda detail: graph.report_progress(f"stories · markdown · {detail}")  # noqa: E731
    edited = graph.edited_files()
    if edited is None:
        return StoryModel.load(root, on_file=on_file)
    return StoryModel.load_files(edited, root, on_file=on_file)


def _typescript_files(graph: Graph, folder: Path) -> list[Path]:
    """TypeScript under folder; with edited files, each whole story folder that holds one. A story reads its examples
    and steps from sibling files, so one edited file needs its story's other files."""
    from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel

    edited = graph.edited_files()
    if edited is not None and not any(path.suffix.lower() in {".ts", ".tsx"} for path in edited):
        return []
    found = scanned_files(folder, {".ts", ".tsx"})
    if edited is None:
        return found
    model = TypeScriptStoryModel("tests")
    stories = {path.parent for path in found if model.is_story_file(path.as_posix())}
    stories = {story for story in stories if any(story == file.parent or story in file.parents for file in edited)}
    return [path for path in found if path in edited or any(story in path.parents for story in stories)]


class _StoryLinks:
    """The edges between the Stories practice and Clean Engineering: a step invokes the operations it calls, an epic
    uses the modules those operations sit in, and an example demonstrates the classes it names and retrieves the
    properties it reads."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.root = Path(graph.folder) if graph.folder else None
        self.stories = graph.practice("stories")
        self.clean = graph.practice("clean_engineering")
        self._lines: dict[str, list[str]] = {}

    def link(self) -> None:
        operations: dict[str, list] = {}
        for operation in self.graph.nodes_of(self.clean, "Operation"):
            operations.setdefault(operation.name, []).append(operation)
        steps = [node for node in self.graph.nodes_of(self.stories) if node.type in {"Step", "Given", "When", "Then"}]
        examples = self.graph.nodes_of(self.stories, "Example")
        for index, step in enumerate(steps, start=1):
            self.graph.report_progress(f"stories · steps · {index}/{len(steps)} · {step.name}")
            self._link_step(step, operations, examples)
        sources = self._function_sources()
        for index, example in enumerate(examples, start=1):
            self.graph.report_progress(f"stories · examples · {index}/{len(examples)} · {example.name}")
            self._link_example(example, sources.get(example.name, ""))

    def _link_step(self, step, operations: dict[str, list], examples: list) -> None:
        body = self._step_body(step)
        called = set(step.get_fact("callees") or []) | set(_MEMBER_CALL.findall(body))
        matched = [operation for name in called for operation in operations.get(name, ())]
        epic = self._epic_for(step) if matched else None
        modules = {node.name: node for node in self.graph.nodes_of(self.clean, "Module")}
        for operation in matched:
            self.graph.link("invokes", step, operation, "relationship")
            self.graph.link("invokedBy", operation, step, "relationship")
            module = modules.get(Path(operation.source.file).parent.name)
            if module is not None and epic is not None:
                self.graph.link("usedBy", module, epic, "relationship")
                self.graph.link("uses", epic, module, "relationship")
        if step.get_fact("phase"):
            for example in examples:
                if re.search(rf"\b{re.escape(example.name)}\b", body):
                    self.graph.link("observes", step, example, "relationship")

    def _link_example(self, example, text: str) -> None:
        for class_node in self.graph.nodes_of(self.clean, "OoadClass"):
            if re.search(rf"\b{re.escape(class_node.name)}\b", text):
                self.graph.link("demonstrates", example, class_node, "grouped")
                self.graph.link("demonstrates", class_node, example, "grouped")
                self.graph.link("demonstratedThrough", class_node, example, "relationship")
        for prop in self.graph.nodes_of(self.clean, "Property"):
            if re.search(rf"\.{re.escape(prop.name)}\b", text):
                self.graph.link("retrievedUsing", example, prop, "relationship")
                self.graph.link("retrievedUsing", prop, example, "relationship")

    def _step_body(self, step) -> str:
        """The step's line and the lines after it; each file is read once per load."""
        if self.root is None or not step.source.file:
            return ""
        lines = self._lines.get(step.source.file)
        if lines is None:
            path = self.root / step.source.file
            lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
            self._lines[step.source.file] = lines
        start = max(0, step.source.start_line - 1)
        return "\n".join(lines[start : start + _STEP_LINES])

    def _function_sources(self) -> dict[str, str]:
        """Each declared ``function name`` in the .ts files, mapped to the first file that declares it."""
        if self.root is None:
            return {}
        files = scanned_files(self.root, {".ts"})
        sources: dict[str, str] = {}
        for index, file in enumerate(files, start=1):
            self.graph.report_progress(f"stories · example sources · {index}/{len(files)} · {file.relative_to(self.root).as_posix()}")
            text = file.read_text(encoding="utf-8")
            for name in _FUNCTION_DECLARATION.findall(text):
                sources.setdefault(name, text)
        return sources

    def _epic_for(self, step):
        """The top-level epic whose tree holds the step; None for a step on no epic."""
        from cdd_guidance.practices.stories.model.story_model import Epic

        node = step.parent
        while node is not None and not (isinstance(node, Epic) and not isinstance(node.parent, Epic)):
            node = node.parent
        return node
