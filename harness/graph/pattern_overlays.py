"""PatternOverlays and GraphOverlay. The pattern overlays a graph applies on top of the practices, such as
``lern_domain_driven``, and what each pattern gives the graph.

A pattern gives the graph a *GraphOverlay*: the nodes it adds on top of the practices and the rules it adds to each. A
pattern keeps its overlay as ``OVERLAY`` in its own ``graph_overlay`` module, which the graph imports the first time it
asks for that pattern, so the patterns depend on the graph and never the other way round.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.guidance.guidance import rules_in

if TYPE_CHECKING:
    from harness.graph.graph import Graph

_PATTERNS_ROOT = Path(__file__).resolve().parents[2] / "cdd_guidance" / "patterns"
_PATTERNS_PACKAGE = "cdd_guidance.patterns"


class GraphOverlay:
    """What one pattern gives the graph on top of the practices: the nodes it reads and the rules it adds to each
    practice, which live in ``<pattern>/practices/<practice>/rules``. A pattern that adds no nodes keeps none, and this
    base gives its rules."""

    direct_kinds: frozenset[str] = frozenset()
    """Relationship kinds of the pattern's schema that place a node as a child in the explorer tree; every other kind is
    listed under its kind's name."""

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern

    @classmethod
    def of(cls, pattern: str) -> GraphOverlay:
        """The overlay the pattern called pattern keeps as ``OVERLAY`` in its ``graph_overlay`` module; this base for a
        pattern that keeps none."""
        module_path = f"{_PATTERNS_PACKAGE}.{pattern}.graph_overlay"
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError as missing:
            if not (missing.name and module_path.startswith(missing.name)):
                raise
            return cls(pattern)
        overlay = getattr(module, "OVERLAY", None)
        return overlay if isinstance(overlay, GraphOverlay) else cls(pattern)

    def display_of(self, kind: str) -> str:
        """How the explorer tree shows an edge of this pattern's kind: as a child, or under the kind's name."""
        return "direct" if kind in self.direct_kinds else "relationship"

    def read(self, graph: Graph) -> None:
        """Add this pattern's nodes and edges to the practices ``graph`` holds."""

    def guidance(self) -> Any:
        """The pattern's guidance, whose rules give each of its graph rules its prose; none when it has no guidance."""
        return None

    def rules_for(self, practice: str) -> dict[str, Any]:
        return rules_in(f"{_PATTERNS_PACKAGE}.{self.pattern}.practices.{practice}.rules")


class PatternOverlays:
    """The pattern overlays a graph applies. Each is a folder holding ``practices/``, named by its path or by the name of
    a folder in ``cdd_guidance/patterns``; a pattern is that folder's name."""

    def __init__(self, overlays: list[str] | tuple[str, ...] = ()) -> None:
        self.paths: list[str] = []
        for overlay in overlays:
            text = str(overlay).strip()
            path = str(self.root_of(text)) if text else ""
            if path and path not in self.paths:
                self.paths.append(path)

    @property
    def patterns(self) -> tuple[str, ...]:
        """The pattern folder names, such as ``lern_domain_driven``, of the overlays that are patterns."""
        found: list[str] = []
        for path in self.paths:
            name = Path(path).name
            if (_PATTERNS_ROOT / name / "practices").is_dir() and name not in found:
                found.append(name)
        return tuple(found)

    @property
    def available(self) -> list[str]:
        """Every pattern in ``cdd_guidance/patterns`` that holds at least one practice."""
        if not _PATTERNS_ROOT.is_dir():
            return []
        return [entry.name for entry in sorted(_PATTERNS_ROOT.iterdir()) if self._holds_practices(entry)]

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

    def _holds_practices(self, entry: Path) -> bool:
        practices = entry / "practices"
        if not entry.is_dir() or entry.name.startswith(".") or not practices.is_dir():
            return False
        return any(child.is_dir() and not child.name.startswith(".") for child in practices.iterdir())
