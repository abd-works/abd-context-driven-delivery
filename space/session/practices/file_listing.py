"""FileListing - which of a session's files a page lists for the guidance selection and the fidelities its link names."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from space.session.files.file_manager import FileEntry

if TYPE_CHECKING:
    from space.session.practices.guidance_selection import GuidanceSelection
    from space.session.session_paths import SessionPaths


class FileListing:
    """*FileListing* is what a page, such as the Files app, lists of a session's files for the session's guidance
    selection and the fidelities the page's link names, and which of them are the session's own work. The fidelities
    listed are those the selection covers once stages were chosen, else the ones the link names of the practices
    selected, in any stage, so a practice turned off hides its files then too, while the stage the selection shows
    for the ticket until someone chooses hides none a link names. Each file it answers says ``is_listed`` and
    ``is_session_work``, so a page draws what Python decided and restates no rule."""

    def __init__(self, selection: GuidanceSelection, linked: list[str], is_repository: bool, paths: SessionPaths) -> None:
        self._selection = selection
        self._linked = list(linked)
        self._is_repository = is_repository
        self._paths = paths

    @cached_property
    def listed(self) -> list[str]:
        """The fidelities whose files are listed, by slug."""
        if self._selection.is_stage_chosen:
            return self._selection.fidelities
        of_practices = self._selection.fidelities_of_practices
        return [slug for slug in self._linked if slug in of_practices]

    @cached_property
    def formats(self) -> list[str]:
        """The formats of the format groups selected, each once, among the groups the fidelities the selection covers and
        those listed offer; none selected, every format is listed."""
        return list(dict.fromkeys(name for group in self._chosen_groups for name in group.formats))

    @cached_property
    def _chosen_groups(self) -> list:
        """The format groups selected among those the fidelities the selection covers and those listed offer."""
        return [group for group in self._selection.format_groups_with(self.listed) if group.is_selected]

    def of_fidelity(self, slug: str, format: str, entry: FileEntry) -> FileEntry:
        """entry, a file fidelity slug declares in format: listed while slug is listed and format is selected, or no
        format is, or it is published to a link, such as a whiteboard, which opens in Claude whatever format is chosen."""
        in_format = self._in_formats(format, entry)
        is_of_listed = slug in self.listed
        return entry.listed_as(is_of_listed and in_format, self._is_work(entry, is_declared=True), self._hiding(is_of_listed and not in_format))

    def of_root(self, entry: FileEntry) -> FileEntry:
        """entry, a file under the session's root: listed while it is in a format selected, or is published to a link,
        such as a design canvas, and belongs to a fidelity listed. A file no fidelity declares, such as a practice's
        example, belongs to no practice, so it is listed only while no practice is selected, which filters no practice.
        The session's sketch holds a section for every practice and is the next thing its person reviews, so it is
        listed whatever is selected, as a file of the session's own folder is."""
        if self._paths.is_sketch(Path(entry.path)):
            return self.of_folder(entry)
        in_format = self._in_formats(entry.format, entry)
        belongs = any(slug in self.listed for slug in entry.fidelities) if entry.fidelities else self._is_no_practice_selected
        return entry.listed_as(in_format and belongs, self._is_work(entry, is_declared=bool(entry.fidelities)), self._hiding(belongs and not in_format))

    def of_folder(self, entry: FileEntry) -> FileEntry:
        """entry, a file of a session's own folder or workpath, which a page opened on that folder lists whatever is
        selected, since the folder is no fidelity's output, and which is the folder's work."""
        return entry.listed_as(True, self._is_work(entry, is_declared=True))

    def _hiding(self, is_hidden_by_formats: bool) -> list[str]:
        """The labels of the format groups selected, such as markdown or diagram, when they alone leave a file out;
        none when they do not, so a page tells a list the formats emptied from one with no files yet."""
        return self._chosen_labels if is_hidden_by_formats else []

    @cached_property
    def _chosen_labels(self) -> list[str]:
        return [group.label for group in self._chosen_groups]

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
