"""A BDD model read from a saved knowledge graph: the realization fidelity drawn from what the graph knows.

The behavior tree is the graph's `bdd` nodes, in each spec file's order. Each observation's call graph starts at what
its `invokes` edges name, and each call is followed through the Clean Engineering model's interactions, which the
graph keeps as facts on the code's members and, for every member the model describes, under `model_members`.
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional

from cdd_guidance.practices.bdd.model.bdd_model import BddModel
from cdd_guidance.practices.bdd.model.nodes import Context, Description, Observation
from cdd_guidance.practices.clean_engineering.model.call_graph import CallGraphEntry
from harness.graph.node_data import decode_node_data

# Following interactions further than this many calls deep adds lines nobody reads; a cycle is cut where it repeats.
_DEEPEST_CALL = 6
NO_OPERATION = "// the graph holds no operation this observation calls"
_BEHAVIOR_TYPES = ("Description", "Context", "Observation")


class GraphBddModel(BddModel):
    """Reads a saved graph (`Graph.write_json`, `graph.save_json`) into descriptions whose observations carry their realization."""

    def parse(self, text: str) -> "GraphBddModel":
        document = json.loads(text) if text.strip() else {}
        practices = document.get("practices", {})
        bdd = practices.get("bdd", {})
        clean = practices.get("clean_engineering", {})
        self._members: Dict[str, dict] = json.loads(clean.get("root_facts") or "{}").get("model_members", {})
        self._code = {row[0]: row for row in clean.get("nodes", [])}
        self._invoked: Dict[str, List[str]] = {}
        for parent, child, kind, *_rest in bdd.get("edges", []):
            if kind == "invokes":
                self._invoked.setdefault(parent, []).append(child)
        rows_by_file: Dict[str, List[list]] = {}
        for row in bdd.get("nodes", []):
            if row[2] in _BEHAVIOR_TYPES:
                rows_by_file.setdefault(row[4], []).append(row)
        for rows in rows_by_file.values():
            self._read_spec(sorted(rows, key=lambda row: (row[5], -row[6])))
        return self

    def _read_spec(self, rows: List[list]) -> None:
        """One spec file's rows, outermost first at each line: a row sits inside the open row whose lines enclose it."""
        open_nodes: List[tuple[int, object]] = []
        for node_id, name, kind, _practice, _file, start, end, *_rest in rows:
            while open_nodes and open_nodes[-1][0] < start:
                open_nodes.pop()
            parent = open_nodes[-1][1] if open_nodes else None
            if kind == "Observation":
                if parent is not None:
                    observation = Observation(name, len(parent.observations) + 1)
                    observation.call_graph = self._realization(node_id)
                    parent.observations.append(observation)
                continue
            if parent is None:
                node = Description(name, len(self.descriptions) + 1)
                self.descriptions.append(node)
            else:
                node = Context(name, len(parent.contexts) + 1)
                parent.contexts.append(node)
            open_nodes.append((end, node))

    def _realization(self, observation_id: str) -> List[CallGraphEntry]:
        entries: List[CallGraphEntry] = []
        for member_id in self._invoked.get(observation_id, []):
            row = self._code.get(member_id)
            if row is not None:
                entries.extend(self._call(member_id.rsplit(":", 1)[-1], row[1], 0, set(), {**decode_node_data(row), "kind": row[2]}))
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
        for node_id, row in self._code.items():
            if row[1] == name and node_id.rsplit(":", 1)[-1] == owner and row[2] in ("Operation", "Property"):
                return {**decode_node_data(row), "kind": row[2]}
        return None


def _member_named(interaction: str) -> Optional[tuple[str, str]]:
    """`Session.change_workpath` or `Repo.switch_branch(name)` as (class, member); None for anything else."""
    match = re.match(r"^([A-Za-z_]\w*)\.([A-Za-z_]\w*)", interaction.strip())
    return (match.group(1), match.group(2)) if match else None
