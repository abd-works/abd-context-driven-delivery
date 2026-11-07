"""The line ranges the catalog's code viewer folds in an example file, so a reader sees its outline first."""
from __future__ import annotations

import re

_STEP_LINE = re.compile(r"^\s*(?:given|when|then|\.(?:and|but))\s*\(")
_STORY_LINE = re.compile(r"^\s*story\s*\(")
_SCENARIO_LINE = re.compile(r"^\s*scenario\s*\(")
_STORY_COMMENT = re.compile(r"\*\s*Story:")
_CLASS_LINE = re.compile(r"^export class (\w+)")
_FOLDED_DECLARATIONS = (
    re.compile(r"^export const \w+ = \{"),
    re.compile(r"^export interface \w+"),
    re.compile(r"^function \w+"),
)
_METHOD_LINE = re.compile(
    r"^\s+(?:public |private |protected |readonly |static |async |get |set )*"
    r"(?:constructor|[A-Za-z_]\w*)\s*(?:<[^>\n]*>)?\s*\("
)
# The tactics example's aggregate roots, which stay open with each operation folded.
_OPEN_TYPE_NAMES = {"Customer", "AccountCredentials"}
_QUOTES = "'\"`"

Fold = tuple[int, int]


class SourceFolds:
    """The folds for one TypeScript example, as 1-based inclusive line ranges. A step of an acceptance test folds its
    callback body, so the Given/When/Then lines read as the scenario; a DDD tactics file keeps its root open to its
    operations and folds every other declaration to its first line."""

    def __init__(self, source: str) -> None:
        self._source = source
        self._lines = source.splitlines()

    @property
    def for_example(self) -> list[Fold] | None:
        """The folds the example's kind calls for: a tactics file's, an acceptance test's, or none, which leaves the
        viewer folding its steps."""
        if "Root" in self._source and "export class " in self._source:
            return self.tactics
        return self.acceptance_test

    @property
    def steps(self) -> list[Fold]:
        """Each Given/When/Then/And/But callback body, from the step's signature to the line that closes it. A step that
        fits on one line stays open."""
        ranges: list[Fold] = []
        index = 0
        while index < len(self._lines):
            end = self._step_end(index)
            if end is not None and end > index:
                ranges.append((index + 1, end + 1))
                index = end + 1
            else:
                index += 1
        return ranges

    @property
    def acceptance_test(self) -> list[Fold] | None:
        """The steps and the test's scaffolding, keeping the story, scenario, and step lines visible; none for a file
        that is not an acceptance test."""
        has_story = any(_STORY_LINE.match(line) for line in self._lines)
        has_scenario = any(_SCENARIO_LINE.match(line) for line in self._lines)
        return self.scenario_steps if has_story and has_scenario else None

    @property
    def scenario_steps(self) -> list[Fold]:
        ranges = [*self.steps, *self._story_scaffolding(), *self._scenario_scaffolding()]
        return sorted({(start, end) for start, end in ranges if end >= start})

    @property
    def tactics(self) -> list[Fold]:
        ranges: list[Fold] = []
        for index, line in enumerate(self._lines):
            if not self._is_declaration(line):
                continue
            end = self._brace_end(index)
            if end is None or end <= index:
                continue
            if self._stays_open(index):
                ranges.extend(self._operation_folds(index + 1, end))
            else:
                ranges.append((index + 1, end + 1))
        return ranges

    def _story_scaffolding(self) -> list[Fold]:
        story = self._first(_STORY_LINE)
        if story is None:
            return []
        comment = next((index for index in range(story) if _STORY_COMMENT.search(self._lines[index])), None)
        if comment is not None and comment < story - 1:
            return [(comment + 2, story)]
        return [(1, story)] if story > 0 else []

    def _scenario_scaffolding(self) -> list[Fold]:
        scenario, first_step = self._first(_SCENARIO_LINE), self._first(_STEP_LINE)
        if scenario is None or first_step is None or first_step <= scenario + 1:
            return []
        return [(scenario + 1, first_step)]

    def _first(self, pattern: re.Pattern[str]) -> int | None:
        return next((index for index, line in enumerate(self._lines) if pattern.match(line)), None)

    def _is_declaration(self, line: str) -> bool:
        return bool(_CLASS_LINE.match(line)) or any(pattern.match(line) for pattern in _FOLDED_DECLARATIONS)

    def _stays_open(self, index: int) -> bool:
        """An aggregate root stays open: a named root, or a class whose comment line above names it a Root."""
        declared = _CLASS_LINE.match(self._lines[index])
        if declared is None:
            return False
        previous = self._lines[index - 1].strip() if index else ""
        return declared.group(1) in _OPEN_TYPE_NAMES or "Root" in previous

    def _operation_folds(self, start: int, end: int) -> list[Fold]:
        ranges: list[Fold] = []
        cursor = start
        while cursor < end:
            operation_end = self._brace_end(cursor) if _METHOD_LINE.match(self._lines[cursor]) else None
            if operation_end is not None and operation_end > cursor:
                ranges.append((cursor + 1, operation_end + 1))
                cursor = operation_end + 1
            else:
                cursor += 1
        return ranges

    def _step_end(self, index: int) -> int | None:
        if not _STEP_LINE.match(self._lines[index]):
            return None
        return self._closing_line(index, _BraceScanner("\n".join(self._lines[index:])).arrow_body_open())

    def _brace_end(self, index: int) -> int | None:
        return self._closing_line(index, _BraceScanner("\n".join(self._lines[index:])).first_brace())

    def _closing_line(self, index: int, opened: int | None) -> int | None:
        if opened is None:
            return None
        text = "\n".join(self._lines[index:])
        closed = _BraceScanner(text).matching_brace(opened)
        return None if closed is None else index + text.count("\n", 0, closed)


class _BraceScanner:
    """Reads TypeScript text for braces, stepping over strings, template expressions, and line comments."""

    def __init__(self, text: str) -> None:
        self._text = text

    def first_brace(self) -> int | None:
        return next((index for index, char in self._code() if char == "{"), None)

    def arrow_body_open(self) -> int | None:
        """Where the block body of the first arrow function opens; none when that arrow has an expression body."""
        arrow = next((index for index, _char in self._code() if self._text.startswith("=>", index)), None)
        if arrow is None:
            return None
        cursor = arrow + 2
        while cursor < len(self._text) and self._text[cursor] in " \t\r\n":
            cursor += 1
        return cursor if cursor < len(self._text) and self._text[cursor] == "{" else None

    def matching_brace(self, open_at: int) -> int | None:
        depth = 0
        for index, char in self._code(open_at):
            depth += {"{": 1, "}": -1}.get(char, 0)
            if char == "}" and depth == 0:
                return index
        return None

    def _code(self, start: int = 0):
        """Each character outside strings and comments, with its position."""
        index, length = start, len(self._text)
        while index < length:
            char = self._text[index]
            if char in _QUOTES:
                index = self._after_string(index)
            elif self._text.startswith("//", index):
                newline = self._text.find("\n", index)
                index = length if newline == -1 else newline + 1
            else:
                yield index, char
                index += 1

    def _after_string(self, start: int) -> int:
        quote, index, length = self._text[start], start + 1, len(self._text)
        while index < length:
            if self._text[index] == "\\":
                index += 2
            elif self._text[index] == quote:
                return index + 1
            elif quote == "`" and self._text.startswith("${", index):
                closed = self.matching_brace(index + 1)
                index = length if closed is None else closed + 1
            else:
                index += 1
        return length
