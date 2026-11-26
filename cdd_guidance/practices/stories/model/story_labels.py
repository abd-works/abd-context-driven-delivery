"""StoryLabels. Which Stories nodes a label names, as a page that shows the story map labels them: a design canvas's
story explorer shows a story, a scenario, an epic by its name, a step by its keyword and its words, an outline's example
by its name, and a person's comment on the page is anchored to that label."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, List, Optional

from cdd_guidance.practices.stories.model.markdown.markup import plain_words
from cdd_guidance.practices.stories.model.story_tree import EPIC_TYPES, EXAMPLE_TYPE, KEY_SEPARATOR, LINKED_TYPES, STEP_TYPES

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from cdd_guidance.practices.stories.model.story_tree import StoryTree

# The keyword a page writes in front of a step's words; an And or But continues the step before it.
_KEYWORD = re.compile(r"^(Given|When|Then|And|But)\s+", re.IGNORECASE)
# What a page writes after a label it cut short.
_CUT_SHORT = ("…", "...")
# A placeholder an outline's step names, which the page fills with the value of the row on show.
_PLACEHOLDER = re.compile(r"\$?\{[^}]+\}|<[^>\s]+>")
# A part of a comment's location that names where on the page it sits rather than what it is about.
_PAGE_PLACE = re.compile(r"^(story explorer|row \d+ of \d+|text\b.*|.*\{\{.*\}\}.*)$", re.IGNORECASE)
_LOCATION_SEPARATOR = "›"
# The node types a label can name besides the steps, in the order a label is matched against them.
_NAMED_TYPES = ("Story", *LINKED_TYPES["Scenario"], *EPIC_TYPES, EXAMPLE_TYPE)


class StoryLabels:
    """The Stories nodes of one story tree by the labels a page shows them with. A label is read as its plain words, so
    the markup a file writes (``++term++``, ``**actor**``, a link) does not matter; a label cut short with ``…`` names
    every node whose label begins with what is shown; a step whose words hold an outline's placeholder matches whatever
    value the page filled in. A label of several lines, such as a run of steps the page shows as one, names each node
    one of its lines names."""

    def __init__(self, tree: "StoryTree") -> None:
        self._tree = tree

    def named_by(self, anchor: str) -> List["Node"]:
        """The nodes anchor names: a key (``Story › Scenario › step``) when it is one, else each line of it, and each
        part of a location written with ``›`` that names something on the story map rather than a place on the page."""
        keyed = self._keyed(anchor.strip())
        if keyed:
            return keyed
        found: List["Node"] = []
        for label in self._labels_in(anchor):
            for node in self.labelled(label):
                if not any(node is held for held in found):
                    found.append(node)
        return found

    def labelled(self, label: str) -> List["Node"]:
        """The nodes shown with label: the steps whose words it says, after its keyword, of the keyword's phase when it
        names Given, When or Then and a step of that phase says them; a step whose words hold an outline's placeholder
        only when no step says the label outright; else the stories, scenarios, epics and examples named so."""
        shown = plain_words(label).strip()
        keyword = _KEYWORD.match(shown)
        words = shown[keyword.end():] if keyword else shown
        cut = next((mark for mark in _CUT_SHORT if words.endswith(mark)), "")
        words = words[: len(words) - len(cut)].strip() if cut else words
        if not words:
            return []
        every = self._tree.every_step()
        steps = [step for step in every if _says_outright(self._words_of(step), words, bool(cut))]
        steps = steps or [step for step in every if _says(self._words_of(step), words, bool(cut))]
        phase = keyword.group(1).lower() if keyword else ""
        if phase in ("given", "when", "then"):
            steps = [step for step in steps if self._tree.step_phase(step) == phase] or steps
        if steps:
            return steps
        nodes = (node for node_type in _NAMED_TYPES for node in self._tree.stories.in_graph.nodes(node_type))
        return [node for node in nodes if _says(plain_words(node.name), words, bool(cut))]

    def _keyed(self, anchor: str) -> List["Node"]:
        if KEY_SEPARATOR.strip() not in anchor:
            return []
        key = KEY_SEPARATOR.join(part.strip() for part in anchor.split(_LOCATION_SEPARATOR))
        for kind in ("Step", "Scenario", "Story"):
            found = self._tree.nodes_keyed(kind, key)
            if found:
                return found
        return []

    def _labels_in(self, anchor: str) -> List[str]:
        """Each line of anchor, and each part of a line written with ``›`` that names no place on the page."""
        labels: List[str] = []
        for line in (line.strip() for line in anchor.splitlines()):
            parts = [part.strip() for part in line.split(_LOCATION_SEPARATOR)] if _LOCATION_SEPARATOR in line else [line]
            labels.extend(part for part in parts if part and not _PAGE_PLACE.match(part))
        return labels

    def _words_of(self, step: "Node") -> str:
        return plain_words(self._tree.step_text(step)).strip()


def _says_outright(words: str, shown: str, cut_short: bool) -> bool:
    """Whether words, with no placeholder, are shown as shown."""
    return not _PLACEHOLDER.search(words) and (words.startswith(shown) if cut_short else words == shown)


def _says(words: str, shown: str, cut_short: bool) -> bool:
    """Whether a node whose label is words is shown as shown: the same words, or, when the page cut the label short, words
    that begin with them. A placeholder in words matches any value; a label cut short names words with a placeholder
    only where at least as much of their own words is shown as of the values filled in (*_begins*)."""
    pattern = _pattern_of(words)
    if not cut_short:
        return bool(pattern.match(shown)) if pattern is not None else words == shown
    if pattern is None:
        return words.startswith(shown)
    return _begins(shown, _PLACEHOLDER.split(words))


def _pattern_of(words: str) -> Optional["re.Pattern[str]"]:
    """words as a pattern whose placeholders match any value; none for words with no placeholder."""
    if not _PLACEHOLDER.search(words):
        return None
    parts = _PLACEHOLDER.split(words)
    return re.compile("^" + ".+?".join(re.escape(part) for part in parts) + "$")


def _begins(shown: str, parts: List[str], said: int = 0, filled: int = 0) -> bool:
    """Whether shown begins the words whose fixed parts are parts, each placeholder between two of them filled with at
    least one character, with at least as many of the words' own characters shown (said) as filled-in ones (filled): a
    label made mostly of a value the page filled in says nothing about which step it is."""
    fixed = parts[0]
    if len(shown) <= len(fixed):
        return fixed.startswith(shown) and said + len(shown.strip()) >= max(filled, 1)
    if not shown.startswith(fixed) or len(parts) == 1:
        return False
    rest = shown[len(fixed):]
    said += len(fixed.strip())
    return any(_begins(rest[length:], parts[1:], said, filled + length) for length in range(1, len(rest) + 1))
