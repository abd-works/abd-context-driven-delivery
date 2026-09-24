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


_GRAPH_DDD_CLASSES = (
    GraphEntity,
    GraphEntityRoot,
    GraphValueObject,
    GraphRepository,
    GraphDomainEvent,
    GraphDomainService,
)

_DESCRIBE_RE = re.compile(r"""with\s+description\s*\(\s*['"](.+?)['"]\s*\)\s*:""")
_CONTEXT_RE = re.compile(r"""with\s+context\s*\(\s*['"](.+?)['"]\s*\)\s*:""")
_IT_RE = re.compile(r"""with\s+it\s*\(\s*['"](.+?)['"]\s*\)\s*:""")


def load_practice_graph(
    path: str | Path,
    *,
    codeql_results: str | Path | None = None,
) -> PracticeGraph:
    return GraphLoader(path, codeql_results).load()


def attach_story_tests(graph: PracticeGraph, paths: list[Path]) -> None:
    GraphLoader.from_graph(graph).attach(paths)


class GraphLoader:
    def __init__(self, path: str | Path, codeql_results: str | Path | None = None) -> None:
        self.root = Path(path).resolve()
        self._codeql_results = Path(codeql_results).resolve() if codeql_results else None
        self.graph = PracticeGraph(self.root)
        self._scope = ""
        self._module = None
        self._class_home: dict[str, Module] = {}
        self._external: dict[str, OoadClass] = {}
        self._home = None
        self._owner_class_name = ""
        self._relative = ""
        self._stack: List[GraphDescription | GraphContext] = []

    @classmethod
    def from_graph(cls, graph: PracticeGraph) -> "GraphLoader":
        loader = cls.__new__(cls)
        loader.graph = graph
        loader.root = graph.root
        loader._codeql_results = None
        loader._scope = ""
        loader._module = None
        loader._class_home = {}
        loader._external = {}
        loader._home = None
        loader._owner_class_name = ""
        loader._relative = ""
        loader._stack = []
        return loader

    def load(self, *, evaluate: bool = True) -> PracticeGraph:
        workspace = Workspace.load(self.root)
        story_map = self._resolve_story_map(workspace.story_map)
        self.graph.story_map = self._load_story_map(story_map)
        self.graph.ce_model = self._load_ce_model()
        self._index_story_epics()
        if self.graph.ce_model is not None:
            self._wire_ce_model(self.graph.ce_model)
            self._wire_ddd_model()
        else:
            self._load_ddd_structure_from_map()
        from .codeql_populate import populate_from_codeql

        populate_from_codeql(self.graph, self.root, results_path=self._codeql_results)
        self._derive_cross_module_dependencies()
        self._load_bdd_descriptions()
        if evaluate:
            self.graph.evaluate_rules(codeql_results=self._codeql_results)
        return self.graph

    def attach(self, paths: list[Path]) -> None:
        self._attach_story_tests(paths)

    def _resolve_story_map(self, story_map: StoryMap) -> StoryMap:
        if story_map.epics:
            return story_map
        from practices.stories.model.markdown.nodes import MarkdownStoryMap

        for name in ("story_map.md", "story-map.md"):
            parsed = self._story_map_from_named_file(MarkdownStoryMap, name)
            if parsed is not None:
                return parsed
        parsed = MarkdownStoryMap.from_workspace(self.root)
        if parsed and parsed.epics:
            return parsed
        return story_map

    def _story_map_from_named_file(self, markdown_story_map, name: str):
        candidate = self.root / name
        if not candidate.is_file():
            return None
        parsed = markdown_story_map.from_workspace(candidate)
        if not parsed or not parsed.epics:
            return None
        parsed.attach_scenarios(MarkdownScenario.from_workspace(self.root))
        return parsed

    def _load_story_map(self, story_map: StoryMap) -> GraphStoryMap:
        target = GraphStoryMap()
        target.translate_from(story_map)
        self.graph.register(target)
        return target

    def _load_ce_model(self) -> Optional[GraphCleanEngineeringModel]:
        parsed = MarkdownCleanEngineeringModel.from_workspace(self.root)
        if parsed is None:
            return None
        self._parsed = parsed
        self._bc_map = load_bounded_context_map(self.root)
        if self._bc_map:
            self._structure_ce_model_with_bc_map()
        else:
            self._promote_ce_model_modules_to_aggregates(parsed)
        target = GraphCleanEngineeringModel(parsed.name, parsed.sequential_order)
        target.translate_from(parsed)
        self.graph.register(target)
        return target

    def _index_story_epics(self) -> None:
        story_map = self.graph.story_map
        assert story_map is not None
        for epic in story_map.epics:
            if not isinstance(epic, GraphEpic):
                continue
            self.graph.register(epic)
            self.graph.index_epic(epic)
            story_map.relate(Kind.OWNS, epic)
            self._register_sub_epic_tree(epic)

    def _register_sub_epic_tree(self, epic: Epic) -> None:
        self._scope = "epic"
        for example in getattr(epic, "examples", []):
            self._register_example(epic, example)
        for sub in epic.sub_epics:
            self._register_sub_epic(epic, sub)
        if isinstance(epic, SubEpic):
            for story in epic.stories:
                self._register_story(epic, story)

    def _register_sub_epic(self, epic: Epic, sub: SubEpic) -> None:
        if not isinstance(sub, GraphSubEpic):
            return
        self.graph.register(sub)
        self.graph.epics[slug(sub.name)] = sub
        epic.relate(Kind.OWNS, sub)
        self._register_sub_epic_tree(sub)
        for story in sub.stories:
            self._register_story(sub, story)

    def _register_story(self, parent: SubEpic, story: Story) -> None:
        if not isinstance(story, GraphStory):
            return
        self.graph.register(story)
        parent.relate(Kind.OWNS, story)
        self._scope = "story"
        for example in getattr(story, "examples", []):
            self._register_example(story, example)
        for scenario in story.scenarios:
            self._register_scenario(story, scenario)

    def _register_scenario(self, story: GraphStory, scenario: Scenario) -> None:
        if not isinstance(scenario, GraphScenario):
            return
        scenario.sync_tree_from_legacy()
        self.graph.register(scenario)
        story.relate(Kind.OWNS, scenario)
        self._wire_scenario_tree(scenario)

    def _wire_scenario_tree(self, scenario: GraphScenario) -> None:
        for background in scenario.backgrounds:
            self._register_background(scenario, background)
        for step in scenario.steps:
            self._register_step(scenario, step)
        self._scope = "scenario"
        for example in scenario.examples:
            self._register_example(scenario, example)

    def _register_background(self, parent: GraphScenario, background: Background) -> None:
        if not isinstance(background, GraphBackground):
            return
        self.graph.register(background)
        parent.relate(Kind.OWNS, background)
        for step in background.steps:
            self._register_step(background, step)

    def _register_step(self, parent, step: Step) -> None:
        if not isinstance(step, GraphStep):
            return
        self.graph.register(step)
        parent.relate(Kind.OWNS, step)

    def _register_example(self, parent, example: Example) -> None:
        if not isinstance(example, GraphExample):
            return
        self.graph.register(example)
        parent.relate(Kind.SCOPES, example)
        example.scope = self._scope

    def _wire_ce_model(self, model: GraphCleanEngineeringModel) -> None:
        for module in model.modules:
            self._wire_ce_module(model, module)

    def _wire_ce_module(self, model: GraphCleanEngineeringModel, module) -> None:
        if not isinstance(module, (GraphModule, GraphBoundedContext, GraphAggregate)):
            return
        self.graph.register(module)
        self.graph.index_module(module)
        model.relate(Kind.OWNS, module)
        if isinstance(module, GraphBoundedContext):
            self._wire_bounded_context(module)
            return
        self._wire_module_classes(module)

    def _wire_bounded_context(self, module: GraphBoundedContext) -> None:
        for agg in module.aggregates:
            if not isinstance(agg, GraphAggregate):
                continue
            self.graph.register(agg)
            self.graph.index_module(agg)
            module.relate(Kind.OWNS, agg)
            self._wire_module_classes(agg)

    def _wire_module_classes(self, module: GraphModule) -> None:
        self._module = module
        for oclass in list(module.classes):
            self._wire_class(oclass)

    def _wire_class(self, oclass: OoadClass) -> None:
        oclass = self._promote_class(oclass)
        self._register_class(oclass)
        if not oclass.property_nodes and not oclass.operation_nodes:
            oclass.sync_tree_from_legacy()
        self._wire_class_properties(oclass)
        self._wire_class_associations(oclass)
        self._wire_class_operations(oclass)

    def _promote_class(self, oclass: OoadClass) -> OoadClass:
        if isinstance(oclass, (GraphClass, *_GRAPH_DDD_CLASSES)):
            return oclass
        return self._replace_module_class(oclass)

    def _replace_module_class(self, oclass: OoadClass) -> OoadClass:
        target = self._promoted_graph_class(oclass)
        target.translate_from(oclass)
        index = self._module.classes.index(oclass)
        self._module.classes[index] = target
        return target

    def _promoted_graph_class(self, oclass: OoadClass) -> OoadClass:
        if ddd_class_kind(oclass.name):
            return graph_ddd_class_for(oclass)
        return GraphClass(plain_class_name(oclass.name), oclass.sequential_order)

    def _register_class(self, oclass: OoadClass) -> None:
        self.graph.register(oclass)
        self._module.relate(Kind.OWNS, oclass)
        oclass.relate(Kind.BELONGS_TO, self._module)

    def _wire_class_properties(self, oclass: OoadClass) -> None:
        for prop in oclass.property_nodes:
            self._register_property(oclass, prop)

    def _wire_class_associations(self, oclass: OoadClass) -> None:
        for rel in oclass.relationships:
            target = self.graph.class_named(rel.target)
            if target is not None:
                oclass.relate(Kind.ASSOCIATES, target)

    def _wire_class_operations(self, oclass: OoadClass) -> None:
        self._owner_class_name = oclass.name
        for op in oclass.operation_nodes:
            self._register_operation(oclass, op)

    def _register_property(self, oclass, prop: CeProperty) -> None:
        if not isinstance(prop, GraphProperty):
            return
        self.graph.register(prop)
        oclass.relate(Kind.OWNS, prop)
        prop.relate(Kind.BELONGS_TO, oclass)
        self._wire_type_hints(prop, prop.type_hint)

    def _register_operation(self, oclass, op: CeOperation) -> None:
        if not isinstance(op, GraphOperation):
            return
        self.graph.register(op)
        oclass.relate(Kind.OWNS, op)
        op.relate(Kind.BELONGS_TO, oclass)
        self._wire_operation_returns(op)
        self._register_parameters(op)
        self._wire_operation_invocations(op)

    def _wire_operation_returns(self, op: GraphOperation) -> None:
        for type_name in pascal_type_names(op.return_type):
            target = self.graph.class_named(type_name)
            if target is not None:
                op.relate(Kind.RETURNS, target)

    def _register_parameters(self, op: GraphOperation) -> None:
        for param in op.parameters:
            self._register_parameter(op, param)

    def _register_parameter(self, op: GraphOperation, param) -> None:
        if not isinstance(param, GraphParameter):
            return
        self.graph.register(param)
        op.relate(Kind.HAS_PARAMETER, param)
        param.relate(Kind.BELONGS_TO, op)
        self._wire_type_hints(param, param.type_hint)

    def _wire_type_hints(self, node, type_hint: str) -> None:
        for type_name in pascal_type_names(type_hint):
            target = self.graph.class_named(type_name)
            if target is not None:
                node.relate(Kind.HAS_TYPE, target)

    def _copy_module_meta(self, source: Module, target: Module) -> None:
        target.description = source.description
        target.seam = source.seam
        target.constraint = source.constraint
        target.seam_terms = list(source.seam_terms)
        target.dependencies = list(source.dependencies)

    def _promote_ce_class(self, source: OoadClass) -> OoadClass:
        promoted = ddd_class_for(source)
        promoted.translate_from(source)
        return promoted

    def _structure_ce_model_with_bc_map(self) -> None:
        self._module_by_name = {m.name.lower(): m for m in self._parsed.modules}
        self._new_modules: list[Module] = []
        self._consumed: set[str] = set()
        for order, bc_entry in enumerate(self._bc_map, start=1):
            self._append_bounded_context(bc_entry, order)
        self._append_unconsumed_modules()
        self._parsed.modules = self._new_modules

    def _append_bounded_context(self, bc_entry, order: int) -> None:
        self._bc_entry = bc_entry
        src = self._module_by_name.get(bc_entry.name.lower())
        if src:
            bc = BoundedContext(src.name, src.sequential_order)
            self._copy_module_meta(src, bc)
            self._consumed.add(bc_entry.name.lower())
        else:
            bc = BoundedContext(bc_entry.name, order)
        self._append_aggregates(bc)
        self._new_modules.append(bc)

    def _append_aggregates(self, bc: BoundedContext) -> None:
        for agg_order, agg_entry in enumerate(self._bc_entry.aggregates, start=1):
            bc.aggregates.append(self._aggregate_from_map(agg_entry, agg_order))

    def _aggregate_from_map(self, agg_entry, agg_order: int) -> Aggregate:
        agg_src = self._module_by_name.get(agg_entry.name.lower())
        if not agg_src:
            return Aggregate(agg_entry.name, agg_order)
        agg = Aggregate(agg_src.name, agg_src.sequential_order)
        self._copy_module_meta(agg_src, agg)
        agg.classes = [self._promote_ce_class(c) for c in agg_src.classes]
        self._consumed.add(agg_entry.name.lower())
        return agg

    def _append_unconsumed_modules(self) -> None:
        for mod in self._parsed.modules:
            if mod.name.lower() in self._consumed:
                continue
            self._new_modules.append(self._promoted_or_module(mod))

    def _promoted_or_module(self, mod: Module) -> Module:
        if not any(ddd_class_kind(c.name) for c in mod.classes):
            return mod
        return self._promote_module_to_aggregate(mod)

    def _promote_module_to_aggregate(self, mod: Module) -> Aggregate:
        agg = Aggregate(mod.name, mod.sequential_order)
        self._copy_module_meta(mod, agg)
        agg.classes = [self._promote_ce_class(c) for c in mod.classes]
        return agg

    def _promote_ce_model_modules_to_aggregates(self, model: CleanEngineeringModel) -> None:
        model.modules = [self._promoted_or_module(mod) for mod in model.modules]

    def _load_ddd_structure_from_map(self) -> None:
        bc_map = load_bounded_context_map(self.root)
        if not bc_map:
            return
        for order, bc_entry in enumerate(bc_map, start=1):
            self._register_map_bounded_context(bc_entry, order)

    def _register_map_bounded_context(self, bc_entry, order: int) -> None:
        self._map_bc = GraphBoundedContext(bc_entry.name, order)
        self.graph.register(self._map_bc)
        self.graph.index_module(self._map_bc)
        for agg_order, agg_entry in enumerate(bc_entry.aggregates, start=1):
            self._register_map_aggregate(agg_entry, agg_order)

    def _register_map_aggregate(self, agg_entry, agg_order: int) -> None:
        agg = GraphAggregate(agg_entry.name, agg_order)
        self.graph.register(agg)
        self.graph.index_module(agg)
        self._map_bc.aggregates.append(agg)
        self._map_bc.relate(Kind.OWNS, agg)

    def _wire_ddd_model(self) -> None:
        self._wire_ddd_relationships()

    def _wire_ddd_relationships(self) -> None:
        self._entity_roots: dict[str, GraphEntityRoot] = {}
        self._wire_aggregate_roots()
        self._wire_repository_access()
        for node in self.graph.nodes.values():
            if isinstance(node, DddEntity):
                self._wire_entity_identity(node)

    def _wire_aggregate_roots(self) -> None:
        for agg in self.graph.nodes_of_type(GraphAggregate):
            self._wire_aggregate_root(agg)

    def _wire_aggregate_root(self, agg: GraphAggregate) -> None:
        for oclass in agg.classes:
            if not isinstance(oclass, GraphEntityRoot):
                continue
            agg.root = oclass
            oclass.aggregate = agg
            agg.relate(Kind.ROOT, oclass)
            oclass.relate(Kind.BELONGS_TO, agg)
            self._entity_roots[oclass.name.lower()] = oclass

    def _wire_repository_access(self) -> None:
        for repo in self.graph.nodes_of_type(GraphRepository):
            self._wire_repository(repo)

    def _wire_repository(self, repo: GraphRepository) -> None:
        root_name = repository_root_name(repo.name)
        if not root_name:
            return
        root = self._entity_root_for(root_name)
        if root is None:
            return
        repo.accesses = root
        repo.relate(Kind.ACCESSES, root)

    def _entity_root_for(self, root_name: str):
        root = self._entity_roots.get(root_name.lower())
        if root is not None:
            return root
        found = self.graph.class_named(root_name)
        if isinstance(found, GraphEntityRoot):
            return found
        return None

    def _wire_entity_identity(self, entity: DddEntity) -> None:
        for prop in entity.property_nodes:
            self._maybe_identity_member(entity, prop)
        for op in entity.operation_nodes:
            if is_identity_property(op.name):
                entity.identity.append(op)
                entity.relate(Kind.HAS_IDENTITY, op)
        for prop in entity.property_nodes:
            self._wire_identity_type(entity, prop)

    def _maybe_identity_member(self, entity: DddEntity, prop) -> None:
        if not is_identity_property(prop.name, prop.type_hint):
            return
        entity.identity.append(prop)
        entity.relate(Kind.HAS_IDENTITY, prop)

    def _wire_identity_type(self, entity: DddEntity, prop) -> None:
        if prop.name != "identity":
            return
        type_name = prop.type_hint.split("|")[0].strip().rstrip("[]")
        identity_cls = self.graph.class_named(type_name)
        if identity_cls is None:
            return
        self._append_identity_from_class(entity, identity_cls)

    def _append_identity_from_class(self, entity: DddEntity, identity_cls) -> None:
        for id_prop in identity_cls.property_nodes:
            if is_identity_property(id_prop.name, id_prop.type_hint):
                entity.identity.append(id_prop)
                entity.relate(Kind.HAS_IDENTITY, id_prop)

    def _wire_operation_invocations(self, operation: GraphOperation) -> None:
        for callee in operation.callees:
            self._wire_invocation(operation, callee)

    def _wire_invocation(self, operation: GraphOperation, callee: str) -> None:
        callee = callee.strip()
        if not callee:
            return
        class_name, op_name = self._split_callee(callee)
        target = self.graph.operation_named(class_name, op_name)
        if target is not None:
            operation.relate(Kind.INVOKES, target)

    def _split_callee(self, callee: str):
        if "." in callee:
            return callee.split(".", 1)
        return self._owner_class_name, callee

    def _domain_modules(self):
        for node in self.graph.nodes.values():
            if isinstance(node, (GraphModule, GraphBoundedContext, GraphAggregate)):
                yield node

    def _domain_classes(self):
        for node in self.graph.nodes.values():
            if isinstance(node, (GraphClass, *_GRAPH_DDD_CLASSES)):
                yield node

    def _derive_cross_module_dependencies(self) -> None:
        self._class_home = {}
        for module in self._domain_modules():
            for oclass in module.classes:
                self._class_home[oclass.node_id] = module
        for oclass in self._domain_classes():
            self._collect_class_dependencies(oclass)

    def _collect_class_dependencies(self, oclass) -> None:
        self._home = self._class_home.get(oclass.node_id)
        if self._home is None:
            return
        self._external = {}
        self._collect_owned_externals(oclass)
        for target in oclass.related(Kind.ASSOCIATES):
            if isinstance(target, OoadClass):
                self._maybe_external(oclass, target)
        self._relate_module_dependencies()

    def _collect_owned_externals(self, oclass) -> None:
        for owned in oclass.related(Kind.OWNS):
            if isinstance(owned, GraphProperty):
                self._collect_property_externals(oclass, owned)
            elif isinstance(owned, GraphOperation):
                self._collect_operation_externals(oclass, owned)

    def _collect_property_externals(self, oclass, owned) -> None:
        for target in owned.related(Kind.HAS_TYPE):
            if isinstance(target, OoadClass):
                self._maybe_external(oclass, target)

    def _collect_operation_externals(self, oclass, owned) -> None:
        for target in owned.related(Kind.RETURNS):
            if isinstance(target, OoadClass):
                self._maybe_external(oclass, target)
        for target in owned.related(Kind.INVOKES):
            if (
                isinstance(owned, GraphOperation)
                and isinstance(target, GraphOperation)
                and owned.name == "__init__"
                and target.name == "__init__"
            ):
                continue
            self._collect_invoke_owner(oclass, target)

    def _collect_invoke_owner(self, oclass, target) -> None:
        if not isinstance(target, GraphOperation):
            return
        for owner in target.related(Kind.BELONGS_TO, direction="in"):
            if isinstance(owner, OoadClass):
                self._maybe_external(oclass, owner)

    def _relate_module_dependencies(self) -> None:
        for ext in self._external.values():
            self._home.relate(Kind.DEPENDS_ON, ext)
            ext_home = self._class_home.get(ext.node_id)
            if ext_home is not None:
                self._home.relate(Kind.DEPENDS_ON, ext_home)

    def _maybe_external(self, owner_class, target) -> None:
        target_home = self._class_home.get(target.node_id)
        if target_home is None or target_home.node_id == self._home.node_id:
            return
        self._external[target.node_id] = target
        owner_class.relate(Kind.DEPENDS_ON, target)

    def _is_python_spec(self, path: Path) -> bool:
        name = path.name.lower()
        return path.suffix.lower() == ".py" and (
            name.endswith("_spec.py") or "_spec." in name
        )

    def _read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return ""

    def _load_bdd_descriptions(self) -> None:
        for path in self._bdd_candidate_paths():
            self._parse_python_bdd_file(path)

    def _bdd_candidate_paths(self) -> list[Path]:
        candidates: list[Path] = []
        for path in sorted(self.root.glob("**/*.py")):
            if path.name in ("examples.py",) or self._is_python_spec(path):
                candidates.append(path)
        return candidates

    def _parse_python_bdd_file(self, path: Path) -> None:
        content = self._read_text(path)
        if "description(" not in content:
            return
        self._stack = []
        for line_no, line in enumerate(content.splitlines(), start=1):
            self._parse_bdd_line(line, line_no)

    def _parse_bdd_line(self, line: str, line_no: int) -> None:
        match = _DESCRIBE_RE.search(line)
        if match:
            self._handle_description_line(match.group(1), line_no)
            return
        match = _CONTEXT_RE.search(line)
        if match:
            self._handle_context_line(match.group(1), line_no)
            return
        match = _IT_RE.search(line)
        if match:
            self._handle_it_line(match.group(1), line_no)
            return
        self._maybe_pop_bdd_stack(line)

    def _handle_description_line(self, label: str, line_no: int) -> None:
        if self._stack and isinstance(self._stack[-1], GraphDescription):
            self._nest_description_as_context(label, line_no)
            return
        self._start_description(label, line_no)

    def _nest_description_as_context(self, label: str, line_no: int) -> None:
        ctx = GraphContext(label, line_no)
        self.graph.register(ctx)
        self._stack[-1].relate(Kind.OWNS, ctx)
        self._stack.append(ctx)

    def _start_description(self, label: str, line_no: int) -> None:
        desc = GraphDescription(label, line_no)
        self.graph.register(desc)
        self.graph.index_description(desc)
        self._stack = [desc]
        cls = self.graph.class_named(self._subject_class_name(label))
        if cls is not None:
            desc.relate(Kind.DESCRIBES, cls)

    def _handle_context_line(self, label: str, line_no: int) -> None:
        if not self._stack:
            return
        ctx = GraphContext(label, line_no)
        self.graph.register(ctx)
        self._stack[-1].relate(Kind.OWNS, ctx)
        self._stack.append(ctx)

    def _handle_it_line(self, label: str, line_no: int) -> None:
        if not self._stack or not isinstance(self._stack[-1], GraphContext):
            return
        obs = GraphObservation(label, line_no)
        self.graph.register(obs)
        self._stack[-1].relate(Kind.OWNS, obs)

    def _maybe_pop_bdd_stack(self, line: str) -> None:
        stripped = line.strip()
        if stripped.startswith("with description(") or stripped.startswith("with context("):
            return
        if stripped == "pass" and len(self._stack) > 1:
            self._stack.pop()

    def _subject_class_name(self, label: str) -> str:
        cleaned = label.strip()
        for prefix in ("a ", "an ", "the "):
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix) :]
                break
        parts = cleaned.split()
        if not parts:
            return cleaned
        return parts[0][:1].upper() + parts[0][1:]

    def _attach_story_tests(self, paths: list[Path]) -> None:
        for path in paths:
            if path.suffix.lower() not in {".ts", ".tsx"}:
                continue
            self._relative = str(path.resolve().relative_to(self.graph.root)).replace("\\", "/")
            self._attach_suites_from(path)

    def _attach_suites_from(self, path: Path) -> None:
        from practices.stories.model.typescript.nodes import TypeScriptStoryMap

        for suite in TypeScriptStoryMap.from_workspace(path):
            self._register_parsed_story_suite(suite)

    def _register_parsed_story_suite(self, suite) -> None:
        from practices.stories.model.source_location import SourceLocation

        story = GraphStory(suite.name, 1)
        story.source = SourceLocation(self._relative, 1)
        self.graph.register(story)
        self._suite_story = story
        self._suite_seen: set[str] = set()
        for index, case in enumerate(suite.cases, start=1):
            self._register_suite_case(case, index)

    def _register_suite_case(self, case, index: int) -> None:
        from practices.stories.model.source_location import SourceLocation

        name = case.covers_scenario or case.name
        if name in self._suite_seen:
            return
        self._suite_seen.add(name)
        scenario = GraphScenario(name, index, self._suite_story.name)
        scenario.source = SourceLocation(
            self._relative,
            case.story_source.line if case.story_source else 1,
        )
        self.graph.register(scenario)
        self._suite_story.relate(Kind.OWNS, scenario)
