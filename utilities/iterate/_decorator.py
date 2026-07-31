"""@iterate decorator - chains Iterator.iterate_session in front of an @action.

iterate_session calls grill_with_context in-method; expanding the chain pulls
that nested grill prose then iterate cadence.
"""
from __future__ import annotations

from typing import Any, Callable

from primitives.actions.action import add_action_wrapper, require_action


def iterate(func: Callable[..., Any]) -> Callable[..., Any]:
    """Chain Iterator.iterate_session in front of an @action.

    Grill comes from ``iterate_session``'s in-method
    ``self._grill_context().grill_with_context(...)`` call.

    Raises TypeError when applied to a non-@action target.
    """
    from iterate.iterate import Iterator

    require_action(func, "iterate")
    func._iterate_wrapped = True  # type: ignore[attr-defined]

    add_action_wrapper(
        func,
        name="iterate",
        chained_action=Iterator.iterate_session,
    )
    return func
