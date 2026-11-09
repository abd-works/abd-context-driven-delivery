"""How the CDD web domain access pattern takes part in the graph: each file that reaches the domain from outside Python
(a route, a node tier, a hand-written adapter, an annotated toolset) becomes a DDD node carrying the facts its rules read."""

from __future__ import annotations

from pathlib import Path

from harness.graph.graph import Graph, Source
from harness.graph.pattern_overlays import GraphOverlay
from harness.graph.skipped_folders import scanned_files


class WebDomainAccessOverlay(GraphOverlay):
    def read(self, graph: Graph) -> None:
        from cdd_guidance.practices.ddd.ddd import Ddd

        ddd = graph.practices.loaded(Ddd)
        if not graph.folder or ddd is None:
            return
        root = Path(graph.folder)
        from cdd_guidance.patterns.cdd_web_domain_access.access_facts import AccessFile

        for file in scanned_files(root):
            tier = AccessFile.at(file).tier()
            if tier is None:
                continue
            semantic, facts = tier
            relative = file.relative_to(root).as_posix()
            node = ddd.in_graph.add_named(semantic, f"ddd:{semantic}:{relative}", file.name, Source.whole_file(relative, str(root)))
            for key, value in facts.items():
                node.set_fact(key, value)

