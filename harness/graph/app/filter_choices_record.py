"""The answers Python gives the explorer's filter, recorded for the explorer's own tests.

The explorer's tests stand in for the cdd server, so they answer ``graph.filter_choices`` from ``filter-choices.json``:
the practices their fixture graph holds (each one's node types, relationships, and rules, and the relationships each
node type sits on), the requests the explorer sends, and Python's answer to each. A real *Graph* works the answers out
here: its practices hold one node of each fixture node type and the fixture's edges between them, and its
``filter_choices`` answers each request through its real filter and each practice's real rule run. The one thing the
fixture gives in place of what a practice reads from its ``schema.yaml`` is the schema: the explorer's tests use a small
world of their own, whose rule labels are few enough to read. So a change to the filter, to how a practice's edges are
indexed, or to how a rule run labels the rules of a node type changes the answers the explorer is tested against. Run
this file to record them again; ``filter_choices_spec.py`` fails while they are stale.
"""
from __future__ import annotations

import sys
from functools import cached_property
from pathlib import Path
from typing import Any

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import cdd_guidance.practices  # noqa: E402,F401 - registers the practices with the practice catalogue
from harness.graph.graph import Graph, Source  # noqa: E402
from harness.graph.schema_rules import PracticeSchema  # noqa: E402
from harness.installation.data_class import data_of  # noqa: E402
from harness.installation.json_file import JsonFile  # noqa: E402

FILE = JsonFile(Path(__file__).resolve().parent / "filter-choices.json")


class FixtureSchema(PracticeSchema):
    """A practice's schema as the explorer's fixture gives it: the rule slugs each node type carries, read from the
    fixture's rule labels (``practice.node.rule``). Everything else a schema answers, it answers as the practice's
    own does."""

    def __init__(self, practice, labels: list[str]) -> None:
        super().__init__(practice)
        carried: dict[str, list[str]] = {}
        for label in labels:
            _practice, node_type, slug = label.split(".", 2)
            carried.setdefault(node_type, []).append(slug)
        self._carried = {node_type: tuple(slugs) for node_type, slugs in carried.items()}

    @cached_property
    def rules(self) -> dict[str, tuple[str, ...]]:
        return dict(self._carried)


class FixtureGraph:
    """The explorer's fixture graph as a real Graph: each fixture practice holds one node of each of its node types,
    an edge of each kind a node type sits on joins that node to the practice's root, and the practice's rule run reads
    the fixture's schema."""

    def __init__(self, fixture: dict[str, Any]) -> None:
        self.graph = Graph()
        for key, held in fixture["practices"].items():
            self._fill(self.graph.practice(key), held, fixture["edges_of_type"])

    def _fill(self, practice, held: dict[str, Any], edges_of_type: dict[str, list[str]]) -> None:
        part = practice.reading.in_graph
        part.rule_run.schema_with = lambda overlays, schema=FixtureSchema(practice, list(held["rules"])): schema
        nodes = {node_type: part.add_named(node_type, f"{practice.key}:{node_type}", node_type.lower(), Source("fixture", 1, 1)) for node_type in held["node_types"]}
        for kind in held["edge_types"]:
            for node_type, node in nodes.items():
                if kind in edges_of_type.get(node_type, []):
                    self.graph.link(kind, part.root, node)

    def answer(self, request: dict[str, Any]) -> dict[str, Any]:
        """Python's answer to one request the explorer sends ``graph.filter_choices``."""
        return data_of(self.graph.filter_choices(request["practices"], request["node_types"], request["practices_before"]))


def recorded(fixture: dict[str, Any]) -> dict[str, Any]:
    """The fixture with Python's answer to each of its requests."""
    graph = FixtureGraph(fixture)
    return {**fixture, "answers": [{"request": entry["request"], "answer": graph.answer(entry["request"])} for entry in fixture["answers"]]}


def read() -> dict[str, Any]:
    return FILE.read()


if __name__ == "__main__":
    FILE.write(recorded(read()))
