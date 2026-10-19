"""Sketch channel — indent describe tree from a BDD sketch."""

from __future__ import annotations

from cdd_guidance.practices.bdd.model.bdd_model import BddModel


class SketchBddModel(BddModel):
    """Parse the boxed/indent sketch; render stays the sketch tree."""

    def parse(self, text: str) -> BddModel:
        from cdd_guidance.actions.sketch.sketch_outline import SketchLens, SketchOutline
        from cdd_guidance.practices.bdd.model.bdd_model import _parse_sketch

        outline = SketchOutline(text)
        if outline.holds(SketchLens.behavior_driven_development):
            text = outline.body_for(SketchLens.behavior_driven_development)
        self.descriptions = _parse_sketch(text)
        return self

    def render(self, canonical: BddModel, previous: str | None = None) -> str:
        from cdd_guidance.practices.bdd.model.bdd_model import _render_sketch

        return "\n\n".join(_render_sketch(item) for item in canonical.descriptions)
