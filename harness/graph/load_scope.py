"""LoadScope. The folder one load or refresh of a graph reads, and the files it is limited to."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from harness.graph.skipped_folders import SKIPPED_FOLDERS, scanned_files

# A refresh reads files a practice keeps in `.context` (model documents, bounded contexts, story maps); every other
# skipped folder, such as a session's reports in `.sessions`, holds nothing a practice reads.
_REFRESH_SKIPPED_FOLDERS = SKIPPED_FOLDERS - {".context"}


class LoadScope:
    """The folder one load or refresh reads, and the files it is limited to: every source file under the folder for a
    load of the whole working copy, or only the files a call names, for a load of the files being edited or a refresh.
    Each call that reads makes its own, and the graph keeps the scope of the read it last made (``graph.scope``), which
    the practices' readers ask while they read: which source files to read, which of them were edited, and the folders
    holding those. A refresh names a file that is gone so that its nodes drop; only the files still there are read."""

    def __init__(self, folder: Path | None, named: Iterable[Path] | None = None, over_whole: bool = False) -> None:
        self.folder = folder
        # Whether the read stands on a graph of the whole working copy: a load of it, or a refresh of named files in it.
        # A load of named files alone (`graph.load_files`) does not, so links across practices cannot be judged there.
        self.over_whole = named is None or over_whole
        # Every file the call names, gone or not; none when the whole folder is read.
        self.named = None if named is None else sorted(set(named))
        # The named files that are there to read.
        self.edited_files = None if self.named is None else [path for path in self.named if path.is_file()]

    @classmethod
    def of_paths(cls, folder: Path, paths: Iterable[str], skipped: frozenset[str] = frozenset()) -> LoadScope:
        """The files at paths under folder, each absolute or from folder: a folder stands for the source files under
        it, and a path outside folder, or inside a folder named in skipped, is left out."""
        root = folder.resolve()
        named: list[Path] = []
        for item in paths or []:
            path = (Path(item) if Path(item).is_absolute() else folder / item).resolve()
            if path != root and root not in path.parents:
                continue
            if skipped.intersection(path.relative_to(root).parts):
                continue
            if path.is_dir():
                named.extend(file.resolve() for file in scanned_files(path))
            else:
                named.append(path)
        return cls(folder, named)

    def refreshing(self, paths: Iterable[str]) -> LoadScope:
        """The scope a refresh of paths reads in this scope's folder: the files at paths, outside the folders no practice
        reads; none of them when no folder is loaded."""
        if self.folder is None:
            return LoadScope(None, [])
        refreshed = self.of_paths(self.folder, paths, _REFRESH_SKIPPED_FOLDERS)
        return LoadScope(refreshed.folder, refreshed.named, over_whole=self.over_whole)

    def source_files(self, root: Path, suffixes: set[str]) -> list[Path]:
        """The files with these suffixes under root; only the edited ones when the scope names files."""
        if self.edited_files is None:
            return scanned_files(root, suffixes)
        return [path for path in self.edited_files if path.suffix.lower() in suffixes]

    @property
    def folders(self) -> list[Path] | None:
        """The folders holding the edited files, below the loaded folder; none when the whole folder is read."""
        if self.edited_files is None or self.folder is None:
            return None
        folder = self.folder.resolve()
        return sorted({parent for path in self.edited_files for parent in path.parents if parent != folder and folder in parent.parents})
