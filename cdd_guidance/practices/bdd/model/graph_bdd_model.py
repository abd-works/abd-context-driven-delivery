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
from typing import Iterable, List, Optional

from cdd_guidance.practices.bdd.model.bdd_model import BddModel
from cdd_guidance.practices.bdd.model.nodes import DescribeBlock
from cdd_guidance.practices.source_code import CallGraph
from cdd_guidance.practices.clean_engineering.model import Operation
from cdd_guidance.practices.clean_engineering.model import Property
from cdd_guidance.practices.clean_engineering.reading.production_classes import parameters_of
from harness.graph.edge import Edge
from harness.graph.graph import Graph, Node
from harness.graph.saved_graph import SavedGraph

# Following interactions further than this many calls deep adds lines nobody reads; a cycle is cut where it repeats.
_DEEPEST_CALL = 6
NO_OPERATION = "// the graph holds no operation this observation calls"
_CHILD_EDGES = ("contexts", "observations")
# A code member a call names: its class and its own name, `("Session", "change_workpath")`.
Member = tuple[str, str]
# The members a call graph has followed to reach a call, outermost first, ending with the member called; the members
# before it are the call's depth.
CallPath = tuple[Member, ...]
_MEMBER_CALL = re.compile(r"^([A-Za-z_]\w*)\.([A-Za-z_]\w*)")


class GraphBddModel(BddModel):
    """Reads a saved graph (`SavedGraph.from_graph`, `graph.save_json`) into descriptions whose observations carry their realization."""

    def parse(self, text: str, file: str = "") -> "GraphBddModel":

        graph = Graph()
        graph.restored_from(SavedGraph.from_text(text))
        self._graph = graph
        bdd = graph.practices.of(self.practice_kind)
        self._clean = bdd.reading.clean_engineering_reading
        for spec in sorted(bdd.reading.in_graph.nodes("Spec"), key=lambda node: node.source.file):
            for saved in self._in_file_order(graph.edges.from_parent("descriptions", spec)):
                self._read_block(saved, self.add_child("description", saved.name))
        return self

    def _read_block(self, saved: Node, block: DescribeBlock) -> None:
        """The saved block's contexts and observations, in the order its file has them, under block."""
        children = self._in_file_order(edge for kind in _CHILD_EDGES for edge in self._graph.edges.from_parent(kind, saved))
        for order, child in enumerate(children, start=1):
            if child.type == "Observation":
                block.add_child("it", child.name, order).call_graph = self._realization(child)
            else:
                self._read_block(child, block.add_child("context", child.name, order))

    def _in_file_order(self, edges: Iterable[Edge]) -> List[Node]:
        return sorted((edge.child for edge in edges), key=lambda node: (node.source.start_line, -node.source.end_line))

    def _realization(self, observation: Node) -> CallGraph:
        entries = CallGraph()
        for edge in self._graph.edges.from_parent("invokes", observation):
            member = edge.child
            entries.extend(self._call(((member.get_fact("owner", ""), member.name),), member))
        if not entries:
            entries.add_line(NO_OPERATION, 0)
        return entries

    def _call(self, path: CallPath, code: Optional[Node]) -> CallGraph:
        """A call on the last member of path, reached through the members before it, then the interactions the model
        gives it, then what it returns."""
        owner, name = path[-1]
        depth = len(path) - 1
        described = self._clean.model_documents.described_member(owner, name) if self._clean is not None else None
        # A described property, a described getter, and a getter's code node all read as a property.
        subject = described if described is not None else code
        is_property = subject is not None and subject.type == "Property"
        signature = ", ".join(f"{label}: {kind}" if kind else label for label, kind in self._parameters(described, code))
        entries = CallGraph()
        entries.add_line(f"-> {owner}.{name}" if is_property else f"-> {owner}.{name}({signature})", depth)
        if depth < _DEEPEST_CALL and described is not None:
            entries.extend(self._interactions(described, path))
        returns = described.value_type.strip() if described is not None else ""
        if returns:
            entries.add_line(f"<- {returns}", depth)
        return entries

    def _interactions(self, described: Operation | Property, path: CallPath) -> CallGraph:
        """The calls the model gives a described member, each with its own interactions, one level below path; a member
        already on path is not followed again."""
        found = CallGraph()
        for interaction in described.callees:
            callee = self._member_named(interaction)
            if callee is not None and callee not in path:
                found.extend(self._call((*path, callee), self._code_member(*callee)))
        return found

    def _member_named(self, interaction: str) -> Optional[Member]:
        """`Session.change_workpath` or `Repo.switch_branch(name)` as (class, member); None for anything else."""
        match = _MEMBER_CALL.match(interaction.strip())
        return (match.group(1), match.group(2)) if match else None

    def _parameters(self, described: Operation | Property | None, code: Optional[Node]) -> List[tuple[str, str]]:
        """Each parameter's name and type: the model's when it describes the member, else the code's."""
        if isinstance(described, Operation):
            return [(parameter.name, (parameter.type_hint or "").strip()) for parameter in described.parameters]
        if described is not None or code is None:
            return []
        return [(parameter.name, (parameter.get_fact("type_hint") or "").strip()) for parameter in parameters_of(code)]

    def _code_member(self, owner: str, name: str) -> Optional[Node]:
        """The code's member owner.name, when the graph loaded it."""
        if self._clean is None:
            return None
        return next((member for member in self._clean.code_index.members_named(name) if member.get_fact("owner") == owner), None)
