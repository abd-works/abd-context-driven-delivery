"""The class cards the story explorer's steps open: each domain term a scenario file links to its class in a model file
(``++[cart](../domain/domain-model.md#cart-entity)++``), with the section under that heading in the model file, which
the explorer shows in place when a reader clicks the term in a step."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

from cdd_guidance.practices.stories.model.markdown.links import DomainTermLinks
from cdd_guidance.practices.stories.model.markdown.markup import MarkdownStep
from cdd_guidance.practices.stories.model.story_map import Step
from harness.markdown.markdown import MarkdownText

# A model file a term's link can name a class in: domain-model.md, class-model.md, or any other *-model.md.
MODEL_FILE_SUFFIX = "-model.md"
# How a card shows a markdown rule (---) between a class's intro and its members.
RULE_MARK = "– – –"
_RULE = re.compile(r"^\s*-{3,}\s*$")
_HEADING_MARKS = re.compile(r"^\s*#+\s*")
_TAB_AS_SPACES = "    "


@dataclass(frozen=True)
class ClassCard:
    """A class as its model file writes it: its heading, with « » around its stereotypes, and every line under the
    heading up to the next heading as high or higher."""

    title: str
    text: str

    @classmethod
    def from_section(cls, lines: list[str]) -> "ClassCard":
        """The card of a section's lines, its heading first: each rule shown as a short dashed line, tabs as spaces."""
        title = _HEADING_MARKS.sub("", lines[0]).strip().replace("<<", "«").replace(">>", "»")
        body = [RULE_MARK if _RULE.match(line) else line.replace("\t", _TAB_AS_SPACES) for line in lines[1:]]
        return cls(title, "\n".join(body).strip("\n"))

    def shown(self) -> Dict[str, str]:
        """The card as the explorer's data holds it."""
        return {"title": self.title, "text": self.text}


class ClassCards:
    """The class card each term the steps link opens, by the key the explorer names it with (the model file from the
    folder the steps name their files from, ``#`` and the heading's anchor). A term linked to more than one class opens
    the one it is linked to most often. Each model file is read once."""

    def __init__(self, root: Optional[Path] = None) -> None:
        """Cards read from the model files the steps link, each step's file a path from root (the project's root)."""
        self.root = Path(root or ".").resolve()
        self._linked: Dict[str, Counter] = {}
        self._cards: Dict[str, Optional[ClassCard]] = {}

    def read(self, steps: Iterable[Step]) -> "ClassCards":
        """Take the terms each of steps links, as the line it was read from writes them; these cards."""
        for step in steps:
            self._read_step(step)
        return self

    def terms_in(self, text: str) -> Dict[str, str]:
        """Each linked term text names as a whole word, longest term first, with the key of the card it opens."""
        if not self._linked:
            return {}
        terms = sorted(self._linked, key=len, reverse=True)
        pattern = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(term) for term in terms) + r")(?!\w)")
        return {found.group(0): self._card_key_of(found.group(0)) for found in pattern.finditer(text)}

    def shown(self) -> Dict[str, Dict[str, str]]:
        """Each card a term opens, by its key, once, as the explorer's data holds them."""
        keys = {self._card_key_of(term) for term in self._linked}
        return {key: self._cards[key].shown() for key in sorted(keys)}

    def _card_key_of(self, term: str) -> str:
        return self._linked[term].most_common(1)[0][0]

    def _read_step(self, step: Step) -> None:
        line = step.line_as_read() if isinstance(step, MarkdownStep) else None
        if not line or step.source is None or not step.source.file:
            return
        folder = (self.root / step.source.file).parent
        for term, target in DomainTermLinks(line).targets().items():
            key = self._card_key(folder, target)
            if key:
                self._linked.setdefault(term.strip(), Counter())[key] += 1

    def _card_key(self, folder: Path, target: str) -> str:
        """The key of the card target names from a step's folder; empty when it names no heading of a model file there."""
        path, _, anchor = target.partition("#")
        if not anchor or not path.endswith(MODEL_FILE_SUFFIX):
            return ""
        model = (folder / path).resolve()
        key = f"{self._named(model)}#{anchor}"
        if key not in self._cards:
            self._cards[key] = self._card_at(model, anchor)
        return key if self._cards[key] is not None else ""

    def _card_at(self, model: Path, anchor: str) -> Optional[ClassCard]:
        if not model.is_file():
            return None
        text = model.read_text(encoding="utf-8")
        lines = MarkdownText(text).anchored_lines(anchor)
        if lines is None:
            return None
        first, last = lines
        return ClassCard.from_section(text.splitlines()[first - 1:last])

    def _named(self, model: Path) -> str:
        """model as a path from the root, or whole when it sits outside it."""
        try:
            return model.relative_to(self.root).as_posix()
        except ValueError:
            return model.as_posix()
