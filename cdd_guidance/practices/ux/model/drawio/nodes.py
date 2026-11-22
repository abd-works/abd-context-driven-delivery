"""Draw.io channel - IA via drawio-ux CLI (Detailed IA + Site Map).

Render copies the UxMap into a DrawioUxMap, whose screens and regions spell their own part of the drawio-ux
command line's state, and invokes `drawio_ux.mjs write`.
Parse prefers the Site Map page for screens/transitions; each screen's layout, regions, controls, stories, and
domain terms come from the Detailed IA page when present. The diagram shows screens, their regions, the labels of the
controls a region holds, transitions, and, in the callout under each screen, the stories, scenarios, and steps the
screen and each of its controls serve, each a link to where it is written when it has one, with the screen's domain
terms; beside what it shows it keeps, as
style keys on its cells (``uxLayout``, ``uxArea``, ``uxControls``, ``uxNav``), a screen's layout, a region's area, each
control's type, and a transition's kind of navigation, so a drawing reads back what was drawn. A control's states and
interactions, descriptions, content types, nav components, and the map's name are not drawn.
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
from cdd_guidance.practices.ux.model.nodes import Control, Region, Screen, ServesStories, Transition
from cdd_guidance.practices.stories.model.story_tree import KEY_SEPARATOR
from cdd_guidance.practices.ux.model.story_link import StoryLink
from cdd_guidance.practices.ux.model.ux_map import UxMap
from harness.drawio import CellStyle, DrawioCell, DrawioFile, UnreadableDrawio
from harness.guidance.practice_formats import Written

_CLI = Path(__file__).with_name("drawio_ux.mjs")
# Writing a two-page diagram takes well under a second; a write still running after this has hung.
_CLI_TIMEOUT_SECONDS = 60
# A Site Map edge drawn both ways carries both triggers in one label, "there / back".
_BOTH_WAYS = " / "
# What joins the labels one cell shows: a row's controls, an action strip's buttons, a callout's stories.
_BESIDE = " · "
# The style keys the drawing keeps for its reader beside what it shows.
_LAYOUT_KEY, _AREA_KEY, _CONTROLS_KEY, _NAV_KEY = "uxLayout", "uxArea", "uxControls", "uxNav"
# The control types the command line draws as a form's rows, and as a list's.
_FORM_TYPES = frozenset({"text", "dropdown", "checkbox"})
_LIST_TYPES = frozenset({"list", "tree"})
_BUTTON = "button"
# The kind of navigation a transition has when its edge says no other.
_ACTION = "action"
# The fill the command line gives a region's action strip.
_ACTION_STRIP_FILL = "#f0f0f0"
_TERMS = "domain terms:"
# The heading a callout line lists each kind of thing served under, in the order the callout lists them.
_SERVED_HEADINGS = {"stories": "Story", "scenarios": "Scenario", "steps": "Step"}
# A callout line that lists what one control serves: `Add To Cart › Quantity serves steps: ...`.
_CONTROL_LINE = re.compile(r"^(?P<by>.+?) serves (?P<kind>stories|scenarios|steps):\s*(?P<items>.*)$", re.IGNORECASE)
# A link as a cell's label draws it, which reads back as the markdown link the other formats write.
_ANCHOR = re.compile(r"<a\s+href=\"(?P<target>[^\"]*)\"[^>]*>(?P<text>.*?)</a>", re.IGNORECASE)
# What a draw.io file holds when it is a UX map: the command line's own mark, or one of the two pages it draws.
_UX_DRAWING_MARKS = ('host="drawio-ux"', 'name="Site Map"', 'name="Detailed IA"')
_LINE_BREAK = re.compile(r"<br\s*/?>")


class DrawioCliMissing(FileNotFoundError):
    """The vendored drawio-ux command line is not beside this module, so no diagram can be written."""


class DrawioCliFailed(RuntimeError):
    """The drawio-ux command line exited with an error or wrote no diagram."""


class DrawioCliTimedOut(DrawioCliFailed):
    """The drawio-ux command line ran past its timeout and was stopped."""


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


class UxCellStyle(CellStyle):
    """One cell's draw.io style as the UX map reads it: what a cell of a mockup draws, from the keys its style holds,
    such as ``strokeColor=none;uxArea=panel;``, and where the cell is drawn."""

    def __init__(self, cell: ET.Element) -> None:
        super().__init__(cell.get("style", ""))
        self._cell = DrawioCell(cell)

    @property
    def is_action_strip(self) -> bool:
        return self.value("fillColor") == _ACTION_STRIP_FILL

    @property
    def draws_controls(self) -> bool:
        """Whether the cell shows a region's controls, not a region: it names their types, it is an unframed row, or
        it is the grey action strip."""
        return _CONTROLS_KEY in self or self.value("strokeColor") == "none" or self.is_action_strip

    @property
    def control_types(self) -> list[str]:
        """The type of each control the cell shows, in the order it shows them; none for a cell that keeps none."""
        return self.value(_CONTROLS_KEY).split(",") if _CONTROLS_KEY in self else []

    @property
    def corner(self) -> tuple[float, float]:
        """Where the cell's top left corner is drawn; the page's own corner for a cell with no geometry."""
        box = self._cell.box
        return (box.x, box.y) if box is not None else (0.0, 0.0)


class DrawnServed(ServesStories):
    """What a screen or a control serves as the callout draws it: each story, scenario, and step a link to where it is
    written when it has a target, else its key."""

    def drawn(self, kind: str) -> list[str]:
        """The label markup of each thing of kind this node serves."""
        return [self._markup(link) for link in self.links_of(kind)]

    def serve_listed(self, kind: str, items: str) -> None:
        """Serve each thing of kind a callout line lists in items."""
        for item in (item.strip() for item in items.split(_BESIDE)):
            if item:
                self._show(kind, item)

    def _markup(self, link: StoryLink) -> str:
        text = html.escape(link.key, quote=False)
        return f'<a href="{html.escape(link.target)}">{text}</a>' if link.target else text


class DrawioControl(Control, DrawnServed):
    """A control as the Detailed IA page shows it: its label, in a row of its region or on the region's action strip,
    and what it serves, in the callout under its screen."""

    @classmethod
    def from_cell(cls, cell: ET.Element) -> list["DrawioControl"]:
        """The controls one cell shows, each with the type the cell keeps for it. Where the cell keeps none, a control
        on an action strip, or one a form shows in brackets as ``[Pay]``, is a button."""
        style = UxCellStyle(cell)
        labels = [label.strip() for label in _plain_text(cell.get("value", "")).split(_BESIDE) if label.strip()]
        kinds = style.control_types
        controls = []
        for index, label in enumerate(labels):
            kind = kinds[index] if index < len(kinds) else (_BUTTON if style.is_action_strip else "")
            if label.startswith("[") and label.endswith("]") and kind in ("", _BUTTON):
                label, kind = label[1:-1].strip(), _BUTTON
            control = cls(label, index)
            control.control_type = kind
            controls.append(control)
        return controls

    @property
    def row_label(self) -> str:
        """What a form's row shows for this control: a button in brackets."""
        return f"[{self.label}]" if self.control_type == _BUTTON else self.label


