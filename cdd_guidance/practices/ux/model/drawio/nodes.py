"""Draw.io channel - IA via drawio-ux CLI (Detailed IA + Site Map).

Render copies the UxMap into a DrawioUxMap, whose screens and regions spell their own part of the drawio-ux
command line's state, and invokes `drawio_ux.mjs write`.
Parse prefers the Site Map page for screens/transitions; region titles come
from the Detailed IA page when present. The diagram carries screens, their regions, and transitions;
layouts, story names, and controls stay in the JSON and HTML formats.
"""

from __future__ import annotations

import html
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, Optional

from harness.installation.json_file import JsonFile
from cdd_guidance.practices.ux.model.nodes import Region, Screen
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


# Layouts the CLI templates understand (alias -> CLI id).
_CLI_LAYOUTS = {
    "stack": "stack",
    "list": "stack",
    "modal": "modal",
    "modal-dialog": "modal",
    "form": "form",
    "sidebar": "sidebar",
    "split-screen": "split-screen",
    "flyout": "flyout",
    "flyout-panel": "flyout",
    "holy-grail": "holy-grail",
}


class DrawioRegion(Region):
    """A region on the Detailed IA page: a form, a list with its actions, or chrome, by the controls it holds."""

    @classmethod
    def from_cell(cls, cell: ET.Element, index: int) -> Optional["DrawioRegion"]:
        """The region a cell inside a screen's box draws; none for a cell that draws no region (an unframed label,
        an annotation, or one with no text)."""
        name = _plain_text(cell.get("value", ""))
        if cell.get("vertex") != "1" or "strokeColor=none" in cell.get("style", "") or not name or _is_annotation(name):
            return None
        return cls(name, index)

    def cli_record(self) -> Dict[str, Any]:
        """This region in the drawio-ux command line's state."""
        area = self.area or "body"
        controls = list(self.controls)
        buttons = [control for control in controls if control.control_type == "button"]
        fields = [control for control in controls if control.control_type in {"text", "dropdown", "checkbox"}]
        lists = [control for control in controls if control.control_type in {"list", "tree"}]
        if fields and not lists:
            return {"name": self.name, "type": "form", "area": area,
                    "fields": [control.label for control in fields] + [f"[{control.label}]" for control in buttons]}
        if lists or buttons:
            labels = [control.label for control in lists] or [control.label for control in controls if control.control_type != "button"]
            return {"name": self.name, "type": "list", "area": area, "fields": labels or [self.name],
                    "actions": [control.label for control in buttons]}
        return {"name": self.name, "type": "chrome", "area": area, "dimmed": False}


class DrawioScreen(Screen):
    """A screen on the Site Map and Detailed IA pages, laid out in its column with the CLI layout its own is closest to."""

    @classmethod
    def from_cell(cls, cell: ET.Element, index: int) -> Optional["DrawioScreen"]:
        """The screen a top-level box on the Site Map draws; none for a cell that draws no screen."""
        name = _plain_text(cell.get("value", ""))
        if cell.get("vertex") != "1" or cell.get("parent") != "1" or not name or _is_annotation(name):
            return None
        return cls(name, index)

    def read_regions(self, detailed: ET.Element, region_type: type[DrawioRegion]) -> None:
        """Its regions: the cells inside its own box on the Detailed IA page, the box titled with its name; a region
        drawn twice is read once."""
        boxes = {
            cell.get("id", "")
            for cell in detailed.iter("mxCell")
            if cell.get("vertex") == "1" and cell.get("parent") == "1" and _plain_text(cell.get("value", "")) == self.name
        }
        for cell in detailed.iter("mxCell"):
            if cell.get("parent", "") not in boxes:
                continue
            region = region_type.from_cell(cell, len(self.regions))
            if region is not None and all(held.name != region.name for held in self.regions):
                self.append_region(region)

    def cli_record(self, column: int) -> Dict[str, Any]:
        """This screen in the drawio-ux command line's state, in column."""
        return {
            "name": self.name,
            "layout": _CLI_LAYOUTS.get((self.layout or "").strip().lower(), "stack"),
            "tabOf": self.chrome_of.name if self.chrome_of else None,
            "col": column,
            "row": 0,
            "regions": [region.cli_record() for region in self.regions],
            "stories": self.story_keys,
            "terms": list(self.domain_terms or self.domain_concepts),
        }


