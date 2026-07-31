"""@echo decorator - chains Echoer.echo_session in front of an @action.

Diagnostic-only. Expands Echoer.echo_session and prepends its "print everything
inside a DO-NOT-FOLLOW fence then stop" instructions to the base action's prose.
Remove @echo to restore the real behaviour.
"""
from __future__ import annotations

from typing import Any, Callable

from primitives.actions.action import add_action_wrapper, require_action


def echo(func: Callable[..., Any]) -> Callable[..., Any]:
    """Chain Echoer.echo_session in front of an @action method (diagnostic only).

    At expansion time the framework expands echo_session and prepends its
    "collect all instructions, fence them with DO-NOT-FOLLOW, stop" prose to
    the base action. Because echo_session's first instruction is to halt after
    emitting the fence, the base action body is captured but never executed.

    Surfaces ``"echo"`` in the action's wrapper chain, which appears as
    ``chain: [echo, ...]`` in the toolset manifest.

    Raises TypeError when applied to a non-@action target.
    """
    from echo.echo import Echoer

    require_action(func, "echo")
    func._echo_wrapped = True  # type: ignore[attr-defined]
    add_action_wrapper(func, name="echo", chained_action=Echoer.echo_session)
    return func
