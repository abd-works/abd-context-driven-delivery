"""How the OSS Portal pattern takes part in the graph: on top of the practices it adds each service (its Cloud Run boot,
Apigee proxy, and migrations) and each aggregate's tier files (view, client, BFF, BFF routes, service, service routes),
wired with the pattern schema's relationship kinds and carrying the facts the pattern's rules read, plus the story test
files on the Stories practice."""

from __future__ import annotations

import re
from pathlib import Path

from harness.graph.graph import Graph, Node, Source
from harness.graph.pattern_overlays import GraphOverlay
from harness.graph.skipped_folders import scanned_files

from cdd_guidance.patterns.lern_domain_driven.tier_facts import TierFile
from cdd_guidance.patterns.oss_portal_domain_driven.tier_facts import AggregateFolder, MigrationFile, OssFile, ProxyFolder

# Each aggregate tier file, by name pattern, and the node type it becomes.
_TIER_FILES = (
    ("{slug}-client.ts", "ClientRoot"),
    ("{slug}-bff.ts", "BffRoot"),
    ("{slug}-bff-routes.ts", "BffRoute"),
    ("{slug}-service.ts", "ServiceRoot"),
    ("{slug}-service-routes.ts", "ServiceRoute"),
)
_VIEW_SUFFIX = ".view.ts"
_STORY_TIERS = {
    ".story.shared.ts": "StoryShared",
    ".story.domain.spec.ts": "DomainSpec",
    ".story.service.spec.ts": "ServiceSpec",
    ".story.bff.spec.ts": "BffSpec",
    ".story.playwright.ts": "PlaywrightSpec",
    ".journey.e2e.ts": "JourneySpec",
}
_SERVICE_FOLDER = re.compile(r"^src/([a-z0-9-]+-service)$")


class OssPortalOverlay(GraphOverlay):
    # The OSS and DDD schema kinds that place a node as a child in the explorer tree.
    direct_kinds = frozenset(
        {
            "owns", "aggregates", "proxy", "migrations", "clientRoot", "bffRoot", "bffRoute", "serviceRoot", "serviceRoute",
            "view", "views", "calls", "routesTo", "repository", "belongsTo",
        }
    )

    def read(self, graph: Graph) -> None:
        if not graph.folder:
            return
        _OssReading(self, graph, Path(graph.folder)).read()