class DrawioUxMap(UxMap):
    screen_type = DrawioScreen
    region_type = DrawioRegion
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
        """A new map of this format, read from a draw.io file."""
        try:
            root_element = ET.fromstring(content.strip())
        except ET.ParseError as error:
            raise UnreadableDrawio(f"draw.io content is not valid XML: {error}") from error
        ux_map = type(self).create()
        ux_map.read_pages(root_element)
        return ux_map

    def read_pages(self, root_element: ET.Element) -> None:
        """Read the diagram's pages into this map: its screens from the Site Map page, each screen's regions from the
        Detailed IA page, then the transitions drawn between screens."""
        site_map = _page_named(root_element, "Site Map")
        detailed = _page_named(root_element, "Detailed IA")
        source = site_map if site_map is not None else root_element
        with self.batch_schema_sync():
            screens = self._read_screens(source)
            if detailed is not None:
                for screen in self.screens:
                    screen.read_regions(detailed, self.region_type)
            self._read_transitions(source, screens)

    def _read_screens(self, source: ET.Element) -> dict[str, Screen]:
        """Each screen the page draws, by the id of the cell that draws it."""
        screens: dict[str, Screen] = {}
        for cell in source.iter("mxCell"):
            screen = self.screen_type.from_cell(cell, len(self.screens))
            if screen is not None:
                self.append_screen(screen)
                screens[cell.get("id", "")] = screen
        return screens

    def _read_transitions(self, source: ET.Element, screens: dict[str, Screen]) -> None:
        """Each edge between two screens is a transition; an edge drawn both ways, `there / back`, is two."""
        for cell in source.iter("mxCell"):
            origin, target = screens.get(cell.get("source", "")), screens.get(cell.get("target", ""))
            if cell.get("edge") != "1" or origin is None or target is None:
                continue
            trigger = _plain_text(cell.get("value", "")) or f"{origin.name} -> {target.name}"
            if _BOTH_WAYS not in trigger:
                self._append_transition(trigger, origin, target)
                continue
            there, back = [part.strip() for part in trigger.split(_BOTH_WAYS, 1)]
            self._append_transition(there, origin, target)
            self._append_transition(back, target, origin)

    def _append_transition(self, trigger: str, origin: Screen, target: Screen) -> None:
        self.transitions.append(self.transition_type(trigger, len(self.transitions), origin, target, trigger))

    def render(self, canonical: UxMap) -> str:
        """canonical as Detailed IA + Site Map: copied into a draw.io map with this map's timeout, which draws itself."""
        drawn = self.copy_of(canonical)
        drawn.cli_timeout_seconds = self.cli_timeout_seconds
        return drawn.save()

    def cli_state(self, target: str) -> Dict[str, Any]:
        """This map as the state drawio_ux.mjs writes to target: its screens in columns and its transitions."""
        return {
            "target": target,
            "screens": [screen.cli_record(index) for index, screen in enumerate(self.screens)],
            "connections": [
                {
                    "from": transition.from_screen.name if transition.from_screen else "",
                    "to": transition.to_screen.name if transition.to_screen else "",
                    "label": transition.trigger or transition.name,
                    "dashed": transition.nav_type == "tab",
                }
                for transition in self.transitions
            ],
            "scope": self.scope,
        }

    def save(self) -> str:
        """Draw Detailed IA + Site Map through the vendored drawio-ux CLI."""
        if not _CLI.is_file():
            raise DrawioCliMissing(f"drawio-ux CLI missing: {_CLI}")
        with tempfile.TemporaryDirectory(prefix="ux-drawio-") as folder:
            out_path = Path(folder) / "information-architecture.drawio"
            state_path = JsonFile(Path(folder) / "state.json").write(self.cli_state(str(out_path)))
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


def _is_annotation(name: str) -> bool:
    lower = name.lower()
    return lower.startswith("stories:") or "domain terms:" in lower


def _plain_text(value: str) -> str:
    plain = re.sub(r"<[^>]+>", " ", value or "")
    return html.unescape(re.sub(r"\s+", " ", plain)).strip()


def _page_named(root_element: ET.Element, name: str) -> Optional[ET.Element]:
    return next((diagram for diagram in root_element.findall("diagram") if diagram.get("name") == name), None)
