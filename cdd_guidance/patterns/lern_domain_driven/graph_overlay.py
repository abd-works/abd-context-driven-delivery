"""How the LERN pattern takes part in the graph: on top of the practices it adds each aggregate's tier files (its node
root, client root, routes, JSON store, and views), the behavior and story test files, and the context mappings a bounded
context lists, wired with the pattern schema's relationship kinds and carrying the facts the pattern's rules read."""

from __future__ import annotations

import re
from pathlib import Path

from harness.graph.graph import Graph, Node, Source
from harness.graph.pattern_overlays import GraphOverlay
from harness.graph.skipped_folders import scanned_files

from cdd_guidance.patterns.lern_domain_driven.tier_facts import AggregateFolder, TierFile

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

    def _link(self, kind: str, parent: Node, child: Node) -> None:
        self.graph.link(kind, parent, child, self.overlay.display_of(kind))

    def read(self) -> None:
        from cdd_guidance.practices.ddd.ddd import Ddd
        from cdd_guidance.practices.stories.stories import Stories

        self._behaviors()
        ddd = self.graph.loaded(Ddd)
        self.stories = self.graph.loaded(Stories)
        if ddd is None or self.stories is None:
            return
        self.ddd = ddd
        self.setup_text = self.overlay.pattern.test_setup_text(self.root)
        self._context_mappings()
        self._tier_folders()
        aggregates = {node.source.file.replace("\\", "/"): node for node in self.ddd.in_graph.nodes("Aggregate")}
        for folder, aggregate in sorted(aggregates.items()):
            self._aggregate(folder, aggregate)
        self._story_files()

    def _behaviors(self) -> None:
        """LERN behavior files on the BDD practice, each carrying the facts its tier rules read."""
        from cdd_guidance.practices.bdd.bdd import Bdd

        bdd = self.graph.loaded(Bdd)
        if bdd is None:
            return
        for file in scanned_files(self.root):
            semantic = _BEHAVIOR_TIERS.get(".".join(file.name.split(".")[1:]))
            if semantic is not None:
                behavior = TierFile.at(self.root, file)
                node = self._file_node(bdd, behavior.relative, semantic, file.name)
                for key, value in behavior.behavior_facts().items():
                    node.set_fact(key, value)

    def _tier_folders(self) -> None:
        """A folder holding its slug's routes or node is an aggregate, even with no domain class: a CDD-backed one has none."""
        for file in scanned_files(self.root):
            folder = file.parent.relative_to(self.root).as_posix()
            is_tier_file = file.name in (f"{file.parent.name}-routes.ts", f"{file.parent.name}-node.ts")
            if is_tier_file and folder.startswith("src/") and not self.ddd.in_graph.holds(f"ddd:Aggregate:{folder}"):
                self.ddd.in_graph.add_named("Aggregate", f"ddd:Aggregate:{folder}", file.parent.name, Source(folder, 1, 1, self.ddd.in_graph.source_root))

    def _aggregate(self, folder: str, aggregate: Node) -> None:
        slug = Path(folder).name
        tiers = {semantic: self._file_node(self.ddd, f"{folder}/{name.format(slug=slug)}", semantic) for name, semantic in _TIER_FILES if (self.root / folder / name.format(slug=slug)).is_file()}
        for tier in tiers.values():
            self._link("owns", aggregate, tier)
        self._other_node_files(folder, slug, aggregate)
        roots = [node for node in self.ddd.in_graph.nodes("EntityRoot") if self._folder_of(node.source.file) == folder]
        repositories = [node for node in self.ddd.in_graph.nodes("Repository") if self._folder_of(node.source.file) == folder]
        self._tier_facts(folder, aggregate, tiers, repositories)
        self._link_tiers(tiers, roots, repositories)
        views = self._views(folder, slug, aggregate, tiers.get("ClientRoot"), repositories[0] if repositories else None)
        if "NodeRoot" in tiers:
            for view in views:
                self._link("views", tiers["NodeRoot"], view)

    def _link_tiers(self, tiers: dict[str, Node], roots: list[Node], repositories: list[Node]) -> None:
        node_root, client_root, route, store = (tiers.get(name) for name in ("NodeRoot", "ClientRoot", "Route", "JsonStore"))
        for entity in roots:
            if node_root is not None:
                self._link("nodeRoot", entity, node_root)
                self._link("hosts", entity, node_root)
            if client_root is not None:
                self._link("interacts", entity, client_root)
        if client_root is not None and route is not None:
            self._link("calls", client_root, route)
        if route is not None and node_root is not None:
            self._link("nodeRoot", route, node_root)
        for repository in repositories:
            if store is not None:
                self._link("writes", repository, store)
            if node_root is not None:
                self._link("nodeRepository", node_root, repository)

    def _tier_facts(self, folder: str, aggregate: Node, tiers: dict[str, Node], repositories: list[Node]) -> None:
        """Read each LERN tier file once and record what its rules need on the node it became."""

        aggregate_folder = AggregateFolder(self.root, folder)
        aggregate.set_fact("web_path_literals", aggregate_folder.web_path_literals())
        aggregate.set_fact("core_request_reads", aggregate_folder.core_request_reads())
        readers = (("NodeRoot", lambda file: file.node_root_facts(self.setup_text)), ("Route", TierFile.route_facts))
        for semantic, facts_of in readers:
            tier = tiers.get(semantic)
            if tier is not None:
                for key, value in facts_of(TierFile.at(self.root, self.root / tier.source.file)).items():
                    tier.set_fact(key, value)
        for repository in repositories:
            file = TierFile.at(self.root, self.root / repository.source.file)
            repository.set_fact("unreset_instances", file.unreset_instances([repository.name], self.setup_text))

    def _other_node_files(self, folder: str, slug: str, aggregate: Node) -> None:
        """Every other ``*-node.ts`` in the aggregate folder is node-tier code too (e.g. ``iccid-inventory-node.ts``)."""
        folder_path = self.root / folder
        for file in sorted(folder_path.glob("*-node.ts")) if folder_path.is_dir() else []:
            if file.name != f"{slug}-node.ts":
                self._link("owns", aggregate, self._file_node(self.ddd, file.relative_to(self.root).as_posix(), "NodeRoot"))

    def _views(self, folder: str, slug: str, aggregate: Node, client_root: Node | None, repository: Node | None) -> list[Node]:
        views = []
        folder_path = self.root / folder
        for file in sorted(folder_path.glob("*.tsx")) if folder_path.is_dir() else []:
            match = _VIEW_EXPORT.search(file.read_text(encoding="utf-8")) if self._is_view_file(file.name, slug) else None
            if match is None:
                continue
            view = self._file_node(self.ddd, file.relative_to(self.root).as_posix(), "View", match.group(1))
            views.append(view)
            self._link("view", aggregate, view)
            if client_root is not None:
                self._link("clientRoot", view, client_root)
            if repository is not None:
                self._link("nodeRepository", view, repository)
        return views

    def _context_mappings(self) -> None:
        """Each ``Local → Remote`` line a bounded context's file lists, mapped to the aggregates it names."""
        for context in self.ddd.in_graph.nodes("BoundedContext"):
            markdown = context.source.file
            path = self.root / markdown if markdown and markdown != "." else None
            if path is None or not path.is_file():
                continue
            for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                match = _CONTEXT_ARROW.match(line.strip())
                map_id = f"ddd:ContextMapping:{markdown}:{index}"
                if match is None or self.ddd.in_graph.holds(map_id):
                    continue
                left, right = match.group(1).strip(), match.group(2).strip()
                mapping = self.ddd.in_graph.add_named("ContextMapping", map_id, f"{left} → {right}", Source(markdown, index, index, self.ddd.in_graph.source_root))
                self._link("mappedTo", context, mapping)
                for kind, label in (("local", left), ("remote", right)):
                    aggregate = self._aggregate_named(label)
                    if aggregate is not None:
                        self._link(kind, mapping, aggregate)

    def _aggregate_named(self, label: str) -> Node | None:
        label = label.strip()
        aggregates = self.ddd.in_graph.nodes("Aggregate")
        for node in aggregates:
            if node.name == label or label.endswith(f"· {node.name}") or label.endswith(f"·{node.name}"):
                return node
        tail = label.split("·")[-1].strip() if "·" in label else label
        return next((node for node in aggregates if node.name == tail), None)

    def _story_files(self) -> None:
        stories = self.stories
        for file in scanned_files(self.root):
            semantic = self._story_semantic(file)
            if semantic is None:
                continue
            story = TierFile.at(self.root, file)
            node = self._file_node(stories, story.relative, semantic, file.name)
            parent = self._parent_story_scope(story.relative)
            if parent is not None:
                self._link("owns", parent, node)
            for key, value in story.story_facts().items():
                node.set_fact(key, value)

    def _parent_story_scope(self, relative: str) -> Node | None:
        """The innermost epic of the stories whose folder holds the file; else the epic named for the file's folder."""
        rel = relative.replace("\\", "/")
        epics = [node for node in self.stories.in_graph.nodes() if node.type in {"Epic", "SubEpic"}]
        holding = [
            (len(self._folder_of(node.source.file)), node)
            for node in epics
            if node.source.file and (rel == self._folder_of(node.source.file) or rel.startswith(f"{self._folder_of(node.source.file)}/"))
        ]
        if holding:
            return max(holding, key=lambda item: item[0])[1]
        parent_name = Path(rel).parent.name.replace("_", "-")
        return next((node for node in epics if node.name.replace("_", "-") == parent_name), None)

    def _file_node(self, practice, relative: str, semantic: str, name: str = "") -> Node:
        """The node for one tier file of practice, made the first time a tier names it."""
        graph = practice.graph
        node_id = f"{practice.key}:{semantic}:{relative}"
        existing = graph.node(node_id)
        if existing is not None:
            return existing
        return practice.in_graph.add_named(semantic, node_id, name or Path(relative).stem, Source.whole_file(relative, practice.in_graph.source_root))

    def _is_view_file(self, filename: str, slug: str) -> bool:
        if filename == f"{slug}-client.tsx" or not filename.endswith(".tsx"):
            return False
        return not any(filename.endswith(f"{suffix}.tsx") for suffix in _VIEW_SKIP_SUFFIXES)

    def _story_semantic(self, file: Path) -> str | None:
        if file.name.endswith(".story.shared.ts"):
            return "StoryShared"
        if file.name.endswith(".story.server.spec.ts"):
            return "ServerSpec"
        if file.name.endswith(".story.domain.spec.ts"):
            return "DomainSpec"
        if "playwright" in file.name and file.suffix == ".ts":
            return "PlaywrightSpec"
        return None

    def _folder_of(self, file_path: str) -> str:
        return str(Path(file_path).parent).replace("\\", "/")
