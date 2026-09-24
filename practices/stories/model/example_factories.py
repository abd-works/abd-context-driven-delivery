"""ExampleFactory names collected from an Epic and its nested SubEpics."""

from __future__ import annotations

from typing import List

from practices.stories.model.nodes import Epic


class ExampleFactories:
    def normalize_factory_name(self, name: str) -> str:
        return Epic("Example factories", 1).normalize_factory_name(name)

    def collect(self, epic: Epic) -> List[str]:
        return epic.collected_example_factories()
