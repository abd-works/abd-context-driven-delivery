"""Sketch channel — indent describe tree from a BDD sketch."""

from __future__ import annotations

from cdd_guidance.practices.bdd.model.bdd_model import BddModel


class SketchBddModel(BddModel):
    """Parse the boxed/indent sketch; render stays the sketch tree."""

    def parse(self, text: str) -> BddModel:
        from cdd_guidance.actions.sketch.sketch_outline import SketchLens, SketchOutline

        outline = SketchOutline(text)
        if outline.holds(SketchLens.of("bdd")):
            text = outline.body_for(SketchLens.of("bdd"))
        return super().parse(text)
