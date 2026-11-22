"""The Backlog's folder and where each idea's file lies in it: an idea of its own, a parent's folder, a child kept in
its parent's folder, or a ticket moved back with its whole folder."""

from __future__ import annotations

from pathlib import Path

from space.session.session_record import SESSION_FILE


class BacklogFolder:
    """*BacklogFolder* is the Backlog's folder, ``.sessions/_backlog``: it answers which of its files are ideas. An
    idea is a markdown file in it, or a folder holding a file of its own name: a ticket moved back keeps its whole
    folder, history and all, and a parent keeps its children's files beside its own."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def idea_files(self) -> list[Path]:
        """Every idea's file, by its name: each file in the folder; each folder's file of its own name, unless a file of
        that name beside it makes the folder that file's ticket rather than a second idea; and every other markdown file
        in a folder that holds no ticket's work, a parent's children."""
        folder = self.folder
        if not folder.is_dir():
            return []
        files = list(folder.glob("*.md"))
        kept = [entry / f"{entry.name}.md" for entry in folder.iterdir() if entry.is_dir() and not (folder / f"{entry.name}.md").exists()]
        parents = [path for path in kept if path.is_file()]
        children = [child for parent in parents if not (parent.parent / SESSION_FILE).is_file() for child in parent.parent.glob("*.md") if child != parent]
        return sorted([*files, *parents, *children], key=lambda path: path.stem)

    def place_of(self, file: Path) -> IdeaPlace:
        """Where the idea whose file is file lies in this Backlog."""
        return IdeaPlace(file, self)


class IdeaPlace:
    """*IdeaPlace* is where one idea's file lies in the Backlog, and the only mover of it: kept on its own, in a folder
    of its own name, or in its parent's folder beside the parent's file. An idea's file is its only copy, so a move
    never deletes it or writes over another file; a folder a move leaves empty goes."""

    def __init__(self, file: Path, backlog_folder: BacklogFolder) -> None:
        self.file = file
        self._backlog = backlog_folder

    @property
    def is_in_own_folder(self) -> bool:
        """Whether its file is kept in a folder of its own name."""
        return self.file.parent.name == self.file.stem

    @property
    def ticket_folder(self) -> Path:
        """The folder a ticket's work would be kept in with it: the folder it is kept in, or a folder of its name
        beside it."""
        return self.file.parent if self.is_in_own_folder else self.file.with_suffix("")

    @property
    def holds_ticket(self) -> bool:
        """Whether its folder keeps a ticket's work, a session's record: a parent's folder keeps only ideas."""
        return (self.ticket_folder / SESSION_FILE).is_file()

    @property
    def parent_file(self) -> Path | None:
        """The file of the parent whose folder keeps this one's file, beside the parent's own; none for an idea of its
        own."""
        folder = self.file.parent
        if folder.parent != self._backlog.folder or self.is_in_own_folder:
            return None
        return folder / f"{folder.name}.md"

    def move_under(self, parent: IdeaPlace) -> None:
        """Move its file into parent's folder, beside parent's own file; a parent kept as one file is first moved into a
        folder of its own name."""
        self._move_into(parent._folder_for_children())

    def move_out(self) -> None:
        """Move its file out of its parent's folder, back to the Backlog's own."""
        self._move_into(self._backlog.folder)

    def remove_emptied_folder(self) -> None:
        """Remove the folder of its own name once nothing is left in it, as when its file was taken into a ticket."""
        folder = self.ticket_folder
        if self.is_in_own_folder and folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()

    def _folder_for_children(self) -> Path:
        """The folder that keeps this idea's children: its own folder, made from its one file the first time it takes
        one."""
        if not self.is_in_own_folder:
            folder = self.file.with_suffix("")
            folder.mkdir()
            self._move_into(folder)
        return self.file.parent

    def _move_into(self, folder: Path) -> None:
        """Move its file into folder, under its own name; a folder it leaves empty, other than the Backlog's, goes."""
        left = self.file.parent
        moved = folder / self.file.name
        self.file.replace(moved)
        self.file = moved
        if left != self._backlog.folder and not any(left.iterdir()):
            left.rmdir()
