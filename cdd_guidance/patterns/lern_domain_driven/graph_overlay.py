"""How the LERN pattern takes part in the graph: on top of the practices it adds each aggregate's tier files (its node
root, client root, routes, JSON store, and views), the behavior and story test files, and the context mappings a bounded
context lists, wired with the pattern schema's relationship kinds and carrying the facts the pattern's rules read."""

from __future__ import annotations

import re
from pathlib import Path

from harness.graph.graph import Graph, Node, PracticeGraph, Source
from harness.graph.pattern_overlays import GraphOverlay
from harness.graph.skipped_folders import scanned_files

_VIEW_EXPORT = re.compile(r"export\s+function\s+(\w+View)\s*\(")
_CONTEXT_ARROW = re.compile(r"^[\s\-*>]*(.+?)\s*→\s*(.+?)\s*$")
_VIEW_SKIP_SUFFIXES = ("-form", "-fields", "-banner", "-messages", "-footer", "-loaded", "-client")
_TIER_FILES = (("{slug}-node.ts", "NodeRoot"), ("{slug}-client.tsx", "ClientRoot"), ("{slug}-routes.ts", "Route"), ("{slug}.json", "JsonStore"))
_BEHAVIOR_TIERS = {
    "spec.shared.ts": "BehaviorShared",
    "behavior.domain.spec.ts": "BehaviorDomain",
    "behavior.server.spec.ts": "BehaviorServer",
    "behavior.playwright.ts": "BehaviorPlaywright",
    "behavior.e2e.ts": "BehaviorE2e",
}


class LernOverlay(GraphOverlay):
    # The LERN and DDD schema kinds that place a node as a child in the explorer tree.
    direct_kinds = frozenset(
        {
            "owns", "root", "entityRoot", "nodeRoot", "clientRoot", "nodeRepository", "repository", "route", "view",
            "views", "mappedTo", "local", "remote", "jsonStore", "hosts", "interacts", "calls", "writes", "stores",
            "writtenBy", "belongsTo",
        }
    )

    def guidance(self):
        from cdd_guidance.patterns.lern_domain_driven.lern_domain_driven import LernDomainDriven

        return LernDomainDriven()

    def read(self, graph: Graph) -> None:
        if not graph.folder:
            return
        _LernReading(self, graph, Path(graph.folder)).read()


def _file_node(practice: PracticeGraph, relative: str, semantic: str, name: str = "") -> Node:
    """The node for one tier file, made the first time a tier names it."""
    node_id = f"{practice.name}:{semantic}:{relative}"
    existing = practice.by_id.get(node_id)
    if existing is not None:
        return existing
    return practice.add_named(semantic, node_id, name or Path(relative).stem, Source.whole_file(relative, practice.source_root))


