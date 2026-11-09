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
            if self._text[index] == opener:
                depth += 1
            elif self._text[index] == closer:
                depth -= 1
                if depth == 0:
                    return index
        return None

    def opening_bracket(self, close_at: int, opener: str = "(", closer: str = ")") -> int:
        """The index of the bracket the one at close_at closes, read backwards; -1 when nothing opens it."""
        depth = 0
        for index in range(close_at, -1, -1):
            if self._text[index] == closer:
                depth += 1
            elif self._text[index] == opener:
                depth -= 1
                if depth == 0:
                    return index
        return -1

    def top_level_indexes(self, mark: str) -> list[int]:
        """Each place mark sits outside every bracket pair, generics included: a `,` between parameters and not one
        inside `Map<K, V>`, a default's `=` and not one inside a destructuring pattern `{ a = 1 }`. An arrow's `>` closes
        no bracket, and the `=` of an arrow `=>` is no mark."""
        found: list[int] = []
        depth = 0
        text = self._text
        for index, char in enumerate(text):
            if char in "<([{":
                depth += 1
            elif char in ")]}" or (char == ">" and text[index - 1 : index] != "="):
                depth = max(0, depth - 1)
            elif char == mark and depth == 0 and text[index + 1 : index + 2] != ">":
                found.append(index)
        return found

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
