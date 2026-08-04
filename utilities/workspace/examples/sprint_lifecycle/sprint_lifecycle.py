"""Example: open or resume a named sprint using Session.ensure_session."""

from __future__ import annotations

from workspace.workspace_session import Session


class SprintLifecycle(Session):
    """Manage a named sprint workspace: open or resume in a single call."""

    def open_sprint(self, workspace: str, name: str) -> str:
        """Start or resume the sprint named *name* under *workspace*.

        Instantiates a ``Session`` bound to *workspace*, then calls
        ``ensure_session`` with a descriptive goal so the sprint folder and
        ``session.md`` are created when missing or left untouched when they
        already exist.

        Returns the absolute path to the ``session.md`` file.
        """
        session = Session(workspace=workspace)
        return session.ensure_session(
            name=name,
            goal="Deliver sprint increment for the named scope",
            fidelities="context, stories, bdd",
            path=workspace,
        )
