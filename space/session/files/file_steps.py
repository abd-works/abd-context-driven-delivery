"""A story test's steps as a viewer shows them: what each step invokes and observes opens in place, as a callout, under
the line of the step that names it, titled as the class it belongs to names it. The session decides both, so a page
draws each callout where it is sent."""

from __future__ import annotations

import re
from typing import Literal

from harness.graph.explorer import NodeSource
from harness.installation.data_class import data_field

StepCalloutKind = Literal["call", "example"]

# Where a comment or a string starts in code: a doc string, a block comment, a line comment, or a quote.
_TRIPLE_QUOTES = ('"""', "'''")
_LINE_COMMENT = "//"
_HASH_COMMENT = "#"
_BLOCK_COMMENT = ("/*", "*/")
_QUOTES = "'\"`"
# The language whose comments start with a hash.
_HASH_COMMENTED = "python"


class StoryTestCode:
    """The code of a story test, its comments and strings blanked, and the lines its steps start on, so a name only a
    comment, a doc string or a step's words hold is found in no line of its code."""

    def __init__(self, text: str, language: str, step_lines: list[int]) -> None:
        self._lines = _Blanked(text, language == _HASH_COMMENTED).code.split("\n")
        self._step_lines = sorted(step_lines)

    def line_naming(self, step_line: int, name: str) -> int:
        """The first line of the step starting at step_line, before the next step starts, whose code names name; the
        step's own line when none does."""
        named = re.compile(rf"\b{re.escape(name)}\b")
        last = min(len(self._lines), self._next_step_after(step_line) - 1)
        return next((line for line in range(step_line, last + 1) if named.search(self._lines[line - 1])), step_line)

    def _next_step_after(self, step_line: int) -> int:
        return next((line for line in self._step_lines if line > step_line), len(self._lines) + 1)


class _Blanked:
    """Text with each character of its comments and strings made a space, its line breaks kept, so every line of the
    code stays the line it was."""

    def __init__(self, text: str, hash_comments: bool) -> None:
        self._text = text
        self._hash_comments = hash_comments

    @property
    def code(self) -> str:
        kept: list[str] = []
        index = 0
        while index < len(self._text):
            skipped = self._prose_end(index)
            kept.append(re.sub(r"[^\n]", " ", self._text[index:skipped]) if skipped > index else self._text[index])
            index = max(skipped, index + 1)
        return "".join(kept)

    def _prose_end(self, index: int) -> int:
        """Where the comment or string starting at index ends; index itself when none starts there."""
        closing = self._closing_at(index)
        if closing:
            return self._end_of(self._text.find(closing, index + 2), len(closing))
        if self._text.startswith(_LINE_COMMENT, index) or (self._hash_comments and self._text.startswith(_HASH_COMMENT, index)):
            return self._end_of(self._text.find("\n", index), 0)
        if self._text[index] not in _QUOTES:
            return index
        return self._string_end(index)

    def _closing_at(self, index: int) -> str:
        """What closes a doc string or block comment starting at index; none when neither starts there."""
        quotes = next((quotes for quotes in _TRIPLE_QUOTES if self._text.startswith(quotes, index)), "")
        return quotes or (_BLOCK_COMMENT[1] if self._text.startswith(_BLOCK_COMMENT[0], index) else "")

    def _string_end(self, index: int) -> int:
        """Where the string quoted at index ends: a back-quoted string may run over lines, any other ends with its line."""
        quote = self._text[index]
        at = index + 1
        while at < len(self._text) and self._text[at] != quote and (quote == "`" or self._text[at] != "\n"):
            at += 2 if self._text[at] == "\\" else 1
        return min(at + 1, len(self._text))

    def _end_of(self, found: int, length: int) -> int:
        return len(self._text) if found < 0 else found + length


class StepCallout:
    """What a step of a story test invokes (a call) or observes (an example), opened in place under the line of the step
    whose code names it, titled by the class it belongs to and its name, or its name alone for a module's function."""

    def __init__(self, kind: StepCalloutKind, line: int, target: NodeSource) -> None:
        self._kind = kind
        self._line = line
        self._target = target

    @property
    @data_field
    def kind(self) -> StepCalloutKind:
        return self._kind

    @property
    @data_field
    def line(self) -> int:
        """The line, counted from 1, of the step's code that names what it reaches; the step's own line when no code
        of the step names it."""
        return self._line

    @property
    @data_field
    def title(self) -> str:
        """The name a viewer gives the callout, such as Ticket.delete."""
        owner = self._target.owner
        return f"{owner}.{self._target.name}" if owner else self._target.name

    @property
    @data_field
    def target(self) -> NodeSource:
        """What the step reaches, with its text and file."""
        return self._target


class FileStep:
    """A step of a story test in the file that reaches code or examples: the line it starts on, and a callout for each
    function and operation it invokes and each example it observes, so a story test's callouts sit on the step whose
    relationships they are."""

    def __init__(self, line: int, callouts: list[StepCallout]) -> None:
        self._line = line
        self._callouts = callouts

    @property
    @data_field
    def line(self) -> int:
        """The line, counted from 1, the step starts on: its decorator or its call."""
        return self._line

    @property
    @data_field
    def callouts(self) -> list[StepCallout]:
        """What the step invokes, then what it observes, each on the line of the step that names it."""
        return list(self._callouts)
