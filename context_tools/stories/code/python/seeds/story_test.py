"""Mamba/RSpec-style base for story scenarios. Copy to tests/story_test.py."""

from __future__ import annotations

from typing import Generic, TypeVar

TApp = TypeVar("TApp")


class StoryScenario(Generic[TApp]):
    """Subclass per story file — boot infrastructure once, background once, reuse state."""

    app: TApp

    @classmethod
    def boot(cls) -> TApp:
        """Infrastructure only (browser, config, wiring). Call from before.all."""
        raise NotImplementedError(f"{cls.__name__}.boot()")

    def background(self) -> None:
        """Shared Given steps for every scenario in this story."""
