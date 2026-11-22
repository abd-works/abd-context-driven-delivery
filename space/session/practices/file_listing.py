"""FileListing - which of a session's files a page lists for the guidance selection and the fidelities its link names."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from space.session.files.file_manager import FileEntry

if TYPE_CHECKING:
    from space.session.practices.guidance_selection import GuidanceSelection


class FileListing:
    """*FileListing* is what a page, such as the Files app, lists of a session's files for the session's guidance
    selection and the fidelities the page's link names, and which of them are the session's own work. The fidelities
    listed are those the selection covers once stages were chosen, else the ones the link names that the selection
    covers, so a practice turned off hides its files then too. Each file it answers says ``is_listed`` and
    ``is_session_work``, so a page draws what Python decided and restates no rule."""

    def __init__(self, selection: GuidanceSelection, linked: list[str], is_repository: bool) -> None:
        self._selection = selection
        self._linked = list(linked)
        self._is_repository = is_repository

    @cached_property
    def listed(self) -> list[str]:
        """The fidelities whose files are listed, by slug."""
        covered = self._selection.fidelities
        return covered if self._selection.is_stage_chosen else [slug for slug in self._linked if slug in covered]

    @cached_property
    def formats(self) -> list[str]:
        """The formats of the format groups selected, each once; none selected, every format is listed."""
        return list(dict.fromkeys(name for group in self._selection.formats if group.is_selected for name in group.formats))

    def of_fidelity(self, slug: str, format: str, entry: FileEntry) -> FileEntry:
        """entry, a file fidelity slug declares in format: listed while slug is listed and format is selected, or no
        format is, or it is published to a link, such as a whiteboard, which opens in Claude whatever format is chosen."""
        listed = slug in self.listed and self._in_formats(format, entry)
        return entry.listed_as(listed, self._is_work(entry, is_declared=True))

    def of_root(self, entry: FileEntry) -> FileEntry:
        """entry, a file under the session's root: listed while it is in a format selected and belongs to a fidelity
        listed. A file no fidelity declares, such as a practice's example, belongs to no practice, so it is listed only
        while no practice is selected, which filters no practice."""
        formats = self.formats
        in_format = not formats or entry.format in formats
        belongs = any(slug in self.listed for slug in entry.fidelities) if entry.fidelities else self._is_no_practice_selected
        return entry.listed_as(in_format and belongs, self._is_work(entry, is_declared=bool(entry.fidelities)))

    def of_folder(self, entry: FileEntry) -> FileEntry:
        """entry, a file of a session's own folder or workpath, which a page opened on that folder lists whatever is
        selected, since the folder is no fidelity's output, and which is the folder's work."""
        return entry.listed_as(True, self._is_work(entry, is_declared=True))

    def _in_formats(self, format: str, entry: FileEntry) -> bool:
        formats = self.formats
        return not formats or bool(entry.link) or format in formats

    def _is_work(self, entry: FileEntry, is_declared: bool) -> bool:
        """In a git repository, a file the branch changed; in a plain folder, a file a fidelity declares or holds that
        is there."""
        return entry.is_changed if self._is_repository else entry.exists and is_declared

    @cached_property
    def _is_no_practice_selected(self) -> bool:
        return not any(practice.is_selected for practice in self._selection.practices)
