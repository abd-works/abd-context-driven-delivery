"""Graphviz DOT export for practice graph hierarchies."""

from __future__ import annotations

from typing import Iterable, Iterator, List, Set, Tuple

from .graph_node import Kind, Node

HIERARCHY_KINDS = frozenset(
    {Kind.OWNS, Kind.SCOPES, Kind.DEMONSTRATED_THROUGH, Kind.HAS_PARAMETER}
)

_CHILD_RANK = {
    "Example": 0,
    "Background": 1,
    "Scenario": 2,
    "Story": 3,
    "SubEpic": 3,
    "Epic": 3,
    "Step": 4,
    "BoundedContext": 1,
    "Aggregate": 2,
    "Module": 2,
    "OoadClass": 3,
    "Entity": 3,
    "EntityRoot": 3,
    "ValueObject": 3,
    "Repository": 3,
    "DomainEvent": 3,
    "DomainService": 3,
    "Property": 4,
    "Operation": 5,
    "Parameter": 6,
}


def _hierarchy_rank(node: Node) -> Tuple[int, int]:
    semantic = node.semantic_type()
    return (
        _CHILD_RANK.get(semantic, 10),
        int(getattr(node, "sequential_order", 0) or 0),
    )


def walk_hierarchy(
    root: Node,
    *,
    kinds: Iterable[str] = HIERARCHY_KINDS,
) -> Iterator[Tuple[int, Node]]:
    """Yield ``(depth, node)`` depth-first over owned and scoped descendants."""
    kind_set = frozenset(kinds)
    seen: Set[str] = set()
    stack: List[Tuple[int, Node, bool]] = [(0, root, True)]

    while stack:
        depth, node, expand = stack.pop()
        if node.node_id in seen:
            if not expand:
                yield depth, node
            continue
        seen.add(node.node_id)
        yield depth, node
        children = [
            (kind, child)
            for kind, child in node.outgoing()
            if kind in kind_set
        ]
        children.sort(key=lambda pair: _hierarchy_rank(pair[1]))
        for kind, child in reversed(children):
            if child.node_id in seen and kind != Kind.DEMONSTRATED_THROUGH:
                continue
            stack.append((depth + 1, child, kind != Kind.DEMONSTRATED_THROUGH))


def hierarchy_text(root: Node) -> str:
    """Indented outline of *root* and every owned/scoped descendant.

    Runs graph rules from this root down (keep-classes-single-responsibility
    first) and writes each hit on the same line as the node that failed.
    """
    graph = getattr(root, "graph", None)
    if graph is not None:
        graph.evaluate_rules()
    lines: List[str] = []
    for depth, node in walk_hierarchy(root):
        try:
            line = _hierarchy_line(depth, node)
            mark = _hierarchy_violations(node)
            if mark:
                line = f"{line}  {mark}"
            lines.append(line)
        except Exception as error:
            name = getattr(node, "name", "") or type(node).__name__
            if graph is not None:
                graph.record_partial_failure(f"hierarchy {name}", error)
            lines.append(f"{'  ' * depth}ERROR: {name}: {error}")
    return "\n".join(lines) + ("\n" if lines else "")


def _hierarchy_line(depth: int, node: Node) -> str:
    semantic = node.semantic_type()
    if semantic == "OoadClass":
        semantic = "Class"
    name = getattr(node, "name", "") or ""
    keyword = getattr(node, "keyword", "") or ""
    indent = "  " * depth
    if semantic == "Step" and keyword:
        display = name
        prefix = f"{keyword} "
        if display.lower().startswith(prefix.lower()):
            display = display[len(prefix) :]
        return f"{indent}Step: {keyword} {display}"
    if semantic == "Property":
        type_hint = getattr(node, "type_hint", "") or ""
        suffix = f": {type_hint}" if type_hint else ""
        return f"{indent}Property: {name}{suffix}"
    if semantic == "Operation":
        return_type = getattr(node, "return_type", "") or ""
        suffix = f": {return_type}" if return_type else ""
        return f"{indent}Operation: {name}(){suffix}"
    if semantic == "Parameter":
        type_hint = getattr(node, "type_hint", "") or ""
        suffix = f": {type_hint}" if type_hint else ""
        return f"{indent}Parameter: {name}{suffix}"
    return f"{indent}{semantic}: {name}"


def graph_name_matches(module_name: str, graphs: list[str] | None) -> bool:
    if not graphs:
        return True
    name = (module_name or "").replace("\\", "/").replace(".", "/")
    for wanted in graphs:
        token = (wanted or "").replace("\\", "/").replace(".", "/").strip().strip("/")
        if token and (name == token or name.endswith("/" + token) or token in name):
            return True
    return False


def violation_row_indexes(marks: list[tuple[int, bool]]) -> list[int]:
    keep = [False] * len(marks)
    stack: list[int] = []
    for index, (depth, marked) in enumerate(marks):
        while stack and marks[stack[-1]][0] >= depth:
            stack.pop()
        if marked:
            keep[index] = True
            for ancestor in stack:
                keep[ancestor] = True
        stack.append(index)
    return [index for index, flagged in enumerate(keep) if flagged]


