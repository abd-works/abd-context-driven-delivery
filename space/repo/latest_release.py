"""The end-to-end results kept once a release lands on the default branch: the landed release's only.

Each release keeps its results in ``.sessions/<release>/e2e-test-results``; screenshots there stay on the machine that
took them (git ignores ``*.png``). When a release lands, its screenshots are pushed as the single commit of the
``e2e-latest`` branch, so the next release can compare against them anywhere, and every older release that finished a
run loses its results: deleted here and committed on the default branch. A release that never finished a run (no
``story-map.html``), such as pml-my's saved recordings, is left alone.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from space.work_state import E2E_RESULTS_FOLDER

if TYPE_CHECKING:
    from space.repo.repo import Repo

LATEST_BRANCH = "e2e-latest"
_RELEASE_MARK = "story-map.html"
# Adding and pushing a full run's screenshots (about a gigabyte) takes minutes, not git's default seconds.
_LARGE_TRANSFER_SECONDS = 1800


class LatestRelease:
    """The release that just landed on the default branch of the clone ``repository``."""

    def __init__(self, repository: Repo, release: str) -> None:
        self._repository = repository
        self.release = release

    @property
    def _sessions(self) -> Path:
        return Path(self._repository.root) / ".sessions"

    def keep(self) -> list[str]:
        """Push this release's screenshots to ``e2e-latest``, then remove every older release's results.

        Returns the releases whose results were removed."""
        if not self._finished_run(self.release):
            return []
        self._publish_screenshots()
        return self._prune_older()

    def _finished_run(self, release: str) -> bool:
        return (self._results(release) / _RELEASE_MARK).is_file()

    def _results(self, release: str) -> Path:
        return self._sessions / release / E2E_RESULTS_FOLDER

    def _publish_screenshots(self) -> None:
        """One commit with no parent, holding only this release's screenshots, force-pushed over the last one."""
        folder = f".sessions/{self.release}/{E2E_RESULTS_FOLDER}"
        with tempfile.TemporaryDirectory() as scratch:
            index = {"GIT_INDEX_FILE": str(Path(scratch) / "index")}
            self._git("add", "--force", "--", f":(glob){folder}/**/*.png", env=index)
            tree = self._git("write-tree", env=index)
        commit = self._git("commit-tree", tree, "-m", f"e2e screenshots: {self.release}")
        self._git("push", "--force", "origin", f"{commit}:refs/heads/{LATEST_BRANCH}")

    def _prune_older(self) -> list[str]:
        older = sorted(
            folder.name
            for folder in self._sessions.iterdir()
            if folder.is_dir() and folder.name != self.release and self._finished_run(folder.name)
        )
        if not older:
            return []
        for release in older:
            shutil.rmtree(self._results(release))
        self._commit_removal(older)
        return older

    def _commit_removal(self, older: list[str]) -> None:
        folders = [f".sessions/{release}/{E2E_RESULTS_FOLDER}" for release in older]
        self._git("rm", "-r", "--cached", "--quiet", "--ignore-unmatch", "--", *folders)
        if not self._git("status", "--porcelain", "--", *folders):
            return
        self._git("commit", "-m", f"e2e results: keep {self.release} only; remove {', '.join(older)}")
        self._git("push", "origin", "HEAD")

    def _git(self, *args: str, env: dict[str, str] | None = None) -> str:
        return type(self._repository).git(self._repository.root, *args, env=env, timeout=_LARGE_TRANSFER_SECONDS)
