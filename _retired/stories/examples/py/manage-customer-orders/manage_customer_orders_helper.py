"""Epic-level helper for the Manage Customer Orders code examples.

Kept as a snake_case module because Python's import system does not accept
hyphens in module names. This is the single naming exception in the code
family — every other file and folder uses kebab-case (matching story slugs).

The helper collects shared type aliases and background factories that the
per-story `<slug>-stories.py` files can reuse. When those files are loaded
by hand (via importlib) rather than by `import` they still work; the epic
helper is the one module tests / adapters can import directly by name.

See: `stories/src/formats/code/architecture-context.md`
"""
from __future__ import annotations

from typing import Literal, TypedDict, Union


class Given(TypedDict):
    given: str


class When(TypedDict):
    when: str


class Then(TypedDict):
    then: str


class And(TypedDict):
    and_: str  # `and` is a Python keyword; adapter maps this back to "and"


class But(TypedDict):
    but: str


Step = Union[Given, When, Then, And, But]
Background = tuple[Given, ...]


StoryStatus = Literal["stub", "exploration", "specification", "engineering"]


def default_background(customer_handle: str = "alex.morgan") -> Background:
    """Standard Background reused across most stories in this epic."""
    return (
        {"given": f'a Customer "{customer_handle}" is signed in with a populated Cart'},
    )
