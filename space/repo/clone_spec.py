"""BDD spec — whether a folder is a git clone the board can list worktrees in."""
import shutil
import subprocess
import tempfile
from pathlib import Path

from expects import be_false, be_true, expect
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from space.repo.repo import Repo  # noqa: E402


with description("a project folder") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="clone-spec-"))

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("with an empty .git folder that only marks its root"):
        with before.each:
            (self.root / ".git").mkdir()

        with it("should not be a clone"):
            expect(Repo(self.root).is_clone).to(be_false)

    with context("that git has made a repository"):
        with before.each:
            subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

        with it("should be a clone"):
            expect(Repo(self.root).is_clone).to(be_true)
