"""Draw.io channel - IA via drawio-ux CLI (Detailed IA + Site Map).

Render builds CLI state from the UxMap and invokes `drawio_ux.mjs write`.
Parse prefers the Site Map page for screens/transitions; region titles come
from the Detailed IA page when present. The diagram carries screens, their regions, and transitions;
layouts, story names, and controls stay in the JSON and HTML formats.
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from cdd_guidance.practices.ux.model.drawio.cli_state import ux_map_to_cli_state

from cdd_guidance.practices.ux.model.nodes import Region, Screen, Transition
from cdd_guidance.practices.ux.model.ux_map import UxMap

_CLI = Path(__file__).with_name("drawio_ux.mjs")
# Writing a two-page diagram takes well under a second; a write still running after this has hung.
_CLI_TIMEOUT_SECONDS = 60
# A Site Map edge drawn both ways carries both triggers in one label, "there / back".
_BOTH_WAYS = " / "


class DrawioCliMissing(FileNotFoundError):
    """The vendored drawio-ux command line is not beside this module, so no diagram can be written."""


class DrawioCliFailed(RuntimeError):
    """The drawio-ux command line exited with an error or wrote no diagram."""


class DrawioCliTimedOut(DrawioCliFailed):
    """The drawio-ux command line ran past its timeout and was stopped."""


class UnreadableDrawio(ValueError):
    """The draw.io content is not XML, so it holds no screens to read."""


class DrawioUxMap(UxMap):
    workspace_files = (
        ".context/information-architecture.drawio",
        ".context/ia.drawio",
        "information-architecture.drawio",
        "ia.drawio",
        "site-map.drawio",
        ".context/*.drawio",
        "*.drawio",
    )
    cli_timeout_seconds: float = _CLI_TIMEOUT_SECONDS

    def parse(self, content: str) -> UxMap:
        stripped = content.strip()
        try:
            root_element = ET.fromstring(stripped)
        except ET.ParseError as error:
            raise UnreadableDrawio(f"draw.io content is not valid XML: {error}") from error
        return DrawioUxMapReader(type(self).create(), root_element).read()

    def render(self, ux_map: UxMap) -> str:
        """Render Detailed IA + Site Map through the vendored drawio-ux CLI."""
        if not _CLI.is_file():
            raise DrawioCliMissing(f"drawio-ux CLI missing: {_CLI}")
        with tempfile.TemporaryDirectory(prefix="ux-drawio-") as folder:
            out_path = Path(folder) / "information-architecture.drawio"
            state_path = Path(folder) / "state.json"
            state_path.write_text(json.dumps(ux_map_to_cli_state(ux_map, str(out_path)), indent=2), encoding="utf-8")
            self._run_cli(["node", str(_CLI), "write", str(out_path), str(state_path)])
            if not out_path.is_file():
                raise DrawioCliFailed(f"drawio-ux write produced no diagram at {out_path}")
            return out_path.read_text(encoding="utf-8")

    def _run_cli(self, command: list[str]) -> None:
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False,
                                    timeout=self.cli_timeout_seconds)
        except subprocess.TimeoutExpired as error:
            raise DrawioCliTimedOut(f"drawio-ux write ran past {self.cli_timeout_seconds} seconds") from error
        if result.returncode != 0:
            raise DrawioCliFailed(f"drawio-ux write failed:\n{result.stdout}\n{result.stderr}")


class DrawioUxMapReader:
    """Reads one draw.io file into a new map: screens from the Site Map page, then each screen's regions from the
    Detailed IA page, then the transitions drawn between screens."""

    def __init__(self, ux_map: UxMap, root_element: ET.Element) -> None:
        self.ux_map = ux_map
        self.root_element = root_element
        self._screen_by_cell: dict[str, Screen] = {}

    def read(self) -> UxMap:
        site_map = self._diagram_named("Site Map")
        detailed = self._diagram_named("Detailed IA")
        source = site_map if site_map is not None else self.root_element
        with self.ux_map.batch_schema_sync():
            self._read_screens(source)
            if detailed is not None:
                self._read_regions(detailed)
            self._read_transitions(source)
        return self.ux_map

    def _read_screens(self, source: ET.Element) -> None:
        for cell in source.iter("mxCell"):
            if cell.get("vertex") != "1" or cell.get("parent") != "1":
                continue
            name = _plain_text(cell.get("value", ""))
            if not name or _is_annotation(name):
                continue
            screen = Screen(name, len(self.ux_map.screens), graph=self.ux_map.graph)
            self.ux_map.append_screen(screen)
            self._screen_by_cell[cell.get("id", "")] = screen

    def _read_regions(self, detailed: ET.Element) -> None:
        screen_by_cell = self._detailed_screen_cells(detailed)
        for cell in detailed.iter("mxCell"):
            screen = screen_by_cell.get(cell.get("parent", ""))
            if cell.get("vertex") != "1" or screen is None or "strokeColor=none" in cell.get("style", ""):
                continue
            region_name = _plain_text(cell.get("value", ""))
            if not region_name or _is_annotation(region_name):
                continue
            if any(region.name == region_name for region in screen.regions):
                continue
            screen.append_region(Region(region_name, len(screen.regions), graph=self.ux_map.graph))

    def _detailed_screen_cells(self, detailed: ET.Element) -> dict[str, Screen]:
        screen_by_name = {screen.name: screen for screen in self.ux_map.screens}
        found: dict[str, Screen] = {}
        for cell in detailed.iter("mxCell"):
            title = _plain_text(cell.get("value", ""))
            if cell.get("vertex") == "1" and cell.get("parent") == "1" and title in screen_by_name:
                found[cell.get("id", "")] = screen_by_name[title]
        return found

    def _read_transitions(self, source: ET.Element) -> None:
        for cell in source.iter("mxCell"):
            if cell.get("edge") != "1":
                continue
            origin = self._screen_by_cell.get(cell.get("source", ""))
            target = self._screen_by_cell.get(cell.get("target", ""))
            if origin is None or target is None:
                continue
            trigger = _plain_text(cell.get("value", "")) or f"{origin.name} -> {target.name}"
            if _BOTH_WAYS not in trigger:
                self._append_transition(trigger, origin, target)
                continue
            there, back = [part.strip() for part in trigger.split(_BOTH_WAYS, 1)]
            self._append_transition(there, origin, target)
            self._append_transition(back, target, origin)

    def _append_transition(self, trigger: str, origin: Screen, target: Screen) -> None:
        self.ux_map.transitions.append(
            Transition(trigger, len(self.ux_map.transitions), origin, target, trigger, graph=self.ux_map.graph)
        )

    def _diagram_named(self, name: str) -> Optional[ET.Element]:
        for diagram in self.root_element.findall("diagram"):
            if diagram.get("name") == name:
                return diagram
        return None


def _is_annotation(name: str) -> bool:
    lower = name.lower()
    return lower.startswith("stories:") or "domain terms:" in lower


def _plain_text(value: str) -> str:
    plain = re.sub(r"<[^>]+>", " ", value or "")
    return html.unescape(re.sub(r"\s+", " ", plain)).strip()
