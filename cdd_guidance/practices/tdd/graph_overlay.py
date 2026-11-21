"""What TDD gives the knowledge graph: the tier each test file is in and the real resources a unit test reaches,
recorded as facts on the node each file gives: a BDD spec, and a Stories story read from its acceptance test file."""
from __future__ import annotations

from pathlib import Path

from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.stories.stories import Stories
from cdd_guidance.practices.tdd.tiers import is_code_file, real_resources_in, tier_of
from harness.graph.graph import Graph, Node
from harness.graph.pattern_overlays import GraphOverlay


class TddOverlay(GraphOverlay):
    """TDD's part of the graph: it adds no nodes, only facts on the test files of the practices it supplements."""

    # The practice and node type each test file is read into.
    TEST_FILE_NODES = ((Bdd, "Spec"), (Stories, "Story"))

    def read(self, graph: Graph) -> None:
        if not graph.folder:
            return
        root = Path(graph.folder)
        for practice_class, node_type in self.TEST_FILE_NODES:
            practice = graph.practices.loaded(practice_class)
            if practice is None or practice.reading.in_graph is None:
                continue
            for node in practice.reading.in_graph.nodes(node_type):
                if is_code_file(node.source.file or ""):
                    self._record(node, root / node.source.file)

    def _record(self, node: Node, path: Path) -> None:
        tier = tier_of(node.source.file)
        node.set_fact("tier", tier)
        text = path.read_text(encoding="utf-8", errors="replace") if tier == "unit" and path.is_file() else ""
        node.set_fact("real_resources", real_resources_in(text))
