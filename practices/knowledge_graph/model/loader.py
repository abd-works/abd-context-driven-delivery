"""Load a PracticeGraph from an on-disk workspace."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from practices.clean_engineering.model.base_class_model import OoadClass
from practices.clean_engineering.model.operation import Operation as CeOperation
from practices.clean_engineering.model.property import Property as CeProperty
from practices.clean_engineering.model.type_refs import pascal_type_names
from practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from practices.stories.model.nodes import Epic, Story, SubEpic
from practices.stories.model.background import Background
from practices.stories.model.example import Example
from practices.stories.model.markdown.nodes import MarkdownScenario
from practices.stories.model.scenario import Scenario
from practices.stories.model.step import Step
from practices.stories.model.story_map import StoryMap
from practices.stories.model.workspace import Workspace

from .graph_node import Kind
from .nodes import (
    GraphClass,
    GraphCleanEngineeringModel,
    GraphBackground,
    GraphContext,
    GraphDescription,
    GraphEpic,
    GraphExample,
    GraphModule,
    GraphObservation,
    GraphOperation,
    GraphParameter,
    GraphProperty,
    GraphScenario,
    GraphStep,
    GraphStory,
    GraphStoryMap,
    GraphSubEpic,
    slug,
)
from .practice_graph import PracticeGraph


def load_practice_graph(path: str | Path) -> PracticeGraph:
    root = Path(path).resolve()
    graph = PracticeGraph(root)

    workspace = Workspace.load(root)
    story_map = _resolve_story_map(root, workspace.story_map)
    graph.story_map = _load_story_map(graph, story_map)
    graph.ce_model = _load_ce_model(graph, root)

    _index_story_epics(graph)
    if graph.ce_model is not None:
        _wire_ce_model(graph, graph.ce_model)

    _derive_cross_module_dependencies(graph)
    _load_bdd_descriptions(graph, root)

    return graph


def _resolve_story_map(root: Path, story_map: StoryMap) -> StoryMap:
    if story_map.epics:
        return story_map
    from practices.stories.model.markdown.nodes import MarkdownStoryMap

    for name in ("story_map.md", "story-map.md"):
        candidate = root / name
        if candidate.is_file():
            parsed = MarkdownStoryMap.from_workspace(candidate)
            if parsed and parsed.epics:
                parsed.attach_scenarios(MarkdownScenario.from_workspace(root))
                return parsed
    parsed = MarkdownStoryMap.from_workspace(root)
    if parsed and parsed.epics:
        return parsed
    return story_map


def _load_story_map(graph: PracticeGraph, story_map: StoryMap) -> GraphStoryMap:
    target = GraphStoryMap()
    target.translate_from(story_map)
    graph.register(target)
    return target


def _load_ce_model(graph: PracticeGraph, root: Path) -> Optional[GraphCleanEngineeringModel]:
    parsed = MarkdownCleanEngineeringModel.from_workspace(root)
    if parsed is None:
        return None
    target = GraphCleanEngineeringModel(parsed.name, parsed.sequential_order)
    target.translate_from(parsed)
    graph.register(target)
    return target


def _index_story_epics(graph: PracticeGraph) -> None:
    assert graph.story_map is not None
    for epic in graph.story_map.epics:
        if not isinstance(epic, GraphEpic):
            continue
        graph.register(epic)
        graph.index_epic(epic)
        graph.relate(graph.story_map, Kind.OWNS, epic)
        _register_sub_epic_tree(graph, epic)


def _register_sub_epic_tree(graph: PracticeGraph, epic: Epic) -> None:
    for example in getattr(epic, "examples", []):
        _register_example(graph, epic, example, scope="epic")
    for sub in epic.sub_epics:
        if not isinstance(sub, GraphSubEpic):
            continue
        graph.register(sub)
        graph.epics[slug(sub.name)] = sub  # type: ignore[assignment]
        graph.relate(epic, Kind.OWNS, sub)
        _register_sub_epic_tree(graph, sub)
        for story in sub.stories:
            _register_story(graph, sub, story)
    if isinstance(epic, SubEpic):
        for story in epic.stories:
            _register_story(graph, epic, story)


def _register_story(graph: PracticeGraph, parent: SubEpic, story: Story) -> None:
    if not isinstance(story, GraphStory):
        return
    graph.register(story)
    graph.relate(parent, Kind.OWNS, story)
    for example in getattr(story, "examples", []):
        _register_example(graph, story, example, scope="story")
    for scenario in story.scenarios:
        _register_scenario(graph, story, scenario)


def _register_scenario(graph: PracticeGraph, story: GraphStory, scenario: Scenario) -> None:
    if not isinstance(scenario, GraphScenario):
        return
    if not scenario.steps and (scenario.given or scenario.interactions or scenario.background):
        scenario.sync_tree_from_legacy()
    graph.register(scenario)
    graph.relate(story, Kind.OWNS, scenario)
    _wire_scenario_tree(graph, scenario)


def _wire_scenario_tree(graph: PracticeGraph, scenario: GraphScenario) -> None:
    for background in scenario.backgrounds:
        _register_background(graph, scenario, background)
    for step in scenario.steps:
        _register_step(graph, scenario, step)
    for example in scenario.examples:
        _register_example(graph, scenario, example, scope="scenario")


def _register_background(graph: PracticeGraph, parent: GraphScenario, background: Background) -> None:
    if isinstance(background, GraphBackground):
        graph.register(background)
        graph.relate(parent, Kind.OWNS, background)
        for step in background.steps:
            _register_step(graph, background, step)


def _register_step(graph: PracticeGraph, parent, step: Step) -> None:
    if isinstance(step, GraphStep):
        graph.register(step)
        graph.relate(parent, Kind.OWNS, step)


def _register_example(graph: PracticeGraph, parent, example: Example, *, scope: str) -> None:
    if isinstance(example, GraphExample):
        graph.register(example)
        graph.relate(parent, Kind.SCOPES, example)
        example.scope = scope


def _wire_ce_model(graph: PracticeGraph, model: GraphCleanEngineeringModel) -> None:
    for module in model.modules:
        if not isinstance(module, GraphModule):
            continue
        graph.register(module)
        graph.index_module(module)
        graph.relate(model, Kind.OWNS, module)
        for index, oclass in enumerate(list(module.classes)):
            _wire_class(graph, module, oclass, index)


def _wire_class(graph: PracticeGraph, module: GraphModule, oclass: OoadClass, index: int) -> None:
    if not isinstance(oclass, GraphClass):
        target = GraphClass(oclass.name, oclass.sequential_order)
        target.translate_from(oclass)
        module.classes[index] = target
        oclass = target
    graph.register(oclass)
    graph.relate(module, Kind.OWNS, oclass)
    graph.relate(oclass, Kind.BELONGS_TO, module)

    if not oclass.property_nodes and not oclass.operation_nodes:
        oclass.sync_tree_from_legacy()

    for prop in oclass.property_nodes:
        _register_property(graph, oclass, prop)

    for rel in oclass.relationships:
        target = graph.find_class(rel.target)
        if target is not None:
            graph.relate(oclass, Kind.ASSOCIATES, target)

    for op in oclass.operation_nodes:
        _register_operation(graph, oclass, op)


def _register_property(graph: PracticeGraph, oclass, prop: CeProperty) -> None:
    if not isinstance(prop, GraphProperty):
        return
    graph.register(prop)
    graph.relate(oclass, Kind.OWNS, prop)
    graph.relate(prop, Kind.BELONGS_TO, oclass)
    for type_name in pascal_type_names(prop.type_hint):
        target = graph.find_class(type_name)
        if target is not None:
            graph.relate(prop, Kind.HAS_TYPE, target)


def _register_operation(graph: PracticeGraph, oclass, op: CeOperation) -> None:
    if not isinstance(op, GraphOperation):
        return
    graph.register(op)
    graph.relate(oclass, Kind.OWNS, op)
    graph.relate(op, Kind.BELONGS_TO, oclass)
    for type_name in pascal_type_names(op.return_type):
        target = graph.find_class(type_name)
        if target is not None:
            graph.relate(op, Kind.RETURNS, target)
    for param in op.parameters:
        if isinstance(param, GraphParameter):
            graph.register(param)
            graph.relate(op, Kind.HAS_PARAMETER, param)
            graph.relate(param, Kind.BELONGS_TO, op)
            for type_name in pascal_type_names(param.type_hint):
                target = graph.find_class(type_name)
                if target is not None:
                    graph.relate(param, Kind.HAS_TYPE, target)
    _wire_operation_invocations(graph, op, oclass.name)


def _wire_operation_invocations(graph: PracticeGraph, operation: GraphOperation, owner_class: str) -> None:
    for callee in operation.callees:
        callee = callee.strip()
        if not callee:
            continue
        if "." in callee:
            class_name, op_name = callee.split(".", 1)
        else:
            class_name, op_name = owner_class, callee
        target = graph.find_operation(class_name, op_name)
        if target is not None:
            graph.relate(operation, Kind.INVOKES, target)


def _derive_cross_module_dependencies(graph: PracticeGraph) -> None:
    class_home: dict[str, GraphModule] = {}
    for module in graph.nodes_of_type(GraphModule):
        for oclass in module.classes:
            if isinstance(oclass, GraphClass):
                class_home[oclass.node_id] = module

    for oclass in graph.nodes_of_type(GraphClass):
        home = class_home.get(oclass.node_id)
        if home is None:
            continue
        external: dict[str, GraphClass] = {}
        for owned in graph.outgoing_nodes(oclass, Kind.OWNS):
            if isinstance(owned, GraphProperty):
                for target in graph.outgoing_nodes(owned, Kind.HAS_TYPE):
                    if isinstance(target, GraphClass):
                        _maybe_external(graph, oclass, home, target, class_home, external)
            elif isinstance(owned, GraphOperation):
                for target in graph.outgoing_nodes(owned, Kind.RETURNS):
                    if isinstance(target, GraphClass):
                        _maybe_external(graph, oclass, home, target, class_home, external)
                for target in graph.outgoing_nodes(owned, Kind.INVOKES):
                    if isinstance(target, GraphOperation):
                        for owner in graph.incoming_nodes(target, Kind.BELONGS_TO):
                            if isinstance(owner, GraphClass):
                                _maybe_external(graph, oclass, home, owner, class_home, external)
        for target in graph.outgoing_nodes(oclass, Kind.ASSOCIATES):
            if isinstance(target, GraphClass):
                _maybe_external(graph, oclass, home, target, class_home, external)

        for ext in external.values():
            graph.relate(home, Kind.DEPENDS_ON, ext)
            ext_home = class_home.get(ext.node_id)
            if ext_home is not None:
                graph.relate(home, Kind.DEPENDS_ON, ext_home)


def _maybe_external(
    graph: PracticeGraph,
    owner_class: GraphClass,
    home: GraphModule,
    target: GraphClass,
    class_home: dict[str, GraphModule],
    external: dict[str, GraphClass],
) -> None:
    target_home = class_home.get(target.node_id)
    if target_home is None or target_home.node_id == home.node_id:
        return
    external[target.node_id] = target
    graph.relate(owner_class, Kind.DEPENDS_ON, target)


def _load_bdd_descriptions(graph: PracticeGraph, root: Path) -> None:
    from practices.bdd.scanners.bdd_scan_helpers import is_python_spec, read_text

    candidates: list[Path] = []
    for path in sorted(root.glob("**/*.py")):
        if path.name in ("examples.py",) or is_python_spec(path):
            candidates.append(path)
    for path in candidates:
        content = read_text(path)
        if "description(" not in content:
            continue
        _parse_python_bdd_file(graph, path, content)


def _parse_python_bdd_file(graph: PracticeGraph, path: Path, content: str) -> None:
    describe_re = re.compile(r"""with\s+description\s*\(\s*['"](.+?)['"]\s*\)\s*:""")
    context_re = re.compile(r"""with\s+context\s*\(\s*['"](.+?)['"]\s*\)\s*:""")
    it_re = re.compile(r"""with\s+it\s*\(\s*['"](.+?)['"]\s*\)\s*:""")

    stack: List[GraphDescription | GraphContext] = []

    for line_no, line in enumerate(content.splitlines(), start=1):
        m_desc = describe_re.search(line)
        if m_desc:
            label = m_desc.group(1)
            if stack and isinstance(stack[-1], GraphDescription):
                ctx = GraphContext(label, line_no)
                graph.register(ctx)
                graph.relate(stack[-1], Kind.OWNS, ctx)
                stack.append(ctx)
                continue
            desc = GraphDescription(label, line_no)
            graph.register(desc)
            graph.index_description(desc)
            stack = [desc]
            subject = _subject_class_name(label)
            cls = graph.find_class(subject)
            if cls is not None:
                graph.relate(desc, Kind.DESCRIBES, cls)
            continue

        m_ctx = context_re.search(line)
        if m_ctx and stack:
            ctx = GraphContext(m_ctx.group(1), line_no)
            graph.register(ctx)
            graph.relate(stack[-1], Kind.OWNS, ctx)
            stack.append(ctx)
            continue

        m_it = it_re.search(line)
        if m_it and stack and isinstance(stack[-1], GraphContext):
            obs = GraphObservation(m_it.group(1), line_no)
            graph.register(obs)
            graph.relate(stack[-1], Kind.OWNS, obs)
            continue

        stripped = line.strip()
        if stripped.startswith("with description(") or stripped.startswith("with context("):
            continue
        if stripped == "pass" and len(stack) > 1:
            stack.pop()


def _subject_class_name(label: str) -> str:
    cleaned = label.strip()
    for prefix in ("a ", "an ", "the "):
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix) :]
            break
    parts = cleaned.split()
    if not parts:
        return cleaned
    return parts[0][:1].upper() + parts[0][1:]
