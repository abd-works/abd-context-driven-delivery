"""FactFile: one file a pattern reads once while its overlay records its nodes, which says what node it becomes and the
facts its rules read on that node, so a rule never opens a file."""

from __future__ import annotations

from pathlib import Path

from cdd_guidance.practices.source_code import SourceText


class FactFile:
    """One file read once: its path from the working copy's root, and its text, held with the line each match in it
    starts on. Each kind of file says which node type it becomes (``node_type``) and the facts it carries (``facts``)."""

    node_type = ""

    def __init__(self, relative: str, text: str) -> None:
        self.relative = relative
        self._source = SourceText(text)

    @classmethod
    def at(cls, root: Path, path: Path, *held) -> "FactFile":
        """The file at path, read now, named from root; held is whatever else the kind of file is made with."""
        return cls(path.relative_to(root).as_posix(), path.read_text(encoding="utf-8", errors="replace"), *held)

    @property
    def facts(self) -> dict:
        """The facts this file carries on the node it becomes."""
        raise NotImplementedError(f"{type(self).__name__} must say what facts it carries")
