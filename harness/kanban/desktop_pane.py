"""The Board pane as a person sees it in the running Claude desktop app, measured in physical pixels."""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

_SCRIPT = Path(__file__).with_name("desktop_pane.ps1")
_CARD_MARKS = {"▾", "▴"}
_CARD_REACH = 260


class BoardPaneNotOpen(Exception):
    """Raised when the desktop app is not showing the Board pane."""

    def __init__(self) -> None:
        super().__init__("Open the Board pane in the Claude desktop app before running these specs")


@dataclass(frozen=True)
class PaneElement:
    kind: str
    name: str
    left: int
    top: int
    width: int
    height: int
    is_offscreen: bool

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height


class DesktopPane:
    """Reads the pane through Windows UI Automation, so a spec sees where things truly landed."""

    def __init__(self) -> None:
        self._window_bottom = 0

    @property
    def window_bottom(self) -> int:
        return self._window_bottom

    def elements(self) -> list[PaneElement]:
        """Everything drawn from the board's title rightward, which leaves out the chat beside it."""
        answer = json.loads(self._run("list"))
        self._window_bottom = answer["window_bottom"]
        found = [PaneElement(**element) for element in answer["elements"]]
        titles = [element for element in found if element.name == "BOARD" and element.kind == "Text"]
        if not titles:
            raise BoardPaneNotOpen()
        return [element for element in found if element.left >= titles[0].left - 60 and element.top >= titles[0].top - 40]

    def named(self, name: str) -> list[PaneElement]:
        return [element for element in self.elements() if element.name == name]

    def card_marks(self) -> list[PaneElement]:
        return [element for element in self.elements() if element.kind == "Button" and element.name in _CARD_MARKS]

    def controls_of_card(self, mark: PaneElement) -> list[PaneElement]:
        """The Buttons under a card's mark, down to the next card in its list."""
        elements = self.elements()
        below = [other.top for other in self.card_marks() if abs(other.left - mark.left) < mark.width and other.top > mark.top]
        end = min(below, default=self._window_bottom)
        return [
            element
            for element in elements
            if element.kind == "Button" and element.name not in _CARD_MARKS
            and mark.right - _CARD_REACH < element.left < mark.right and mark.top < element.top < end
        ]

    def press(self, element: PaneElement) -> None:
        self._run("press", "-X", str(element.left), "-Y", str(element.top))

    def colour_at(self, left: int, top: int) -> str:
        return self._run("colour", "-X", str(left), "-Y", str(top)).strip()

    def _run(self, command: str, *arguments: str) -> str:
        finished = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(_SCRIPT), command, *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        return finished.stdout
