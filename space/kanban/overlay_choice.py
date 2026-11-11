"""The pattern overlays a session can choose, as the chat bar offers them."""

from __future__ import annotations

from harness.installation.data_class import data_field


class OverlayChoice:
    """*OverlayChoice* is one pattern a person can overlay on a session's graph: its name, the icon the chat bar shows
    for it, and whether the session has chosen it."""

    def __init__(self, pattern: str, is_chosen: bool) -> None:
        self._pattern = pattern
        self._is_chosen = is_chosen

    @property
    @data_field
    def pattern(self) -> str:
        """The pattern's name, its folder under cdd_guidance/patterns, such as lern_domain_driven."""
        return self._pattern

    @property
    @data_field
    def icon(self) -> str:
        """The pattern's first and last letter in capitals: LN for lern_domain_driven."""
        return f"{self._pattern[:1]}{self._pattern[-1:]}".upper()

    @property
    @data_field
    def is_chosen(self) -> bool:
        """Whether the session overlays this pattern on its graph."""
        return self._is_chosen
