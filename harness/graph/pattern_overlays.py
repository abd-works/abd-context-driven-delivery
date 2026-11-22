"""PatternOverlays and GraphOverlay. The pattern overlays a graph applies on top of the practices, such as
``lern_domain_driven``, and what each pattern gives the graph.

A pattern is a *PracticeGuidance* (LernDomainDriven, CddWebDomainAccess, CddClaudeMod) that owns a *GraphOverlay*: the
nodes it adds on top of the practices and the rules it adds to each. The pattern makes its overlay once and keeps it as
``graph_overlay``; the overlay holds its pattern. The package that defines the patterns registers their classes with
``REGISTERED_PATTERNS`` when it is imported. Each graph holds one *PatternOverlays*, which makes each pattern once, the first time the graph
applies it or reads its schemas, so the patterns depend on the graph and never the other way round.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.annotations.class_folder import class_folder
from harness.annotations.class_registry import ClassRegistry
from harness.graph.practice_rule import PracticeGraphRule, SharedPracticeGraphRule
from harness.graph.schema_conformance import FRAMEWORK_RULES
from harness.graph.practice_reading import PracticeReading

if TYPE_CHECKING:
    from harness.graph.graph import Graph, Node
    from harness.guidance.guidance import PracticeGuidance

# A practice's graph rules by slug.
GraphChecks = dict[str, PracticeGraphRule]


class GraphOverlay:
    """What one pattern or practice supplement gives the graph on top of the practices: the nodes it reads and the rules
    it adds to each practice, which live in its ``practices/<practice>/rules``, and the rules it shares across practices,
    which live in its ``rules``. One that adds no nodes keeps this base, which gives its rules."""

    direct_kinds: frozenset[str] = frozenset()
    """Relationship kinds of the pattern's schema that place a node as a child in the explorer tree; every other kind is
    listed under its kind's name."""

    def __init__(self, pattern: PracticeGuidance) -> None:
        self.pattern = pattern
        """The pattern's guidance, which owns this overlay; its rules give each of the overlay's graph rules its prose."""
        self._rules: dict[str, GraphChecks] = {}

    @property
    def name(self) -> str:
        """The pattern's or supplement's folder name, such as ``lern_domain_driven`` or ``tdd``, which names its schema
        files and its rule labels."""
        return getattr(self.pattern, "pattern", None) or self.pattern.key

    def display_of(self, kind: str) -> str:
        """How the explorer tree shows an edge of this pattern's kind: as a child, or under the kind's name."""
        return "direct" if kind in self.direct_kinds else "relationship"

    def read(self, graph: Graph) -> None:
        """Add this pattern's nodes and edges to the practices ``graph`` holds."""

    def adds_rules_to(self, node: Node) -> bool:
        """Whether node carries the rules this overlay adds: every node does, unless the pattern is constrained to a
        language, as LERN is to TypeScript."""
        return True

    def practice_file(self, practice_key: str, name: str) -> Path:
        """The file called name the pattern keeps beside its rules for the practice of practice_key, such as its
        ``schema.yaml``; it may not exist."""
        return Path(self.pattern.module_dir) / "practices" / practice_key / "model" / name

    @property
    def roles(self) -> list[str]:
        """The layers the pattern's table names (`| Layer | File | Role |`): the roles a folder can hold of it when its
        layers sit in several folders. None for a pattern with no such table."""
        rows = self.pattern.section_text("Overview").splitlines()
        header = next((index for index, row in enumerate(rows) if row.strip().startswith("| Layer |")), None)
        if header is None:
            return []
        roles: list[str] = []
        for row in rows[header + 2:]:
            if not row.strip().startswith("|"):
                break
            roles.append(row.strip().strip("|").split("|")[0].strip())
        return roles

    def rules_for(self, practice: PracticeGuidance) -> GraphChecks:
        """The graph rules this pattern adds to practice, by slug, read once from the pattern's own folder: its package
        is the held pattern's own, the way a practice reads its rules from its own package."""
        if practice.key not in self._rules:
            package = type(self.pattern).__module__.rsplit(".", 1)[0]
            own = PracticeReading.rules_in(f"{package}.practices.{practice.key}.rules")
            self._rules[practice.key] = {**own, **self._shared_rules_for(practice, package)}
        return self._rules[practice.key]

    def _shared_rules_for(self, practice: PracticeGuidance, package: str) -> GraphChecks:
        """The rules in its own ``rules`` package it shares across practices, each bound to practice's node types; none
        it does not name practice in."""
        bound = {slug: rule.for_practice(practice) for slug, rule in PracticeReading.rules_in(f"{package}.rules").items() if isinstance(rule, SharedPracticeGraphRule)}
        return {slug: rule for slug, rule in bound.items() if rule is not None}


