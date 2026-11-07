"""A BDD model read from a saved knowledge graph: the realization fidelity drawn from what the graph knows.

The behavior tree is the graph's `bdd` nodes, in each spec file's order. Each observation's call graph starts at what
its `invokes` edges name, and each call is followed through the Clean Engineering model's interactions, which the
graph saves under `model_members` on the Clean Engineering practice's root. Each code member's saved facts name its
class under `owner`. Every saved node and edge is read through the graph's own `Node.fact` and `Edge.fact`, so this
model reads fields by name and never depends on how the graph lays them out in the file.
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional

from cdd_guidance.practices.bdd.model.bdd_model import BddModel
from cdd_guidance.practices.bdd.model.nodes import Context, Description, Observation
from cdd_guidance.practices.clean_engineering.model.call_graph import CallGraphEntry
from harness.graph.graph import Edge, Node

# Following interactions further than this many calls deep adds lines nobody reads; a cycle is cut where it repeats.
_DEEPEST_CALL = 6
NO_OPERATION = "// the graph holds no operation this observation calls"
_BEHAVIOR_TYPES = ("Description", "Context", "Observation")


class GraphBddModel(BddModel):
    """Reads a saved graph (`Graph.write_json`, `graph.save_json`) into descriptions whose observations carry their realization."""

    def parse(self, text: str) -> "GraphBddModel":
        practices = (json.loads(text) if text.strip() else {}).get("practices", {})
        bdd = practices.get("bdd", {})
        self._read_clean_engineering(practices.get("clean_engineering", {}))
        self._invoked = self._invoked_members(bdd.get("edges", []))
        for nodes in self._behavior_by_file(bdd.get("nodes", [])).values():
            self._read_spec(sorted(nodes, key=lambda node: (node["line"], -node["end_line"])))
        return self

    def _read_clean_engineering(self, saved: dict) -> None:
        """The model's described members by `Class.member`, and the code's nodes by id."""
        self._members: Dict[str, dict] = json.loads(saved.get("root_facts") or "{}").get("model_members", {})
        code = (Node.fact(saved_node) for saved_node in saved.get("nodes", []))
        self._code: Dict[str, dict] = {node["node_id"]: node for node in code if node is not None}

    def _invoked_members(self, saved_edges: list) -> Dict[str, List[str]]:
        """The code members each observation invokes, by observation id."""
        invoked: Dict[str, List[str]] = {}
        for edge in filter(None, (Edge.fact(saved_edge) for saved_edge in saved_edges)):
            if edge["kind"] == "invokes":
                invoked.setdefault(edge["parent_id"], []).append(edge["child_id"])
        return invoked

    def _behavior_by_file(self, saved_nodes: list) -> Dict[str, List[dict]]:
        """The describe-tree nodes of each spec file."""
        by_file: Dict[str, List[dict]] = {}
        for node in filter(None, (Node.fact(saved_node) for saved_node in saved_nodes)):
            if node["semantic_type"] in _BEHAVIOR_TYPES:
                by_file.setdefault(node["file"], []).append(node)
        return by_file

    def _read_spec(self, nodes: List[dict]) -> None:
        """One spec file's nodes, outermost first at each line: a node sits inside the open node whose lines enclose it."""
        open_nodes: List[tuple[int, object]] = []
        for saved in nodes:
            while open_nodes and open_nodes[-1][0] < saved["line"]:
                open_nodes.pop()
            parent = open_nodes[-1][1] if open_nodes else None
            if saved["semantic_type"] == "Observation":
                self._add_observation(saved, parent)
                continue
            open_nodes.append((saved["end_line"], self._add_block(saved["name"], parent)))

    def _add_observation(self, saved: dict, parent) -> None:
        if parent is None:
            return
        observation = Observation(saved["name"], len(parent.observations) + 1)
        observation.call_graph = self._realization(saved["node_id"])
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

    def _realization(self, observation_id: str) -> List[CallGraphEntry]:
        entries: List[CallGraphEntry] = []
        for member_id in self._invoked.get(observation_id, []):
            member = self._code.get(member_id)
            if member is not None:
                facts = self._facts_of(member)
                entries.extend(self._call(facts.get("owner", ""), member["name"], 0, set(), facts))
        return entries or [CallGraphEntry(depth=0, kind="call", text=NO_OPERATION)]

    def _call(self, owner: str, name: str, depth: int, trail: set, code_facts: Optional[dict] = None) -> List[CallGraphEntry]:
        """A call on owner.name, then the interactions the model gives it, then what it returns."""
        described = self._members.get(f"{owner}.{name}", {})
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

    def _code_facts(self, owner: str, name: str) -> Optional[dict]:
        """The facts on the code's member owner.name, when the graph loaded it."""
        for member in self._code.values():
            if member["name"] == name and member["semantic_type"] in ("Operation", "Property"):
                if member["data"].get("owner") == owner:
                    return self._facts_of(member)
        return None

    def _facts_of(self, member: dict) -> dict:
        """A code member's saved facts, with its kind (Operation or Property)."""
        return {**member["data"], "kind": member["semantic_type"]}


def _member_named(interaction: str) -> Optional[tuple[str, str]]:
    """`Session.change_workpath` or `Repo.switch_branch(name)` as (class, member); None for anything else."""
    match = re.match(r"^([A-Za-z_]\w*)\.([A-Za-z_]\w*)", interaction.strip())
    return (match.group(1), match.group(2)) if match else None
