"""Spec support for the graph: counting the graphs code makes, so a spec can say an operation reads no graph back
and builds none of its own; and the state a build leaves each practice in, so a spec can say two graphs hold the same
nodes, edges, and violations, and name each one that differs."""

from __future__ import annotations

import json

from harness.graph.graph import Graph, Node, PracticeNodes

# What a practice's state lists, each sorted, so two states compare entry by entry.
_LISTED = ("nodes", "edges", "violations")


class GraphsMade:
    """Counts the graphs made while it is open."""

    def __init__(self) -> None:
        self.made = 0
        self._init = Graph.__init__

    def __enter__(self) -> GraphsMade:
        counter = self

        def counted(graph, *arguments, **keywords):
            counter.made += 1
            counter._init(graph, *arguments, **keywords)

        Graph.__init__ = counted
        return self

    def __exit__(self, *_exc) -> None:
        Graph.__init__ = self._init


def practice_state(part: PracticeNodes) -> dict:
    """One practice's nodes where they sit with their facts, its edges, and its violations, as a build leaves them."""
    found = part.nodes()
    return {
        "nodes": sorted((node.node_id, node.type, node.source.file, node.source.start_line, node.source.end_line, _facts(node)) for node in found),
        "root": _facts(part.root),
        "edges": sorted((edge.kind, edge.parent.node_id, edge.child.node_id) for edge in part.edge_index.of()),
        "violations": sorted((violation.rule, violation.node_id, violation.message) for node in found for violation in node.rules.violations),
    }


def graph_state(graph: Graph) -> dict[str, dict]:
    """The state of every practice open in graph, by the practice's key."""
    return {key: practice_state(practice.reading.in_graph) for key, practice in graph.practices.opened.items()}


def state_differences(held: dict[str, dict], built: dict[str, dict]) -> dict[str, dict]:
    """Where the graph state held differs from the state built, practice by practice: each node, edge, and violation
    only one of them lists, and the root's facts when they differ; empty when the two are the same."""
    found: dict[str, dict] = {}
    for key in sorted(set(held) | set(built)):
        ours, theirs = held.get(key), built.get(key)
        if ours is None or theirs is None:
            found[key] = {"practice open in only one graph": "held" if theirs is None else "built"}
            continue
        differs = {
            listed: {"only held": sorted(set(ours[listed]) - set(theirs[listed])), "only built": sorted(set(theirs[listed]) - set(ours[listed]))}
            for listed in _LISTED
            if ours[listed] != theirs[listed]
        }
        if ours["root"] != theirs["root"]:
            differs["root"] = {"held": ours["root"], "built": theirs["root"]}
        if differs:
            found[key] = differs
    return found


def _facts(node: Node) -> str:
    """The node's facts as the saved graph writes them."""
    return json.dumps(node.facts, sort_keys=True)