# The patterns are classes, and a class is defined once per process, so the registry of them is one per process too:
# each pattern class by its ``pattern`` name, the name a graph applies it by.
REGISTERED_PATTERNS: ClassRegistry[PracticeGuidance] = ClassRegistry(lambda pattern_class: pattern_class.pattern)


class PatternOverlays:
    """The pattern overlays one graph applies. Each is a folder holding ``practices/``, named by its path or by the name
    of a registered pattern; a pattern is its folder's name. It is made with the registry of pattern classes, the
    process's ``REGISTERED_PATTERNS`` unless a caller hands it another; the pattern objects are this object's own, each
    made the first time it is wanted."""

    def __init__(self, overlays: list[str] | tuple[str, ...] = (), registered: ClassRegistry[PracticeGuidance] = REGISTERED_PATTERNS) -> None:
        self._registered = registered
        self._made: dict[str, PracticeGuidance] = {}
        self.paths: list[str] = []
        self.patterns: list[PracticeGuidance] = []
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

    def _patterns_at(self, paths: list[str]) -> list[PracticeGuidance]:
        """The registered pattern each overlay root is, each made once by this object."""
        patterns: list[PracticeGuidance] = []
        for path in paths:
            name = Path(path).name
            if self._registered.has(name) and self._holds_practices(self._folder_of(name)):
                pattern = self.pattern_named(name)
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
        return [self.pattern_named(name).graph_overlay for name in self.available]

    def checks_of(self, practice: PracticeGuidance, overlays: list[str] | None = None) -> GraphChecks:
        """The graph rules practice checks with these overlays applied, or with the overlays named, such as those a
        saved graph was saved with, by slug: the framework's own, which every practice checks, its own, then those each
        pattern adds to it, then those each supplement the practice holds adds, whatever overlays were chosen. Each
        pattern is the one this object made, so asking again makes none."""
        patterns = self.patterns if overlays is None else self._patterns_at(self._paths_of(overlays))
        merged = {**FRAMEWORK_RULES, **practice.reading.graph_checks}
        for pattern in patterns:
            merged.update(pattern.graph_overlay.rules_for(practice))
        for overlay in self.supplement_overlays_of([practice]):
            merged.update(overlay.rules_for(practice))
        return merged

    def overlays_for(self, practice: PracticeGuidance) -> tuple[GraphOverlay, ...]:
        """The overlays practice's schema reads: each applied pattern's, then each of its supplements', which apply
        whatever overlays were chosen."""
        return (*self.graph_overlays, *self.supplement_overlays_of([practice]))

    def supplement_overlays_of(self, practices: list[PracticeGuidance]) -> list[GraphOverlay]:
        """The graph overlay of each supplement the practices hold, once each: what a graph reads and checks for its
        supplements, as it does for its applied patterns."""
        found: list[GraphOverlay] = []
        for practice in practices:
            for supplement in practice.working_set.supplements:
                overlay = supplement.graph_overlay
                if overlay is not None and overlay not in found:
                    found.append(overlay)
        return found

    @property
    def names(self) -> list[str]:
        """Every registered pattern by name, in name order, whether its folder holds practices yet or not: the patterns a
        person can choose to overlay."""
        return sorted(self._registered.names)

    @property
    def available(self) -> list[str]:
        """Every registered pattern that holds at least one practice."""
        return [name for name in self.names if self._holds_practices(self._folder_of(name))]

    def root_of(self, overlay: str) -> Path:
        """The overlay root a path or pattern name names: the folder itself when it holds ``practices/``, else the
        pattern of that name, else the folder as it is."""
        candidate = Path(overlay)
        if candidate.is_dir() and (candidate / "practices").is_dir():
            return candidate.resolve()
        if self._registered.has(overlay) and (self._folder_of(overlay) / "practices").is_dir():
            return self._folder_of(overlay)
        return candidate.resolve()

    def _folder_of(self, name: str) -> Path:
        """The folder the registered pattern name is defined in."""
        return class_folder(self._registered.named(name))

    def pattern_named(self, name: str) -> PracticeGuidance:
        """The guidance of the registered pattern name, whether its folder holds practices or not, made the first time
        this object wants it: what an action reads a pattern's own rules from."""
        if name not in self._made:
            self._made[name] = self._registered.named(name)()
        return self._made[name]

    def _holds_practices(self, entry: Path) -> bool:
        practices = entry / "practices"
        if not entry.is_dir() or entry.name.startswith(".") or not practices.is_dir():
            return False
        return any(child.is_dir() and not child.name.startswith(".") for child in practices.iterdir())
