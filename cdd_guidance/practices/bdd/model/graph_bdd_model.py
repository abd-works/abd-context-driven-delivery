"""A BDD model read from a saved knowledge graph: the realization fidelity drawn from what the graph knows.

The behavior tree is the graph's `bdd` nodes, read by following the `descriptions`, `contexts`, and `observations` edges
from each spec. Each observation's call graph starts at what its `invokes` edges name, and each call is followed
through the interactions of the operation the Clean Engineering model documents describe, which the Clean Engineering
practice holds. Each code member's saved facts name its class under `owner`, and its parameters are the `Parameter`
nodes its `hasParameter` edges lead to. The saved file is read back into the graph's own nodes and edges, the way the
graph reloads it, so this model asks nodes for their facts and edges for their ends and never reads the file's layout.
"""

from __future__ import annotations

import re
from typing import List, Optional

from cdd_guidance.practices.bdd.model.bdd_model import BddModel
from cdd_guidance.practices.bdd.model.nodes import DescribeBlock
from cdd_guidance.practices.clean_engineering.model.call_graph import CallGraph, CallGraphEntry
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from harness.graph.graph import Node
from harness.graph.saved_graph import SavedGraph

# Following interactions further than this many calls deep adds lines nobody reads; a cycle is cut where it repeats.
_DEEPEST_CALL = 6
NO_OPERATION = "// the graph holds no operation this observation calls"
_MEMBER_TYPES = ("Operation", "Property")
_CHILD_EDGES = ("contexts", "observations")


class GraphBddModel(BddModel):
    """Reads a saved graph (`Graph.saved`, `graph.save_json`) into descriptions whose observations carry their realization."""

    def parse(self, text: str) -> "GraphBddModel":
        graph = SavedGraph.from_text(text).restored_graph()
        self._graph = graph
        bdd = graph.practice_of(self.practice_kind())
        self._clean = bdd.clean_engineering_practice
        for spec in sorted(graph.nodes_of(bdd, "Spec"), key=lambda node: node.source.file):
            for saved in self._in_file_order(graph.edges_from("descriptions", spec)):
                self._read_block(saved, self.add_description(saved.name))
        return self

    def _read_block(self, saved: Node, block: DescribeBlock) -> None:
        """The saved block's contexts and observations, in the order its file has them, under block."""
        children = self._in_file_order(edge for kind in _CHILD_EDGES for edge in self._graph.edges_from(kind, saved))
        for order, child in enumerate(children, start=1):
            if child.type == "Observation":
                block.add_child("it", child.name, order).call_graph = self._realization(child)
            else:
                self._read_block(child, block.add_child("context", child.name, order))

    def _in_file_order(self, edges) -> List[Node]:
        return sorted((edge.child for edge in edges), key=lambda node: (node.source.start_line, -node.source.end_line))

    def _realization(self, observation: Node) -> CallGraph:
        entries = CallGraph()
        for edge in self._graph.edges_from("invokes", observation):
            member = edge.child
            entries.extend(self._call(member.get_fact("owner", ""), member.name, 0, set(), member))
        return entries or CallGraph([CallGraphEntry(depth=0, kind="call", text=NO_OPERATION)])

    def _call(self, owner: str, name: str, depth: int, trail: set, code: Optional[Node]) -> List[CallGraphEntry]:
        """A call on owner.name, then the interactions the model gives it, then what it returns."""
        described = self._clean.described_member(owner, name) if self._clean is not None else None
        is_property = isinstance(described, Property) if described is not None else code is not None and code.type == "Property"
        signature = ", ".join(f"{label}: {kind}" if kind else label for label, kind in self._parameters(described, code))
        entries = [CallGraphEntry(depth=depth, kind="out", text=f"{owner}.{name}" if is_property else f"{owner}.{name}({signature})")]
        if depth < _DEEPEST_CALL and described is not None:
            for interaction in described.callees:
                callee = _member_named(interaction)
                if callee is None or callee in trail:
                    continue
                entries.extend(self._call(callee[0], callee[1], depth + 1, trail | {(owner, name)}, self._code_member(*callee)))
        returns = _returned(described)
        if returns:
            entries.append(CallGraphEntry(depth=depth, kind="in", text=returns))
        return entries

    def _parameters(self, described, code: Optional[Node]) -> List[tuple[str, str]]:
        """Each parameter's name and type: the model's when it describes the member, else the code's."""
        if isinstance(described, Operation):
            return [(parameter.name, (parameter.type_hint or "").strip()) for parameter in described.parameters]
        if described is not None or code is None:
            return []
        parameters = [edge.child for edge in self._graph.edges_from("hasParameter", code)]
        return [(parameter.name, (parameter.get_fact("type_hint") or "").strip()) for parameter in parameters]

    def _code_member(self, owner: str, name: str) -> Optional[Node]:
        """The code's member owner.name, when the graph loaded it."""
        if self._clean is None:
            return None
        for node_type in _MEMBER_TYPES:
            for member in self._graph.nodes_of(self._clean, node_type):
                if member.name == name and member.get_fact("owner") == owner:
                    return member
        return None


def _returned(described) -> str:
    """What the described member gives back: an operation's return type, a property's type."""
    if isinstance(described, Operation):
        return (described.return_type or "").strip()
    if isinstance(described, Property):
        return (described.type_hint or "").strip()
    return ""


def _member_named(interaction: str) -> Optional[tuple[str, str]]:
    """`Session.change_workpath` or `Repo.switch_branch(name)` as (class, member); None for anything else."""
    match = re.match(r"^([A-Za-z_]\w*)\.([A-Za-z_]\w*)", interaction.strip())
    return (match.group(1), match.group(2)) if match else None
