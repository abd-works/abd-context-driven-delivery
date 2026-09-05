"""Typed return value for ``render_*`` operations across backends."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RenderSummary:
    """Summary of a diagram render operation.

    Backends return this from outline / exploration / increments renders.
    Dict-style access is preserved for backward compatibility with callers
    that historically destructured a plain dictionary.
    """

    epics: int
    sub_epic_count: int
    diagram_generated: bool
    story_count: int = 0
    increments: Optional[int] = None
    ac_count: Optional[int] = None
    exploration: bool = False

    _KEYS = (
        'epics', 'sub_epic_count', 'diagram_generated', 'story_count',
        'increments', 'ac_count', 'exploration',
    )

    def __getitem__(self, key: str):
        if key in self._KEYS:
            return getattr(self, key)
        raise KeyError(f"'{key}' not found in RenderSummary")

    def __setitem__(self, key: str, value) -> None:
        if key in self._KEYS:
            setattr(self, key, value)
            return
        raise KeyError(f"Cannot set '{key}' in RenderSummary")

    def get(self, key: str, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key: str) -> bool:
        return key in self._KEYS

    def __eq__(self, other) -> bool:
        if isinstance(other, dict):
            return self.to_dict() == other
        return super().__eq__(other)

    def to_dict(self) -> dict:
        result = {
            'epics': self.epics,
            'sub_epic_count': self.sub_epic_count,
            'diagram_generated': self.diagram_generated,
        }
        if self.story_count > 0:
            result['story_count'] = self.story_count
        if self.increments is not None:
            result['increments'] = self.increments
        if self.ac_count is not None:
            result['ac_count'] = self.ac_count
        if self.exploration:
            result['exploration'] = True
        return result
