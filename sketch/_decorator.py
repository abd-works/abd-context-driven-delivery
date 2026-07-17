"""@sketch decorator — chains Sketcher.sketch_session in front of an @action.

The decorator registers a chained_action reference on the target function.
At expansion time, ActionExpander expands Sketcher.sketch_session and prepends
its real instructions to the base action's prose — no preamble strings.
"""
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Callable

from action.action import add_action_wrapper, require_action


def sketch(func: Callable[..., Any]) -> Callable[..., Any]:
    """Chain Sketcher.sketch_session in front of an @action method.

    At expansion time the framework expands sketch_session and prepends its
    prose to the base action's instructions. The base action is unchanged;
    its body runs after the sketch loop completes.

    Captures the directory of the module containing the decorated function and
    passes it as ``agent_dir`` to ``sketch_session`` via ``static_kwargs``.
    This enables tiered template discovery to find the agent's own
    ``sketch-template.*`` file (e.g. ``ooad/sketch-template.md``) rather than
    falling back to the default.

    Surfaces ``"sketch"`` in the action's wrapper chain, which appears as
    ``chain: [sketch, ...]`` in the toolset manifest so the AI sees the full
    pipeline before calling.

    Raises TypeError when applied to a non-@action target.
    """
    from sketch.sketch import Sketcher

    require_action(func, "sketch")
    func._sketch_wrapped = True  # type: ignore[attr-defined]

    try:
        agent_dir = str(Path(inspect.getfile(func)).parent)
    except (TypeError, OSError):
        agent_dir = ""

    add_action_wrapper(
        func,
        name="sketch",
        chained_action=Sketcher.sketch_session,
        static_kwargs={"agent_dir": agent_dir} if agent_dir else {},
    )
    return func
