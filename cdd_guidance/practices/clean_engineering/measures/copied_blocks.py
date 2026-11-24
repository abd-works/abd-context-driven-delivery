"""The blocks of code a file repeats from another file, found as jscpd finds them: a run of at least five lines of code,
holding at least fifty tokens, written the same in two files. Blank lines and lines holding only a comment are left
out, and each line is compared with its indentation stripped, so a block moved into a class or out of one is still the
same block. A copy is one more place a fix has to be made, and the copy nobody remembers is the one left broken."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# The fewest lines of code and tokens a repeated run must hold to be a copied block, as the gate ran jscpd.
FEWEST_LINES = 5
FEWEST_TOKENS = 50
# A string, a name or number, or one character of punctuation: the tokens a line is counted in.
_TOKEN = re.compile(r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'|\w+|[^\s\w]')
# What opens a comment line, by the file's extension; any other extension is a brace language.
_COMMENT_OPENERS = {".py": ("#",)}
_BRACE_COMMENT_OPENERS = ("//", "/*", "*", "*/")


@dataclass(frozen=True)
class CodeLine:
    """One line of code of a file: its number in the file, its text without indentation, and its tokens."""

    number: int
    text: str
    tokens: int


@dataclass(frozen=True)
class CopiedBlock:
    """A run of lines one file writes as another file does: where it is, and where its copy is."""

    file: str
    first: int
    last: int
    copy_file: str
    copy_first: int
    copy_last: int

    @property
    def said(self) -> str:
        """Where the block is and where its copy is, as a violation names them."""
        return f"{self.file} lines {self.first}-{self.last}, also in {self.copy_file} lines {self.copy_first}-{self.copy_last}"


class CopiedBlocks:
    """The copied blocks of a set of code files, each named by its path from the source root. Every file is read once,
    and every run of five lines indexed, so the blocks of any one file are found against all the others."""

    def __init__(self, files: dict[str, Path]) -> None:
        self._lines = {name: self._code_lines(path) for name, path in files.items()}
        self._written: dict[tuple[str, ...], list[tuple[str, int]]] = {}
        for name, lines in self._lines.items():
            for start in range(len(lines) - FEWEST_LINES + 1):
                self._written.setdefault(self._window(lines, start), []).append((name, start))

    def of(self, name: str) -> list[CopiedBlock]:
        """The blocks the file named repeats from another file, in the order they come in it."""
        lines = self._lines.get(name, [])
        copied_at: dict[int, tuple[str, int]] = {}
        for start in range(len(lines) - FEWEST_LINES + 1):
            elsewhere = [found for found in self._written[self._window(lines, start)] if found[0] != name]
            if elsewhere:
                copied_at[start] = elsewhere[0]
        return [block for run in self._runs(sorted(copied_at)) for block in self._block(name, lines, run, copied_at)]

    def _runs(self, starts: list[int]) -> list[list[int]]:
        """The starts of windows that overlap or touch, gathered into runs."""
        runs: list[list[int]] = []
        for start in starts:
            if runs and start <= runs[-1][-1] + FEWEST_LINES:
                runs[-1].append(start)
            else:
                runs.append([start])
        return runs

    def _block(self, name: str, lines: list[CodeLine], run: list[int], copied_at: dict[int, tuple[str, int]]) -> list[CopiedBlock]:
        """The run as a copied block, when it holds enough tokens; nothing when it does not."""
        first, last = run[0], run[-1] + FEWEST_LINES - 1
        if sum(line.tokens for line in lines[first : last + 1]) < FEWEST_TOKENS:
            return []
        copy_file, copy_start = copied_at[first]
        copy_lines = self._lines[copy_file]
        copy_last = min(copy_start + last - first, len(copy_lines) - 1)
        return [CopiedBlock(name, lines[first].number, lines[last].number, copy_file, copy_lines[copy_start].number, copy_lines[copy_last].number)]

    def _window(self, lines: list[CodeLine], start: int) -> tuple[str, ...]:
        return tuple(line.text for line in lines[start : start + FEWEST_LINES])

    def _code_lines(self, path: Path) -> list[CodeLine]:
        """The file's lines of code: not blank, and not only a comment. A character that is not UTF-8 is read as a
        replacement, since a block is compared as text and the file's own reader reports a file it cannot read."""
        text = path.read_text(encoding="utf-8", errors="replace")
        openers = _COMMENT_OPENERS.get(path.suffix, _BRACE_COMMENT_OPENERS)
        stripped = ((number, line.strip()) for number, line in enumerate(text.splitlines(), start=1))
        return [CodeLine(number, line, len(_TOKEN.findall(line))) for number, line in stripped if line and not line.startswith(openers)]