def prune_to_violations(
    entries: Iterable[Tuple[int, Node]],
) -> List[Tuple[int, Node]]:
    rows = list(entries)
    keep = violation_row_indexes(
        [(depth, bool(_hierarchy_violations(node))) for depth, node in rows]
    )
    return [rows[index] for index in keep]


def _hierarchy_violations(node: Node) -> str:
    graph = getattr(node, "graph", None)
    if graph is None:
        return ""
    try:
        hits = list(graph._violations_by_node.get(node.node_id, []))
    except Exception as error:
        graph.record_partial_failure(
            f"violations {getattr(node, 'name', type(node).__name__)}",
            error,
        )
        return f"[ERROR] {error}"
    hits.sort(
        key=lambda violation: (
            0 if violation.rule_slug == "keep-classes-single-responsibility" else 1,
            violation.rule_slug,
        )
    )
    if not hits:
        return ""
    return " | ".join(
        f"[{violation.rule_slug}] {violation.message}" for violation in hits
    )


def dot_graph_from_node(
    root: Node,
    *,
    kinds: Iterable[str] = HIERARCHY_KINDS,
    graph_name: str = "practice_graph",
) -> str:
    """Return a DOT digraph for *root* and every descendant via hierarchy edges."""
    kind_set = frozenset(kinds)
    nodes, edges = _collect_hierarchy(root, kind_set)
    return _render_dot(nodes, edges, graph_name=graph_name)


def dot_graph_from_roots(
    roots: Iterable[Node],
    *,
    kinds: Iterable[str] = HIERARCHY_KINDS,
    graph_name: str = "practice_graph",
) -> str:
    """Merge hierarchy subgraphs for multiple roots into one DOT digraph."""
    kind_set = frozenset(kinds)
    all_nodes: List[Node] = []
    all_edges: List[Tuple[Node, str, Node]] = []
    seen_nodes: Set[str] = set()
    seen_edges: Set[Tuple[str, str, str]] = set()

    for root in roots:
        nodes, edges = _collect_hierarchy(root, kind_set)
        for node in nodes:
            if node.node_id in seen_nodes:
                continue
            seen_nodes.add(node.node_id)
            all_nodes.append(node)
        for from_node, kind, to_node in edges:
            key = (from_node.node_id, kind, to_node.node_id)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            all_edges.append((from_node, kind, to_node))

    return _render_dot(all_nodes, all_edges, graph_name=graph_name)


def _collect_hierarchy(
    root: Node,
    kinds: frozenset[str],
) -> Tuple[List[Node], List[Tuple[Node, str, Node]]]:
    nodes: List[Node] = []
    edges: List[Tuple[Node, str, Node]] = []
    seen: Set[str] = set()
    stack: List[Node] = [root]

    while stack:
        node = stack.pop()
        if node.node_id in seen:
            continue
        seen.add(node.node_id)
        nodes.append(node)
        for kind, child in node.outgoing():
            if kind not in kinds:
                continue
            edges.append((node, kind, child))
            if child.node_id not in seen:
                stack.append(child)

    return nodes, edges


def _render_dot(
    nodes: List[Node],
    edges: List[Tuple[Node, str, Node]],
    *,
    graph_name: str,
) -> str:
    lines = [f"digraph {_dot_name(graph_name)} {{"]
    lines.append('  rankdir=TB;')
    lines.append('  node [shape=box, fontname="Helvetica"];')
    lines.append('  edge [fontname="Helvetica", fontsize=10];')

    for node in nodes:
        lines.append(
            f'  {_dot_id(node.node_id)} [label={_dot_label(node)}];'
        )

    for from_node, kind, to_node in edges:
        lines.append(
            f'  {_dot_id(from_node.node_id)} -> {_dot_id(to_node.node_id)} '
            f'[label={_dot_string(kind)}];'
        )

    lines.append('}')
    return '\n'.join(lines) + '\n'


def _dot_name(name: str) -> str:
    safe = ''.join(ch if ch.isalnum() or ch == '_' else '_' for ch in name)
    return safe or 'practice_graph'


def _dot_id(node_id: str) -> str:
    return _dot_string(node_id)


def _dot_label(node: Node) -> str:
    semantic = node.semantic_type()
    practice = getattr(node, 'practice', '')
    name = _node_display_name(node)
    if practice:
        return _dot_string(f'{semantic}\\n{name}\\n({practice})')
    return _dot_string(f'{semantic}\\n{name}')


def _node_display_name(node: Node) -> str:
    name = getattr(node, 'name', '') or type(node).__name__
    if len(name) > 72:
        return name[:69] + '...'
    return name


def _dot_string(value: str) -> str:
    escaped = (
        value.replace('\\', '\\\\')
        .replace('"', '\\"')
        .replace('\n', '\\n')
        .replace('\r', '')
    )
    return f'"{escaped}"'
