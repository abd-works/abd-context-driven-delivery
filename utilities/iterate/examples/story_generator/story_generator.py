"""story_generator — shows Iterator driving one grilled story-map slice toward a goal."""
from __future__ import annotations

from iterate.iterate import Iterator


class StoryGenerator:
    """Example: iterate a story-map one grilled slice at a time toward a delivery goal."""

    def generate_slice(self, path: str, goal: str) -> str:
        """Produce one validated output slice toward *goal* under *path*.

        Instantiates Iterator rooted at the session path, then calls
        iterate_session so the framework grills the plan, marks a tick,
        generates only the unlocked slice, and validates it — one tick only.
        """
        iterator = Iterator(path=path)
        return iterator.iterate_session(plan=goal)
