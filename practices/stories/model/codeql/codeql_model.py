"""CodeQL graph types for Stories — wrap live Stories types."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from practices.stories.model.source_location import SourceLocation
from practices.stories.model.story_model import (
    Background as SourceBackground,
    Example as SourceExample,
    Examples,
    Epic as SourceEpic,
    StepType,
    Scenario as SourceScenario,
    Step as SourceStep,
    Story as SourceStory,
    StoryMap as SourceStoryMap,
    Epic as SourceEpic,
)

from harness.knowledge_graph.model.graph_node import Kind, Node

if TYPE_CHECKING:
    from harness.knowledge_graph.model.practice_graph import PracticeGraph


class Example(SourceExample, Node):
    practice = "stories"
    _semantic_type_name = "Example"

    def demonstrates(self, cls: Node) -> None:
        if cls.semantic_type() != "OoadClass":
            return
        if cls.node_id in {node.node_id for node in self.related(Kind.DEMONSTRATES)}:
            return
        self.relate(Kind.DEMONSTRATES, cls)

    def retrieved_using(self, member: Node) -> None:
        """An example is read back through at most one operation or property."""
        if member.semantic_type() not in {"Operation", "Property"}:
            return
        if self.related(Kind.RETRIEVED_USING):
            return
        self.relate(Kind.RETRIEVED_USING, member)

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
        owned = graph.ce_class_named(class_name)
        if owned is None:
            return
        entry = self._demonstrate_entry
        for example in self.matching(entry.get("export_name") or "", entry.get("file") or ""):
            example.demonstrates(owned)


class Step(SourceStep, Node):
    practice = "stories"
    _semantic_type_name = "Step"

    def invokes(self, target: Node) -> None:
        """A when step calls zero or more operations or properties."""
        if self.step_type != StepType.WHEN:
            return
        if target.semantic_type() not in {"Operation", "Property"}:
            return
        if target.node_id in {node.node_id for node in self.related(Kind.INVOKES)}:
            return
        self.relate(Kind.INVOKES, target)

    def observes(self, example: Node) -> None:
        """A then step watches at most one example."""
        if self.step_type != StepType.THEN:
            return
        if example.semantic_type() != "Example":
            return
        if self.related(Kind.OBSERVES):
            return
        self.relate(Kind.OBSERVES, example)

    def loads(self, example: Node) -> None:
        """A given step arranges zero or more examples."""
        if self.step_type != StepType.GIVEN:
            return
        if example.semantic_type() != "Example":
            return
        if example.node_id in {node.node_id for node in self.related(Kind.LOADS)}:
            return
        self.relate(Kind.LOADS, example)

    @classmethod
    def from_source(cls, source: SourceStep) -> "Step":
        return cls(
            text=source.text,
            step_type=source.step_type,
            sequential_order=source.sequential_order,
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
            target = graph.operation_named(
                story_call.get("callee_class") or "",
                story_call.get("callee_operation") or "",
            )
            if target is None:
                target = self._property_named(
                    graph,
                    story_call.get("callee_class") or "",
                    story_call.get("callee_operation") or "",
                )
            if step is None or target is None:
                continue
            step.invokes(target)

    def _property_named(self, graph: "PracticeGraph", class_name: str, property_name: str):
        owner = graph.class_named(class_name)
        if owner is None:
            return None
        for node in owner.related(Kind.OWNS):
            if node.semantic_type() == "Property" and node.name == property_name:
                return node
        return None

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
            if target is None:
                continue
            if step.step_type == StepType.WHEN:
                step.invokes(target)
                continue
            if step.step_type != StepType.THEN:
                continue
            watched = step.related(Kind.OBSERVES)
            if watched:
                watched[0].retrieved_using(target)

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

    def loads(self, example: Node) -> None:
        if example.semantic_type() != "Example":
            return
        if example.node_id in {node.node_id for node in self.related(Kind.LOADS)}:
            return
        self.relate(Kind.LOADS, example)

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
        return Example(source.name, source.value, source.sequential_order)

    def aggregate_from_steps(self) -> None:
        """A scenario's invokes and observes are the union of its steps."""
        self._copy_edges(self._owned_steps(), (Kind.INVOKES, Kind.OBSERVES))

    def _owned_steps(self) -> List[Step]:
        steps: List[Step] = []
        for step in self.related(Kind.OWNS):
            if step.semantic_type() != "Step":
                continue
            steps.append(step)
            steps.extend(step.ands)
        return steps

    def _copy_edges(self, sources: List[Node], kinds: tuple) -> None:
        held = {kind: {node.node_id for node in self.related(kind)} for kind in kinds}
        for source in sources:
            for kind in kinds:
                for target in source.related(kind):
                    if target.node_id in held[kind]:
                        continue
                    self.relate(kind, target)
                    held[kind].add(target.node_id)

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
        return Example(source.name, source.value, source.sequential_order)

    def aggregate_from_scenarios(self) -> None:
        """A story's invokes and observes are the union of its scenarios."""
        scenarios = [
            node for node in self.related(Kind.OWNS) if node.semantic_type() == "Scenario"
        ]
        Scenario._copy_edges(self, scenarios, (Kind.INVOKES, Kind.OBSERVES))


