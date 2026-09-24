"""Draw.io channel - IA via drawio-ux CLI (Detailed IA + Site Map).

Render builds CLI state from the UxMap and invokes `drawio_ux.mjs write`.
Parse prefers the Site Map page for screens/transitions; region titles come
from the Detailed IA page when present. JSON is still accepted for sideways
transform tests.
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

from practices.ux.model.drawio.cli_state import ux_map_to_cli_state
from practices.ux.model.json.nodes import JsonUxMap
from practices.ux.model.nodes import Region, Screen, Transition
from practices.ux.model.ux_map import UxMap

_CLI = Path(__file__).with_name("drawio_ux.mjs")


class DrawioUxMap(UxMap):
    def parse(self, content: str) -> UxMap:
        stripped = content.strip()
        if stripped.startswith("{"):
            return JsonUxMap.create().parse(stripped)
        return self._parse_mxfile(stripped)

    def render(self, ux_map: UxMap) -> str:
        """Render Detailed IA + Site Map through the vendored drawio-ux CLI."""
        if not _CLI.is_file():
            raise FileNotFoundError(f"drawio-ux CLI missing: {_CLI}")
        with tempfile.TemporaryDirectory(prefix="ux-drawio-") as tmp:
            tmp_path = Path(tmp)
            out_path = tmp_path / "information-architecture.drawio"
            state_path = tmp_path / "state.json"
            state = ux_map_to_cli_state(ux_map, str(out_path))
            state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
            result = subprocess.run(
                ["node", str(_CLI), "write", str(out_path), str(state_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0 or not out_path.is_file():
                raise RuntimeError(
                    "drawio-ux write failed:\n"
                    f"{result.stdout}\n{result.stderr}"
                )
            return out_path.read_text(encoding="utf-8")

    @classmethod
    def from_workspace(cls, root: Path) -> Optional[UxMap]:
        root = Path(root)
        loader = cls.create()
        for candidate in (
            root / ".context" / "information-architecture.drawio",
            root / ".context" / "ia.drawio",
            root / "information-architecture.drawio",
            root / "ia.drawio",
            root / "site-map.drawio",
        ):
            if candidate.is_file():
                return loader.parse(candidate.read_text(encoding="utf-8"))
        matches = sorted((root / ".context").glob("*.drawio")) if (root / ".context").is_dir() else []
        matches += sorted(root.glob("*.drawio"))
        if matches:
            return loader.parse(matches[0].read_text(encoding="utf-8"))
        return None

    def _parse_mxfile(self, text: str) -> UxMap:
        ux_map = type(self).create()
        try:
            root_el = ET.fromstring(text)
        except ET.ParseError:
            ux_map.context.notes.append("drawio parse failed - invalid XML")
            return ux_map

        site_map = self._diagram_by_name(root_el, "Site Map")
        detailed = self._diagram_by_name(root_el, "Detailed IA")
        source = site_map if site_map is not None else root_el
        self._id_to_screen = self._append_site_screens(ux_map, source)
        if detailed is not None:
            self._append_detailed_regions(ux_map, detailed)
        self._append_transitions(ux_map, source)
        return ux_map

    def _append_site_screens(self, ux_map: UxMap, source: ET.Element) -> dict[str, Screen]:
        id_to_screen: dict[str, Screen] = {}
        for cell in source.iter("mxCell"):
            if cell.get("vertex") != "1" or cell.get("parent") != "1":
                continue
            name = self._strip_html(cell.get("value", ""))
            if not name or self._is_annotation(name):
                continue
            screen = Screen(name, len(ux_map.screens))
            ux_map.append_screen(screen)
            id_to_screen[cell.get("id", "")] = screen
        return id_to_screen

    def _append_detailed_regions(self, ux_map: UxMap, detailed: ET.Element) -> None:
        name_to_screen = {screen.name: screen for screen in ux_map.screens}
        detailed_ids: dict[str, Screen] = {}
        for cell in detailed.iter("mxCell"):
            if cell.get("vertex") != "1" or cell.get("parent") != "1":
                continue
            title = self._strip_html(cell.get("value", ""))
            if title in name_to_screen:
                detailed_ids[cell.get("id", "")] = name_to_screen[title]
        for cell in detailed.iter("mxCell"):
            parent = cell.get("parent", "")
            if cell.get("vertex") != "1" or parent not in detailed_ids:
                continue
            if "strokeColor=none" in cell.get("style", ""):
                continue
            region_name = self._strip_html(cell.get("value", ""))
            if not region_name or self._is_annotation(region_name):
                continue
            screen = detailed_ids[parent]
            if any(region.name == region_name for region in screen.regions):
                continue
            screen.append_region(Region(region_name, len(screen.regions)))

    def _append_transitions(self, ux_map: UxMap, source: ET.Element) -> None:
        for cell in source.iter("mxCell"):
            if cell.get("edge") != "1":
                continue
            src = self._id_to_screen.get(cell.get("source", ""))
            tgt = self._id_to_screen.get(cell.get("target", ""))
            if src is None or tgt is None:
                continue
            trigger = self._strip_html(cell.get("value", "")) or f"{src.name} -> {tgt.name}"
            self._edge_src = src
            self._edge_tgt = tgt
            self._append_edge_transitions(ux_map, trigger)

    def _append_edge_transitions(self, ux_map: UxMap, trigger: str) -> None:
        src = self._edge_src
        tgt = self._edge_tgt
        if " / " not in trigger:
            ux_map.transitions.append(
                Transition(
                    trigger,
                    len(ux_map.transitions),
                    from_screen=src.name,
                    to_screen=tgt.name,
                    trigger=trigger,
                )
            )
            return
        left, right = [part.strip() for part in trigger.split(" / ", 1)]
        ux_map.transitions.append(
            Transition(
                left,
                len(ux_map.transitions),
                from_screen=src.name,
                to_screen=tgt.name,
                trigger=left,
            )
        )
        ux_map.transitions.append(
            Transition(
                right,
                len(ux_map.transitions),
                from_screen=tgt.name,
                to_screen=src.name,
                trigger=right,
            )
        )

    def _diagram_by_name(self, root_el: ET.Element, name: str) -> Optional[ET.Element]:
        for diagram in root_el.findall("diagram"):
            if diagram.get("name") == name:
                return diagram
        return None

    def _is_annotation(self, name: str) -> bool:
        lower = name.lower()
        return lower.startswith("stories:") or "domain terms:" in lower

    def _strip_html(self, value: str) -> str:
        plain = re.sub(r"<[^>]+>", " ", value or "")
        return html.unescape(re.sub(r"\s+", " ", plain)).strip()
