"""How the LERN pattern takes part in the graph: on top of the practices it adds each aggregate's tier files (its node
root, client root, routes, JSON store, and views) and the behavior and story test files, wired with the pattern schema's
relationship kinds and carrying the facts the pattern's rules read. The context mappings a bounded context lists are
DDD's own nodes, which DDD's reading makes."""

from __future__ import annotations

import re
from pathlib import Path

from harness.graph.edge import EdgeType
from harness.graph.graph import Graph, Node, PracticeNodes
from harness.graph.pattern_overlays import GraphOverlay
from harness.graph.skipped_folders import scanned_files

from cdd_guidance.patterns.lern_domain_driven.tier_facts import AggregateFolder, TierFile

_VIEW_EXPORT = re.compile(r"export\s+function\s+(\w+View)\s*\(")
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
            "views", "jsonStore", "hosts", "interacts", "calls", "writes", "stores",
            "writtenBy", "belongsTo",
        }
    )

    def read(self, graph: Graph) -> None:
        if not graph.folder:
            return
        _LernReading(self, graph, Path(graph.folder)).read()


class _LernReading:
    """One read of the LERN tiers of a working copy onto the practices the graph holds."""

    def __init__(self, overlay: LernOverlay, graph: Graph, root: Path) -> None:
        self.overlay = overlay
        self.graph = graph
        self.root = root

    def link(self, kind: str, parent: Node, child: Node) -> None:
        self.graph.edges.record(EdgeType.from_kind(kind, self.overlay.display_of(kind)), parent, child)

    def read(self) -> None:
        from cdd_guidance.practices.ddd.ddd import Ddd
        from cdd_guidance.practices.stories.stories import Stories

        self._behaviors()
        ddd = self.graph.practices.loaded(Ddd)
        stories = self.graph.practices.loaded(Stories)
        if ddd is None or stories is None:
            return
        self.ddd = self.graph.practices.part_of(ddd)
        self.story_nodes = self.graph.practices.part_of(stories)
        self.setup_text = self.overlay.pattern.test_setup_text(self.root)
        self._tier_folders()
        aggregates = {node.source.file.replace("\\", "/"): node for node in self.ddd.nodes("Aggregate")}
        for folder, aggregate in sorted(aggregates.items()):
            self._aggregate(folder, aggregate)
        self._story_files()
        _record_screen_stories(self.story_nodes)

    def _behaviors(self) -> None:
        """LERN behavior files on the BDD practice, each carrying the facts its tier rules read."""
        from cdd_guidance.practices.bdd.bdd import Bdd

        bdd = self.graph.practices.loaded(Bdd)
        if bdd is None:
            return
        for file in scanned_files(self.root):
            semantic = _BEHAVIOR_TIERS.get(".".join(file.name.split(".")[1:]))
            if semantic is not None:
                behavior = TierFile.at(self.root, file)
                self.graph.practices.part_of(bdd).add_file(semantic, behavior.relative, file.name).set_facts(behavior.behavior_facts())

    def _tier_folders(self) -> None:
        """A folder holding its slug's routes or node is an aggregate, even with no domain class: a CDD-backed one has none."""
        for file in scanned_files(self.root):
            folder = file.parent.relative_to(self.root).as_posix()
            is_tier_file = file.name in (f"{file.parent.name}-routes.ts", f"{file.parent.name}-node.ts")
            if is_tier_file and folder.startswith("src/"):
                self.ddd.add_file("Aggregate", folder, file.parent.name)

    def _aggregate(self, folder: str, aggregate: Node) -> None:
        _AggregateTiers(self, folder, aggregate).read()

    def _story_files(self) -> None:
        for file in scanned_files(self.root):
            semantic = self._story_semantic(file)
            if semantic is None:
                continue
            story = TierFile.at(self.root, file)
            node = self.story_nodes.add_file(semantic, story.relative, file.name)
            parent = self._parent_story_scope(story.relative)
            if parent is not None:
                self.link("owns", parent, node)
            node.set_facts(story.story_facts())

    def _parent_story_scope(self, relative: str) -> Node | None:
        """The innermost epic of the stories whose folder holds the file; else the epic named for the file's folder."""
        rel = relative.replace("\\", "/")
        epics = [node for node in self.story_nodes.nodes() if node.type in {"Epic", "SubEpic"}]
        holding = [
            (len(self.folder_of(node.source.file)), node)
            for node in epics
            if node.source.file and (rel == self.folder_of(node.source.file) or rel.startswith(f"{self.folder_of(node.source.file)}/"))
        ]
        if holding:
            return max(holding, key=lambda item: item[0])[1]
        parent_name = Path(rel).parent.name.replace("_", "-")
        return next((node for node in epics if node.name.replace("_", "-") == parent_name), None)

    def _story_semantic(self, file: Path) -> str | None:
        if file.name.endswith(".story.shared.ts"):
            return "StoryShared"
        if file.name.endswith(".story.server.spec.ts"):
            return "ServerSpec"
        if file.name.endswith(".story.domain.spec.ts"):
            return "DomainSpec"
        if ("playwright" in file.name or file.name.endswith(".story.ui.spec.ts")) and file.suffix == ".ts":
            return "PlaywrightSpec"
        return None

    def folder_of(self, file_path: str) -> str:
        return str(Path(file_path).parent).replace("\\", "/")


