"""What Correct on a broken rule's banner, in the Graph app and the Files app, asks the chat to do about one rule broken
at one place. The words are written here, so the pages only ask for them and send them."""

from __future__ import annotations

# A correction is made the Clean Engineering way, test first, so a fix that changes what the code does is caught.
_HOW_TO_FIX = [
    "Fix this violation using the Clean Engineering practice guidelines and a test-driven approach.",
    "Run or add tests that express the intended behavior before or alongside the fix.",
]
# What a correction's lines are joined with.
_LINE = "\n"


class CorrectedPlace:
    """The node a correction is for, as the Graph app shows it: its name and type, its file, the lines the broken rule
    marks, and the node's text."""

    def __init__(self, name: str, type: str, file: str, lines: tuple[int, int], excerpt: str) -> None:
        self.name = name
        self.type = type
        self.file = file
        self.start_line, self.end_line = lines
        self.excerpt = excerpt

    @property
    def file_span(self) -> str:
        """The file and the lines marked, or the file alone when no line is."""
        return f"{self.file}:{self.start_line}-{self.end_line}" if self.start_line >= 1 else self.file


# A correction that names no node: a comment on a file's lines, which names them itself.
_NOWHERE = CorrectedPlace("", "", "", (0, 0), "")


class ViolationCorrection:
    """A rule broken somewhere, with what it says is wrong, as Correct sends it: as a whole prompt for a chat told
    nothing else, naming the place, or as the words of a comment on the rule's lines, which already name and quote them."""

    def __init__(self, rule: str, message: str, place: CorrectedPlace | None = None) -> None:
        self._rule = rule
        self._message = message
        self._place = place

    @property
    def prompt(self) -> str:
        """The whole correction: how to fix it, the node, the file and lines, the rule, the code, and what is wrong."""
        place = self._place or _NOWHERE
        return _LINE.join([
            *_HOW_TO_FIX,
            "",
            f"Node: {place.name} ({place.type})",
            f"File: {place.file_span}" if place.file_span else "",
            f"Rule: {self._rule}",
            "",
            "Erroneous code:",
            "```",
            place.excerpt,
            "```",
            "",
            f"Violation: {self._message}",
        ])

    @property
    def comment(self) -> str:
        """The correction as a comment on the rule's lines: how to fix it, the rule, and what is wrong."""
        return _LINE.join([*_HOW_TO_FIX, "", f"Rule: {self._rule}", f"Violation: {self._message}"])
