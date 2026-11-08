"""*GitCitation*, the only source citation catalog pages give: a git blob URL in the repository the catalog shows."""
from __future__ import annotations

import inspect
from pathlib import Path

from harness.process.git import Git

_REPO_ROOT = Path(__file__).resolve().parents[2]


class GitCitation:
    """Git blob URLs, the only source citation catalog pages give. An SSH remote and a trailing ``.git`` are written
    as the plain https address of the repository."""

    def __init__(self, repo_url: str = "", ref: str = "") -> None:
        self.repo_url = self._https(repo_url)
        self.ref = ref

    @classmethod
    def from_checkout(cls, repo_root: Path | None = None) -> GitCitation:
        """The checkout's origin and the commit it has checked out."""
        git = Git(repo_root or _REPO_ROOT)
        return cls(git.run("remote", "get-url", "origin"), git.run("rev-parse", "HEAD"))

    def blob_url(self, path: Path, lines: tuple[int, int] | None = None) -> str:
        try:
            relative = path.resolve().relative_to(_REPO_ROOT)
        except ValueError:
            relative = path
        url = f"{self.repo_url.rstrip('/')}/blob/{self.ref}/{relative.as_posix()}"
        if lines:
            start, end = lines
            url += f"#L{start}-L{end}" if end != start else f"#L{start}"
        return url

    def blob_url_for_callable(self, func: object) -> str:
        source_file = Path(inspect.getsourcefile(func))  # type: ignore[arg-type]
        _, start_line = inspect.getsourcelines(func)  # type: ignore[arg-type]
        end_line = start_line + len(inspect.getsource(func).splitlines()) - 1  # type: ignore[arg-type]
        return self.blob_url(source_file, (start_line, end_line))

    def _https(self, repo_url: str) -> str:
        url = repo_url.strip()
        if url.startswith("git@"):
            hostname, _, path = url[len("git@"):].partition(":")
            url = f"https://{hostname}/{path}"
        return url[: -len(".git")] if url.endswith(".git") else url
