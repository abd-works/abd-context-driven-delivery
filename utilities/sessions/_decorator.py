"""@workspace_session decorator — chains WorkspaceSession.workspace_session_bind in front of an @action.

The decorator registers a chained_action reference on the target function.
At expansion time, ActionExpander expands workspace_session_bind against the
host instance (when it merges WorkspaceSession) and prepends its prose.
"""
from __future__ import annotations

from typing import Any, Callable

from primitives.actions.action import add_action_wrapper, require_action


def workspace_session(func: Callable[..., Any]) -> Callable[..., Any]:
    """Chain WorkspaceSession.workspace_session_bind in front of an @action.

    At expansion time the framework expands workspace_session_bind and prepends
    its prose (session_guidance + live session resource) to the base action.

    Surfaces ``"workspace_session"`` in the action's wrapper chain, which appears
    as ``chain: [workspace_session, ...]`` in the toolset manifest.

    Raises TypeError when applied to a non-@action target.
    """
    from sessions.workspace_session import WorkspaceSession

    require_action(func, "workspace_session")
    func._workspace_session_wrapped = True  # type: ignore[attr-defined]
    add_action_wrapper(
        func,
        name="workspace_session",
        chained_action=WorkspaceSession.workspace_session_bind,
    )
    return func
