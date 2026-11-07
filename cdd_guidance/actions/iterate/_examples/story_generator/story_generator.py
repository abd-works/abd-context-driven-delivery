"""story_generator — shows Iterate driving one grilled story-map slice toward a goal."""
from __future__ import annotations

from cdd_guidance.actions.iterate.iterate import Iterate


class StoryGenerator:
    """Example: iterate a story-map one grilled slice at a time toward a delivery goal."""

    def generate_slice(self, path: str, goal: str) -> str:
        """Produce one validated output slice toward *goal* under *path*.

        Instantiates Iterate rooted at the session path, then calls
        iterate_session so the framework grills the plan, marks the cycle due,
        generates only the unlocked slice, and validates it — one cycle only.
        """
        iterator = Iterate(path=path)
        return iterator.iterate_session(plan=goal)