class _OssReading:
    """One read of the OSS tiers of a working copy onto the practices the graph holds."""

    def __init__(self, overlay: OssPortalOverlay, graph: Graph, root: Path) -> None:
        self.overlay = overlay
        self.graph = graph
        self.root = root

    def _link(self, kind: str, parent: Node, child: Node) -> None:
        self.graph.link(kind, parent, child, self.overlay.display_of(kind))

    def read(self) -> None:
        from cdd_guidance.practices.ddd.ddd import Ddd
        from cdd_guidance.practices.stories.stories import Stories

        self.ddd = self.graph.practices.loaded(Ddd)
        self.stories = self.graph.practices.loaded(Stories)
        if self.ddd is not None:
            self._aggregate_folders()
            services = self._services()
            aggregates = {node.source.file.replace("\\", "/"): node for node in self.ddd.reading.in_graph.nodes("Aggregate")}
            for folder, aggregate in sorted(aggregates.items()):
                if folder.startswith("src/"):
                    self._aggregate(folder, aggregate, services.get(Path(folder).parent.as_posix()))
        if self.stories is not None:
            self._story_files()

    # Services --------------------------------------------------------------------------------------------------------

    def _services(self) -> dict[str, Node]:
        """A node for each `src/<name>-service` folder, owning its proxy and its migrations."""
        services: dict[str, Node] = {}
        src = self.root / "src"
        for folder in sorted(src.iterdir()) if src.is_dir() else []:
            relative = folder.relative_to(self.root).as_posix()
            if not folder.is_dir() or not _SERVICE_FOLDER.match(relative):
                continue
            service = self._file_node(self.ddd, relative, "Service", folder.name)
            services[relative] = service
            proxy_folder = folder / f"{folder.name}-proxy"
            if proxy_folder.is_dir():
                proxy = self._file_node(self.ddd, proxy_folder.relative_to(self.root).as_posix(), "Proxy", proxy_folder.name)
                self._set_facts(proxy, ProxyFolder(self.root, proxy_folder).facts())
                self._link("proxy", service, proxy)
            migrations = folder / "migrations"
            for file in sorted(migrations.iterdir()) if migrations.is_dir() else []:
                if file.is_file():
                    migration = self._file_node(self.ddd, file.relative_to(self.root).as_posix(), "Migration", file.name)
                    self._set_facts(migration, MigrationFile(file.name, file.read_text(encoding="utf-8")).facts())
                    self._link("migrations", service, migration)
        return services

    # Aggregates ------------------------------------------------------------------------------------------------------

    def _aggregate_folders(self) -> None:
        """A folder holding its slug's service or BFF file is an aggregate, even before DDD has read a domain class."""
        for file in scanned_files(self.root):
            slug = file.parent.name
            folder = file.parent.relative_to(self.root).as_posix()
            if file.name in (f"{slug}-service.ts", f"{slug}-bff.ts") and folder.startswith("src/") and not self.ddd.reading.in_graph.holds(f"ddd:Aggregate:{folder}"):
                self.ddd.reading.in_graph.add_named("Aggregate", f"ddd:Aggregate:{folder}", slug, Source(folder, 1, 1, self.ddd.reading.in_graph.source_root))

    def _aggregate(self, folder: str, aggregate: Node, service: Node | None) -> None:
        slug = Path(folder).name
        service_name = Path(folder).parent.name
        if service is not None:
            self._link("aggregates", service, aggregate)
        tiers = {
            semantic: self._file_node(self.ddd, f"{folder}/{name.format(slug=slug)}", semantic)
            for name, semantic in _TIER_FILES
            if (self.root / folder / name.format(slug=slug)).is_file()
        }
        for tier in tiers.values():
            self._link("owns", aggregate, tier)
        self._tier_facts(folder, slug, service_name, aggregate, tiers)
        self._link_tiers(tiers)
        views = self._views(folder, aggregate, tiers.get("ClientRoot"))
        if "BffRoot" in tiers:
            for view in views:
                self._link("views", tiers["BffRoot"], view)

    def _tier_facts(self, folder: str, slug: str, service_name: str, aggregate: Node, tiers: dict[str, Node]) -> None:
        """Read each tier file once and record what its rules need on the node it became."""
        aggregate.set_fact("web_path_literals", AggregateFolder(self.root, folder).web_path_literals())
        core = self.root / folder / f"{slug}.ts"
        aggregate.set_fact("framework_imports", OssFile.at(self.root, core).core_facts()["framework_imports"] if core.is_file() else [])
        readers = {
            "ClientRoot": OssFile.browser_facts,
            "BffRoot": OssFile.bff_facts,
            "BffRoute": OssFile.bff_facts,
            "ServiceRoot": lambda file: file.service_facts(service_name),
            "ServiceRoute": lambda file: file.service_route_facts(service_name),
        }
        for semantic, node in tiers.items():
            self._set_facts(node, readers[semantic](OssFile.at(self.root, self.root / node.source.file)))

    def _link_tiers(self, tiers: dict[str, Node]) -> None:
        client, bff, bff_route, service, service_route = (tiers.get(name) for name in ("ClientRoot", "BffRoot", "BffRoute", "ServiceRoot", "ServiceRoute"))
        if client is not None and bff_route is not None:
            self._link("calls", client, bff_route)
        if bff_route is not None and bff is not None:
            self._link("bffRoot", bff_route, bff)
        if bff is not None and service_route is not None:
            self._link("routesTo", bff, service_route)
        if service_route is not None and service is not None:
            self._link("serviceRoot", service_route, service)

    def _views(self, folder: str, aggregate: Node, client: Node | None) -> list[Node]:
        views = []
        folder_path = self.root / folder
        for file in sorted(folder_path.glob(f"*{_VIEW_SUFFIX}")) if folder_path.is_dir() else []:
            view = self._file_node(self.ddd, file.relative_to(self.root).as_posix(), "DomainView", file.name.removesuffix(_VIEW_SUFFIX))
            self._set_facts(view, OssFile.at(self.root, file).view_facts())
            views.append(view)
            self._link("view", aggregate, view)
            if client is not None:
                self._link("clientRoot", view, client)
        return views

    # Stories ---------------------------------------------------------------------------------------------------------

    def _story_files(self) -> None:
        for file in scanned_files(self.root):
            semantic = next((semantic for suffix, semantic in _STORY_TIERS.items() if file.name.endswith(suffix)), None)
            if semantic is None:
                continue
            story = TierFile.at(self.root, file)
            node = self._file_node(self.stories, story.relative, semantic, file.name)
            self._set_facts(node, {**story.story_facts(), **story.behavior_facts()})

    # Nodes -----------------------------------------------------------------------------------------------------------

    def _set_facts(self, node: Node, facts: dict) -> None:
        for key, value in facts.items():
            node.set_fact(key, value)

    def _file_node(self, practice, relative: str, semantic: str, name: str = "") -> Node:
        """The node for one file or folder of practice, made the first time the overlay names it."""
        graph = practice.reading.graph
        node_id = f"{practice.key}:{semantic}:{relative}"
        existing = graph.node(node_id)
        if existing is not None:
            return existing
        return practice.reading.in_graph.add_named(semantic, node_id, name or Path(relative).stem, Source.whole_file(relative, practice.reading.in_graph.source_root))