class _AggregateTiers:
    """One aggregate folder's tier files, entity roots, and repositories, found once and linked onto the graph by the
    reading that found the folder."""

    def __init__(self, reading: _LernReading, folder: str, aggregate: Node) -> None:
        self.reading = reading
        self.folder = folder
        self.slug = Path(folder).name
        self.aggregate = aggregate
        in_graph = reading.ddd
        self.tiers = {
            semantic: in_graph.add_file(semantic, f"{folder}/{name.format(slug=self.slug)}")
            for name, semantic in _TIER_FILES
            if (reading.root / folder / name.format(slug=self.slug)).is_file()
        }
        self.roots = [node for node in in_graph.nodes("EntityRoot") if reading.folder_of(node.source.file) == folder]
        self.repositories = [node for node in in_graph.nodes("Repository") if reading.folder_of(node.source.file) == folder]

    def read(self) -> None:
        for tier in self.tiers.values():
            self.reading.link("owns", self.aggregate, tier)
        self._other_node_files()
        self._tier_facts()
        self._link_tiers()
        views = self._views()
        node_root = self.tiers.get("NodeRoot")
        if node_root is not None:
            for view in views:
                self.reading.link("views", node_root, view)

    def _link_tiers(self) -> None:
        link = self.reading.link
        node_root, client_root, route, store = (self.tiers.get(name) for name in ("NodeRoot", "ClientRoot", "Route", "JsonStore"))
        for entity in self.roots:
            if node_root is not None:
                link("nodeRoot", entity, node_root)
                link("hosts", entity, node_root)
            if client_root is not None:
                link("interacts", entity, client_root)
        if client_root is not None and route is not None:
            link("calls", client_root, route)
        if route is not None and node_root is not None:
            link("nodeRoot", route, node_root)
        for repository in self.repositories:
            if store is not None:
                link("writes", repository, store)
            if node_root is not None:
                link("nodeRepository", node_root, repository)

    def _tier_facts(self) -> None:
        """Read each LERN tier file once and record what its rules need on the node it became."""
        root, setup_text = self.reading.root, self.reading.setup_text
        aggregate_folder = AggregateFolder(root, self.folder)
        self.aggregate.set_fact("web_path_literals", aggregate_folder.web_path_literals())
        self.aggregate.set_fact("core_request_reads", aggregate_folder.core_request_reads())
        readers = (("NodeRoot", lambda file: file.node_root_facts(setup_text)), ("Route", TierFile.route_facts))
        for semantic, facts_of in readers:
            tier = self.tiers.get(semantic)
            if tier is not None:
                tier.set_facts(facts_of(TierFile.at(root, root / tier.source.file)))
        for repository in self.repositories:
            file = TierFile.at(root, root / repository.source.file)
            repository.set_fact("unreset_instances", file.unreset_instances([repository.name], setup_text))

    def _other_node_files(self) -> None:
        """Every other ``*-node.ts`` in the aggregate folder is node-tier code too (e.g. ``iccid-inventory-node.ts``)."""
        folder_path = self.reading.root / self.folder
        for file in sorted(folder_path.glob("*-node.ts")) if folder_path.is_dir() else []:
            if file.name != f"{self.slug}-node.ts":
                node = self.reading.ddd.add_file("NodeRoot", file.relative_to(self.reading.root).as_posix())
                self.reading.link("owns", self.aggregate, node)

    def _views(self) -> list[Node]:
        """The aggregate's view files, each linked to the aggregate, its client root, and its first repository."""
        link = self.reading.link
        client_root = self.tiers.get("ClientRoot")
        repository = self.repositories[0] if self.repositories else None
        views = []
        folder_path = self.reading.root / self.folder
        for file in sorted(folder_path.glob("*.tsx")) if folder_path.is_dir() else []:
            match = _VIEW_EXPORT.search(file.read_text(encoding="utf-8")) if self._is_view_file(file.name) else None
            if match is None:
                continue
            view = self.reading.ddd.add_file("View", file.relative_to(self.reading.root).as_posix(), match.group(1))
            views.append(view)
            link("view", self.aggregate, view)
            if client_root is not None:
                link("clientRoot", view, client_root)
            if repository is not None:
                link("nodeRepository", view, repository)
        return views

    def _is_view_file(self, filename: str) -> bool:
        if filename == f"{self.slug}-client.tsx" or not filename.endswith(".tsx"):
            return False
        return not any(filename.endswith(f"{suffix}.tsx") for suffix in _VIEW_SKIP_SUFFIXES)


def _record_screen_stories(story_nodes: PracticeNodes) -> None:
    """Whether a Playwright file's describe names each story (``has_screen_story``), which the screen-story rule reads:
    the screen story that drives the page the domain and server specs cannot see."""
    driven = {_story_key(name) for spec in story_nodes.nodes("PlaywrightSpec") for name in spec.get_fact("screen_stories", [])}
    for story in story_nodes.nodes("Story"):
        story.set_fact("has_screen_story", _story_key(story.name) in driven)


def _story_key(name: str) -> str:
    """A story's name as a describe may write it: lower case, with its words one space apart."""
    return " ".join(name.lower().split())
