"""A BDD model read from a saved knowledge graph: the realization fidelity drawn from what the graph knows.

The behavior tree is the graph's `bdd` nodes, in each spec file's order. Each observation's call graph starts at what
its `invokes` edges name, and each call is followed through the Clean Engineering model's interactions, which the
graph saves under `model_members` on the Clean Engineering practice's root. Each code member's saved facts name its
class under `owner`. The saved file is read back into the graph's own nodes and edges, the way the graph reloads it,
so this model asks nodes for their facts and edges for their ends and never reads the file's layout.
"""

from __future__ import annotations

import re
from typing import List, Optional

from cdd_guidance.practices.bdd.model.bdd_model import BddModel
from cdd_guidance.practices.bdd.model.nodes import Context, Description, Observation
from cdd_guidance.practices.clean_engineering.model.call_graph import CallGraphEntry
from harness.graph.graph import Node
from harness.graph.saved_graph import SavedGraph

# Following interactions further than this many calls deep adds lines nobody reads; a cycle is cut where it repeats.
_DEEPEST_CALL = 6
NO_OPERATION = "// the graph holds no operation this observation calls"
_BEHAVIOR_TYPES = ("Description", "Context", "Observation")
_MEMBER_TYPES = ("Operation", "Property")


class GraphBddModel(BddModel):
    """Reads a saved graph (`Graph.write_json`, `graph.save_json`) into descriptions whose observations carry their realization."""

    def parse(self, text: str) -> "GraphBddModel":
        graph = SavedGraph.from_text(text).restored_graph()
        self._graph = graph
        self._bdd = graph.practice("bdd")
        self._clean = graph.practice("clean_engineering")
        for nodes in self._behavior_by_file().values():
            self._read_spec(sorted(nodes, key=lambda node: (node.source.start_line, -node.source.end_line)))
        return self

    def _behavior_by_file(self) -> dict[str, List[Node]]:
        """The describe-tree nodes of each spec file."""
        by_file: dict[str, List[Node]] = {}
        for node_type in _BEHAVIOR_TYPES:
            for node in self._graph.nodes_of(self._bdd, node_type):
                by_file.setdefault(node.source.file, []).append(node)
        return by_file

    def _read_spec(self, nodes: List[Node]) -> None:
        """One spec file's nodes, outermost first at each line: a node sits inside the open node whose lines enclose it."""
        open_nodes: List[tuple[int, object]] = []
        for saved in nodes:
            while open_nodes and open_nodes[-1][0] < saved.source.start_line:
                open_nodes.pop()
            parent = open_nodes[-1][1] if open_nodes else None
            if saved.type == "Observation":
                self._add_observation(saved, parent)
                continue
            open_nodes.append((saved.source.end_line, self._add_block(saved.name, parent)))

    def _add_observation(self, saved: Node, parent) -> None:
        if parent is None:
            return
        observation = Observation(saved.name, len(parent.observations) + 1)
        observation.call_graph = self._realization(saved)
        parent.observations.append(observation)

    def _add_block(self, name: str, parent):
        """An outermost block becomes a description; any block inside another becomes a context."""
        if parent is None:
            node = Description(name, len(self.descriptions) + 1)
            self.descriptions.append(node)
            return node
        node = Context(name, len(parent.contexts) + 1)
        parent.contexts.append(node)
        return node

    def _realization(self, observation: Node) -> List[CallGraphEntry]:
        entries: List[CallGraphEntry] = []
        for edge in self._graph.edges_from("invokes", observation):
            facts = _member_facts(edge.child)
            entries.extend(self._call(facts.get("owner", ""), edge.child.name, 0, set(), facts))
        return entries or [CallGraphEntry(depth=0, kind="call", text=NO_OPERATION)]

    def _call(self, owner: str, name: str, depth: int, trail: set, code_facts: Optional[dict] = None) -> List[CallGraphEntry]:
        """A call on owner.name, then the interactions the model gives it, then what it returns."""
        described = self._described_members().get(f"{owner}.{name}", {})
        facts = {**(code_facts or {}), **described}
        is_property = facts.get("kind") == "Property"
        parameters = facts.get("model_parameters") or facts.get("parameters") or []
        signature = ", ".join(f"{label}: {kind}" if kind else label for label, kind in parameters)
        entries = [CallGraphEntry(depth=depth, kind="out", text=f"{owner}.{name}" if is_property else f"{owner}.{name}({signature})")]
        if depth < _DEEPEST_CALL:
            for interaction in facts.get("interactions") or []:
                callee = _member_named(interaction)
                if callee is None or callee in trail:
                    continue
                entries.extend(self._call(callee[0], callee[1], depth + 1, trail | {(owner, name)}, self._code_facts(*callee)))
        returns = facts.get("model_returns") or ""
        if returns:
            entries.append(CallGraphEntry(depth=depth, kind="in", text=returns))
        return entries

    def _described_members(self) -> dict:
        """The members the Clean Engineering model describes, by `Class.member`, as its practice's root records them."""
        return self._graph.root_of(self._clean).get_fact("model_members", {}) or {}

    def _code_facts(self, owner: str, name: str) -> Optional[dict]:
        """The facts on the code's member owner.name, when the graph loaded it."""
        for node_type in _MEMBER_TYPES:
            for member in self._graph.nodes_of(self._clean, node_type):
                if member.name == name and member.facts.get("owner") == owner:
                    return _member_facts(member)
        return None


def _member_facts(member: Node) -> dict:
    """A code member's saved facts, with its kind (Operation or Property)."""
    return {**member.facts, "kind": member.type}


def _member_named(interaction: str) -> Optional[tuple[str, str]]:
    """`Session.change_workpath` or `Repo.switch_branch(name)` as (class, member); None for anything else."""
    match = re.match(r"^([A-Za-z_]\w*)\.([A-Za-z_]\w*)", interaction.strip())
    return (match.group(1), match.group(2)) if match else None
