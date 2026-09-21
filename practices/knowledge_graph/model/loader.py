"""Load a PracticeGraph from an on-disk workspace."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass
from practices.ddd.model.nodes import Aggregate, BoundedContext, Entity as DddEntity, ddd_class_for
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
from practices.ddd.model import (
    is_identity_property,
    load_bounded_context_map,
    plain_class_name,
    repository_root_name,
)
from practices.ddd.model.stereotypes import ddd_class_kind

from .nodes import (
    GraphAggregate,
    GraphBoundedContext,
    GraphClass,
    GraphCleanEngineeringModel,
    GraphBackground,
    GraphContext,
    GraphDescription,
    GraphDomainEvent,
    GraphDomainService,
    GraphEntity,
    GraphEntityRoot,
    GraphEpic,
    GraphExample,
    GraphModule,
    GraphObservation,
    GraphOperation,
    GraphParameter,
    GraphProperty,
    GraphRepository,
    GraphScenario,
    GraphStep,
    GraphStory,
    GraphStoryMap,
    GraphSubEpic,
    GraphValueObject,
    graph_ddd_class_for,
    slug,
)
from .practice_graph import PracticeGraph


def load_practice_graph(
    path: str | Path,
    *,
    codeql_results: str | Path | None = None,
) -> PracticeGraph:
    root = Path(path).resolve()
    codeql_path = Path(codeql_results).resolve() if codeql_results else None
    graph = PracticeGraph(root)

    workspace = Workspace.load(root)
    story_map = _resolve_story_map(root, workspace.story_map)
    graph.story_map = _load_story_map(graph, story_map)
    graph.ce_model = _load_ce_model(graph, root)

    _index_story_epics(graph)
    if graph.ce_model is not None:
        _wire_ce_model(graph, graph.ce_model)
        _wire_ddd_model(graph, root)
    else:
        _load_ddd_structure_from_map(graph, root)

    from .codeql_populate import populate_from_codeql

    populate_from_codeql(graph, root, results_path=codeql_path)
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
    bc_map = load_bounded_context_map(root)
    if bc_map:
        _structure_ce_model_with_bc_map(parsed, bc_map)
    else:
        _promote_ce_model_modules_to_aggregates(parsed)
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
        if not isinstance(module, (GraphModule, GraphBoundedContext, GraphAggregate)):
            continue
        graph.register(module)
        graph.index_module(module)
        graph.relate(model, Kind.OWNS, module)
        if isinstance(module, GraphBoundedContext):
            for agg in module.aggregates:
                if not isinstance(agg, GraphAggregate):
                    continue
                graph.register(agg)
                graph.index_module(agg)
                graph.relate(module, Kind.OWNS, agg)
                for index, oclass in enumerate(list(agg.classes)):
                    _wire_class(graph, agg, oclass, index)
        else:
            for index, oclass in enumerate(list(module.classes)):
                _wire_class(graph, module, oclass, index)


def _wire_class(graph: PracticeGraph, module: GraphModule, oclass: OoadClass, index: int) -> None:
    if not isinstance(oclass, (GraphClass, *_GRAPH_DDD_CLASSES)):
        if ddd_class_kind(oclass.name):
            target = graph_ddd_class_for(oclass)
            target.translate_from(oclass)
            module.classes[index] = target
            oclass = target
        elif not isinstance(oclass, GraphClass):
            target = GraphClass(plain_class_name(oclass.name), oclass.sequential_order)
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


_GRAPH_DDD_CLASSES = (
    GraphEntity,
    GraphEntityRoot,
    GraphValueObject,
    GraphRepository,
    GraphDomainEvent,
    GraphDomainService,
)


def _copy_module_meta(source: Module, target: Module) -> None:
    target.description = source.description
    target.seam = source.seam
    target.constraint = source.constraint
    target.seam_terms = list(source.seam_terms)
    target.dependencies = list(source.dependencies)


def _promote_ce_class(source: OoadClass) -> OoadClass:
    promoted = ddd_class_for(source)
    promoted.translate_from(source)
    return promoted


def _structure_ce_model_with_bc_map(model: CleanEngineeringModel, bc_map) -> None:
    module_by_name = {m.name.lower(): m for m in model.modules}
    new_modules: list[Module] = []
    consumed: set[str] = set()

    for order, bc_entry in enumerate(bc_map, start=1):
        src = module_by_name.get(bc_entry.name.lower())
        if src:
            bc = BoundedContext(src.name, src.sequential_order)
            _copy_module_meta(src, bc)
            consumed.add(bc_entry.name.lower())
        else:
            bc = BoundedContext(bc_entry.name, order)

        for agg_order, agg_entry in enumerate(bc_entry.aggregates, start=1):
            agg_src = module_by_name.get(agg_entry.name.lower())
            if agg_src:
                agg = Aggregate(agg_src.name, agg_src.sequential_order)
                _copy_module_meta(agg_src, agg)
                agg.classes = [_promote_ce_class(c) for c in agg_src.classes]
                consumed.add(agg_entry.name.lower())
            else:
                agg = Aggregate(agg_entry.name, agg_order)
            bc.aggregates.append(agg)

        new_modules.append(bc)

    for mod in model.modules:
        if mod.name.lower() in consumed:
            continue
        if any(ddd_class_kind(c.name) for c in mod.classes):
            agg = Aggregate(mod.name, mod.sequential_order)
            _copy_module_meta(mod, agg)
            agg.classes = [_promote_ce_class(c) for c in mod.classes]
            new_modules.append(agg)
        else:
            new_modules.append(mod)

    model.modules = new_modules


def _promote_ce_model_modules_to_aggregates(model: CleanEngineeringModel) -> None:
    promoted: list[Module] = []
    for mod in model.modules:
        if any(ddd_class_kind(c.name) for c in mod.classes):
            agg = Aggregate(mod.name, mod.sequential_order)
            _copy_module_meta(mod, agg)
            agg.classes = [_promote_ce_class(c) for c in mod.classes]
            promoted.append(agg)
        else:
            promoted.append(mod)
    model.modules = promoted


def _load_ddd_structure_from_map(graph: PracticeGraph, root: Path) -> None:
    bc_map = load_bounded_context_map(root)
    if not bc_map:
        return
    for order, bc_entry in enumerate(bc_map, start=1):
        bc = GraphBoundedContext(bc_entry.name, order)
        graph.register(bc)
        graph.index_module(bc)
        for agg_order, agg_entry in enumerate(bc_entry.aggregates, start=1):
            agg = GraphAggregate(agg_entry.name, agg_order)
            graph.register(agg)
            graph.index_module(agg)
            bc.aggregates.append(agg)
            graph.relate(bc, Kind.OWNS, agg)


def _wire_ddd_model(graph: PracticeGraph, root: Path) -> None:
    del root  # BC map already applied during CE load when present
    _wire_ddd_relationships(graph)


def _wire_ddd_relationships(graph: PracticeGraph) -> None:
    entity_roots: dict[str, GraphEntityRoot] = {}

    for agg in graph.nodes_of_type(GraphAggregate):
        for oclass in agg.classes:
            if isinstance(oclass, GraphEntityRoot):
                agg.root = oclass
                oclass.aggregate = agg
                graph.relate(agg, Kind.ROOT, oclass)
                graph.relate(oclass, Kind.BELONGS_TO, agg)
                entity_roots[oclass.name.lower()] = oclass

    for repo in graph.nodes_of_type(GraphRepository):
        root_name = repository_root_name(repo.name)
        if not root_name:
            continue
        root = entity_roots.get(root_name.lower())
        if root is None:
            found = graph.find_class(root_name)
            if isinstance(found, GraphEntityRoot):
                root = found
        if root is not None:
            repo.accesses = root
            graph.relate(repo, Kind.ACCESSES, root)

    for node in graph.nodes.values():
        if isinstance(node, DddEntity):
            _wire_entity_identity(graph, node)


def _wire_entity_identity(graph: PracticeGraph, entity: DddEntity) -> None:
    for prop in entity.property_nodes:
        if is_identity_property(prop.name, prop.type_hint):
            entity.identity.append(prop)
            graph.relate(entity, Kind.HAS_IDENTITY, prop)
    for op in entity.operation_nodes:
        if is_identity_property(op.name):
            entity.identity.append(op)
            graph.relate(entity, Kind.HAS_IDENTITY, op)
    for prop in entity.property_nodes:
        if prop.name != "identity":
            continue
        type_name = prop.type_hint.split("|")[0].strip().rstrip("[]")
        identity_cls = graph.find_class(type_name)
        if identity_cls is None:
            continue
        for id_prop in identity_cls.property_nodes:
            if is_identity_property(id_prop.name, id_prop.type_hint):
                entity.identity.append(id_prop)
                graph.relate(entity, Kind.HAS_IDENTITY, id_prop)


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


def _domain_modules(graph: PracticeGraph):
    for node in graph.nodes.values():
        if isinstance(node, (GraphModule, GraphBoundedContext, GraphAggregate)):
            yield node


def _domain_classes(graph: PracticeGraph):
    for node in graph.nodes.values():
        if isinstance(node, (GraphClass, *_GRAPH_DDD_CLASSES)):
            yield node


def _derive_cross_module_dependencies(graph: PracticeGraph) -> None:
    class_home: dict[str, Module] = {}
    for module in _domain_modules(graph):
        for oclass in module.classes:
            class_home[oclass.node_id] = module

    for oclass in _domain_classes(graph):
        home = class_home.get(oclass.node_id)
        if home is None:
            continue
        external: dict[str, OoadClass] = {}
        for owned in graph.outgoing_nodes(oclass, Kind.OWNS):
            if isinstance(owned, GraphProperty):
                for target in graph.outgoing_nodes(owned, Kind.HAS_TYPE):
                    if isinstance(target, OoadClass):
                        _maybe_external(graph, oclass, home, target, class_home, external)
            elif isinstance(owned, GraphOperation):
                for target in graph.outgoing_nodes(owned, Kind.RETURNS):
                    if isinstance(target, OoadClass):
                        _maybe_external(graph, oclass, home, target, class_home, external)
                for target in graph.outgoing_nodes(owned, Kind.INVOKES):
                    if isinstance(target, GraphOperation):
                        for owner in graph.incoming_nodes(target, Kind.BELONGS_TO):
                            if isinstance(owner, OoadClass):
                                _maybe_external(graph, oclass, home, owner, class_home, external)
        for target in graph.outgoing_nodes(oclass, Kind.ASSOCIATES):
            if isinstance(target, OoadClass):
                _maybe_external(graph, oclass, home, target, class_home, external)

        for ext in external.values():
            graph.relate(home, Kind.DEPENDS_ON, ext)
            ext_home = class_home.get(ext.node_id)
            if ext_home is not None:
                graph.relate(home, Kind.DEPENDS_ON, ext_home)


def _maybe_external(
    graph: PracticeGraph,
    owner_class: OoadClass,
    home: Module,
    target: OoadClass,
    class_home: dict[str, Module],
    external: dict[str, OoadClass],
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
