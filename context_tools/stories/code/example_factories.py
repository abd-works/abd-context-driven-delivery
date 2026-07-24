"""Shared domain helpers — collect ExampleFactory names from the story graph.

Epic / SubEpic may declare ``example_factories`` (e.g. ``CartExampleFactory``).
Language emitters live next to each converter:
``code/python/``, ``code/javascript/``, ``document/markdown/``.
"""

from __future__ import annotations

import re
from typing import Iterable, List

from context_tools.stories.story_model.nodes import Epic, SubEpic

_FACTORY_NAME = re.compile(r"^[A-Z][A-Za-z0-9]*ExampleFactory$")


def normalize_factory_name(name: str) -> str:
    """Ensure PascalCase …ExampleFactory (accepts Cart or CartExampleFactory)."""
    raw = (name or "").strip()
    if not raw:
        return ""
    if raw.endswith("ExampleFactory"):
        return raw
    return f"{raw}ExampleFactory"


def collect_example_factories(epic: Epic) -> List[str]:
    """Epic factories + nested SubEpic factories + *ExampleFactory domain_concepts."""
    names: list[str] = []
    seen: set[str] = set()

    def _add(raw: str) -> None:
        name = normalize_factory_name(raw)
        if not name or name in seen:
            return
        if not _FACTORY_NAME.match(name):
            return
        seen.add(name)
        names.append(name)

    for raw in getattr(epic, "example_factories", None) or []:
        _add(raw)
    for concept in getattr(epic, "domain_concepts", None) or []:
        if str(concept).endswith("ExampleFactory"):
            _add(str(concept))

    def _walk(subs: Iterable[SubEpic]) -> None:
        for sub in subs or []:
            for raw in getattr(sub, "example_factories", None) or []:
                _add(raw)
            for concept in getattr(sub, "domain_concepts", None) or []:
                if str(concept).endswith("ExampleFactory"):
                    _add(str(concept))
            _walk(getattr(sub, "sub_epics", None) or [])

    _walk(getattr(epic, "sub_epics", None) or [])
    return names
