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

    # One process answers every chat, so every tool call and every session of a checkout works on one Repo, which holds
    # the one WorkState of its .sessions/session.json.
    with context("that two tool calls name"):
        with before.each:
            subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
            (self.root / "docs").mkdir()

        with it("should be one repository for both"):
            expect(Repo.of_project(self.root) is Repo.of_project(self.root / "docs")).to(be_true)

        with it("should be the repository the checkout's sessions work in"):
            from space.session.sessions import Sessions

            expect(Sessions.of_project(self.root).repo is Repo.of_project(self.root)).to(be_true)

        with it("should be its own main clone"):
            expect(Repo.of_project(self.root).main_clone is Repo.of_project(self.root)).to(be_true)
