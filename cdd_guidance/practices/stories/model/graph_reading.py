"""How Stories takes part in the graph: it reads the story tests (or, when there are none, the story maps) into a
story model, which writes itself onto the graph, then links each step to the operations it calls and each example to
the classes and properties it shows."""

from __future__ import annotations

import re
from functools import cached_property
from pathlib import Path

from harness.graph.skipped_folders import scanned_files
from harness.guidance.practice_reading import PracticeReading

from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel

_MEMBER_CALL = re.compile(r"\.([\w$]+)\s*\(")
_STEP_TYPES = frozenset({"Step", "Given", "When", "Then"})
# A story map's epic is recorded as an Epic, or as a SubEpic under another epic; a map built on a graph without being
# recorded calls every epic an Epic.
_EPIC_TYPES = frozenset({"Epic", "SubEpic"})


class StoriesReading(PracticeReading):
    """How Stories takes part in the graph: it reads the story tests under its root, through the TypeScript format
    Stories holds, or the story maps there when there are none, with edited files only what they touch; writes the
    story map onto its graph; and links each step to the Clean Engineering operations it calls and each example to the
    classes and properties it shows, so it reads after Clean Engineering."""

    reads_after = ("clean_engineering",)
    source_ordered_types = frozenset({"Background", "Scenario", "Step", "Story"})
    # A step is recorded as the Given, When, or Then it is, while the schema keeps every step's rules on Step (its
    # given, when, and then types are each a Step), so each carries Step's rules; its check says which kind it judges.
    rule_types = {
        "SubEpic": ("Epic", "StoryNode"),
        "Epic": ("StoryNode",),
        "Story": ("StoryNode",),
        "Given": ("Step",),
        "When": ("Step",),
        "Then": ("Step",),
    }

    recorded_map = None
    """The story map this practice last wrote onto its graph, whose nodes its links start from."""

    @cached_property
    def story_tree(self) -> "StoryTree":
        """The story map as this practice's graph holds it, read through its edges and saved facts: what every reader of
        Stories' nodes asks for an epic's stories, a story's scenarios, or a scenario's steps."""
        return StoryTree(self)

    @property
    def root(self) -> Path:
        """The folder the practice reads its story tests and story maps from."""
        return Path(self.in_graph.source_root)

    @property
    def object_model(self) -> PracticeReading | None:
        """The part of the Clean Engineering practice the graph that holds Stories reads beside it, whose operations its
        steps call and whose classes its examples show; none when the graph reads none."""
        from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering

        loaded = self.graph.practices.loaded(CleanEngineering) if self.graph is not None else None
        return loaded.reading if loaded is not None else None

    @property
    def domain_model(self) -> PracticeReading | None:
        """The part of the DDD practice the graph that holds Stories reads beside it, whose aggregates its scenarios
        name; none when the graph reads none."""
        from cdd_guidance.practices.ddd.ddd import Ddd

        loaded = self.graph.practices.loaded(Ddd) if self.graph is not None else None
        return loaded.reading if loaded is not None else None

    def read_working_copy(self) -> None:
        """Read the story tests, or the story maps when there are none, write the story map onto its graph, and link
        each step to the operations it calls and each example to the classes and properties it shows."""
        self.recorded_map = self._story_map()
        self.graph.report_progress("stories · record")
        self.recorded_map.record(self.practice, on_node=lambda detail: self.graph.report_progress(f"stories · record · {detail}"))
        self._link_background_givens()
        clean = self.object_model
        if clean is not None:
            StoryLinks(self, clean, self.story_tree).link()

    def _link_background_givens(self) -> None:
        """Record the ``given`` edge from each background to the Given steps it holds: the step its schema says it is
        given by, which a working copy's read records itself rather than leaving it to the schema's evidence."""
        for background in self.in_graph.nodes("Background"):
            for edge in self.graph.edges_from("steps", background):
                if edge.child.type == "Given":
                    self.graph.link("given", background, edge.child, "relationship")

    def _story_map(self):
        model = self._story_tests()
        if model.epics:
            return model
        self.graph.report_progress("stories · markdown")
        model = self._story_maps()
        if not self._reads_markdown_scenarios:
            model.drop_scenarios()
            self._take_code_scenarios(model)
        return model

    @property
    def _reads_markdown_scenarios(self) -> bool:
        """Whether the fidelity the practice works at lists markdown among the formats it writes: a story test written in
        markdown is read only there. Code is a format of every fidelity, so a fidelity that lists no markdown reads its
        scenarios from code alone; with no fidelity, every format is read."""
        current = self.practice.fidelities.current
        return current is None or "markdown" in current.outputs

    def _take_code_scenarios(self, model) -> None:
        """Give each story of model the scenarios its story files in code under the root hold, in each code format the
        practice reads: its story tests, its shared stories, and its screen specs, by the files each format names its
        story files; with edited files, only those among them."""
        readers = [reader for reader in (self.practice.formats.adapter(name) for name in self.practice.formats) if isinstance(reader, CodeStoryModel)]
        suffixes = {Path(suffix).suffix for reader in readers for suffix in reader.story_file_suffixes}
        edited = self.graph.scope.edited_files
        project = Path(self.graph.scope.folder) if self.graph.scope.folder is not None else self.root
        for path in scanned_files(self.root, suffixes):
            reader = next((reader for reader in readers if reader.is_story_file(path.as_posix())), None)
            if reader is None or (edited is not None and path not in edited):
                continue
            text = path.read_text(encoding="utf-8")
            file = path.relative_to(self.root).as_posix()
            model.source_texts[file] = text
            model.add_scenarios(reader.stories_of(text, file, project)[0], file)

    def _story_tests(self):
        sources = self._typescript_files()
        files: dict[str, str] = {}
        for index, path in enumerate(sources, start=1):
            relative = path.relative_to(self.root).as_posix()
            self.graph.report_progress(f"stories · {index}/{len(sources)} · {relative}")
            files[relative] = path.read_text(encoding="utf-8")
        self.graph.report_progress("stories · parse")
        return self.practice.formats.adapter("typescript").parse(files, on_file=lambda detail: self.graph.report_progress(f"stories · parse · {detail}"))

    def _story_maps(self):
        """The story maps under the practice's root; with edited files, only the story maps among them."""
        on_file = lambda detail: self.graph.report_progress(f"stories · markdown · {detail}")  # noqa: E731
        edited = self.graph.scope.edited_files
        if edited is None:
            return self.practice.read_folder(self.root, on_file=on_file)
        return self.practice.read_files(edited, self.root, on_file=on_file)

    def _typescript_files(self) -> list[Path]:
        """TypeScript under the root; with edited files, each whole story folder that holds one. A story reads its
        examples and steps from sibling files, so one edited file needs its story's other files."""
        edited = self.graph.scope.edited_files
        if edited is not None and not any(path.suffix.lower() in {".ts", ".tsx"} for path in edited):
            return []
        found = scanned_files(self.root, {".ts", ".tsx"})
        if edited is None:
            return found
        reader = self.practice.formats.adapter("typescript")
        stories = {path.parent for path in found if reader.is_story_file(path.as_posix())}
        stories = {story for story in stories if any(story == file.parent or story in file.parents for file in edited)}
        return [path for path in found if path in edited or any(story in path.parents for story in stories)]


