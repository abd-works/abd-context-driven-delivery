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

    @classmethod
    def matching(
        cls,
        index: Dict[str, List["Example"]],
        export_name: str,
        file_path: str,
    ) -> List["Example"]:
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

    @classmethod
    def wire_demonstrates(cls, graph: "PracticeGraph", entries: List[dict]) -> None:
        examples_by_name: Dict[str, List[Example]] = {}
        for example in graph.nodes_of_type(Example):
            examples_by_name.setdefault(example.name.lower(), []).append(example)
        for entry in entries:
            cls_names = entry.get("demonstrates") or []
            if not cls_names:
                continue
            for example in cls.matching(
                examples_by_name, entry.get("export_name") or "", entry.get("file") or ""
            ):
                for class_name in cls_names:
                    owned = graph.class_named(class_name)
                    if owned is not None:
                        example.demonstrates(owned)


class Step(SourceStep, Node):
    practice = "stories"
    _semantic_type_name = "Step"

    def invokes(self, operation: Node) -> None:
        self.relate(Kind.INVOKES, operation)

    def observes(self, target: Node) -> None:
        self.relate(Kind.OBSERVES, target)

    def demonstrated_through(self, example: Example) -> None:
        self.relate(Kind.DEMONSTRATED_THROUGH, example)

    @classmethod
    def wire_calls(cls, graph: "PracticeGraph", story_calls: List[dict]) -> None:
        for story_call in story_calls:
            step = cls.at(
                graph,
                story_call.get("story_file") or "",
                int(story_call.get("line") or 0),
                story_call.get("step_text") or "",
            )
            operation = graph.operation_named(
                story_call.get("callee_class") or "",
                story_call.get("callee_operation") or "",
            )
            if step is None or operation is None:
                continue
            step.invokes(operation)

    @classmethod
    def wire_observations(cls, graph: "PracticeGraph", observations: List[dict]) -> None:
        from practices.clean_engineering.model.codeql.codeql_model import Operation, Property

        for obs in observations:
            step = cls.at(graph, obs.get("story_file") or "", int(obs.get("line") or 0), "")
            if step is None:
                continue
            owned_class = graph.class_named(obs.get("target_class") or "")
            if owned_class is None:
                continue
            target = None
            for owned in owned_class.related(Kind.OWNS):
                if obs.get("member_kind") == "operation" and isinstance(owned, Operation):
                    if owned.name == obs.get("target_member"):
                        target = owned
                        break
                if obs.get("member_kind") == "property" and isinstance(owned, Property):
                    if owned.name == obs.get("target_member"):
                        target = owned
                        break
            if target is not None:
                step.observes(target)

    @classmethod
    def at(
        cls,
        graph: "PracticeGraph",
        story_file: str,
        line: int,
        step_text: str = "",
    ) -> Optional["Step"]:
        normalized = story_file.replace("\\", "/").lstrip("./")
        best: Tuple[int, Optional[Step]] = (1_000_000, None)
        for step in graph.nodes_of_type(Step):
            if step_text and step_text.lower() in step.text.lower():
                return step
            src = getattr(step, "source", None)
            if src is None:
                continue
            src_file = str(src.file).replace("\\", "/").lstrip("./")
            if src_file != normalized and not src_file.endswith(normalized):
                continue
            if line <= 0:
                return step
            delta = abs(int(src.line) - line)
            if delta < best[0]:
                best = (delta, step)
        if best[1] is not None and best[0] <= 5:
            return best[1]
        return None


class Background(SourceBackground, Node):
    practice = "stories"
    _semantic_type_name = "Background"

    def load_step(self, source: SourceStep) -> Step:
        return _step_from(source)


