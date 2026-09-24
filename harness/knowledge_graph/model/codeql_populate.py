"""Populate a PracticeGraph from CodeQL export facts.

Markdown and story-map channels supply narrative structure (epics, scenarios,
steps, example names). CodeQL supplies the code index: classes, operations,
resolved call edges, story test call sites, and example→class links.

Run order inside ``load_practice_graph``:

1. Prose / markdown skeleton
2. ``populate_from_codeql`` (this module) when export JSON is present
3. Derived edges (cross-module dependsOn)
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from practices.clean_engineering.model.base_class_model import OoadClass
from practices.ddd.model.stereotypes import ddd_class_kind

from .codeql_export import (
    CodeQLPracticeGraphExport,
    load_codeql_export,
    resolve_codeql_results_path,
)
from .graph_node import Kind
from .nodes import (
    GraphClass,
    GraphExample,
    GraphModule,
    GraphOperation,
    GraphProperty,
    GraphStep,
    graph_ddd_class_for,
)
from .practice_graph import PracticeGraph


def populate_from_codeql(
    graph: PracticeGraph,
    root: Path,
    *,
    results_path: Path | None = None,
) -> bool:
    """Merge CodeQL facts into *graph*. Returns True when export was applied."""
    populate = CodeQLPopulate(graph)
    populate.root = root
    populate.results_path = results_path
    return populate.apply()


class CodeQLPopulate:
    def __init__(self, graph: PracticeGraph) -> None:
        self.graph = graph
        self.root: Path = graph.root
        self.results_path: Path | None = None
        self.export: CodeQLPracticeGraphExport
        self.modules: Dict[str, GraphModule] = {}
        self.classes: Dict[str, OoadClass] = {}
        self._module_order = 1
        self._examples_by_name: Dict[str, List[GraphExample]] = {}

    def apply(self) -> bool:
        export_path = resolve_codeql_results_path(self.root, self.results_path)
        if export_path is None:
            return False
        self.export = load_codeql_export(export_path)
        self._ensure_ce_nodes()
        self._wire_codeql_calls()
        self._wire_story_calls()
        self._wire_story_observations()
        self._wire_example_demonstrates()
        return True

    def _ensure_ce_nodes(self) -> None:
        self.modules = {}
        for mod in self.graph.nodes_of_type(GraphModule):
            self.modules[mod.name.lower()] = mod
        self.classes = {}
        for cls in self.graph.nodes.values():
            if isinstance(cls, OoadClass):
                self.classes[cls.name.lower()] = cls
        self._module_order = 1
        self._ensure_modules_and_classes()
        self._ensure_properties()
        self._ensure_operations()

    def _ensure_modules_and_classes(self) -> None:
        for entry in self.export.classes:
            mod = self._module_for(entry)
            self._class_for(entry, mod)

    def _module_for(self, entry) -> GraphModule:
        key = entry.module.lower()
        existing = self.modules.get(key)
        if existing is not None:
            return existing
        mod = GraphModule(entry.module, self._module_order)
        self._module_order += 1
        self.graph.register(mod)
        self.graph.index_module(mod)
        self.modules[key] = mod
        if self.graph.ce_model is None:
            return mod
        self.graph.ce_model.modules.append(mod)
        self.graph.ce_model.relate(Kind.OWNS, mod)
        return mod

    def _class_for(self, entry, mod: GraphModule) -> OoadClass:
        existing = self.classes.get(entry.name.lower())
        if existing is not None:
            return existing
        decorated = entry.name
        if entry.stereotypes:
            decorated = f"{entry.name} {' '.join(f'<<{s}>>' for s in entry.stereotypes)}"
        stub = OoadClass(decorated, len(mod.classes) + 1)
        if entry.stereotypes or ddd_class_kind(decorated):
            cls = graph_ddd_class_for(stub)
        else:
            cls = GraphClass(entry.name, len(mod.classes) + 1)
        mod.classes.append(cls)
        self.classes[entry.name.lower()] = cls
        self.graph.register(cls)
        mod.relate(Kind.OWNS, cls)
        cls.relate(Kind.BELONGS_TO, mod)
        return cls

    def _ensure_properties(self) -> None:
        for prop in self.export.properties:
            cls = self.classes.get(prop.class_name.lower())
            if cls is None:
                continue
            if any(p.name == prop.name for p in cls.property_nodes):
                continue
            self._add_property(cls, prop)

    def _add_property(self, cls: OoadClass, prop) -> None:
        if not cls.property_nodes and cls.properties:
            cls.sync_tree_from_legacy()
        node = GraphProperty(
            prop.name,
            len(cls.property_nodes) + 1,
            type_hint=prop.type_hint,
        )
        cls.property_nodes.append(node)
        self.graph.register(node)
        cls.relate(Kind.OWNS, node)
        node.relate(Kind.BELONGS_TO, cls)
        target = self.graph.find_class(prop.type_hint.split("|")[0].strip().rstrip("[]"))
        if target is None:
            return
        node.relate(Kind.HAS_TYPE, target)

    def _ensure_operations(self) -> None:
        for op in self.export.operations:
            cls = self.classes.get(op.class_name.lower())
            if cls is None:
                continue
            if any(o.name == op.name for o in cls.operation_nodes):
                continue
            self._add_operation(cls, op)

    def _add_operation(self, cls: OoadClass, op) -> None:
        if not cls.operation_nodes and cls.operations:
            cls.sync_tree_from_legacy()
        node = GraphOperation(
            op.name,
            len(cls.operation_nodes) + 1,
            return_type=op.return_type,
        )
        node.legacy_parameters = list(op.parameters)
        node._sync_parameters_from_legacy()
        cls.operation_nodes.append(node)
        self.graph.register(node)
        cls.relate(Kind.OWNS, node)
        node.relate(Kind.BELONGS_TO, cls)
        ret = self.graph.find_class(op.return_type.split("|")[0].strip().rstrip("[]"))
        if ret is None:
            return
        node.relate(Kind.RETURNS, ret)

    def _wire_codeql_calls(self) -> None:
        for call in self.export.calls:
            caller = self.graph.find_operation(call.caller_class, call.caller_operation)
            callee = self.graph.find_operation(call.callee_class, call.callee_operation)
            if caller is None or callee is None:
                continue
            caller.relate(Kind.INVOKES, callee)

    def _wire_story_calls(self) -> None:
        for story_call in self.export.story_calls:
            step = self._find_step(story_call)
            operation = self.graph.find_operation(
                story_call.callee_class, story_call.callee_operation
            )
            if step is None or operation is None:
                continue
            step.relate(Kind.INVOKES, operation)

    def _wire_story_observations(self) -> None:
        for obs in self.export.story_observations:
            step = self._find_step(obs)
            if step is None:
                continue
            cls = self.graph.find_class(obs.target_class)
            if cls is None:
                continue
            target = self._observation_target(cls, obs)
            if target is None:
                continue
            step.relate(Kind.OBSERVES, target)

    def _observation_target(self, cls, obs):
        for owned in self.graph.outgoing_nodes(cls, Kind.OWNS):
            if (
                obs.member_kind == "operation"
                and isinstance(owned, GraphOperation)
                and owned.name == obs.target_member
            ):
                return owned
            if (
                obs.member_kind == "property"
                and isinstance(owned, GraphProperty)
                and owned.name == obs.target_member
            ):
                return owned
        return None

    def _wire_example_demonstrates(self) -> None:
        self._examples_by_name = {}
        for example in self.graph.nodes_of_type(GraphExample):
            self._examples_by_name.setdefault(example.name.lower(), []).append(example)
        for entry in self.export.example_exports:
            if not entry.demonstrates:
                continue
            self._relate_demonstrates(entry)

    def _relate_demonstrates(self, entry) -> None:
        for example in self._match_examples(entry):
            self._demonstrate_classes(example, entry.demonstrates)

    def _demonstrate_classes(self, example: GraphExample, cls_names: List[str]) -> None:
        for class_name in cls_names:
            cls = self.graph.find_class(class_name)
            if cls is None:
                continue
            example.relate(Kind.DEMONSTRATES, cls)

    def _match_examples(self, entry) -> List[GraphExample]:
        export_lower = entry.export_name.lower()
        if export_lower in self._examples_by_name:
            return self._examples_by_name[export_lower]
        stem = Path(entry.file).stem.replace(".examples", "").replace("-", " ")
        if stem.lower() in self._examples_by_name:
            return self._examples_by_name[stem.lower()]
        out: List[GraphExample] = []
        for examples in self._examples_by_name.values():
            for ex in examples:
                if export_lower in ex.name.lower() or ex.name.lower() in export_lower:
                    out.append(ex)
        return out

    def _find_step(self, story_call) -> Optional[GraphStep]:
        step_text = getattr(story_call, "step_text", "")
        normalized = story_call.story_file.replace("\\", "/").lstrip("./")
        best: Tuple[int, Optional[GraphStep]] = (1_000_000, None)
        for step in self.graph.nodes_of_type(GraphStep):
            if step_text and step_text.lower() in step.text.lower():
                return step
            src = getattr(step, "source", None)
            if src is None:
                continue
            src_file = str(src.file).replace("\\", "/").lstrip("./")
            if src_file != normalized and not src_file.endswith(normalized):
                continue
            if story_call.line <= 0:
                return step
            delta = abs(int(src.line) - story_call.line)
            if delta < best[0]:
                best = (delta, step)
        if best[1] is not None and best[0] <= 5:
            return best[1]
        return None
