"""The section of a sketch one practice writes, opened by the headings that practice declares."""

from __future__ import annotations


class SketchLens:
    """The section of a sketch that one practice writes, opened by the headings the practice declares, such as
    ``stories:``. Each practice holds its own (``PracticeGuidance.sketch_lens``), so a reader of a sketch asks the
    practice for it rather than naming the practice."""

    def __init__(self, titles: tuple[str, ...]) -> None:
        self.titles = titles

    def opens(self, title: str) -> bool:
        """True when this title is the section heading or marker this practice writes under."""
        return title.strip().lower() in self.titles
