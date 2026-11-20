"""Sketch channel — the describe tree of a BDD sketch, in the heading notation of `templates/bdd-sketch.md`."""

from __future__ import annotations

import re

from cdd_guidance.practices.sketch_document.sketch_outline import SketchOutline
from cdd_guidance.practices.bdd.model.bdd_model import BddModel
from cdd_guidance.practices.bdd.model.nodes import Context, Description, Observation
from harness.guidance.guidance import SketchLens

_FENCE = "```"
_FENCE_LINE = re.compile(r"^([ \t]*)```.*$", re.MULTILINE)
# WHY: the sketch outline drops fence lines when it turns headings into indentation, and the tree's reader needs them
# to tell an observation's call lines from states. Each fence line crosses the outline as this line and is put back.
_KEPT_FENCE = "⟦fence⟧"
# `###` opens a subject, one level under the section's `##` heading; each state nested in it adds one `#`.
_SUBJECT_DEPTH = 3


class SketchBddModel(BddModel):
    """Reads the BDD section of a sketch, headings for subjects and states above fenced observations, and writes a
    describe tree in that notation."""

    # The BDD section of a sketch, opened by either of its headings; the practice holds this lens.
    lens = SketchLens(("bdd:", "behavior driven development:"))

    def parse(self, text: str) -> BddModel:
        outline = SketchOutline(_FENCE_LINE.sub(rf"\1{_KEPT_FENCE}", text))
        if outline.holds(self.lens):
            text = outline.body_for(self.lens).replace(_KEPT_FENCE, _FENCE)
        return super().parse(text)

    def render(self, canonical: BddModel, previous: str | None = None) -> str:
        """The spec as the BDD section of a sketch: the fidelity it holds, the section's heading, then each subject."""
        realized = any(self._is_realized(node) for node in canonical.behavior_nodes() if isinstance(node, Observation))
        blocks = [f"Fidelity: {'realization' if realized else 'behavior'}", f"## {self.lens.titles[-1]}"]
        for description in canonical.descriptions:
            blocks.extend(self._heading_blocks(description, _SUBJECT_DEPTH))
        return "\n\n".join(blocks) + "\n"

    def _heading_blocks(self, block: Description | Context, depth: int) -> list[str]:
        """The block's heading, its observations in fences, then each state nested in it one heading deeper. A heading
        holds its own observations above its nested headings, since whatever follows a heading belongs to it."""
        blocks = [f"{'#' * depth} {block.name}", *self._fences(list(block.observations))]
        for nested in block.contexts:
            blocks.extend(self._heading_blocks(nested, depth + 1))
        return blocks

    def _fences(self, observations: list[Observation]) -> list[str]:
        """One fence for each observation that carries a realization, its call lines above it; observations that carry
        none share a fence with their neighbours."""
        fences: list[list[str]] = []
        shared: list[str] | None = None
        for observation in observations:
            if self._is_realized(observation):
                fences.append(self._realized_lines(observation, "")[1:-1])
                shared = None
                continue
            if shared is None:
                shared = []
                fences.append(shared)
            shared.append(f"it {observation.name}")
        return ["\n".join([_FENCE, *lines, _FENCE]) for lines in fences]

    def _is_realized(self, observation: Observation) -> bool:
        return bool(observation.surface_lines or observation.call_graph)
