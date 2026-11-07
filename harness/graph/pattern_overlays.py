"""PatternOverlays. The pattern overlays a graph applies on top of the practices, such as ``lern_domain_driven``."""

from __future__ import annotations

from pathlib import Path

_PATTERNS_ROOT = Path(__file__).resolve().parents[2] / "cdd_guidance" / "patterns"


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