class StoryTree:
    """The story map as the graph holds it: each epic's sub-epics and stories, each story's scenarios, each scenario's
    steps, and the epic above any of them, read through the edges Stories records and the facts each node saves. It
    answers the same for the objects a read parsed and for the plain nodes of a graph opened from its save, so every
    reader of Stories' nodes, in this practice or another, asks it rather than a parsed object's attributes."""

    def __init__(self, stories: PracticeReading) -> None:
        self.stories = stories

    def epic_of(self, node):
        """The epic of the story map whose tree holds node, the outermost found up the graph's own edges; none for a
        node under no epic."""
        epic = None
        above = self.stories.graph.direct_parent(node)
        while above is not None:
            epic = above if above.type in _EPIC_TYPES else epic
            above = self.stories.graph.direct_parent(above)
        return epic

    def sub_epics(self, epic) -> list:
        """The sub-epics directly under epic, in the order the map lists them."""
        return self._below(epic, "decomposedInto", _EPIC_TYPES)

    def stories_under(self, epic) -> list:
        """The stories directly under epic or a sub-epic, in the order the map lists them."""
        return self._below(epic, "decomposedInto", {"Story"})

    def scenarios(self, story) -> list:
        """The story's scenarios, in the order its story test or map lists them."""
        return self._below(story, "scenarios", {"Scenario"})

    def steps(self, scenario) -> list:
        """The scenario's own steps, without the steps chained onto them, in order."""
        return [edge.child for edge in self.stories.graph.edges_from("steps", scenario)]

    def _below(self, parent, kind: str, node_types) -> list:
        return [edge.child for edge in self.stories.graph.edges_from(kind, parent) if edge.child.type in node_types]


class StoryLinks:
    """The edges between the Stories practice and Clean Engineering: a step invokes the operations it calls, an epic
    uses the modules those operations sit in, and an example demonstrates the classes it names and retrieves the
    properties it reads. Each is read from the facts every step and example saves with the graph (its body's text, the
    names its source holds) and from the graph's own edges, never from the parsed object behind a node: a refresh in a
    worker process holds the steps and examples it did not read again as plain nodes, and links them the same way."""

    def __init__(self, stories: PracticeReading, clean: PracticeReading, tree: "StoryTree") -> None:
        self.stories = stories
        self.clean = clean
        self.tree = tree
        self.graph = stories.graph

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
        matched = [member for name in called for member in self.clean.code_index.members_named(name)]
        epic = self.tree.epic_of(step) if matched else None
        for operation in matched:
            self.graph.link("invokes", step, operation, "relationship")
            self.graph.link("invokedBy", operation, step, "relationship")
            module = self._module_of(operation)
            if module is not None and epic is not None:
                self.graph.link("usedBy", module, epic, "relationship")
                self.graph.link("uses", epic, module, "relationship")
        if step.get_fact("phase"):
            for example in self._observed_by(step, body):
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

    def _observed_by(self, step, body: str) -> list:
        """The examples step observes: those its own text and body name, and for a Then, those its scenario's Givens
        name, the state whose outcome it observes."""
        texts = [body]
        if step.get_fact("phase") == "then":
            texts.extend(self._step_body(given) for given in self._givens_of(step))
        return [example for example in self.examples if any(re.search(rf"\b{re.escape(example.name)}\b", text) for text in texts)]

    def _givens_of(self, step) -> list:
        """The Given steps of the scenario step sits in, with the steps chained onto them."""
        scenario = self.graph.direct_parent(step)
        while scenario is not None and scenario.type != "Scenario":
            scenario = self.graph.direct_parent(scenario)
        if scenario is None:
            return []
        givens = [found for found in self.tree.steps(scenario) if found.get_fact("phase") == "given"]
        return [*givens, *(edge.child for given in givens for edge in self.graph.edges_from("ands", given))]

    def _step_body(self, step) -> str:
        """The step's own text and the body its story test gives it."""
        return f"{step.name}\n{step.get_fact('body_text') or ''}"

    def _module_of(self, operation):
        """The Clean Engineering module that holds the operation: the nearest module above it in the graph."""
        owner = self.graph.direct_parent(operation)
        while owner is not None and owner not in self.modules:
            owner = self.graph.direct_parent(owner)
        return owner
