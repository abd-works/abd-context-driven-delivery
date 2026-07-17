"""@grill_with_context decorator — chains GrillContext.grill_with_context in front of an @action.

The decorator registers a chained_action reference on the target function.
At expansion time, ActionExpander expands grill_with_context and prepends its
real instructions to the base action's prose — no preamble strings.
"""
from __future__ import annotations

from typing import Any, Callable

from action.action import add_action_wrapper, require_action


def grill_with_context(func: Callable[..., Any]) -> Callable[..., Any]:
    """Chain GrillContext.grill_with_context in front of an @action method.

    At expansion time the framework expands grill_with_context and prepends
    its prose to the base action's instructions. The base action is unchanged;
    its body runs after the grill loop completes.

    Surfaces ``"grill_with_context"`` in the action's wrapper chain, which
    appears as ``chain: [grill_with_context, ...]`` in the toolset manifest.

    Raises TypeError when applied to a non-@action target.
    """
    from grill_context.grill_context import GrillContext

    require_action(func, "grill_with_context")
    func._grill_wrapped = True  # type: ignore[attr-defined]
    add_action_wrapper(
        func,
        name="grill_with_context",
        chained_action=GrillContext.grill_with_context,
    )
    return func
