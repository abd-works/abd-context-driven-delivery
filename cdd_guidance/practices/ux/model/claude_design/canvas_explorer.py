"""The story explorer a canvas version holds (``project/screens/explorer.dc.html``), read back: the tree it lists, each
story with its scenarios, and the prototype screen each scenario plays. The walk of the canvas's screens and the UX
graph rules read the explorer this way, so both judge what a reader of the published canvas sees."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional

# Where the explorer's template writes its tree, as story_canvas.py renders it.
_TREE_OPENS = "tree() {\nreturn "
EXPLORER_FILE = "screens/explorer.dc.html"


class ExplorerTreeUnreadable(ValueError):
    """The explorer page holds no tree the story canvas wrote, so nothing can be read of what it lists."""

    def __init__(self, page: Path) -> None:
        super().__init__(f"{page} holds no story tree as the story canvas writes it (tree() {{ return [...]; }}); render the canvas again")
        self.page = page


@dataclass(frozen=True)
class ExplorerScenario:
    """One scenario as the explorer lists it under its story: its name, whether it is the story's Background, the
    prototype screen it plays (the artboard's stem, empty when it plays none), its step groups, each the lines the
    reader picks at once, in order, and each group's kind (``when`` where the Customer acts, else ``given`` or
    ``then``)."""

    story: str
    name: str
    background: bool
    screen: str
    groups: tuple = ()
    kinds: tuple = ()
    rows: tuple = ()

    def kind_of(self, index: int) -> str:
        """The kind of the step group at index, empty when the explorer names none."""
        return self.kinds[index] if index < len(self.kinds) else ""

    def played(self) -> List["PlayedScenario"]:
        """The scenarios the explorer plays for this one: an outline's each example row, as the fixtures bundle names
        it (``<outline>: <row>``, or the outline's name with the row's values in its placeholders), with its steps
        reading that row's values; any other scenario as itself."""
        if not self.rows:
            return [PlayedScenario(self, self.name, self.groups)]
        return [PlayedScenario(self, self._row_name(row, values), tuple(filled(group, values) for group in self.groups))
                for row, values in self.rows]

    def _row_name(self, row: str, values: dict) -> str:
        return filled(self.name, values) if _PLACEHOLDER.search(self.name) else f"{self.name}: {row}"


@dataclass(frozen=True)
class PlayedScenario:
    """One scenario the explorer plays on a screen: the scenario it lists (*listed*), the name the screen loads it by,
    and its step groups as the reader sees them."""

    listed: ExplorerScenario
    name: str
    groups: tuple


# A placeholder an outline's steps name a column of its Examples table by: {column}, ${column} or <column>.
_PLACEHOLDER = re.compile(r"\$\{([^}]+)\}|\{([^}]+)\}|<([^>]+)>")


def filled(text: str, values: dict) -> str:
    """text with each placeholder that names a column of values read as that column's value."""
    def value(match: re.Match) -> str:
        column = next(part for part in match.groups() if part is not None).strip()
        return str(values[column]) if column in values else match.group(0)
    return _PLACEHOLDER.sub(value, text)


class CanvasExplorer:
    """The explorer page of one canvas version's project folder."""

    def __init__(self, project: Path) -> None:
        self.project = Path(project)

    @property
    def page(self) -> Path:
        return self.project / EXPLORER_FILE

    def exists(self) -> bool:
        return self.page.is_file()

    def tree(self) -> list:
        """The tree the page lists: epics, each with its sub-epics (``e``), nested as deep as the story map nests
        them, and the stories directly under it (``s``), each story's scenarios (``c``)."""
        text = self.page.read_text(encoding="utf-8")
        start = text.find(_TREE_OPENS)
        if start < 0:
            raise ExplorerTreeUnreadable(self.page)
        try:
            tree, _ = json.JSONDecoder().raw_decode(text, start + len(_TREE_OPENS))
        except json.JSONDecodeError as refused:
            raise ExplorerTreeUnreadable(self.page) from refused
        return tree

    def stories(self) -> Iterator[tuple[str, List[ExplorerScenario]]]:
        """Each story the tree lists, in its order, with the scenarios listed under it."""
        for epic in self.tree():
            for story in _stories_under(epic):
                yield story["n"], [ExplorerScenario(story["n"], scenario["n"], bool(scenario.get("b")), scenario.get("p", ""),
                                                    tuple(group["x"] for group in scenario.get("t", [])),
                                                    tuple(group.get("k", "") for group in scenario.get("t", [])),
                                                    tuple(scenario.get("r", {}).items()))
                                   for scenario in story.get("c", [])]

    def scenarios(self) -> Iterator[ExplorerScenario]:
        """Each scenario the tree lists, Backgrounds left out, in the tree's order."""
        for _, scenarios in self.stories():
            yield from (scenario for scenario in scenarios if not scenario.background)

    def artboard_of(self, scenario: ExplorerScenario) -> Optional[Path]:
        """The artboard the explorer plays for scenario, beside the explorer page; none when it plays no screen."""
        return self.page.parent / f"{scenario.screen}.dc.html" if scenario.screen else None


def _stories_under(epic: dict) -> Iterator[dict]:
    """The stories under an epic of the tree, in its order: its sub-epics' (``e``), as deep as they nest, then its own
    (``s``)."""
    for sub in epic.get("e", []):
        yield from _stories_under(sub)
    yield from epic.get("s", [])
