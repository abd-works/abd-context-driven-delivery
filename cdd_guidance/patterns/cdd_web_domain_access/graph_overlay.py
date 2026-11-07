"""How the CDD web domain access pattern takes part in the graph: each file that reaches the domain from outside Python
(a route, a node tier, a hand-written adapter, an annotated toolset) becomes a DDD node carrying the facts its rules read."""

from __future__ import annotations

from pathlib import Path

from harness.graph.graph import Graph, Source
from harness.graph.graph_practice import GraphOverlay, GraphPractices
from harness.graph.skipped_folders import scanned_files


class WebDomainAccessOverlay(GraphOverlay):
    def guidance(self):
        from cdd_guidance.patterns.cdd_web_domain_access.cdd_web_domain_access import CddWebDomainAccess

        return CddWebDomainAccess()

    def read(self, graph: Graph) -> None:
        if not graph.folder or "ddd" not in graph.practices:
            return
        ddd = graph.practice("ddd")
        root = Path(graph.folder)
        for file in scanned_files(root):
            tier = _access_tier(file, file.read_text(encoding="utf-8", errors="replace"))
            if tier is None:
                continue
            semantic, facts = tier
            relative = file.relative_to(root).as_posix()
            node = ddd.add_named(semantic, f"ddd:{semantic}:{relative}", file.name, Source.whole_file(relative, str(root)))
            for key, value in facts.items():
                node.set_fact(key, value)


def _access_tier(file: Path, text: str) -> tuple[str, dict] | None:
    from cdd_guidance.patterns.cdd_web_domain_access import access_facts

    if file.name.endswith("-routes.ts"):
        return "AccessRoute", access_facts.route_facts(text)
    if access_facts.is_hand_written_adapter(file.name, text):
        return "AccessHandWrittenAdapter", {}
    if file.name.endswith("-node.ts"):
        return "AccessNode", access_facts.node_facts(text)
    if file.suffix == ".py" and access_facts.is_annotated(text):
        return "AccessAnnotatedToolset", access_facts.annotated_toolset_facts(text)
    return None


GraphPractices.register_overlay(WebDomainAccessOverlay("cdd_web_domain_access"))