class DrawioRegion(Region):
    """A region on the Detailed IA page: a form, a list with its actions, or chrome, by the controls it holds."""

    @classmethod
    def from_cell(cls, cell: ET.Element, index: int) -> Optional["DrawioRegion"]:
        """The region a cell inside a screen's box draws; none for a cell that draws no region (a cell that shows
        controls, an annotation, or one with no text)."""
        name = _plain_text(cell.get("value", ""))
        style = UxCellStyle(cell)
        if cell.get("vertex") != "1" or style.draws_controls or not name or _is_annotation(name):
            return None
        region = cls(name, index)
        region.area = style.value(_AREA_KEY)
        return region

    def read_controls(self, cell: ET.Element, control_type: type[DrawioControl]) -> None:
        """Take the controls cell shows, each once, since a list's row is drawn twice. Its buttons come after its other
        controls, as the drawing shows them apart."""
        shown = [control for control in control_type.from_cell(cell) if all(held.name != control.name for held in self.controls)]
        ordered = sorted([*self.controls, *shown], key=lambda control: control.control_type == _BUTTON)
        self.controls.refill(ordered)
        self._renumber(self.controls)

    def cli_record(self) -> Dict[str, Any]:
        """This region in the drawio-ux command line's state: every control it holds is shown, a form's one to a row,
        a list's in its rows with its buttons on the action strip, each with its type kept beside it."""
        record = {"name": self.name, "area": self.area or "body", "uxArea": self.area}
        controls = list(self.controls)
        if not controls:
            return {**record, "type": "chrome", "dimmed": False}
        buttons = [control for control in controls if control.control_type == _BUTTON]
        shown = [control for control in controls if control.control_type != _BUTTON]
        kinds = {control.control_type for control in shown}
        if kinds & _FORM_TYPES and not kinds & _LIST_TYPES:
            rows = shown + buttons
            return {**record, "type": "form", "fields": [control.row_label for control in rows],
                    "fieldKinds": [control.control_type for control in rows]}
        return {**record, "type": "list", "fields": [control.label for control in shown],
                "fieldKinds": [control.control_type for control in shown],
                "actions": [control.label for control in buttons]}


