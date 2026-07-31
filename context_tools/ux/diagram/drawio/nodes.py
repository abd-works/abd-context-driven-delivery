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

from context_tools.ux.diagram.drawio.cli_state import ux_map_to_cli_state
from context_tools.ux.document.json.nodes import JsonUxMap
from context_tools.ux.ux_model.nodes import Region, Screen, Transition
from context_tools.ux.ux_model.ux_map import UxMap

_CLI = Path(__file__).with_name("drawio_ux.mjs")


class DrawioUxMap(UxMap):
    @classmethod
    def parse(cls, content: str) -> UxMap:
        stripped = content.strip()
        if stripped.startswith("{"):
            return JsonUxMap.parse(stripped)
        return cls._parse_mxfile(stripped)

    @classmethod
    def render(cls, ux_map: UxMap) -> str:
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
        for candidate in (
            root / ".context" / "information-architecture.drawio",
            root / ".context" / "ia.drawio",
            root / "information-architecture.drawio",
            root / "ia.drawio",
            root / "site-map.drawio",
        ):
            if candidate.is_file():
                return cls.parse(candidate.read_text(encoding="utf-8"))
        matches = sorted((root / ".context").glob("*.drawio")) if (root / ".context").is_dir() else []
        matches += sorted(root.glob("*.drawio"))
        if matches:
            return cls.parse(matches[0].read_text(encoding="utf-8"))
        return None

    @classmethod
    def _parse_mxfile(cls, text: str) -> UxMap:
        ux_map = cls()
        try:
            root_el = ET.fromstring(text)
        except ET.ParseError:
            ux_map.context.notes.append("drawio parse failed - invalid XML")
            return ux_map

        site_map = _diagram_by_name(root_el, "Site Map")
        detailed = _diagram_by_name(root_el, "Detailed IA")
        source = site_map if site_map is not None else root_el

        id_to_screen: dict[str, Screen] = {}
        for cell in source.iter("mxCell"):
            if cell.get("vertex") != "1" or cell.get("parent") != "1":
                continue
            name = _strip_html(cell.get("value", ""))
            if not name or _is_annotation(name):
                continue
            screen = Screen(name, len(ux_map.screens))
            ux_map.append_screen(screen)
            id_to_screen[cell.get("id", "")] = screen

        if detailed is not None:
            name_to_screen = {screen.name: screen for screen in ux_map.screens}
            detailed_ids: dict[str, Screen] = {}
            for cell in detailed.iter("mxCell"):
                if cell.get("vertex") != "1" or cell.get("parent") != "1":
                    continue
                title = _strip_html(cell.get("value", ""))
                if title in name_to_screen:
                    detailed_ids[cell.get("id", "")] = name_to_screen[title]
            for cell in detailed.iter("mxCell"):
                parent = cell.get("parent", "")
                if cell.get("vertex") != "1" or parent not in detailed_ids:
                    continue
                style = cell.get("style", "")
                if "strokeColor=none" in style:
                    continue
                region_name = _strip_html(cell.get("value", ""))
                if not region_name or _is_annotation(region_name):
                    continue
                screen = detailed_ids[parent]
                if any(region.name == region_name for region in screen.regions):
                    continue
                screen.append_region(Region(region_name, len(screen.regions)))

        for cell in source.iter("mxCell"):
            if cell.get("edge") != "1":
                continue
            src = id_to_screen.get(cell.get("source", ""))
            tgt = id_to_screen.get(cell.get("target", ""))
            if src is None or tgt is None:
                continue
            trigger = _strip_html(cell.get("value", "")) or f"{src.name} -> {tgt.name}"
            if " / " in trigger:
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
            else:
                ux_map.transitions.append(
                    Transition(
                        trigger,
                        len(ux_map.transitions),
                        from_screen=src.name,
                        to_screen=tgt.name,
                        trigger=trigger,
                    )
                )

        return ux_map


def _diagram_by_name(root_el: ET.Element, name: str) -> Optional[ET.Element]:
    for diagram in root_el.findall("diagram"):
        if diagram.get("name") == name:
            return diagram
    return None


def _is_annotation(name: str) -> bool:
    lower = name.lower()
    return lower.startswith("stories:") or "domain terms:" in lower


def _strip_html(value: str) -> str:
    plain = re.sub(r"<[^>]+>", " ", value or "")
    return html.unescape(re.sub(r"\s+", " ", plain)).strip()
