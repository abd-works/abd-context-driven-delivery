"""Where each class card of a diagram links: the class's heading in the model document the diagram is drawn beside,
else the code file and line the class was read from.

A diagram is written in the folder of the model document it draws (``shop-model.md``, ``domain-model.md``,
``class-model.md``), so each card links to the first heading of a model document in that folder whose words start
with the class's name, by the anchor GitHub and VS Code give that heading. A class no heading names links to the code
it was read from, when its source names a code file that is there. A diagram drawn for a board in Claude, which
opens only a web address, links each place where its checkout's origin shows it.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, NamedTuple, Optional

from harness.catalog_generator.git_citation import GitCitation
from harness.markdown.markdown import MarkdownText, heading_anchor

from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass

# How the name of a model document ends: `shop-model.md`, `domain-model.md`, `class-model.md`.
MODEL_DOCUMENT_ENDING = "-model.md"
# The class a heading names: the first word of its words, `Order` in `Order <<Aggregate Root>>` or `Order : Entity`.
_NAMED_CLASS = re.compile(r"^\W*([A-Za-z_][\w.]*)")


class ClassPlace(NamedTuple):
    """Where a class is described: a file, the anchor of its heading in a model document or the line it starts on in
    code, and the link the diagram's card carries to it."""

    path: Path
    anchor: str
    line: int
    link: str


class ClassModelLinks:
    """The place each class of a diagram written in folder links to: its heading in a model document there, else the
    code it was read from; linked from the folder, or, with a citation, where the checkout's origin shows it."""

    def __init__(self, folder: Path, citation: Optional[GitCitation] = None) -> None:
        self._folder = Path(folder).resolve()
        self._citation = citation
        self._headings: Dict[str, ClassPlace] = {}
        for document in sorted(self._folder.glob(f"*{MODEL_DOCUMENT_ENDING}")):
            self._read_headings(document)

    def place_of(self, oclass: OoadClass) -> Optional[ClassPlace]:
        """The class's heading in a model document in the folder, else the code file and line its source names; none
        when it has neither."""
        return self._headings.get(oclass.name) or self._code_place(oclass)

    def _read_headings(self, document: Path) -> None:
        """Each class a heading of document names, at that heading's anchor, the first heading of a name winning; a
        heading whose words another heading also has takes ``-1``, ``-2`` as GitHub numbers it."""
        seen: Dict[str, int] = {}
        for _start, _end, _level, words in MarkdownText(document.read_text(encoding="utf-8")).headings():
            anchor = heading_anchor(words)
            count = seen.get(anchor)
            seen[anchor] = 0 if count is None else count + 1
            named = _NAMED_CLASS.match(words)
            if named is None:
                continue
            numbered = anchor if count is None else f"{anchor}-{count + 1}"
            self._headings.setdefault(named.group(1), ClassPlace(document, numbered, 0, self._link(document, numbered, 0)))

    def _code_place(self, oclass: OoadClass) -> Optional[ClassPlace]:
        """The code file and line the class's source names, when that file is there and is not a markdown document."""
        source = getattr(oclass, "source", None)
        if source is None or not source.root or not source.file or source.file == "." or source.file.endswith(".md"):
            return None
        path = Path(source.root, source.file).resolve()
        if not path.is_file():
            return None
        line = oclass.line or source.start_line or 1
        return ClassPlace(path, "", line, self._link(path, "", line))

    def _link(self, path: Path, anchor: str, line: int) -> str:
        """The link to path at anchor, or at line in code: from the folder, or where the citation's origin shows it."""
        if self._citation is not None:
            return self._citation.blob_url(path, (line, line) if line else None) + (f"#{anchor}" if anchor else "")
        return self._relative(path) + (f"#{anchor}" if anchor else "")

    def _relative(self, path: Path) -> str:
        """path as a link from the diagram's folder; as it is when it sits on another drive."""
        try:
            return Path(os.path.relpath(path, self._folder)).as_posix()
        except ValueError:  # another drive on Windows
            return path.as_posix()

