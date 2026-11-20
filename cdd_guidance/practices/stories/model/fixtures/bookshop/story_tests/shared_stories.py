"""SharedStories. The scenarios a sub-epic's Python tiers replay, each registered by its story and scenario name."""

from __future__ import annotations


class SharedStories:
    def __init__(self, sub_epic: str) -> None:
        self.sub_epic = sub_epic
        self.scenarios: dict[tuple[str, str], object] = {}

    def scenario(self, story: str, name: str):
        def register(build):
            self.scenarios[(story, name)] = build
            return build

        return register
