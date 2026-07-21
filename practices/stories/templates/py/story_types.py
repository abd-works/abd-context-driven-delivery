"""Story types for Python spec-files.

Python's type system is dynamic — we can't produce a compile-time analogue of
TypeScript's `TierImpl<S>`. Instead the runner does runtime step-key
assertions (see `story_runner.py`): every step string in a scenario must
resolve to a callable in `tier.given` / `tier.when` / `tier.then`; missing
keys fail the run with a clear message.

The Story shape mirrors the TS reference architecture:

    STORY: Story = {
        "story": "Submit Order",
        "actor": "Customer",
        "domain_terms": ("Order", "Cart"),
        "evidence": ("Checkout workshop 2026-05-04",),

        "scenario_key": {
            "name": "order accepted for a valid cart and payment",
            "given": ("a Cart CART-9001 containing 3 Items totalling 149.98 USD",),
            "interactions": (
                {
                    "when": ("the Customer submits the Order",),
                    "then": ("an Order is created with status placed",),
                },
            ),
        },
    }

`given`, and every `when` / `then` inside an interaction, is a tuple of
plain-prose step strings. First step of each phase is unprefixed; continuation
steps carry their own `"And "` / `"But "` prefix inside the string, and the
tier's `given` / `when` / `then` dicts use the SAME string as the dispatch key.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Tuple, TypedDict, Union


StepFn = Callable[[], Union[None, Awaitable[None]]]
"""One step body. May be sync or async — the runner awaits either."""


class Interaction(TypedDict):
    """A when-then block within a scenario."""

    when: Tuple[str, ...]
    then: Tuple[str, ...]


class Scenario(TypedDict):
    """A behaviour walk-through under a story."""

    name: str
    given: Tuple[str, ...]
    interactions: Tuple[Interaction, ...]


# `Story` is a Story metadata dict merged with one Scenario per key. Python
# can't statically enforce the union like TS, so this is documented as a
# convention: unknown extra keys are treated as Scenario values by the runner.
Story = Dict[str, Any]


class TierImpl(TypedDict):
    """Tier contract — dispatch tables plus a cleanup hook.

    `given` / `when` / `then` are dicts keyed by the EXACT step strings from
    the scenario. `cleanup` runs after every scenario, regardless of outcome.
    """

    given: Dict[str, StepFn]
    when: Dict[str, StepFn]
    then: Dict[str, StepFn]
    cleanup: StepFn
