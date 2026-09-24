"""CodeQL graph types for Stories — wrap live Stories types."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from practices.stories.model.background import Background as SourceBackground
from practices.stories.model.example import Example as SourceExample
from practices.stories.model.nodes import Epic as SourceEpic, Story as SourceStory, SubEpic as SourceSubEpic
from practices.stories.model.scenario import Phase, Scenario as SourceScenario
from practices.stories.model.source_location import SourceLocation
from practices.stories.model.step import Step as SourceStep
from practices.stories.model.story_map import StoryMap as SourceStoryMap

from harness.knowledge_graph.model.graph_node import Kind, Node

if TYPE_CHECKING:
    from harness.knowledge_graph.model.practice_graph import PracticeGraph


class Example(SourceExample, Node):
    practice = "stories"
    _semantic_type_name = "Example"

    def demonstrates(self, cls: Node) -> None:
        self.relate(Kind.DEMONSTRATES, cls)

    def matching(
        self,
        export_name: str,
        file_path: str,
    ) -> List["Example"]:
        index = self._index
        export_lower = export_name.lower()
        if export_lower in index:
            return index[export_lower]
        stem = Path(file_path).stem.replace(".examples", "").replace("-", " ")
        if stem.lower() in index:
            return index[stem.lower()]
        out: List[Example] = []
        for examples in index.values():
            for example in examples:
                if export_lower in example.name.lower() or example.name.lower() in export_lower:
                    out.append(example)
        return out

    def wire_demonstrates(self, graph: "PracticeGraph", entries: List[dict]) -> None:
        self._index: Dict[str, List[Example]] = {}
        for example in graph.nodes_of_type(Example):
            self._index.setdefault(example.name.lower(), []).append(example)
        for entry in entries:
            self._wire_demonstrates_entry(graph, entry)

    def _wire_demonstrates_entry(self, graph: "PracticeGraph", entry: dict) -> None:
        self._demonstrate_entry = entry
        for class_name in entry.get("demonstrates") or []:
            self._demonstrate_class(graph, class_name)

    def _demonstrate_class(self, graph: "PracticeGraph", class_name: str) -> None:
        owned = graph.class_named(class_name)
        if owned is None:
            return
        entry = self._demonstrate_entry
        for example in self.matching(entry.get("export_name") or "", entry.get("file") or ""):
            example.demonstrates(owned)


class Step(SourceStep, Node):
    practice = "stories"
    _semantic_type_name = "Step"

    def invokes(self, operation: Node) -> None:
        self.relate(Kind.INVOKES, operation)

    def observes(self, target: Node) -> None:
        self.relate(Kind.OBSERVES, target)

    @classmethod
    def from_source(cls, source: SourceStep) -> "Step":
        return cls(
            text=source.text,
            phase=source.phase,
            sequential_order=source.sequential_order,
            is_continuation=source.is_continuation,
            keyword=getattr(source, "keyword", "") or "",
            concepts=list(source.concepts),
            values=list(source.values),
            actor=source.actor,
            source=source.source,
            name=source.name,
        )

    def wire_calls(self, graph: "PracticeGraph", story_calls: List[dict]) -> None:
        self._graph = graph
        for story_call in story_calls:
            self._step_text = story_call.get("step_text") or ""
            step = self.at(
                story_call.get("story_file") or "",
                int(story_call.get("line") or 0),
            )
            operation = graph.operation_named(
                story_call.get("callee_class") or "",
                story_call.get("callee_operation") or "",
            )
            if step is None or operation is None:
                continue
            step.invokes(operation)

    def wire_observations(self, graph: "PracticeGraph", observations: List[dict]) -> None:
        from practices.clean_engineering.model.codeql.codeql_model import Operation, Property

        self._graph = graph
        self._step_text = ""
        for obs in observations:
            step = self.at(obs.get("story_file") or "", int(obs.get("line") or 0))
            if step is None:
                continue
            owned_class = graph.class_named(obs.get("target_class") or "")
            if owned_class is None:
                continue
            self._owned_class = owned_class
            self._observation = obs
            self._operation_type = Operation
            self._property_type = Property
            target = self._owned_member()
            if target is not None:
                step.observes(target)

    def _owned_member(self):
        for owned in self._owned_class.related(Kind.OWNS):
            if self._is_observed_member(owned):
                return owned
        return None

    def _is_observed_member(self, owned) -> bool:
        kind = self._observation.get("member_kind")
        name = self._observation.get("target_member")
        if kind == "operation" and isinstance(owned, self._operation_type):
            return owned.name == name
        if kind == "property" and isinstance(owned, self._property_type):
            return owned.name == name
        return False

    def at(self, story_file: str, line: int) -> Optional["Step"]:
        self._lookup_file = story_file.replace("\\", "/").lstrip("./")
        self._lookup_line = line
        by_text = self._step_matching_text()
        if by_text is not None:
            return by_text
        return self._step_near_line()

    def _step_matching_text(self) -> Optional["Step"]:
        step_text = self._step_text
        if not step_text:
            return None
        for step in self._graph.nodes_of_type(Step):
            if step_text.lower() in step.text.lower():
                return step
        return None

    def _step_near_line(self) -> Optional["Step"]:
        best: Tuple[int, Optional[Step]] = (1_000_000, None)
        for step in self._graph.nodes_of_type(Step):
            src = getattr(step, "source", None)
            if src is None:
                continue
            src_file = str(src.file).replace("\\", "/").lstrip("./")
            if src_file != self._lookup_file and not src_file.endswith(self._lookup_file):
                continue
            if self._lookup_line <= 0:
                return step
            delta = abs(int(src.line) - self._lookup_line)
            if delta < best[0]:
                best = (delta, step)
        if best[1] is not None and best[0] <= 5:
            return best[1]
        return None


class Background(SourceBackground, Node):
    practice = "stories"
    _semantic_type_name = "Background"

    def load_step(self, source: SourceStep) -> Step:
        return Step.from_source(source)


class Scenario(SourceScenario, Node):
    practice = "stories"
    _semantic_type_name = "Scenario"

    def load_background(self, source: SourceBackground) -> Background:
        return Background(source.name, source.sequential_order)

    def load_step(self, source: SourceStep) -> Step:
        return Step.from_source(source)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)

    def owner_of(self, entry: dict):
        scenarios = self._scenarios
        backgrounds = self._backgrounds
        if entry.get("scenario"):
            key = (
                StoryMap().normalized_file(entry.get("file") or ""),
                Node().slug(entry.get("story") or ""),
                (entry.get("scenario") or "").lower(),
            )
            found = scenarios.get(key)
            if found is not None:
                return found
            for (_file, story_slug, scenario_name), scenario in scenarios.items():
                if scenario_name == (entry.get("scenario") or "").lower() and story_slug == Node().slug(
                    entry.get("story") or ""
                ):
                    return scenario
        if entry.get("background"):
            for bg_entry, background in backgrounds:
                if Node().slug(bg_entry.get("story") or "") != Node().slug(entry.get("story") or ""):
                    continue
                if (bg_entry.get("name") or "background") == (entry.get("background") or "background"):
                    return background
        return None


class Story(SourceStory, Node):
    practice = "stories"
    _semantic_type_name = "Story"

    def load_background(self, source: SourceBackground) -> Background:
        return Background(source.name, source.sequential_order)

    def load_scenario(self, source: SourceScenario) -> Scenario:
        return Scenario(source.name, source.sequential_order, source.story_name)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)


class SubEpic(SourceSubEpic, Node):
    practice = "stories"
    _semantic_type_name = "SubEpic"

    def load_sub_epic(self, source: SourceSubEpic) -> "SubEpic":
        return SubEpic(source.name, source.sequential_order)

    def load_story(self, source: SourceStory) -> Story:
        return Story(source.name, source.sequential_order, source.story_type)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)


class Epic(SourceEpic, Node):
    practice = "stories"
    _semantic_type_name = "Epic"

    def load_sub_epic(self, source: SourceSubEpic) -> SubEpic:
        return SubEpic(source.name, source.sequential_order)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)


class StoryMap(SourceStoryMap, Node):
    practice = "stories"
    _semantic_type_name = "StoryMap"

    def load_epic(self, source: SourceEpic) -> Epic:
        return Epic(source.name, source.sequential_order)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)

    def owner_of_example(self, entry: dict):
        kind = entry.get("owner_kind") or ""
        owner = entry.get("owner") or ""
        if kind == "story_map":
            graph = getattr(self, "_example_graph", None)
            if graph is not None and graph.story_map is not None:
                return graph.story_map
            return self
        if kind == "epic":
            return self._example_epics.get(Node().slug(owner))
        if kind == "sub_epic":
            return self._sub_epic_named(owner)
        if kind == "story":
            return self._example_stories.get(Node().slug(owner))
        return self._example_owner_by_slug(owner)

    def _sub_epic_named(self, owner: str):
        owner_slug = Node().slug(owner)
        for (_epic, sub_slug), sub in self._example_subs.items():
            if sub_slug == owner_slug:
                return sub
        return None

    def _example_owner_by_slug(self, owner: str):
        owner_slug = Node().slug(owner) if owner else ""
        if owner_slug in self._example_epics:
            return self._example_epics[owner_slug]
        found = self._sub_epic_named(owner)
        if found is not None:
            return found
        if not owner_slug:
            return self
        return None

    def ensure(self, graph: "PracticeGraph", raw: dict) -> None:
        self._example_epics = getattr(self, "_example_epics", {}) or {}
        self._example_subs = getattr(self, "_example_subs", {}) or {}
        self._example_stories = getattr(self, "_example_stories", {}) or {}
        self._example_graph = graph
        if graph.story_map is None:
            graph.story_map = StoryMap()
            graph.register(graph.story_map)
        story_map: StoryMap = graph.story_map
        epics: Dict[str, Epic] = {Node().slug(e.name): e for e in graph.nodes_of_type(Epic)}
        subs: Dict[Tuple[str, str], SubEpic] = {}
        for sub in graph.nodes_of_type(SubEpic):
            parent = ""
            for epic in epics.values():
                if sub in epic.sub_epics:
                    parent = Node().slug(epic.name)
                    break
            subs[(parent, Node().slug(sub.name))] = sub
        stories: Dict[str, Story] = {Node().slug(s.name): s for s in graph.nodes_of_type(Story)}
        for entry in raw.get("stories") or []:
            epic_name = self._display_name(entry.get("epic") or "") or "Stories"
            sub_name = self._display_name(entry.get("sub_epic") or "")
            epic = epics.get(Node().slug(epic_name))
            if epic is None:
                epic = story_map.load_epic(Epic(epic_name, len(epics) + 1))
                story_map.epics.append(epic)
                graph.register(epic)
                story_map.relate(Kind.OWNS, epic)
                epics[Node().slug(epic_name)] = epic
            parent: Epic | SubEpic = epic
            if sub_name:
                key = (Node().slug(epic_name), Node().slug(sub_name))
                sub = subs.get(key)
                if sub is None:
                    sub = epic.load_sub_epic(SubEpic(sub_name, len(epic.sub_epics) + 1))
                    epic.sub_epics.append(sub)
                    graph.register(sub)
                    epic.relate(Kind.OWNS, sub)
                    subs[key] = sub
                parent = sub
            if Node().slug(entry.get("name") or "") in stories:
                story = stories[Node().slug(entry.get("name") or "")]
            elif hasattr(parent, "load_story"):
                story = parent.load_story(Story(entry.get("name") or "", len(parent.stories) + 1))
                story.source = SourceLocation(entry.get("file") or "", int(entry.get("line") or 0))
                parent.stories.append(story)
                graph.register(story)
                parent.relate(Kind.OWNS, story)
                stories[Node().slug(story.name)] = story
            else:
                story = Story(entry.get("name") or "", len(getattr(parent, "stories", []) or []) + 1)
                story.source = SourceLocation(entry.get("file") or "", int(entry.get("line") or 0))
                graph.register(story)
                parent.relate(Kind.OWNS, story)
                stories[Node().slug(story.name)] = story
        backgrounds: List[Tuple[dict, Background]] = []
        for entry in raw.get("backgrounds") or []:
            story = stories.get(Node().slug(entry.get("story") or ""))
            if story is None or story.backgrounds:
                continue
            background = story.load_background(Background(entry.get("name") or "background", 1))
            story.backgrounds.append(background)
            graph.register(background)
            story.relate(Kind.OWNS, background)
            backgrounds.append((entry, background))
        scenarios: Dict[Tuple[str, str, str], Scenario] = {}
        for entry in raw.get("scenarios") or []:
            story = stories.get(Node().slug(entry.get("story") or ""))
            if story is None:
                continue
            key = (
                self.normalized_file(entry.get("file") or ""),
                Node().slug(entry.get("story") or ""),
                (entry.get("name") or "").lower(),
            )
            scenario = story.load_scenario(
                Scenario(entry.get("name") or "", len(story.scenarios) + 1, story.name)
            )
            scenario.source = SourceLocation(entry.get("file") or "", int(entry.get("line") or 0))
            story.scenarios.append(scenario)
            graph.register(scenario)
            story.relate(Kind.OWNS, scenario)
            scenarios[key] = scenario
        created_steps: List[Tuple[dict, Step]] = []
        for entry in raw.get("steps") or []:
            finder = Scenario()
            finder._scenarios = scenarios
            finder._backgrounds = backgrounds
            parent = finder.owner_of(entry)
            if parent is None:
                continue
            phase = self._phase_for(entry.get("phase") or "", entry.get("keyword") or "")
            is_continuation = entry.get("keyword") in {"And", "But"}
            order = len(parent.steps) + 1 if hasattr(parent, "steps") else 1
            step = parent.load_step(
                Step(
                    text=entry.get("text") or "",
                    phase=phase,
                    sequential_order=order,
                    is_continuation=is_continuation,
                    keyword=entry.get("keyword") or "",
                    source=SourceLocation(entry.get("file") or "", int(entry.get("line") or 0)),
                )
            )
            parent.steps.append(step)
            graph.register(step)
            parent.relate(Kind.OWNS, step)
            created_steps.append((entry, step))
        story_map._example_epics = epics
        story_map._example_subs = subs
        story_map._example_stories = stories
        self._example_epics = epics
        self._example_subs = subs
        self._example_stories = stories
        self._example_graph = graph
        self._ensure_examples(raw.get("example_exports") or [])
        self._wire_demonstrated_through(graph, created_steps)
        calls = Step("", Phase.GIVEN, 0)
        calls.wire_calls(graph, raw.get("story_calls") or [])
        calls.wire_observations(graph, raw.get("story_observations") or [])
        Example("", 0).wire_demonstrates(graph, raw.get("example_exports") or [])

    def _ensure_examples(self, entries: List[dict]) -> None:
        existing = {ex.name.lower(): ex for ex in self._example_graph.nodes_of_type(Example)}
        for entry in entries:
            name = entry.get("export_name") or ""
            example = existing.get(name.lower())
            if example is not None:
                continue
            owner = self.owner_of_example(entry)
            if owner is None:
                owner = self._example_graph.story_map
            self._example_entry = entry
            self._example_name = name
            example = self._new_example(owner)
            self._example_graph.register(example)
            existing[name.lower()] = example
            if owner is not None:
                if getattr(owner, "_graph", None) is None:
                    self._example_graph.register(owner)
                owner.examples.append(example)
                owner.relate(Kind.SCOPES, example)

    def _new_example(self, owner):
        order = len(getattr(owner, "examples", []) or []) + 1 if owner is not None else 1
        scope = self._example_entry.get("owner_kind") or "story"
        if owner is not None and hasattr(owner, "load_example"):
            return owner.load_example(Example(self._example_name, order, {}, scope=scope))
        return Example(self._example_name, order, {}, scope=scope)

    def _wire_demonstrated_through(self, graph: "PracticeGraph", created_steps) -> None:
        by_name: Dict[str, Example] = {}
        for example in graph.nodes_of_type(Example):
            by_name[example.name] = example
            by_name[example.name.lower()] = example
        for entry, step in created_steps:
            for name in entry.get("uses_examples") or []:
                example = by_name.get(name) or by_name.get(name.lower())
                if example is None:
                    continue
                step.demonstrated_through(example)


    def _display_name(self, name: str) -> str:
        if not name:
            return ""
        if " " in name:
            return name
        return name.replace("-", " ").replace("_", " ").title()

    def normalized_file(self, path: str) -> str:
        return path.replace("\\", "/").lstrip("./")

    def _phase_for(self, phase: str, keyword: str) -> Phase:
        value = (phase or keyword or "given").lower()
        mapping = {"given": Phase.GIVEN, "when": Phase.WHEN, "then": Phase.THEN}
        if value in {"and", "but"}:
            return Phase.THEN
        return mapping.get(value, Phase.GIVEN)
