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
    export_path = resolve_codeql_results_path(root, results_path)
    if export_path is None:
        return False
    export = load_codeql_export(export_path)
    _ensure_ce_nodes(graph, export)
    _wire_codeql_calls(graph, export)
    _wire_story_calls(graph, export)
    _wire_story_observations(graph, export)
    _wire_example_demonstrates(graph, export)
    return True


def _ensure_ce_nodes(graph: PracticeGraph, export: CodeQLPracticeGraphExport) -> None:
    modules: Dict[str, GraphModule] = {}
    for mod in graph.nodes_of_type(GraphModule):
        modules[mod.name.lower()] = mod

    classes: Dict[str, OoadClass] = {}
    for cls in graph.nodes.values():
        if isinstance(cls, OoadClass):
            classes[cls.name.lower()] = cls

    order = 1
    for entry in export.classes:
        mod = modules.get(entry.module.lower())
        if mod is None:
            mod = GraphModule(entry.module, order)
            order += 1
            graph.register(mod)
            graph.index_module(mod)
            modules[entry.module.lower()] = mod
            if graph.ce_model is not None:
                graph.ce_model.modules.append(mod)
                graph.relate(graph.ce_model, Kind.OWNS, mod)

        cls = classes.get(entry.name.lower())
        if cls is None:
            decorated = entry.name
            if entry.stereotypes:
                decorated = f"{entry.name} {' '.join(f'<<{s}>>' for s in entry.stereotypes)}"
            stub = OoadClass(decorated, len(mod.classes) + 1)
            if entry.stereotypes or ddd_class_kind(decorated):
                cls = graph_ddd_class_for(stub)
            else:
                cls = GraphClass(entry.name, len(mod.classes) + 1)
            mod.classes.append(cls)
            classes[entry.name.lower()] = cls
            graph.register(cls)
            graph.relate(mod, Kind.OWNS, cls)
            graph.relate(cls, Kind.BELONGS_TO, mod)

    for prop in export.properties:
        cls = classes.get(prop.class_name.lower())
        if cls is None:
            continue
        if any(p.name == prop.name for p in cls.property_nodes):
            continue
        if not cls.property_nodes and cls.properties:
            cls.sync_tree_from_legacy()
        node = GraphProperty(
            prop.name,
            len(cls.property_nodes) + 1,
            type_hint=prop.type_hint,
        )
        cls.property_nodes.append(node)
        graph.register(node)
        graph.relate(cls, Kind.OWNS, node)
        graph.relate(node, Kind.BELONGS_TO, cls)
        target = graph.find_class(prop.type_hint.split("|")[0].strip().rstrip("[]"))
        if target is not None:
            graph.relate(node, Kind.HAS_TYPE, target)

    for op in export.operations:
        cls = classes.get(op.class_name.lower())
        if cls is None:
            continue
        if any(o.name == op.name for o in cls.operation_nodes):
            continue
        if not cls.operation_nodes and cls.operations:
            cls.sync_tree_from_legacy()
        node = GraphOperation(
            op.name,
            len(cls.operation_nodes) + 1,
            return_type=op.return_type,
        )
        node._legacy_parameters = list(op.parameters)
        node._sync_parameters_from_legacy()
        cls.operation_nodes.append(node)
        graph.register(node)
        graph.relate(cls, Kind.OWNS, node)
        graph.relate(node, Kind.BELONGS_TO, cls)
        ret = graph.find_class(op.return_type.split("|")[0].strip().rstrip("[]"))
        if ret is not None:
            graph.relate(node, Kind.RETURNS, ret)


def _wire_codeql_calls(graph: PracticeGraph, export: CodeQLPracticeGraphExport) -> None:
    for call in export.calls:
        caller = graph.find_operation(call.caller_class, call.caller_operation)
        callee = graph.find_operation(call.callee_class, call.callee_operation)
        if caller is None or callee is None:
            continue
        graph.relate(caller, Kind.INVOKES, callee)


def _wire_story_calls(graph: PracticeGraph, export: CodeQLPracticeGraphExport) -> None:
    for story_call in export.story_calls:
        step = _find_step(graph, story_call.story_file, story_call.line, story_call.step_text)
        operation = graph.find_operation(story_call.callee_class, story_call.callee_operation)
        if step is None or operation is None:
            continue
        graph.relate(step, Kind.INVOKES, operation)


def _wire_story_observations(graph: PracticeGraph, export: CodeQLPracticeGraphExport) -> None:
    for obs in export.story_observations:
        step = _find_step(graph, obs.story_file, obs.line, "")
        if step is None:
            continue
        cls = graph.find_class(obs.target_class)
        if cls is None:
            continue
        target = None
        for owned in graph.outgoing_nodes(cls, Kind.OWNS):
            if obs.member_kind == "operation" and isinstance(owned, GraphOperation):
                if owned.name == obs.target_member:
                    target = owned
                    break
            if obs.member_kind == "property" and isinstance(owned, GraphProperty):
                if owned.name == obs.target_member:
                    target = owned
                    break
        if target is not None:
            graph.relate(step, Kind.OBSERVES, target)


def _wire_example_demonstrates(graph: PracticeGraph, export: CodeQLPracticeGraphExport) -> None:
    examples_by_name: Dict[str, List[GraphExample]] = {}
    for example in graph.nodes_of_type(GraphExample):
        examples_by_name.setdefault(example.name.lower(), []).append(example)

    for entry in export.example_exports:
        cls_names = entry.demonstrates
        if not cls_names:
            continue
        matched = _match_examples(examples_by_name, entry.export_name, entry.file)
        for example in matched:
            for class_name in cls_names:
                cls = graph.find_class(class_name)
                if cls is not None:
                    graph.relate(example, Kind.DEMONSTRATES, cls)


def _match_examples(
    index: Dict[str, List[GraphExample]],
    export_name: str,
    file_path: str,
) -> List[GraphExample]:
    export_lower = export_name.lower()
    if export_lower in index:
        return index[export_lower]
    stem = Path(file_path).stem.replace(".examples", "").replace("-", " ")
    if stem.lower() in index:
        return index[stem.lower()]
    out: List[GraphExample] = []
    for examples in index.values():
        for ex in examples:
            if export_lower in ex.name.lower() or ex.name.lower() in export_lower:
                out.append(ex)
    return out


def _find_step(
    graph: PracticeGraph,
    story_file: str,
    line: int,
    step_text: str,
) -> Optional[GraphStep]:
    normalized = story_file.replace("\\", "/").lstrip("./")
    best: Tuple[int, Optional[GraphStep]] = (1_000_000, None)
    for step in graph.nodes_of_type(GraphStep):
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
