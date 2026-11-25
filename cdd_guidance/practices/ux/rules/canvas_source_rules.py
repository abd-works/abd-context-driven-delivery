"""The story canvas rules on where a screen's files and values come from, at the mockup fidelity. A screen on the
canvas shows the product: every file it loads traces back to the product's own code, and every value it shows comes
from the scenario's fixtures, so a position kept for a step group says only where the screen is. Each rule reads the
canvas version the UX map's own file leads to (*PortedCanvas*); a map with no canvas beside it finds nothing."""

from __future__ import annotations

import json
import posixpath
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Iterator, Optional

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding

from cdd_guidance.practices.ux.model.claude_design.screen_artboard import PortedCanvas, ScreenArtboard
from cdd_guidance.practices.ux.model.claude_design.screen_sources import FIXTURES, ScreenSources
from cdd_guidance.practices.ux.rules.canvas_rules import ported_canvas

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

SCREENS = "screens"
EXPLORER = "explorer.dc.html"
# The canvas's own runtime, which Claude Design supplies beside every screen.
CANVAS_RUNTIME = ("screens/support.js",)
# The file in the UX practice's root that names the settings a project keeps as positions though they hold text.
ACCEPTED_POSITIONS_FILE = "position-settings.json"


def screen_artboards(canvas: PortedCanvas) -> Iterator[tuple[str, ScreenArtboard]]:
    """Each story screen's artboard in the canvas's screens folder, by its slug; the explorer is left out."""
    folder = canvas.project / SCREENS
    for path in sorted(folder.glob("*.dc.html")) if folder.is_dir() else []:
        if path.name != EXPLORER:
            yield path.name[: -len(".dc.html")], ScreenArtboard.at(path)


def _components(canvas: PortedCanvas, artboard: ScreenArtboard, seen: Optional[set] = None) -> list[tuple[str, ScreenArtboard]]:
    """The artboards a screen draws through ``dc-import``, by their path in the project folder, and the ones those
    draw in turn."""
    seen = set() if seen is None else seen
    found = []
    for name in artboard.imports:
        path = f"{SCREENS}/{name}.dc.html"
        if path in seen or not (canvas.project / path).is_file():
            continue
        seen.add(path)
        imported = ScreenArtboard.at(canvas.project / path)
        found += [(path, imported), *_components(canvas, imported, seen)]
    return found


def _loaded(artboard: ScreenArtboard) -> list[str]:
    """Each file the artboard loads, by its path in the project folder (the artboard sits in the screens folder)."""
    return [posixpath.normpath(posixpath.join(SCREENS, link.split("?")[0].split("#")[0])) for link in artboard.links]


class ScreenFilesFromProduction(PracticeGraphRule):
    """Every file a canvas screen loads (its scripts, its stylesheets, the artboards it draws through dc-import, and
    what those load) traces to the product's own code: the render records each copy's source in
    ``screen-sources.json``, and a source in the UX practice's folder, where prototypes live, or one nobody recorded,
    is reported by name with where it came from."""

    slug = "screen-files-from-production"
    node_types = ("UxMap",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        canvas = ported_canvas(node)
        if canvas is None:
            return []
        loaded: dict[str, list[str]] = {}
        for slug, artboard in screen_artboards(canvas):
            components = _components(canvas, artboard)
            for path in [*_loaded(artboard), *(component for component, _ in components),
                         *(file for _, imported in components for file in _loaded(imported))]:
                if path not in CANVAS_RUNTIME and slug not in loaded.setdefault(path, []):
                    loaded[path].append(slug)
        sources = ScreenSources(canvas.project)
        ux_folder = PurePosixPath(Path(node.source.file).parent.as_posix())
        findings = []
        for path, slugs in sorted(loaded.items()):
            origin = sources.origin(path)
            shown = ", ".join(slugs)
            if origin is None:
                findings.append(Finding(node, f"Screens {shown} load {path}, which screen-sources.json does not trace to any source; "
                                              f"copy it from the product's code through the screen's markup files and render again."))
            elif origin.get("kind") != FIXTURES and not _production(origin.get("from", ""), ux_folder):
                findings.append(Finding(node, f"Screens {shown} load {path}, copied from {origin.get('from')}, which is not the "
                                              f"product's code; load the production file, or a converted copy of it, instead."))
        return findings


def _production(source: str, ux_folder: PurePosixPath) -> bool:
    """Whether source, named from the project's root, is the product's code: inside the project and outside the UX
    practice's folder, which holds the prototypes and the canvases."""
    path = PurePosixPath(source)
    if path.is_absolute() or source.startswith("..") or ":" in source:
        return False
    return str(ux_folder) in ("", ".") or not (path == ux_folder or ux_folder in path.parents)


class PositionsHoldNoData(PracticeGraphRule):
    """A screen's positions say only where the screen is (a page, an open sheet, a choice among the component's own
    options), because every value a reader sees comes from the scenario's fixtures. A setting is a position when its
    value is true or false, or one of the options the component's data-props give that setting; text, a number, or a
    value the component does not offer is example data, reported by screen, setting and scenario, unless the project
    names the setting in ``position-settings.json`` in the UX practice's folder."""

    slug = "positions-hold-no-data"
    node_types = ("UxMap",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        canvas = ported_canvas(node)
        if canvas is None:
            return []
        accepted = _accepted_positions(Path(node.source.root, node.source.file).parent)
        findings = []
        for slug, artboard in screen_artboards(canvas):
            settings: dict = {}
            for _, component in _components(canvas, artboard):
                settings.update(component.settings)
            held: dict[str, list[str]] = {}
            for scenario, groups in artboard.positions.items():
                for group in groups:
                    for setting, value in group.items():
                        if setting in accepted or _is_position(value, settings.get(setting)):
                            continue
                        shown = f"{scenario or 'the story'} ({json.dumps(value, ensure_ascii=False)})"
                        if shown not in held.setdefault(setting, []):
                            held[setting].append(shown)
            for setting, scenarios in held.items():
                findings.append(Finding(node, f"Screen {slug} keeps {setting} as a position, but it holds example data in "
                                              f"{', '.join(scenarios)}; give the value through the scenario's fixtures."))
        return findings


def _is_position(value, setting: Optional[dict]) -> bool:
    """Whether value places the screen: true or false, or one of the options the component gives the setting."""
    if value is None or isinstance(value, bool):
        return True
    editor = (setting or {}).get("editor")
    if editor == "boolean":
        return True
    if editor == "enum":
        return value in ((setting or {}).get("options") or [])
    return False


def _accepted_positions(ux_folder: Path) -> set[str]:
    """The settings the project keeps as positions though their values are text or numbers."""
    file = ux_folder / ACCEPTED_POSITIONS_FILE
    if not file.is_file():
        return set()
    try:
        held = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    return {name for name in (held.get("accepted") or []) if isinstance(name, str)} if isinstance(held, dict) else set()
