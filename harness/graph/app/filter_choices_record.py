"""The answers Python gives the explorer's filter, recorded for the explorer's own tests.

The explorer's tests stand in for the cdd server, so they answer ``graph.filter_choices`` from ``filter-choices.json``:
the practices their fixture graph holds (each one's node types, relationships, and rules, and the relationships each
node type sits on), the requests the explorer sends, and Python's answer to each. ``Graph.filter_choices`` works the
answers out here, on a graph holding exactly those practices, so a change to the Python rule changes the answers the
explorer is tested against. Run this file to record them again; ``filter_choices_spec.py`` fails while they are stale.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from harness.graph.graph import Graph  # noqa: E402
from harness.installation.data_class import data_of  # noqa: E402

FILE = Path(__file__).resolve().parent / "filter-choices.json"


class FixturePractice:
    """One practice of the explorer's fixture graph, as the filter reads a loaded practice: its node types, its
    relationships in their order, the edges each node type sits on, and the labels of the rules each node type runs."""

    def __init__(self, held: dict[str, Any], edges_of_type: dict[str, list[str]]) -> None:
        self.node_types = list(held["node_types"])
        self.edge_types = {kind: SimpleNamespace(kind=kind, order=order, is_offered=True) for order, kind in enumerate(held["edge_types"])}
        self._edges = [(node_type, kind) for node_type in self.node_types for kind in edges_of_type.get(node_type, [])]
        self._rules = list(held["rules"])

    def edges(self, kind: str) -> list[SimpleNamespace]:
        return [SimpleNamespace(parent=SimpleNamespace(type=node_type), child=SimpleNamespace(type="")) for node_type, held in self._edges if held == kind]

    def rule_labels_for(self, types: set[str]) -> set[str]:
        return {label for label in self._rules if label.split(".")[1] in types}


class FixtureGraph:
    """The explorer's fixture graph as ``Graph.filter_choices`` reads a graph: its practices by key, and its own filter."""

    def __init__(self, fixture: dict[str, Any]) -> None:
        edges_of_type = fixture["edges_of_type"]
        self.practices = {key: SimpleNamespace(reading=SimpleNamespace(in_graph=FixturePractice(held, edges_of_type))) for key, held in fixture["practices"].items()}
        self.filter = SimpleNamespace(clear=lambda: None)

    def answer(self, request: dict[str, Any]) -> dict[str, Any]:
        """Python's answer to one request the explorer sends ``graph.filter_choices``."""
        return data_of(Graph.filter_choices(self, request["practices"], request["node_types"], request["practices_before"]))


def recorded(fixture: dict[str, Any]) -> dict[str, Any]:
    """The fixture with Python's answer to each of its requests."""
    graph = FixtureGraph(fixture)
    return {**fixture, "answers": [{"request": entry["request"], "answer": graph.answer(entry["request"])} for entry in fixture["answers"]]}


def read() -> dict[str, Any]:
    return json.loads(FILE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    FILE.write_text(json.dumps(recorded(read()), indent=2) + "\n", encoding="utf-8")
