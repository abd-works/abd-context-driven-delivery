"""The settings block at the top of a template or example file, as the catalog reads it."""
from __future__ import annotations

import re

_YAML_FENCE = "---"
_COMMENT_FENCES = ("# ---", "#---")
_HEADING = re.compile(r"^#{1,6}\s", re.MULTILINE)


class FrontMatter:
    """The settings at the top of a file: a YAML block between ``---`` lines, or, in a code template, the same block
    written as ``# ---`` comment lines. The catalog reads a template's settings to match it to a fidelity, and drops an
    example's settings before showing the example."""

    def __init__(self, text: str) -> None:
        self._text = text
        self._lines = text.splitlines()

    @property
    def settings(self) -> str:
        """The settings text, with a comment block's ``#`` marks removed; empty when the file opens with none."""
        if not self._lines:
            return ""
        opening = self._lines[0].strip()
        if opening == _YAML_FENCE:
            end = self._closing_line()
            return "\n".join(self._lines[1:end]) if end is not None else ""
        if opening in _COMMENT_FENCES:
            return "\n".join(self._comment_settings())
        return ""

    @property
    def content(self) -> str:
        """The text without its YAML settings block. A ``---`` pair holding a markdown heading is two horizontal rules
        around a section, not settings, so that text is left whole."""
        if not self._text.startswith(_YAML_FENCE) or self._lines[0].strip() != _YAML_FENCE:
            return self._text
        end = self._closing_line()
        if end is None or _HEADING.search("\n".join(self._lines[1:end])):
            return self._text
        return "\n".join(self._lines[end + 1:]).lstrip("\n")

    def _closing_line(self) -> int | None:
        return next((index for index, line in enumerate(self._lines[1:], 1) if line.strip() == _YAML_FENCE), None)

    def _comment_settings(self) -> list[str]:
        settings: list[str] = []
        for line in self._lines[1:]:
            stripped = line.strip()
            if stripped in (*_COMMENT_FENCES, _YAML_FENCE):
                break
            settings.append(stripped[2:].lstrip() if stripped.startswith("#") else stripped)
        return settings
