"""Each story of one story map beside its copy in another map, so a copy of the map delivers its own copies in each
increment."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from cdd_guidance.practices.stories.model.story_model import Increment, Story, StoryModel


class StoryCopies:
    """A story map (``original``) beside a copy of it (``copy``) that copied the original's stories in order: each
    original story beside its copy."""

    def __init__(self, original: "StoryModel", copy: "StoryModel") -> None:
        self._copy = copy
        self._increments = list(original.increments)
        self._copies = {id(story): copied for story, copied in zip(original.descendants.stories(), copy.descendants.stories())}

    def copy_increments(self, copy_increment: Callable[["Increment"], "Increment"]) -> None:
        """Give the copy each increment of the original, as copy_increment copies it, delivering the copies of the
        stories the original's increment delivers."""
        for increment in self._increments:
            copied = copy_increment(increment)
            copied.stories = self._delivered_by(increment)
            self._copy.increments.append(copied)

    def _delivered_by(self, increment: "Increment") -> List["Story"]:
        return [self._copies[id(story)] for story in increment.stories if id(story) in self._copies]
