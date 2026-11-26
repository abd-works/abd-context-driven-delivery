"""How the CDD web domain access pattern takes part in the graph: each file that reaches the domain from outside Python
(a route, a node tier, a hand-written adapter, an annotated toolset) becomes a DDD node carrying the facts its rules read."""

from __future__ import annotations

from pathlib import Path

from harness.graph.graph import Graph
from harness.graph.pattern_overlays import GraphOverlay
from harness.graph.skipped_folders import scanned_files

from cdd_guidance.patterns.cdd_web_domain_access.access_facts import AccessFile
from cdd_guidance.practices.ddd.ddd import Ddd


class WebDomainAccessOverlay(GraphOverlay):
    def read(self, graph: Graph) -> None:
        ddd = graph.practices.loaded(Ddd)
        if not graph.folder or ddd is None:
            return
        root = Path(graph.folder)
        ddd_nodes = graph.practices.part_of(ddd)
        for file in scanned_files(root):
            access = AccessFile.at(root, file)
            if access.node_type:
                ddd_nodes.add_file(access.node_type, access.relative, file.name).set_facts(access.facts)