class _LernReading:
    """One read of the LERN tiers of a working copy onto the practices the graph holds."""

    def __init__(self, overlay: LernOverlay, graph: Graph, root: Path) -> None:
        self.overlay = overlay
        self.graph = graph
        self.root = root

    def _link(self, practice: PracticeGraph, kind: str, parent: Node, child: Node) -> None:
        practice.link(kind, parent, child, self.overlay.display_of(kind))

    def read(self) -> None:
        from cdd_guidance.patterns.lern_domain_driven.tier_facts import test_setup_text

        self._behaviors()
        if "ddd" not in self.graph.practices or "stories" not in self.graph.practices:
            return
        self.ddd = self.graph.practice("ddd")
        self.setup_text = test_setup_text(self.root)
        self._context_mappings()
        self._tier_folders()
        aggregates = {node.source.file.replace("\\", "/"): node for node in self.ddd.nodes.get("Aggregate", [])}
        for folder, aggregate in sorted(aggregates.items()):
            self._aggregate(folder, aggregate)
        self._story_files()

    def _behaviors(self) -> None:
        """LERN behavior files on the BDD practice, each carrying the facts its tier rules read."""
        from cdd_guidance.patterns.lern_domain_driven.tier_facts import behavior_file_facts

        if "bdd" not in self.graph.practices:
            return
        bdd = self.graph.practice("bdd")
        for file in scanned_files(self.root):
            semantic = _BEHAVIOR_TIERS.get(".".join(file.name.split(".")[1:]))
            if semantic is not None:
                node = _file_node(bdd, file.relative_to(self.root).as_posix(), semantic, file.name)
                for key, value in behavior_file_facts(file.read_text(encoding="utf-8")).items():
                    node.set_fact(key, value)

    def _tier_folders(self) -> None:
        """A folder holding its slug's routes or node is an aggregate, even with no domain class: a CDD-backed one has none."""
        for file in scanned_files(self.root):
            folder = file.parent.relative_to(self.root).as_posix()
            is_tier_file = file.name in (f"{file.parent.name}-routes.ts", f"{file.parent.name}-node.ts")
            if is_tier_file and folder.startswith("src/") and f"ddd:Aggregate:{folder}" not in self.ddd.by_id:
                self.ddd.add_named("Aggregate", f"ddd:Aggregate:{folder}", file.parent.name, Source(folder, 1, 1, self.ddd.source_root))

    def _aggregate(self, folder: str, aggregate: Node) -> None:
        slug = Path(folder).name
        tiers = {semantic: _file_node(self.ddd, f"{folder}/{name.format(slug=slug)}", semantic) for name, semantic in _TIER_FILES if (self.root / folder / name.format(slug=slug)).is_file()}
        for tier in tiers.values():
            self._link(self.ddd, "owns", aggregate, tier)
        self._other_node_files(folder, slug, aggregate)
        roots = [node for node in self.ddd.nodes.get("EntityRoot", []) if _folder_of(node.source.file) == folder]
        repositories = [node for node in self.ddd.nodes.get("Repository", []) if _folder_of(node.source.file) == folder]
        self._tier_facts(folder, aggregate, tiers, repositories)
        self._link_tiers(tiers, roots, repositories)
        views = self._views(folder, slug, aggregate, tiers.get("ClientRoot"), repositories[0] if repositories else None)
        if "NodeRoot" in tiers:
            for view in views:
                self._link(self.ddd, "views", tiers["NodeRoot"], view)

    def _link_tiers(self, tiers: dict[str, Node], roots: list[Node], repositories: list[Node]) -> None:
        node_root, client_root, route, store = (tiers.get(name) for name in ("NodeRoot", "ClientRoot", "Route", "JsonStore"))
        for entity in roots:
            if node_root is not None:
                self._link(self.ddd, "nodeRoot", entity, node_root)
                self._link(self.ddd, "hosts", entity, node_root)
            if client_root is not None:
                self._link(self.ddd, "interacts", entity, client_root)
        if client_root is not None and route is not None:
            self._link(self.ddd, "calls", client_root, route)
        if route is not None and node_root is not None:
            self._link(self.ddd, "nodeRoot", route, node_root)
        for repository in repositories:
            if store is not None:
                self._link(self.ddd, "writes", repository, store)
            if node_root is not None:
                self._link(self.ddd, "nodeRepository", node_root, repository)

    def _tier_facts(self, folder: str, aggregate: Node, tiers: dict[str, Node], repositories: list[Node]) -> None:
        """Read each LERN tier file once and record what its rules need on the node it became."""
        from cdd_guidance.patterns.lern_domain_driven.tier_facts import core_request_reads, node_root_facts, route_facts, unreset_instances, web_path_literals

        aggregate.set_fact("web_path_literals", web_path_literals(self.root, folder))
        aggregate.set_fact("core_request_reads", core_request_reads(self.root, folder))
        readers = (("NodeRoot", lambda text: node_root_facts(text, self.setup_text)), ("Route", route_facts))
        for semantic, facts_of in readers:
            tier = tiers.get(semantic)
            if tier is not None:
                for key, value in facts_of((self.root / tier.source.file).read_text(encoding="utf-8")).items():
                    tier.set_fact(key, value)
        for repository in repositories:
            text = (self.root / repository.source.file).read_text(encoding="utf-8")
            repository.set_fact("unreset_instances", unreset_instances(text, [repository.name], self.setup_text))

    def _other_node_files(self, folder: str, slug: str, aggregate: Node) -> None:
        """Every other ``*-node.ts`` in the aggregate folder is node-tier code too (e.g. ``iccid-inventory-node.ts``)."""
        folder_path = self.root / folder
        for file in sorted(folder_path.glob("*-node.ts")) if folder_path.is_dir() else []:
            if file.name != f"{slug}-node.ts":
                self._link(self.ddd, "owns", aggregate, _file_node(self.ddd, file.relative_to(self.root).as_posix(), "NodeRoot"))

    def _views(self, folder: str, slug: str, aggregate: Node, client_root: Node | None, repository: Node | None) -> list[Node]:
        views = []
        folder_path = self.root / folder
        for file in sorted(folder_path.glob("*.tsx")) if folder_path.is_dir() else []:
            match = _VIEW_EXPORT.search(file.read_text(encoding="utf-8")) if _is_view_file(file.name, slug) else None
            if match is None:
                continue
            view = _file_node(self.ddd, file.relative_to(self.root).as_posix(), "View", match.group(1))
            views.append(view)
            self._link(self.ddd, "view", aggregate, view)
            if client_root is not None:
                self._link(self.ddd, "clientRoot", view, client_root)
            if repository is not None:
                self._link(self.ddd, "nodeRepository", view, repository)
        return views

    def _context_mappings(self) -> None:
        """Each ``Local → Remote`` line a bounded context's file lists, mapped to the aggregates it names."""
        for context in self.ddd.nodes.get("BoundedContext", []):
            markdown = context.source.file
            path = self.root / markdown if markdown and markdown != "." else None
            if path is None or not path.is_file():
                continue
            for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                match = _CONTEXT_ARROW.match(line.strip())
                map_id = f"ddd:ContextMapping:{markdown}:{index}"
                if match is None or map_id in self.ddd.by_id:
                    continue
                left, right = match.group(1).strip(), match.group(2).strip()
                mapping = self.ddd.add_named("ContextMapping", map_id, f"{left} → {right}", Source(markdown, index, index, self.ddd.source_root))
                self._link(self.ddd, "mappedTo", context, mapping)
                for kind, label in (("local", left), ("remote", right)):
                    aggregate = self._aggregate_named(label)
                    if aggregate is not None:
                        self._link(self.ddd, kind, mapping, aggregate)

    def _aggregate_named(self, label: str) -> Node | None:
        label = label.strip()
        aggregates = self.ddd.nodes.get("Aggregate", [])
        for node in aggregates:
            if node.name == label or label.endswith(f"· {node.name}") or label.endswith(f"·{node.name}"):
                return node
        tail = label.split("·")[-1].strip() if "·" in label else label
        return next((node for node in aggregates if node.name == tail), None)

    def _story_files(self) -> None:
        from cdd_guidance.patterns.lern_domain_driven.tier_facts import story_file_facts

        stories = self.graph.practice("stories")
        for file in scanned_files(self.root):
            semantic = _story_semantic(file)
            if semantic is None:
                continue
            relative = file.relative_to(self.root).as_posix()
            node = _file_node(stories, relative, semantic, Path(relative).name)
            parent = _parent_story_scope(stories, relative)
            if parent is not None:
                self._link(stories, "owns", parent, node)
            for key, value in story_file_facts(file.read_text(encoding="utf-8")).items():
                node.set_fact(key, value)


