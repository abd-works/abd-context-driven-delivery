"""Graphviz DOT export for practice graph hierarchies."""

from __future__ import annotations

from typing import Iterable, List, Set, Tuple

from .graph_node import GraphNodeMixin, Kind

HIERARCHY_KINDS = frozenset({Kind.OWNS, Kind.SCOPES})


def dot_graph_from_node(
    root: GraphNodeMixin,
    *,
    kinds: Iterable[str] = HIERARCHY_KINDS,
    graph_name: str = "practice_graph",
) -> str:
    """Return a DOT digraph for *root* and every descendant via hierarchy edges."""
    kind_set = frozenset(kinds)
    nodes, edges = _collect_hierarchy(root, kind_set)
    return _render_dot(nodes, edges, graph_name=graph_name)


def dot_graph_from_roots(
    roots: Iterable[GraphNodeMixin],
    *,
    kinds: Iterable[str] = HIERARCHY_KINDS,
    graph_name: str = "practice_graph",
) -> str:
    """Merge hierarchy subgraphs for multiple roots into one DOT digraph."""
    kind_set = frozenset(kinds)
    all_nodes: List[GraphNodeMixin] = []
    all_edges: List[Tuple[GraphNodeMixin, str, GraphNodeMixin]] = []
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
    root: GraphNodeMixin,
    kinds: frozenset[str],
) -> Tuple[List[GraphNodeMixin], List[Tuple[GraphNodeMixin, str, GraphNodeMixin]]]:
    nodes: List[GraphNodeMixin] = []
    edges: List[Tuple[GraphNodeMixin, str, GraphNodeMixin]] = []
    seen: Set[str] = set()
    stack: List[GraphNodeMixin] = [root]

    while stack:
        node = stack.pop()
        if node.node_id in seen:
            continue
        seen.add(node.node_id)
        nodes.append(node)
        for kind, child in node.graph.outgoing(node):
            if kind not in kinds:
                continue
            edges.append((node, kind, child))
            if child.node_id not in seen:
                stack.append(child)

    return nodes, edges


def _render_dot(
    nodes: List[GraphNodeMixin],
    edges: List[Tuple[GraphNodeMixin, str, GraphNodeMixin]],
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


def _dot_label(node: GraphNodeMixin) -> str:
    semantic = getattr(node, '_semantic_type_name', type(node).__name__)
    practice = getattr(node, 'practice', '')
    name = _node_display_name(node)
    if practice:
        return _dot_string(f'{semantic}\\n{name}\\n({practice})')
    return _dot_string(f'{semantic}\\n{name}')


def _node_display_name(node: GraphNodeMixin) -> str:
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
