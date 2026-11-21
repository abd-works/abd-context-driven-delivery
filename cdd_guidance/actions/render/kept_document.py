"""A document or a drawing rendered onto one that is already there: what only the file held stays in it.

A format's adapter is handed the file as it was (``previous``) and keeps what it knows how to keep: a drawing's layout,
a document's own words. What it does not keep would be lost when the render is saved, so the Render action puts it back
before it writes the file, whatever the adapter did:

- **Markdown**: each line of the file that carried content and is nowhere in the rendered document is kept below the
  document, under a heading saying it is no longer in the model, in the order the file had it.
- **A draw.io drawing**: each cell the file drew that the render does not is added back to the drawing as it was, and a
  cell both draw keeps the place the file gave it, since people lay a drawing out by hand.
- **A whiteboard**: the same, for its elements.

A drawing rendered with fewer than half of the file's cells was written by a format that names its cells anew on every render;
adding the file's cells would draw everything twice, so that drawing is saved as rendered and its format has to keep
its own cells.

What is kept this way is named in the result, for whoever decides where it belongs: a note a person added stays, and
a card whose thing the model no longer holds is deleted from the drawing by hand.
"""

from __future__ import annotations

import copy
import json
import xml.etree.ElementTree as ET

from harness.guidance.practice_formats import Reshaped
from harness.markdown.format import Format

NO_LONGER_IN_MODEL = "no longer in the model"
_HEADING = f"## Kept from this file, {NO_LONGER_IN_MODEL}"
_HEADING_NOTE = "The lines below were in this file and the render did not write them. Move each to where it belongs, then delete it from here."
# The two cells every draw.io page holds, which no one draws.
_PAGE_CELLS = frozenset({"0", "1"})
_PLACE = ("x", "y")


class KeptDocument:
    """One format's way to keep, in a rendered document or drawing, what only the file already there held."""

    def __init__(self, format: Format) -> None:
        self._format = format

    def onto(self, existing: str, rendered: str) -> Reshaped:
        """rendered with what only existing held put back, and what was put back named; rendered itself, untouched,
        when existing held nothing more, or when existing is empty or cannot be read as the format."""
        if not existing.strip():
            return Reshaped(rendered, [], [])
        if self._format.name == "markdown":
            return self._markdown(existing, rendered)
        try:
            return self._drawio(existing, rendered) if self._format.name == "drawio" else self._whiteboard(existing, rendered)
        except (ET.ParseError, json.JSONDecodeError, KeyError, TypeError):
            return Reshaped(rendered, [], [])

    def _markdown(self, existing: str, rendered: str) -> Reshaped:
        lines = existing.splitlines()
        marked = next((index for index, line in enumerate(lines) if line.strip() == _HEADING), len(lines))
        carried = [line for line in lines[marked + 1:] if line.strip() and line.strip() != _HEADING_NOTE]
        written = rendered.splitlines()
        unplaced = [line for line in lines[:marked] if line.strip() and not any(line.strip() in held for held in written)]
        apart = [line for line in [*carried, *unplaced] if not any(line.strip() in held for held in written)]
        if not apart:
            return Reshaped(rendered, [], [])
        below = "\n\n".join(apart)
        text = f"{rendered.rstrip(chr(10))}\n\n{_HEADING}\n\n{_HEADING_NOTE}\n\n{below}\n"
        return Reshaped(text, [f"{len(apart)} line(s) set apart"], [])

    def _drawio(self, existing: str, rendered: str) -> Reshaped:
        before, after = ET.fromstring(existing), ET.fromstring(rendered)
        old_root, new_root = before.find(".//root"), after.find(".//root")
        drawn = {cell.get("id"): cell for cell in new_root if cell.get("id")}
        held = {cell.get("id"): cell for cell in old_root if cell.get("id") and cell.get("id") not in _PAGE_CELLS}
        if not self._are_mostly_drawn(held, drawn):
            return Reshaped(rendered, [], [])
        only_in_file = [cell for name, cell in held.items() if name not in drawn]
        moved = [self._placed_as(cell, drawn[name]) for name, cell in held.items() if name in drawn]
        if not only_in_file and not any(moved):
            return Reshaped(rendered, [], [])
        new_root.extend(copy.deepcopy(cell) for cell in only_in_file)
        kept = [f"{cell.get('id')} '{cell.get('value') or cell.get('label') or ''}'" for cell in only_in_file]
        return Reshaped(ET.tostring(after, encoding="unicode"), kept, [])

    def _are_mostly_drawn(self, held: dict, drawn: dict) -> bool:
        """Whether the render drew at least half of what the file holds under the names the file gives it: a format that
        keeps its names. One that names its cells anew draws few or none of them, and is left as rendered."""
        return bool(held) and 2 * sum(1 for name in held if name in drawn) >= len(held)

    def _placed_as(self, held: ET.Element, drawn: ET.Element) -> bool:
        """Give the drawn cell the place the file's cell has; true when that moved it."""
        was, now = held.find(".//mxGeometry") if held.tag != "mxGeometry" else held, drawn.find(".//mxGeometry")
        if was is None or now is None or all(was.get(side) == now.get(side) for side in _PLACE):
            return False
        for side in (side for side in _PLACE if was.get(side) is not None):
            now.set(side, was.get(side))
        return True

    def _whiteboard(self, existing: str, rendered: str) -> Reshaped:
        before, after = json.loads(existing), json.loads(rendered)
        held, drawn = before["elements"], after["elements"]
        if not self._are_mostly_drawn(held, drawn):
            return Reshaped(rendered, [], [])
        only_in_file = [name for name in before.get("order", list(held)) if name in held and name not in drawn]
        moved = [name for name in held if name in drawn and any(held[name].get(side) != drawn[name].get(side) for side in _PLACE if side in held[name])]
        if not only_in_file and not moved:
            return Reshaped(rendered, [], [])
        for name in moved:
            drawn[name].update({side: held[name][side] for side in _PLACE if side in held[name]})
        drawn.update({name: held[name] for name in only_in_file})
        after["order"] = [*after.get("order", []), *only_in_file]
        kept = [f"{name} '{held[name].get('text', '')}'" for name in only_in_file]
        return Reshaped(json.dumps(after), kept, [])
