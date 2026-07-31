"""@sketch decorator - chains Sketcher.sketch_session in front of an @action.

sketch_session calls grill_with_context in-method; expanding the chain pulls
that nested grill prose then sketch cadence.
"""
from __future__ import annotations

from typing import Any, Callable

from primitives.actions.action import OWNER_MODULE_DIR, add_action_wrapper, require_action


def sketch(func: Callable[..., Any]) -> Callable[..., Any]:
    """Chain Sketcher.sketch_session in front of an @action.

    Grill comes from ``sketch_session``'s in-method
    ``self._grill_context().grill_with_context(...)`` call.

    ``agent_dir`` resolves at manifest time to the concrete toolset owner's module
    directory (``@owner``) so domain templates are found when ``sketch`` lives on base Context.

    Raises TypeError when applied to a non-@action target.
    """
    from sketch.sketch import Sketcher

    require_action(func, "sketch")
    func._sketch_wrapped = True  # type: ignore[attr-defined]

    add_action_wrapper(
        func,
        name="sketch",
        chained_action=Sketcher.sketch_session,
        static_kwargs={"agent_dir": OWNER_MODULE_DIR},
    )
    return func
