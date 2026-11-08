"""The settings block at the top of a markdown, template, or example file."""
from __future__ import annotations

import re
from pathlib import Path

_YAML_FENCE = "---"
_COMMENT_FENCES = ("# ---", "#---")
_HEADING = re.compile(r"^#{1,6}\s", re.MULTILINE)


class FlatSettings:
    """Settings written as flat ``key: value`` lines, as a front matter block or a simple ```yaml block writes them:
    each value as written, without its quotes. Blank lines, ``#`` comments, and list items are not settings, and nested
    YAML is not read here; a reader that has PyYAML reads that."""

    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def fields(self) -> dict[str, str]:
        found: dict[str, str] = {}
        for raw in self._text.splitlines():
            line = raw.strip()
            if not line or line.startswith(("#", "- ")) or ":" not in line:
                continue
            key, _, value = line.partition(":")
            found[key.strip()] = value.strip().strip("'\"")
        return found


class FrontMatter:
    """The settings at the top of a file: a YAML block between ``---`` lines, or, in a code template, the same block
    written as ``# ---`` comment lines. The catalog reads a template's settings to match it to a fidelity and drops an
    example's settings before showing it; the installer reads a standing rule's ``description`` and ``globs``."""

    def __init__(self, text: str) -> None:
        self._text = text
        self._lines = text.splitlines()

    @classmethod
    def of_file(cls, path: Path) -> FrontMatter:
        """The settings at the top of the file at path, and the content after them; an empty one for a file that is
        not there."""
        return cls(path.read_text(encoding="utf-8") if path.is_file() else "")

    @property
    def text(self) -> str:
        """The whole file as written, settings and content."""
        return self._text

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
    def fields(self) -> dict[str, str]:
        """Each ``key: value`` line of the settings, the value as written without its quotes; a settings block is a
        flat list of names, so nested YAML is not read here."""
        return FlatSettings(self.settings).fields

    @property
    def content(self) -> str:
        """The text after its YAML settings block, its own line endings kept. A ``---`` pair holding a markdown heading
        is two horizontal rules around a section, not settings, so that text is left whole."""
        if not self._lines or self._lines[0].strip() != _YAML_FENCE:
            return self._text
        end = self._closing_line()
        if end is None or _HEADING.search("\n".join(self._lines[1:end])):
            return self._text
        return "".join(self._text.splitlines(keepends=True)[end + 1:]).lstrip("\r\n")

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
