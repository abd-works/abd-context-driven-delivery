"""ChangedArtifact - a file just edited in a session, checked against the graph rules of each fidelity the session shows
that declares it, with no explicit validate, so the chat bar's violation count follows every edit."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.installation.data_class import data_field

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance
    from space.session.session import Session


class ChangedArtifact:
    """A file a person or an agent just changed in a session. Checking it runs Validate on it for each fidelity the
    session's guidance selection shows (``GuidanceSelection.covered``) whose practice the session works on and which
    declares the file, so the graph rules run on it as they would on an explicit validate: a report is saved beside the
    graph it checked and the session's log gets the validate line the board and the chat bar count violations from. A
    file no shown fidelity declares, or one outside the session's roots, is checked by none of them: nothing is there to
    check, so nothing is written."""

    def __init__(self, session: Session, path: str) -> None:
        self._session = session
        self._path = path
        # The fidelities whose graph rules ran on the file, set by check.
        self._checked: list[FidelityGuidance] = []

    @property
    @data_field
    def path(self) -> str:
        """The changed file, as the edit named it: from the project's root, or absolute."""
        return self._path

    @property
    @data_field
    def checked(self) -> list[str]:
        """The slug of each fidelity whose graph rules ran on the file, such as stories-story-map; none when no fidelity
        the session shows declares it."""
        return [fidelity.slug for fidelity in self._checked]

    def check(self) -> ChangedArtifact:
        """Run the graph rules of each fidelity that declares the file on it, as Validate runs them on the file alone."""
        declaring = self._declaring()
        for fidelity in declaring:
            fidelity.actions.validate(paths=[self._path])
        self._checked = declaring
        return self

    def _declaring(self) -> list[FidelityGuidance]:
        """Each fidelity the session shows, of a practice it works on, that declares the file; none for a file that is
        gone or lies outside the session's roots, which Validate would refuse."""
        file = self._session.paths.path_named(self._path)
        if not file.is_file() or not self._session.session_files.in_root(file):
            return []
        written = self._session.paths.from_project(file)
        shown = self._session.guidance.covered
        return [fidelity for fidelity in shown if fidelity.session_output.is_enabled and fidelity.declared.includes(written)]
