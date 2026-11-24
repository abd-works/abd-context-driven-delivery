"""What Fix this one, Fix rule and Fix all, on a broken rule in the Graph app and the Files app, ask the chat to do about
the rules broken where they were pressed. The words are written here, so the pages only ask for them and send them."""

from __future__ import annotations

# A correction is made the Clean Engineering way, test first, so a fix that changes what the code does is caught.
_HOW_TO_FIX_ONE = "Fix this violation using the Clean Engineering practice guidelines and a test-driven approach."
_HOW_TO_FIX_SEVERAL = "Fix these {count} violations using the Clean Engineering practice guidelines and a test-driven approach."
_TESTS_FIRST = "Run or add tests that express the intended behavior before or alongside the fix."
# What a correction's lines are joined with, and what parts its several violations.
_LINE = "\n"
_BETWEEN_VIOLATIONS = "\n\n"


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
    """A rule broken somewhere, with what it says is wrong, as Fix this one sends it: as a whole prompt for a chat told
    nothing else, naming the place, or as the words of a comment on the rule's lines, which already name and quote them."""

    def __init__(self, rule: str, message: str, place: CorrectedPlace | None = None) -> None:
        self._rule = rule
        self._message = message
        self._place = place

    @property
    def prompt(self) -> str:
        """The whole correction: how to fix it, the node, the file and lines, the rule, the code, and what is wrong."""
        return _LINE.join([_HOW_TO_FIX_ONE, _TESTS_FIRST, "", self.described])

    @property
    def described(self) -> str:
        """What is broken, without how to fix it: the node, the file and lines, the rule, the code, and what is wrong."""
        place = self._place or _NOWHERE
        return _LINE.join([
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
        return _LINE.join([_HOW_TO_FIX_ONE, _TESTS_FIRST, "", f"Rule: {self._rule}", f"Violation: {self._message}"])


class ViolationCorrections:
    """Every rule broken where Fix rule or Fix all was pressed, as one prompt: how to fix them, said once, then each
    correction, numbered, so the chat works through them together rather than one prompt at a time."""

    def __init__(self, corrections: list[ViolationCorrection]) -> None:
        self._corrections = list(corrections)

    @property
    def prompt(self) -> str:
        """How to fix them all test first, then each correction; one correction alone is its own prompt, and none is
        nothing to send."""
        if len(self._corrections) <= 1:
            return self._corrections[0].prompt if self._corrections else ""
        numbered = [f"Violation {number}:\n{correction.described}" for number, correction in enumerate(self._corrections, start=1)]
        how = _LINE.join([_HOW_TO_FIX_SEVERAL.format(count=len(self._corrections)), _TESTS_FIRST])
        return _BETWEEN_VIOLATIONS.join([how, *numbered])
