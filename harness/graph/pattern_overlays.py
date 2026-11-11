"""PatternOverlays and GraphOverlay. The pattern overlays a graph applies on top of the practices, such as
``lern_domain_driven``, and what each pattern gives the graph.

A pattern is a *PracticeGuidance* (LernDomainDriven, CddWebDomainAccess, CddClaudeMod) that owns a *GraphOverlay*: the
nodes it adds on top of the practices and the rules it adds to each. The pattern makes its overlay once and keeps it as
``graph_overlay``; the overlay holds its pattern. The package that defines the patterns registers their classes here
when it is imported. Each graph holds one *PatternOverlays*, which makes each pattern once, the first time the graph
applies it or reads its schemas, so the patterns depend on the graph and never the other way round.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from harness.annotations.class_folder import class_folder
from harness.guidance.practice_reading import rules_in

if TYPE_CHECKING:
    from harness.graph.graph import Graph


class GraphOverlay:
    """What one pattern gives the graph on top of the practices: the nodes it reads and the rules it adds to each
    practice, which live in the pattern's ``practices/<practice>/rules``. A pattern that adds no nodes keeps this base,
    which gives its rules."""

    direct_kinds: frozenset[str] = frozenset()
    """Relationship kinds of the pattern's schema that place a node as a child in the explorer tree; every other kind is
    listed under its kind's name."""

    def __init__(self, pattern: Any) -> None:
        self.pattern = pattern
        """The pattern's guidance, which owns this overlay; its rules give each of the overlay's graph rules its prose."""
        self._rules: dict[str, dict[str, Any]] = {}

    @property
    def name(self) -> str:
        """The pattern's folder name, such as ``lern_domain_driven``, which names its schema files and its rule labels."""
        return self.pattern.pattern

    def display_of(self, kind: str) -> str:
        """How the explorer tree shows an edge of this pattern's kind: as a child, or under the kind's name."""
        return "direct" if kind in self.direct_kinds else "relationship"

    def read(self, graph: Graph) -> None:
        """Add this pattern's nodes and edges to the practices ``graph`` holds."""

    def practice_file(self, practice_key: str, name: str) -> Path:
        """The file called name the pattern keeps beside its rules for the practice of practice_key, such as its
        ``schema.yaml``; it may not exist."""
        return Path(self.pattern.module_dir) / "practices" / practice_key / "model" / name

    def rules_for(self, practice: Any) -> dict[str, Any]:
        """The graph rules this pattern adds to practice, by slug, read once from the pattern's own folder: its package
        is the held pattern's own, the way a practice reads its rules from its own package."""
        if practice.key not in self._rules:
            package = type(self.pattern).__module__.rsplit(".", 1)[0]
            self._rules[practice.key] = rules_in(f"{package}.practices.{practice.key}.rules")
        return self._rules[practice.key]


class PatternOverlays:
    """The pattern overlays one graph applies. Each is a folder holding ``practices/``, named by its path or by the name
    of a registered pattern; a pattern is its folder's name. The registry of pattern classes is the process's, as the
    practice catalogue is; the pattern objects are this object's own, each made the first time it is wanted."""

    _registered: ClassVar[dict[str, type]] = {}

    @classmethod
    def register(cls, *pattern_classes: type) -> None:
        """Hold pattern_classes as the patterns a graph can apply, each by its ``pattern`` name."""
        PatternOverlays._registered = {pattern_class.pattern: pattern_class for pattern_class in pattern_classes}

    def __init__(self, overlays: list[str] | tuple[str, ...] = ()) -> None:
        self._made: dict[str, Any] = {}
        self.paths: list[str] = []
        self.patterns: list[Any] = []
        self.apply(overlays)

    def apply(self, overlays: list[str] | tuple[str, ...]) -> None:
        """Apply the overlays named, each a folder or a pattern's name, in place of those applied before. The patterns
        among them are found here, once, and kept, so asking for them reads no folder."""
        self.paths = self._paths_of(overlays)
        self.patterns = self._patterns_at(self.paths)

    def _paths_of(self, overlays: list[str] | tuple[str, ...]) -> list[str]:
        """The overlay root of each overlay named, once each, in order."""
        paths: list[str] = []
        for overlay in overlays:
            text = str(overlay).strip()
            path = str(self.root_of(text)) if text else ""
            if path and path not in paths:
                paths.append(path)
        return paths

    def _patterns_at(self, paths: list[str]) -> list[Any]:
        """The registered pattern each overlay root is, each made once by this object."""
        patterns: list[Any] = []
        for path in paths:
            name = Path(path).name
            if name in self._registered and self._holds_practices(self._folder_of(name)):
                pattern = self._pattern(name)
                if pattern not in patterns:
                    patterns.append(pattern)
        return patterns

    @property
    def graph_overlays(self) -> list[GraphOverlay]:
        """What each applied pattern gives the graph: its nodes and its rules."""
        return [pattern.graph_overlay for pattern in self.patterns]

    @property
    def every_graph_overlay(self) -> list[GraphOverlay]:
        """The overlay of every registered pattern that holds a practice, applied or not."""
        return [self._pattern(name).graph_overlay for name in self.available]

    def checks_of(self, practice: Any, overlays: list[str] | None = None) -> dict[str, Any]:
        """The graph rules practice checks with these overlays applied, or with the overlays named, such as those a
        saved graph was saved with, by slug: its own, then those each pattern adds to it. Each pattern is the one this
        object made, so asking again makes none."""
        patterns = self.patterns if overlays is None else self._patterns_at(self._paths_of(overlays))
        merged = dict(practice.reading.graph_checks)
        for pattern in patterns:
            merged.update(pattern.graph_overlay.rules_for(practice))
        return merged

    @property
    def names(self) -> list[str]:
        """Every registered pattern by name, in name order, whether its folder holds practices yet or not: the patterns a
        person can choose to overlay."""
        return sorted(self._registered)

    @property
    def available(self) -> list[str]:
        """Every registered pattern that holds at least one practice."""
        return [name for name in sorted(self._registered) if self._holds_practices(self._folder_of(name))]

    def root_of(self, overlay: str) -> Path:
        """The overlay root a path or pattern name names: the folder itself when it holds ``practices/``, else the
        pattern of that name, else the folder as it is."""
        candidate = Path(overlay)
        if candidate.is_dir() and (candidate / "practices").is_dir():
            return candidate.resolve()
        if overlay in self._registered and (self._folder_of(overlay) / "practices").is_dir():
            return self._folder_of(overlay)
        return candidate.resolve()

    def _folder_of(self, name: str) -> Path:
        """The folder the registered pattern name is defined in."""
        return class_folder(self._registered[name])

    def _pattern(self, name: str) -> Any:
        """The guidance of the registered pattern name, made the first time this object wants it."""
        if name not in self._made:
            self._made[name] = self._registered[name]()
        return self._made[name]

    def _holds_practices(self, entry: Path) -> bool:
        practices = entry / "practices"
        if not entry.is_dir() or entry.name.startswith(".") or not practices.is_dir():
            return False
        return any(child.is_dir() and not child.name.startswith(".") for child in practices.iterdir())
