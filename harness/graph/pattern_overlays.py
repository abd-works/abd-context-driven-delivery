"""PatternOverlays and GraphOverlay. The pattern overlays a graph applies on top of the practices, such as
``lern_domain_driven``, and what each pattern gives the graph.

A pattern is a *PracticeGuidance* (LernDomainDriven, CddWebDomainAccess, CddClaudeMod) that owns a *GraphOverlay*: the
nodes it adds on top of the practices and the rules it adds to each. The pattern makes its overlay once and keeps it as
``graph_overlay``; the overlay holds its pattern. The graph is given the pattern objects the overlays it applies name,
made once per process here, so the patterns depend on the graph and never the other way round.
"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from harness.guidance.guidance import rules_in

if TYPE_CHECKING:
    from harness.graph.graph import Graph

_PATTERNS_ROOT = Path(__file__).resolve().parents[2] / "cdd_guidance" / "patterns"
_PATTERNS_PACKAGE = "cdd_guidance.patterns"


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
        """The graph rules this pattern adds to practice, by slug, read once from the pattern's own folder."""
        if practice.key not in self._rules:
            package = type(self.pattern).__module__.rsplit(".", 1)[0]
            self._rules[practice.key] = rules_in(f"{package}.practices.{practice.key}.rules")
        return self._rules[practice.key]


class PatternOverlays:
    """The pattern overlays a graph applies. Each is a folder holding ``practices/``, named by its path or by the name of
    a folder in ``cdd_guidance/patterns``; a pattern is that folder's name, and its guidance is made once per process."""

    _made: ClassVar[dict[str, Any]] = {}

    def __init__(self, overlays: list[str] | tuple[str, ...] = ()) -> None:
        self.paths: list[str] = []
        for overlay in overlays:
            text = str(overlay).strip()
            path = str(self.root_of(text)) if text else ""
            if path and path not in self.paths:
                self.paths.append(path)

    @property
    def patterns(self) -> list[Any]:
        """The guidance of each overlay that is a pattern, such as LernDomainDriven, each the one made for its folder."""
        found: list[Any] = []
        for path in self.paths:
            name = Path(path).name
            if (_PATTERNS_ROOT / name / "practices").is_dir():
                pattern = self._pattern(name)
                if pattern not in found:
                    found.append(pattern)
        return found

    @property
    def available(self) -> list[str]:
        """Every pattern in ``cdd_guidance/patterns`` that holds at least one practice."""
        if not _PATTERNS_ROOT.is_dir():
            return []
        return [entry.name for entry in sorted(_PATTERNS_ROOT.iterdir()) if self._holds_practices(entry)]

    @property
    def practice_schema_files(self) -> list[Path]:
        """The schema every pattern keeps for each practice it adds to, applied or not."""
        if not _PATTERNS_ROOT.is_dir():
            return []
        return sorted(_PATTERNS_ROOT.glob("*/practices/*/model/schema.yaml"))

    def root_of(self, overlay: str) -> Path:
        """The overlay root a path or pattern name names: the folder itself when it holds ``practices/``, else the
        pattern of that name, else the folder as it is."""
        candidate = Path(overlay)
        if candidate.is_dir() and (candidate / "practices").is_dir():
            return candidate.resolve()
        named = _PATTERNS_ROOT / overlay
        if named.is_dir() and (named / "practices").is_dir():
            return named.resolve()
        return candidate.resolve() if candidate.is_dir() else named.resolve()

    def _pattern(self, name: str) -> Any:
        """The guidance the pattern folder ``name`` declares in its module of the same name, made the first time."""
        if name not in self._made:
            module = importlib.import_module(f"{_PATTERNS_PACKAGE}.{name}.{name}")
            declared = next(
                member
                for member in vars(module).values()
                if inspect.isclass(member) and member.__module__ == module.__name__ and getattr(member, "pattern", "") == name
            )
            self._made[name] = declared()
        return self._made[name]

    def _holds_practices(self, entry: Path) -> bool:
        practices = entry / "practices"
        if not entry.is_dir() or entry.name.startswith(".") or not practices.is_dir():
            return False
        return any(child.is_dir() and not child.name.startswith(".") for child in practices.iterdir())