class Scenario(SourceScenario, Node):
    practice = "stories"
    _semantic_type_name = "Scenario"

    def load_background(self, source: SourceBackground) -> Background:
        return Background(source.name, source.sequential_order)

    def load_step(self, source: SourceStep) -> Step:
        return _step_from(source)

    def load_example(self, source: SourceExample) -> Example:
        return Example(source.name, source.sequential_order, dict(source.fields), source.scope)

    @classmethod
    def owner_of(
        cls,
        entry: dict,
        scenarios: Dict[Tuple[str, str, str], "Scenario"],
        backgrounds: List[Tuple[dict, Background]],
    ):
        if entry.get("scenario"):
            key = (
                _norm_file(entry.get("file") or ""),
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

    def owner_of_example(
        self,
        entry: dict,
        epics: Dict[str, Epic],
        subs: Dict[Tuple[str, str], SubEpic],
        stories: Dict[str, Story],
    ):
        kind = entry.get("owner_kind") or ""
        owner = entry.get("owner") or ""
        if kind == "story_map":
            return self
        if kind == "epic":
            return epics.get(Node().slug(owner))
        if kind == "sub_epic":
            for (_epic, sub_slug), sub in subs.items():
                if sub_slug == Node().slug(owner):
                    return sub
            return None
        if kind == "story":
            return stories.get(Node().slug(owner))
        owner_slug = Node().slug(owner) if owner else ""
        if owner_slug in epics:
            return epics[owner_slug]
        for (_epic, sub_slug), sub in subs.items():
            if sub_slug == owner_slug:
                return sub
        if not owner_slug:
            return self
        return None

    @classmethod
    def ensure(cls, graph: "PracticeGraph", raw: dict) -> None:
        if graph.story_map is None:
            graph.story_map = cls()
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
            epic_name = _display(entry.get("epic") or "") or "Stories"
            sub_name = _display(entry.get("sub_epic") or "")
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
            elif isinstance(parent, SubEpic):
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
                _norm_file(entry.get("file") or ""),
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
            parent = Scenario.owner_of(entry, scenarios, backgrounds)
            if parent is None:
                continue
            phase = _phase_for(entry.get("phase") or "", entry.get("keyword") or "")
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
        story_map._ensure_examples(graph, raw.get("example_exports") or [], epics, subs, stories)
        story_map._wire_demonstrated_through(graph, created_steps)
        Step.wire_calls(graph, raw.get("story_calls") or [])
        Step.wire_observations(graph, raw.get("story_observations") or [])
        Example.wire_demonstrates(graph, raw.get("example_exports") or [])

    def _ensure_examples(
        self,
        graph: "PracticeGraph",
        entries: List[dict],
        epics: Dict[str, Epic],
        subs: Dict[Tuple[str, str], SubEpic],
        stories: Dict[str, Story],
    ) -> None:
        existing = {ex.name.lower(): ex for ex in graph.nodes_of_type(Example)}
        for entry in entries:
            name = entry.get("export_name") or ""
            example = existing.get(name.lower())
            if example is None:
                owner = self.owner_of_example(entry, epics, subs, stories)
                order = len(getattr(owner, "examples", []) or []) + 1 if owner is not None else 1
                if owner is not None and hasattr(owner, "load_example"):
                    example = owner.load_example(
                        Example(name, order, {}, scope=entry.get("owner_kind") or "story")
                    )
                else:
                    example = Example(name, order, {}, scope=entry.get("owner_kind") or "story")
                graph.register(example)
                existing[name.lower()] = example
                if owner is not None:
                    owner.examples.append(example)
                    owner.relate(Kind.SCOPES, example)

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


def _step_from(source: SourceStep) -> Step:
    return Step(
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


def _display(name: str) -> str:
    if not name:
        return ""
    if " " in name:
        return name
    return name.replace("-", " ").replace("_", " ").title()


def _norm_file(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def _phase_for(phase: str, keyword: str) -> Phase:
    value = (phase or keyword or "given").lower()
    mapping = {"given": Phase.GIVEN, "when": Phase.WHEN, "then": Phase.THEN}
    if value in {"and", "but"}:
        return Phase.THEN
    return mapping.get(value, Phase.GIVEN)
