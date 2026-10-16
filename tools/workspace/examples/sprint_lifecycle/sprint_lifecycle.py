"""Example: open or resume a named sprint using Workspace.open_work_session."""

from workspace.workspace import Workspace


class SprintLifecycle:
    """Minimal pattern for starting or resuming a named sprint."""

    def open_sprint(self, workspace: str, name: str) -> str:
        """Open a sprint under *workspace* with slug *name*.

        Call ``open_work_session`` with a descriptive goal on first create so the sprint
        folder and session.md Start block capture intent.
        """
        parent = Workspace(workspace)
        session = parent.open_work_session(
            name=name,
            goal="Example sprint — replace with real goal text",
            fidelities="model",
            contexts="bdd",
        )
        return session.session_branch
