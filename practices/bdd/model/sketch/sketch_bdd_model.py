"""Sketch channel — indent describe tree from a BDD sketch."""

from __future__ import annotations

from practices.bdd.model.bdd_model import BddModel


class SketchBddModel(BddModel):
    """Parse the boxed/indent sketch; render stays the sketch tree."""

    def render(self, canonical: BddModel, previous: str | None = None) -> str:
        from practices.bdd.model.bdd_model import _render_sketch

        return "\n\n".join(_render_sketch(item) for item in canonical.descriptions)