class DrawioScreen(Screen, DrawnServed):
    """A screen on the Site Map and Detailed IA pages, laid out in its column with the CLI layout its own is closest to."""

    @classmethod
    def from_cell(cls, cell: ET.Element, index: int) -> Optional["DrawioScreen"]:
        """The screen a top-level box on the Site Map draws; none for a cell that draws no screen."""
        name = _plain_text(cell.get("value", ""))
        if cell.get("vertex") != "1" or cell.get("parent") != "1" or not name or _is_annotation(name):
            return None
        return cls(name, index)

    def read_detail(self, detailed: ET.Element, ux_map: "DrawioUxMap") -> None:
        """What the Detailed IA page draws of this screen, in the box titled with its name: its layout, its regions
        with the controls each shows, and the stories and domain terms in the callout under the box. Its regions and
        controls are made of ux_map's node types."""
        boxes = [
            cell
            for cell in detailed.iter("mxCell")
            if cell.get("vertex") == "1" and cell.get("parent") == "1" and _plain_text(cell.get("value", "")) == self.name
        ]
        if not boxes:
            return
        self.layout = UxCellStyle(boxes[0]).value(_LAYOUT_KEY)
        self._read_regions(detailed, {box.get("id", "") for box in boxes}, ux_map)
        callout = Callout.under(boxes[0], detailed)
        if callout is not None:
            callout.annotate(self)

    def _read_regions(self, detailed: ET.Element, boxes: set[str], ux_map: "DrawioUxMap") -> None:
        """Its regions, the framed cells inside its boxes, each with the controls the cells after it show; a region
        drawn twice is read once."""
        region: Optional[DrawioRegion] = None
        for cell in detailed.iter("mxCell"):
            if cell.get("parent", "") not in boxes:
                continue
            if UxCellStyle(cell).draws_controls:
                if region is not None:
                    region.read_controls(cell, ux_map.control_type)
                continue
            found = ux_map.region_type.from_cell(cell, len(self.regions))
            if found is None:
                continue
            region = next((held for held in self.regions if held.name == found.name), None)
            if region is None:
                region = found
                self.append_region(region)

    def cli_record(self, column: int) -> Dict[str, Any]:
        """This screen in the drawio-ux command line's state, in column."""
        return {
            "name": self.name,
            "layout": _CLI_LAYOUTS.get((self.layout or "").strip().lower(), "stack"),
            "uxLayout": self.layout,
            "tabOf": self.chrome_of.name if self.chrome_of else None,
            "col": column,
            "row": 0,
            "regions": [region.cli_record() for region in self.regions],
            "stories": self.drawn("Story"),
            "scenarios": self.drawn("Scenario"),
            "steps": self.drawn("Step"),
            "terms": list(self.domain_terms or self.domain_concepts),
            "served": self._served_by_controls(),
        }

    def _served_by_controls(self) -> list[Dict[str, Any]]:
        """One callout line for each kind of thing each control serves, under the control's region and name."""
        return [
            {"by": f"{region.name}{KEY_SEPARATOR}{control.name}", "kind": heading, "items": control.drawn(kind)}
            for region in self.regions
            for control in region.controls
            for heading, kind in _SERVED_HEADINGS.items()
            if control.links_of(kind)
        ]

    def control_at(self, place: str) -> Optional[Control]:
        """The control a callout line names by its region and its own name, `Add To Cart › Quantity`."""
        return next(
            (control for region in self.regions for control in region.controls
             if f"{region.name}{KEY_SEPARATOR}{control.name}" == place),
            None,
        )


