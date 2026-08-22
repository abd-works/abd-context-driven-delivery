"""Example: open or resume a named sprint using Session.open."""

from workspace.workspace_session import WorkSession


class SprintLifecycle:
    """Minimal pattern for starting or resuming a named sprint."""

    def open_sprint(self, workspace: str, name: str) -> str:
        """Open a sprint under *workspace* with slug *name*.

        Call ``open`` with a descriptive goal on first create so the sprint
        folder and session.md Start block capture intent.
        """
        session = WorkSession(path=workspace, session=name, workspace=workspace)
        return session.open(
            name=name,
            goal="Example sprint — replace with real goal text",
            fidelities="model",
            contexts="bdd",
        )
