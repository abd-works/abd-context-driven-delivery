"""Sketch channel — indent describe tree from a BDD sketch."""

from __future__ import annotations

from cdd_guidance.practices.sketch_document.sketch_outline import SketchOutline
from cdd_guidance.practices.bdd.model.bdd_model import BddModel
from harness.guidance.guidance import SketchLens


class SketchBddModel(BddModel):
    """Parse the boxed/indent sketch; render stays the sketch tree."""

    # The BDD section of a sketch, opened by either of its headings; the practice holds this lens.
    lens = SketchLens(("bdd:", "behavior driven development:"))

    def parse(self, text: str) -> BddModel:
        outline = SketchOutline(text)
        if outline.holds(self.lens):
            text = outline.body_for(self.lens)
        return super().parse(text)