class Callout:
    """The note the Detailed IA page draws under a screen: the stories, scenarios, and steps the screen serves and the
    domain terms it names, one line each, then a line for each kind of thing each of its controls serves."""

    def __init__(self, cell: ET.Element) -> None:
        self._lines = [_plain_text(_ANCHOR.sub(r"[\g<text>](\g<target>)", line)) for line in _LINE_BREAK.split(cell.get("value", ""))]

    @classmethod
    def under(cls, box: ET.Element, detailed: ET.Element) -> Optional["Callout"]:
        """The callout drawn under box: the annotation whose left edge is the box's, nearest below the box's top; none
        when the page draws none there."""
        left, top = UxCellStyle(box).corner
        below = [
            (UxCellStyle(cell).corner[1], order, cell)
            for order, cell in enumerate(detailed.iter("mxCell"))
            if cell.get("vertex") == "1" and cell.get("parent") == "1" and _is_annotation(_plain_text(cell.get("value", "")))
            and UxCellStyle(cell).corner[0] == left and UxCellStyle(cell).corner[1] >= top
        ]
        return cls(min(below, key=lambda found: found[:2])[2]) if below else None

    def annotate(self, screen: "DrawioScreen") -> None:
        """Give screen each story, scenario, and step the callout lists for it, attach each domain term it lists, and
        give each control of screen what its own lines list."""
        for heading, kind in _SERVED_HEADINGS.items():
            screen.serve_listed(kind, self._listed(f"{heading}:"))
        for term in self._listed(_TERMS).split(_BESIDE):
            screen.attach_domain_term(term.strip())
        for line in self._lines:
            served = _CONTROL_LINE.match(line)
            control = screen.control_at(served.group("by").strip()) if served is not None else None
            if isinstance(control, DrawnServed):
                control.serve_listed(_SERVED_HEADINGS[served.group("kind").lower()], served.group("items"))

    def _listed(self, heading: str) -> str:
        """What the line that starts with heading lists after it; nothing when the callout has no such line."""
        line = next((line for line in self._lines if line.lower().startswith(heading)), "")
        return line[len(heading):]


