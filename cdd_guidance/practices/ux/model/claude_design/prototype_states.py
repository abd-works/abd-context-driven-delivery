"""The positions a prototype-state file keeps for each story's screen (*PrototypeStates*).

A project that ports a Claude Design prototype keeps, for each UX-map screen by its slug, the prototype's settings
that open it at that story's state, and under ``scenarios`` one state per step group the story explorer lists for each
scenario::

    {"view-cart": {"start": "catalog", "demoCartOpen": true,
                   "scenarios": {"View the cart": [{"start": "catalog"}, {"start": "catalog", "demoCartOpen": true}]}}}

A screen takes only where it is from those settings (``position-is-not-data``): the settings that hold data, such as
the plans a demo cart starts with, are named by the project and left out, because the scenario's bound domain objects
give those values. Entries that are not a screen's state, such as a note on the file, are passed over.

See ``story_canvas.md`` beside this file, *Prototype screens*."""

from __future__ import annotations

import dataclasses
import json
from functools import cached_property
from pathlib import Path
from typing import Collection, Optional

from cdd_guidance.practices.ux.model.claude_design.story_screen import StoryScreen

SCENARIOS = "scenarios"


class PrototypeStatesUnreadable(ValueError):
    """The prototype-state file is not JSON, so no screen can be placed from it."""


class PrototypeStates:
    """A prototype-state *file* and the *data_settings* its states hold that are data, not position."""

    def __init__(self, file: Path, data_settings: Collection[str]) -> None:
        self.file = Path(file)
        self.data_settings = frozenset(data_settings)

    @cached_property
    def states(self) -> dict[str, dict]:
        """Each screen's state, by slug."""
        try:
            document = json.loads(self.file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as unreadable:
            raise PrototypeStatesUnreadable(f"{self.file} is not JSON: {unreadable}") from unreadable
        return {slug: state for slug, state in document.items() if isinstance(state, dict)}

    def story_position(self, slug: str) -> Optional[dict]:
        """Where the screen of slug opens for its story, without its scenarios or data settings; None when the file
        keeps no state for slug."""
        state = self.states.get(slug)
        if state is None:
            return None
        return self._placed({name: value for name, value in state.items() if name != SCENARIOS})

    def positions(self, slug: str) -> dict[str, list[dict]]:
        """Each scenario's positions for the screen of slug, one per step group, without data settings."""
        scenarios = (self.states.get(slug) or {}).get(SCENARIOS, {})
        return {scenario: [self._placed(group) for group in groups] for scenario, groups in scenarios.items()}

    def story_screens(self, ux_map_file: Path, screen: StoryScreen) -> dict[str, StoryScreen]:
        """A StoryScreen, by slug, for each screen of the UX map at ux_map_file that the file keeps a state for: screen,
        as the project configures every one (its markup, named input, root class), titled from its slug, showing the
        first story the UX map names for it (else its slug), placed at the file's positions, with its own artboard."""
        records = json.loads(Path(ux_map_file).read_text(encoding="utf-8")).get("screens", [])
        found = {}
        for record in records:
            slug = record.get("slug") or record.get("name")
            if slug not in self.states:
                continue
            found[slug] = dataclasses.replace(
                screen, title=slug.replace("-", " ").title(), story=self._story_of(record, slug),
                positions=self.positions(slug), story_position=self.story_position(slug), artboard=f"/screens/{slug}.dc.html")
        return found

    def _story_of(self, record: dict, slug: str) -> str:
        """The first story the UX-map record names, without the link a story map writes around it."""
        names = record.get("story_names") or []
        return names[0].split("](")[0].lstrip("[") if names else slug

    def _placed(self, settings: dict) -> dict:
        return {name: value for name, value in settings.items() if name not in self.data_settings}
