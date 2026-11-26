"""The bracket structure of a span of brace-language source: which bracket closes which, and where a mark sits outside
every bracket pair. Every reader of brace-language code asks it, and the rule measures in *SourceText* hold one."""

from __future__ import annotations


class BracketStructure:
    """<<Value Object>> A span of text read for its brackets."""

    def __init__(self, text: str) -> None:
        self._text = text

    def closing_bracket(self, open_at: int, opener: str = "{", closer: str = "}") -> int | None:
        """The index of the bracket that closes the one at open_at; None when the text never closes it."""
        depth = 0
        for index in range(open_at, len(self._text)):
            depth += self._depth_change(index, opener, closer)
            if depth == 0 and self._text[index] == closer:
                return index
        return None

    def opening_bracket(self, close_at: int, opener: str = "(", closer: str = ")") -> int:
        """The index of the bracket the one at close_at closes, read backwards; -1 when nothing opens it."""
        depth = 0
        for index in range(close_at, -1, -1):
            depth += self._depth_change(index, closer, opener)
            if depth == 0 and self._text[index] == opener:
                return index
        return -1

    def top_level_indexes(self, mark: str) -> list[int]:
        """Each place mark sits outside every bracket pair, generics included: a `,` between parameters and not one
        inside `Map<K, V>`, a default's `=` and not one inside a destructuring pattern `{ a = 1 }`. An arrow's `>` closes
        no bracket, and the `=` of an arrow `=>` is no mark."""
        found: list[int] = []
        depth = 0
        for index, char in enumerate(self._text):
            change = self._nesting_change(index)
            if change:
                depth = max(0, depth + change)
            elif char == mark and depth == 0 and self._text[index + 1 : index + 2] != ">":
                found.append(index)
        return found

    def _depth_change(self, index: int, deeper: str, shallower: str) -> int:
        """How the character at index moves the depth of one kind of bracket pair: in by one, out by one, or not."""
        char = self._text[index]
        return 1 if char == deeper else -1 if char == shallower else 0

    def _nesting_change(self, index: int) -> int:
        """How the character at index moves the depth of every kind of bracket, generics included; an arrow's `>`
        closes nothing."""
        char = self._text[index]
        if char in "<([{":
            return 1
        if char in ")]}" or (char == ">" and self._text[index - 1 : index] != "="):
            return -1
        return 0

    def top_level_index(self, mark: str) -> int:
        """The first place mark sits outside every bracket pair; -1 when it sits at none."""
        return next(iter(self.top_level_indexes(mark)), -1)

    def braced(self, open_at: int) -> str | None:
        """The text inside the `{` at open_at and the `}` that closes it; None when open_at is no `{` or nothing
        closes it."""
        if open_at >= len(self._text) or self._text[open_at] != "{":
            return None
        close = self.closing_bracket(open_at)
        return self._text[open_at + 1 : close] if close is not None else None


def split_top_level(text: str) -> list[str]:
    """The comma-separated parts of a parameter list, keeping commas inside brackets or generics; blanks dropped."""
    starts = [0] + [index + 1 for index in BracketStructure(text).top_level_indexes(",")]
    ends = [index - 1 for index in starts[1:]] + [len(text)]
    return [text[start:end].strip() for start, end in zip(starts, ends) if text[start:end].strip()]
