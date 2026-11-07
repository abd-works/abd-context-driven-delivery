"""Sketch channel — indent describe tree from a BDD sketch."""

from __future__ import annotations

from cdd_guidance.actions.sketch.sketch_outline import SketchLens, SketchOutline
from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.bdd.model.bdd_model import BddModel


class SketchBddModel(BddModel):
    """Parse the boxed/indent sketch; render stays the sketch tree."""

    # The BDD section of a sketch, opened by the headings the practice declares; made once.
    lens = SketchLens(Bdd.sketch_titles)

    def parse(self, text: str) -> BddModel:
        outline = SketchOutline(text)
        if outline.holds(self.lens):
            text = outline.body_for(self.lens)
        return super().parse(text)
