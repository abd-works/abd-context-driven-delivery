"""A session.json the board could not read, which it names instead of showing no ticket at all."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.installation.data_class import data_field
from harness.installation.json_file import JsonFileUnreadable

if TYPE_CHECKING:
    from space.repo.repo import Repo


class UnreadableSessionFile:
    """*UnreadableSessionFile* is one ticket's session.json that does not hold a JSON object, such as a file a crash
    cut off half way or one left with a merge's conflict marks. The board shows every other ticket and names this
    file, with what is wrong in it, so a person repairs it; nothing is written over it. Made from the failure the read
    raised, in the repository the board reads."""

    def __init__(self, repo: Repo, failure: JsonFileUnreadable) -> None:
        self._repo = repo
        self._failure = failure

    @property
    @data_field
    def file(self) -> str:
        """The file, as a path from the repository's top."""
        return self._repo.path_from_top(self._failure.path)

    @property
    @data_field
    def error(self) -> str:
        """What the read said is wrong, naming the file in full."""
        return str(self._failure)