class Epic(SourceEpic, Node):
    practice = "stories"
    _semantic_type_name = "Epic"

    def uses(self, module: Node) -> None:
        if module.semantic_type() != "Module":
            return
        if module.node_id in {node.node_id for node in self.related(Kind.USES)}:
            return
        self.relate(Kind.USES, module)

    def load_epic(self, source: SourceEpic) -> "Epic":
        return Epic(source.name, source.sequential_order)

    def load_story(self, source: SourceStory) -> Story:
        return Story(source.name, source.sequential_order, source.story_type)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.value, source.sequential_order)




class StoryMap(SourceStoryMap, Node):
    practice = "stories"
    _semantic_type_name = "StoryMap"

    def load_epic(self, source: SourceEpic) -> Epic:
        return Epic(source.name, source.sequential_order)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.value, source.sequential_order)

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
        subs: Dict[Tuple[str, str], Epic] = {}
        for sub in graph.nodes_of_type(Epic):
            parent = ""
            for epic in epics.values():
                if sub in epic.epics:
                    parent = Node().slug(epic.name)
                    break
            subs[(parent, Node().slug(sub.name))] = sub
        stories: Dict[Tuple[str, str], Story] = {}
        chain: Dict[Tuple[str, ...], Epic] = {}
        for entry in raw.get("stories") or []:
            owners = [self._display_name(name) for name in (entry.get("owners") or []) if name]
            if not owners:
                epic_name = self._display_name(entry.get("epic") or "") or "Stories"
                sub_name = self._display_name(entry.get("sub_epic") or "")
                owners = [epic_name] + ([sub_name] if sub_name else [])
            parent = self._epic_at(graph, story_map, chain, epics, subs, owners)
            story_key = (
                self.normalized_file(entry.get("file") or ""),
                Node().slug(entry.get("name") or ""),
            )
            story = stories.get(story_key)
            if story is None:
                story = Story(entry.get("name") or "", len(parent.stories) + 1)
                story.source = SourceLocation(entry.get("file") or "", int(entry.get("line") or 0))
                actor = (entry.get("actor") or "").strip()
                if actor:
                    story.actors = [actor]
                parent.stories.append(story)
                graph.register(story)
                parent.relate(Kind.OWNS, story)
                stories[story_key] = story
        backgrounds: List[Tuple[dict, Background]] = []
        for entry in raw.get("backgrounds") or []:
            story = stories.get(self._story_key(entry))
            if story is None or story.backgrounds:
                continue
            background = Background(entry.get("name") or "background", 1)
            background.source = SourceLocation(
                entry.get("file") or "",
                int(entry.get("line") or 0),
                int(entry.get("end_line") or 0),
            )
            story.backgrounds.append(background)
            graph.register(background)
            story.relate(Kind.OWNS, background)
            backgrounds.append((entry, background))
        self._example_backgrounds: Dict[Tuple[str, str, str], Background] = {}
        scenarios: Dict[Tuple[str, str, str], Scenario] = {}
        for entry in raw.get("scenarios") or []:
            story = stories.get(self._story_key(entry))
            if story is None:
                continue
            key = (
                self.normalized_file(entry.get("file") or ""),
                Node().slug(entry.get("story") or ""),
                (entry.get("name") or "").lower(),
            )
            scenario = Scenario(entry.get("name") or "", len(story.scenarios) + 1, story.name)
            scenario.source = SourceLocation(
                entry.get("file") or "",
                int(entry.get("line") or 0),
                int(entry.get("end_line") or 0),
            )
            story.scenarios.append(scenario)
            graph.register(scenario)
            story.relate(Kind.OWNS, scenario)
            scenarios[key] = scenario
        self._example_scenarios = scenarios
        for entry, background in backgrounds:
            key = (
                self.normalized_file(entry.get("file") or ""),
                Node().slug(entry.get("story") or ""),
                (entry.get("name") or "").lower(),
            )
            self._example_backgrounds[key] = background
        created_steps = self._place_steps(graph, scenarios, backgrounds, raw.get("steps") or [])
        story_map._example_epics = epics
        story_map._example_subs = subs
        story_map._example_stories = stories
        self._example_epics = epics
        self._example_subs = subs
        self._example_stories = stories
        self._example_graph = graph
        self._ensure_examples(raw.get("example_exports") or [])
        self._wire_step_examples(graph, created_steps, [node for _, node in backgrounds])
        calls = Step("", StepType.GIVEN, 0)
        calls.wire_calls(graph, raw.get("story_calls") or [])
        calls.wire_observations(graph, raw.get("story_observations") or [])
        Example("").wire_demonstrates(graph, raw.get("example_exports") or [])
        self._aggregate_cross_practice(graph)

    def _epic_at(self, graph, story_map, chain, epics, subs, owners: List[str]) -> Epic:
        parent = None
        built: List[str] = []
        for name in owners:
            built.append(Node().slug(name))
            key = tuple(built)
            node = chain.get(key)
            if node is None:
                node = Epic(name, (len(story_map.epics) if parent is None else len(parent.epics)) + 1)
                if parent is None:
                    story_map.epics.append(node)
                    story_map.relate(Kind.OWNS, node)
                    epics[Node().slug(name)] = node
                else:
                    parent.epics.append(node)
                    parent.relate(Kind.OWNS, node)
                    subs[(Node().slug(parent.name), Node().slug(name))] = node
                graph.register(node)
                chain[key] = node
            parent = node
        return parent

    def _story_key(self, entry: dict) -> Tuple[str, str]:
        return (
            self.normalized_file(entry.get("file") or ""),
            Node().slug(entry.get("story") or entry.get("name") or ""),
        )

    def _place_steps(self, graph, scenarios, backgrounds, entries: List[dict]) -> List[Tuple[dict, Step]]:
        """Given, When, and Then stay steps. And and But sit on the step they continue."""
        grouped: Dict[int, Tuple[object, List[dict]]] = {}
        order: List[int] = []
        for entry in entries:
            finder = Scenario()
            finder._scenarios = scenarios
            finder._backgrounds = backgrounds
            parent = finder.owner_of(entry)
            if parent is None:
                continue
            identity = id(parent)
            if identity not in grouped:
                grouped[identity] = (parent, [])
                order.append(identity)
            grouped[identity][1].append(entry)
        created: List[Tuple[dict, Step]] = []
        phases = {"given": StepType.GIVEN, "when": StepType.WHEN, "then": StepType.THEN}
        for identity in order:
            parent, rows = grouped[identity]
            built: List[Step] = []
            previous: Optional[Step] = None
            for row in rows:
                word = (row.get("keyword") or "given").lower()
                text = row.get("text") or ""
                source = SourceLocation(row.get("file") or "", int(row.get("line") or 0))
                if word in {"and", "but"} and previous is not None:
                    extra = Step(text, previous.step_type, len(previous.ands) + 1, keyword=word, source=source)
                    previous.ands = [*previous.ands, extra]
                    graph.register(extra)
                    created.append((row, extra))
                    continue
                phase = phases.get(word)
                if phase is None:
                    continue
                step = Step(text, phase, len(built) + 1, keyword=word, source=source)
                if parent.semantic_type() == "Background" and step.keyword != "Given":
                    previous = step
                    continue
                built.append(step)
                previous = step
                graph.register(step)
                parent.relate(Kind.OWNS, step)
                for name in row.get("uses_examples") or []:
                    if hasattr(parent, "examples"):
                        parent.examples[name] = name
                created.append((row, step))
            parent.steps = built
        return created

    def _ensure_examples(self, entries: List[dict]) -> None:
        self._examples_by_file: Dict[Tuple[str, str], Example] = {}
        for example in self._example_graph.nodes_of_type(Example):
            file_name = self.normalized_file(getattr(getattr(example, "source", None), "file", "") or "")
            self._examples_by_file[(file_name, example.name.lower())] = example
        for entry in entries:
            name = entry.get("export_name") or ""
            file_name = self.normalized_file(entry.get("file") or "")
            example = self._examples_by_file.get((file_name, name.lower()))
            if example is None:
                self._example_entry = entry
                self._example_name = name
                example = self._new_example(None)
                example.source = SourceLocation(entry.get("file") or "", int(entry.get("line") or 0))
                self._example_graph.register(example)
                self._examples_by_file[(file_name, name.lower())] = example

    def _stories_in_sub_epic(self, sub_name: str):
        sub = self._sub_epic_named(sub_name)
        if sub is None:
            return []
        return list(getattr(sub, "stories", []) or [])

    def _scope_example(self, owner, example: Example) -> None:
        if owner is None or example is None:
            return
        if getattr(owner, "_graph", None) is None:
            self._example_graph.register(owner)
        owned = getattr(owner, "examples", None)
        if owned is None:
            return
        owned[example.name] = example
        owner.relate(Kind.SCOPES, example)

    def _wire_imported_examples(self, entries: List[dict]) -> None:
        for entry in entries:
            name = (entry.get("export_name") or "").lower()
            file_name = self.normalized_file(entry.get("file") or "")
            example = self._examples_by_file.get((file_name, name))
            if example is None:
                continue
            seen: set[str] = set()
            for use in entry.get("used_by") or []:
                story = self._example_stories.get(Node().slug(use.get("story") or ""))
                if story is None or story.node_id in seen:
                    continue
                seen.add(story.node_id)
                self._scope_example(story, example)

    def _imported_owner(self, use: dict):
        key = (
            self.normalized_file(use.get("file") or ""),
            Node().slug(use.get("story") or ""),
            (use.get("name") or "").lower(),
        )
        if use.get("kind") == "background":
            return self._example_backgrounds.get(key)
        return self._example_scenarios.get(key)

    def _new_example(self, owner):
        order = len(getattr(owner, "examples", {}) or {}) + 1 if owner is not None else 1
        return Example(self._example_name, {}, order)

    def _remember_examples(self, node, names) -> None:
        held = getattr(node, "_example_names", None)
        if held is None:
            held = []
            node._example_names = held
        for name in names:
            if name and name not in held:
                held.append(name)

    def _example_named(self, by_name: Dict[str, Example], name: str):
        return by_name.get(name) or by_name.get(str(name).lower())

    def _wire_step_examples(self, graph: "PracticeGraph", created_steps, backgrounds) -> None:
        by_name: Dict[str, Example] = {}
        for example in graph.nodes_of_type(Example):
            by_name[example.name] = example
            by_name[example.name.lower()] = example
        for entry, step in created_steps:
            examples = [
                example
                for name in (entry.get("uses_examples") or [])
                if (example := self._example_named(by_name, name)) is not None
            ]
            if step.step_type == StepType.GIVEN:
                for example in examples:
                    step.loads(example)
            elif step.step_type == StepType.THEN and examples:
                step.observes(examples[0])
        for background in backgrounds:
            for step in background.related(Kind.OWNS):
                if step.semantic_type() != "Step":
                    continue
                for example in step.related(Kind.LOADS):
                    background.loads(example)
                for extra in step.ands:
                    for example in extra.related(Kind.LOADS):
                        background.loads(example)

    def _aggregate_cross_practice(self, graph: "PracticeGraph") -> None:
        for scenario in graph.nodes_of_type(Scenario):
            scenario.aggregate_from_steps()
        for story in graph.nodes_of_type(Story):
            story.aggregate_from_scenarios()
        for epic in graph.nodes_of_type(Epic):
            self._wire_epic_modules(epic)

    def _wire_epic_modules(self, epic: Epic) -> None:
        for story in self._stories_under(epic):
            for node in story.related(Kind.OWNS):
                self._use_modules_from(epic, node)
                if node.semantic_type() != "Scenario":
                    continue
                for step in node.related(Kind.OWNS):
                    self._use_modules_from(epic, step)
                    for extra in getattr(step, "ands", []):
                        self._use_modules_from(epic, extra)

    def _stories_under(self, epic: Epic) -> List:
        stories = []
        for child in epic.related(Kind.OWNS):
            if child.semantic_type() == "Story":
                stories.append(child)
            elif child.semantic_type() == "Epic":
                stories.extend(self._stories_under(child))
        return stories

    def _use_modules_from(self, epic: Epic, node) -> None:
        for kind in (Kind.LOADS, Kind.OBSERVES, Kind.INVOKES):
            for target in node.related(kind):
                if target.semantic_type() == "Example":
                    for cls in target.related(Kind.DEMONSTRATES):
                        module = self._module_of(cls)
                        if module is not None:
                            epic.uses(module)
                    continue
                module = self._module_of(target)
                if module is not None:
                    epic.uses(module)

    def _module_of(self, node):
        home = node.home_module
        if home is not None and home.semantic_type() == "Module":
            return home
        return None


    @classmethod
    def load_folder(cls, folder) -> "StoryMap":
        """Build the story map from the story queries over a folder of story files."""
        from pathlib import Path

        from harness.knowledge_graph.model.codeql_query import query_workspace
        from harness.knowledge_graph.model.practice_graph import PracticeGraph

        root = Path(folder)
        export = query_workspace(root)
        graph = PracticeGraph(root)
        cls().ensure(graph, cls._raw(export))
        return graph.story_map

    @staticmethod
    def _raw(export) -> dict:
        from dataclasses import asdict

        return {
            "stories": [
                {
                    "name": story.text,
                    "file": story.file,
                    "epic": story.epic,
                    "sub_epic": story.sub_epic,
                    "line": story.line,
                    "actor": story.actor,
                    "owners": list(story.owners),
                }
                for story in export.stories
            ],
            "scenarios": [asdict(scenario) | {"name": scenario.text} for scenario in export.scenarios],
            "backgrounds": [
                asdict(background) | {"name": background.text} for background in export.backgrounds
            ],
            "steps": [asdict(step) for step in export.steps],
            "example_exports": [asdict(example) for example in export.example_exports],
        }

    def _display_name(self, name: str) -> str:
        if not name:
            return ""
        if " " in name:
            return name
        return name.replace("-", " ").replace("_", " ").title()

    def normalized_file(self, path: str) -> str:
        return path.replace("\\", "/").lstrip("./")