def _is_view_file(filename: str, slug: str) -> bool:
    if filename == f"{slug}-client.tsx" or not filename.endswith(".tsx"):
        return False
    return not any(filename.endswith(f"{suffix}.tsx") for suffix in _VIEW_SKIP_SUFFIXES)


def _story_semantic(file: Path) -> str | None:
    if file.name.endswith(".story.shared.ts"):
        return "StoryShared"
    if file.name.endswith(".story.server.spec.ts"):
        return "ServerSpec"
    if file.name.endswith(".story.domain.spec.ts"):
        return "DomainSpec"
    if "playwright" in file.name and file.suffix == ".ts":
        return "PlaywrightSpec"
    return None


def _folder_of(file_path: str) -> str:
    return str(Path(file_path).parent).replace("\\", "/")


def _parent_story_scope(stories: PracticeGraph, relative: str) -> Node | None:
    """The innermost epic whose folder holds the file; else the epic named for the file's folder."""
    rel = relative.replace("\\", "/")
    epics = [node for node in stories.by_id.values() if node.type in {"Epic", "SubEpic"}]
    holding = [
        (len(_folder_of(node.source.file)), node)
        for node in epics
        if node.source.file and (rel == _folder_of(node.source.file) or rel.startswith(f"{_folder_of(node.source.file)}/"))
    ]
    if holding:
        return max(holding, key=lambda item: item[0])[1]
    parent_name = Path(rel).parent.name.replace("_", "-")
    return next((node for node in epics if node.name.replace("_", "-") == parent_name), None)


OVERLAY = LernOverlay("lern_domain_driven")
