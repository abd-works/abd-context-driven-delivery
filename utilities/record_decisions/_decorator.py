"""@record_decisions decorator - chains RecordDecisions.record_decisions_session in front of an @action.

The decorator registers a chained_action reference on the target function.
At expansion time, ActionExpander expands record_decisions_session and prepends
its real instructions to the base action's prose - no preamble strings.
"""
from __future__ import annotations

from typing import Any, Callable

from primitives.actions.action import add_action_wrapper, require_action


def record_decisions(func: Callable[..., Any]) -> Callable[..., Any]:
    """Chain RecordDecisions.record_decisions_session in front of an @action method.

    At expansion time the framework expands record_decisions_session and prepends
    its prose to the base action's instructions. The base action is unchanged;
    CDR guidance stays active while the rest of the chain (grill, sketch, generate)
    runs, so decisions can be recorded as they crystallise.

    Surfaces ``"record_decisions"`` in the action's wrapper chain, which appears as
    ``chain: [record_decisions, ...]`` in the toolset manifest.

    Raises TypeError when applied to a non-@action target.
    """
    from record_decisions.record_decisions import RecordDecisions

    require_action(func, "record_decisions")
    func._record_decisions_wrapped = True  # type: ignore[attr-defined]
    add_action_wrapper(
        func,
        name="record_decisions",
        chained_action=RecordDecisions.record_decisions_session,
    )
    return func
