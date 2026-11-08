"""How Stories takes part in the graph: it reads the story tests (or, when there are none, the story maps) into a
story model, which writes itself onto the graph, then links each step to the operations it calls and each example to
the classes and properties it shows."""

from __future__ import annotations

import re
from functools import cached_property
from pathlib import Path

from harness.graph.skipped_folders import scanned_files
from harness.guidance.guidance import PracticeGuidance

_MEMBER_CALL = re.compile(r"\.([\w$]+)\s*\(")
_STEP_TYPES = frozenset({"Step", "Given", "When", "Then"})


def align_story_node(node) -> None:
    """A step sits on its label's line; a scenario, story, or background runs to the close of its call; an example
    sits on its export."""
    if node.type in {"Step", "Given", "When", "Then"}:
        node.source.align_to_label(node.name)
    elif node.type in {"Scenario", "Story", "Background"}:
        node.source.widen_to_call_close()
    elif node.type == "Example":
        node.source.align_to_example_export(node.practice.in_graph.source_root, node.name)


class StoriesReading:
    """One read of the Stories practice's working copy: the story tests under its root, through the TypeScript format
    Stories holds, or the story maps there when there are none; with edited files, only what they touch."""

    def __init__(self, practice: PracticeGuidance) -> None:
        self.practice = practice
        self.graph = practice.graph
        self.root = Path(practice.in_graph.source_root)

    def story_map(self):
        model = self._story_tests()
        if model.epics:
            return model
        self.graph.report_progress("stories · markdown")
        return self._story_maps()

    def _story_tests(self):
        sources = self._typescript_files()
        files: dict[str, str] = {}
        for index, path in enumerate(sources, start=1):
            relative = path.relative_to(self.root).as_posix()
            self.graph.report_progress(f"stories · {index}/{len(sources)} · {relative}")
            files[relative] = path.read_text(encoding="utf-8")
        self.graph.report_progress("stories · parse")
        return self.practice.typescript_stories.parse(files, on_file=lambda detail: self.graph.report_progress(f"stories · parse · {detail}"))

    def _story_maps(self):
        """The story maps under the practice's root; with edited files, only the story maps among them."""
        on_file = lambda detail: self.graph.report_progress(f"stories · markdown · {detail}")  # noqa: E731
        edited = self.graph.edited_files()
        if edited is None:
            return self.practice.read_folder(self.root, on_file=on_file)
        return self.practice.read_files(edited, self.root, on_file=on_file)

    def _typescript_files(self) -> list[Path]:
        """TypeScript under the root; with edited files, each whole story folder that holds one. A story reads its
        examples and steps from sibling files, so one edited file needs its story's other files."""
        edited = self.graph.edited_files()
        if edited is not None and not any(path.suffix.lower() in {".ts", ".tsx"} for path in edited):
            return []
        found = scanned_files(self.root, {".ts", ".tsx"})
        if edited is None:
            return found
        reader = self.practice.typescript_stories
        stories = {path.parent for path in found if reader.is_story_file(path.as_posix())}
        stories = {story for story in stories if any(story == file.parent or story in file.parents for file in edited)}
        return [path for path in found if path in edited or any(story in path.parents for story in stories)]


class StoryLinks:
    """The edges between the Stories practice and Clean Engineering: a step invokes the operations it calls, an epic
    uses the modules those operations sit in, and an example demonstrates the classes it names and retrieves the
    properties it reads. Each is read from the facts every step and example saves with the graph (its body's text, the
    names its source holds) and from the graph's own edges, never from the parsed object behind a node: a refresh in a
    worker process holds the steps and examples it did not read again as plain nodes, and links them the same way."""

    def __init__(self, stories: PracticeGuidance, clean: PracticeGuidance) -> None:
        self.stories = stories
        self.clean = clean
        self.graph = stories.graph

    @cached_property
    def operations(self) -> dict[str, list]:
        """Clean Engineering's operations by name, read from the graph once."""
        found: dict[str, list] = {}
        for operation in self.clean.in_graph.nodes("Operation"):
            found.setdefault(operation.name, []).append(operation)
        return found

    @cached_property
    def modules(self) -> set:
        """Clean Engineering's modules, read from the graph once."""
        return set(self.clean.in_graph.nodes("Module"))

    @cached_property
    def examples(self) -> list:
        """The examples on the Stories graph, read once."""
        return self.stories.in_graph.nodes("Example")

    def link(self) -> None:
        steps = [node for node in self.stories.in_graph.nodes() if node.type in _STEP_TYPES]
        for index, step in enumerate(steps, start=1):
            self.graph.report_progress(f"stories · steps · {index}/{len(steps)} · {step.name}")
            self._link_step(step)
        for index, example in enumerate(self.examples, start=1):
            self.graph.report_progress(f"stories · examples · {index}/{len(self.examples)} · {example.name}")
            self._link_example(example)

    def _link_step(self, step) -> None:
        body = self._step_body(step)
        called = set(step.get_fact("callees") or []) | set(_MEMBER_CALL.findall(body))
        matched = [operation for name in called for operation in self.operations.get(name, ())]
        epic = self._epic_for(step) if matched else None
        for operation in matched:
            self.graph.link("invokes", step, operation, "relationship")
            self.graph.link("invokedBy", operation, step, "relationship")
            module = self._module_of(operation)
            if module is not None and epic is not None:
                self.graph.link("usedBy", module, epic, "relationship")
                self.graph.link("uses", epic, module, "relationship")
        if step.get_fact("phase"):
            for example in self.examples:
                if re.search(rf"\b{re.escape(example.name)}\b", body):
                    self.graph.link("observes", step, example, "relationship")

    def _link_example(self, example) -> None:
        names = set(example.get_fact("source_names") or [])
        reads = set(example.get_fact("source_reads") or [])
        for class_node in self.clean.in_graph.nodes("OoadClass"):
            if class_node.name in names:
                self.graph.link("demonstrates", example, class_node, "grouped")
                self.graph.link("demonstrates", class_node, example, "grouped")
                self.graph.link("demonstratedThrough", class_node, example, "relationship")
        for prop in self.clean.in_graph.nodes("Property"):
            if prop.name in reads:
                self.graph.link("retrievedUsing", example, prop, "relationship")
                self.graph.link("retrievedUsing", prop, example, "relationship")

    def _step_body(self, step) -> str:
        """The step's own text and the body its story test gives it."""
        return f"{step.name}\n{step.get_fact('body_text') or ''}"

    def _module_of(self, operation):
        """The Clean Engineering module that holds the operation: the nearest module above it in the graph."""
        owner = self.graph.direct_parent(operation)
        while owner is not None and owner not in self.modules:
            owner = self.graph.direct_parent(owner)
        return owner

    def _epic_for(self, step):
        """The top-level epic whose tree holds the step, found up the graph's own edges; None for a step on no epic."""
        node = self.graph.direct_parent(step)
        while node is not None and node.type != "Epic":
            node = self.graph.direct_parent(node)
        return node