class DrawioUxMap(UxMap):
    screen_type = DrawioScreen
    region_type = DrawioRegion
    control_type = DrawioControl
    cli_timeout_seconds: float = _CLI_TIMEOUT_SECONDS
    map_file_suffixes = (".drawio",)
    not_a_map_failures = (UnreadableDrawio,)

    def reads_file(self, file: Path, text: str) -> bool:
        """A drawing the drawio-ux command line wrote, or one that has its Site Map or Detailed IA page; any other
        drawing is another practice's, such as a story map."""
        return any(mark in text for mark in _UX_DRAWING_MARKS)

    def parse(self, text: str, file: str = "") -> UxMap:
        """A new map of this format, read from a draw.io file."""
        ux_map = type(self).create()
        ux_map._read_pages(DrawioFile.from_text(text))
        return ux_map

    def _read_pages(self, drawing: DrawioFile) -> None:
        """Read the diagram's pages into this map: its screens from the Site Map page, what the Detailed IA page draws
        of each screen (its layout, regions, controls, stories, and domain terms), then the transitions drawn between
        screens."""
        site_map = drawing.page("Site Map")
        detailed = drawing.page("Detailed IA")
        source = (site_map or drawing.whole).element
        with self.batch_schema_sync():
            screens = self._read_screens(source)
            if detailed is not None:
                for screen in self.screens:
                    screen.read_detail(detailed.element, self)
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
            nav_type = self._nav_type_of(cell)
            if _BOTH_WAYS not in trigger:
                self._append_transition(trigger, origin, target).nav_type = nav_type
                continue
            there, back = [part.strip() for part in trigger.split(_BOTH_WAYS, 1)]
            self._append_transition(there, origin, target).nav_type = nav_type
            self._append_transition(back, target, origin).nav_type = nav_type

    def _nav_type_of(self, edge: ET.Element) -> str:
        """The kind of navigation an edge draws: the one it keeps, else a tab for a dashed line, else an action, the
        kind a transition is made with."""
        style = UxCellStyle(edge)
        return style.value(_NAV_KEY) or ("tab" if style.value("dashed") == "1" else _ACTION)

    def _append_transition(self, trigger: str, origin: Screen, target: Screen) -> Transition:
        transition = self.transition_type(trigger, len(self.transitions)).joining(origin, target)
        self.transitions.append(transition)
        return transition

    def render(self, canonical: UxMap, written: Written = Written()) -> str:
        """canonical as Detailed IA + Site Map: copied into a draw.io map with this map's timeout, which draws itself.
        previous is the drawing as it is now: a source that holds no screen, such as the UX context file, has nothing
        to draw, so a drawing that holds screens stays as it is rather than being written over with an empty one. A
        drawing that holds what canonical does not (a screen, a region, a control, a transition, a story or a domain
        term a person drew) keeps it: the drawing is laid out again, and nothing it showed is left out."""
        previous = written.previous
        held = self.parse(previous) if previous else None
        if held is not None and not canonical.screens and held.screens:
            return previous

        drawn = self.copy_of(canonical)
        if held is not None:
            drawn.keep_what_only(held)
        drawn.cli_timeout_seconds = self.cli_timeout_seconds
        return drawn.save()

    def _cli_state(self, target: str) -> Dict[str, Any]:
        """This map as the state drawio_ux.mjs writes to target: its screens in columns and its transitions."""
        return {
            "target": target,
            "screens": [screen.cli_record(index) for index, screen in enumerate(self.screens)],
            "connections": [
                {
                    "from": transition.from_name,
                    "to": transition.to_name,
                    "label": transition.trigger or transition.name,
                    "dashed": transition.nav_type == "tab",
                    "navType": transition.nav_type,
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
            state_path = JsonFile(Path(folder) / "state.json").write(self._cli_state(str(out_path)))
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
    """Whether a cell's text is a callout's: it starts with what a screen serves, or lists domain terms or what a
    control serves."""
    lower = name.lower()
    starts = any(lower.startswith(f"{heading}:") for heading in _SERVED_HEADINGS)
    return starts or _TERMS in lower or any(f" serves {heading}:" in lower for heading in _SERVED_HEADINGS)



def _plain_text(markup: str) -> str:
    plain = re.sub(r"<[^>]+>", " ", markup or "")
    return html.unescape(re.sub(r"\s+", " ", plain)).strip()
