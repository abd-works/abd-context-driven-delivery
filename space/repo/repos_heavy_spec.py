"""Repos - the repositories kept beside one another, and opening one in a chat of its own."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.mcp.cdd_home import CddHome
from harness.git.git import Git
from space.repo.new_repository import FolderIsAWorktreeError
from space.repo.repos import CddConfig, InstallFailedError, NotAReposFolderError, PublishFailedError, Repos, RepoNameRequiredError, UnknownVisibilityError


def _repository(folder: Path) -> Path:
    folder.mkdir(parents=True)
    git = Git(folder)
    git.run("init", "-b", "main")
    (folder / "README.md").write_text("x\n", encoding="utf-8")
    git.run("add", "-A")
    git.run("-c", "user.name=spec", "-c", "user.email=spec@example.com", "commit", "-m", "first")
    return folder


with description("Repos") as self:
    with before.each:
        self.top = Path(tempfile.mkdtemp(prefix="cdd-repos-")).resolve()
        self.home = CddHome(self.top / ".cdd")
        self.here = _repository(self.top / "abd-cdd")
        self.repos = Repos(self.here, CddConfig.in_home(self.home))

    with after.each:
        shutil.rmtree(self.top, ignore_errors=True)

    with context("with no repos folder chosen"):
        with it("should keep repositories beside the calling chat's main clone"):
            expect(self.repos.folder).to(equal(self.top))

    with context("choosing the repos folder"):
        with it("should keep the folder chosen in the person's cdd config"):
            chosen = self.top / "elsewhere"
            chosen.mkdir()
            self.repos.set_folder(str(chosen))
            expect(Repos(self.here, CddConfig.in_home(self.home)).folder).to(equal(chosen.resolve()))

        with it("should refuse a folder that is not there"):
            expect(lambda: self.repos.set_folder(str(self.top / "missing"))).to(raise_error(NotAReposFolderError))

    with context("listing the repositories beside one another"):
        with before.each:
            _repository(self.top / "other")
            (self.top / "plain-folder").mkdir()
            self.here_git = Git(self.here)
            self.here_git.run("worktree", "add", "-b", "ticket-1", str(self.top / "abd-cdd-ticket-1"))

        with it("should list each repository, leaving out plain folders and linked worktrees"):
            expect([repo.name for repo in self.repos.siblings()]).to(equal(["abd-cdd", "other"]))

        with it("should name each repository's branch"):
            expect({repo.name: repo.branch for repo in self.repos.siblings()}["other"]).to(equal("main"))

    with context("opening a repository that is not there yet"):
        with before.each:
            (self.here / ".gitignore").write_text("never-mind\n", encoding="utf-8")
            self.answer = self.repos.open("new-work", publish=False, install=False, start_chat=False)
            self.root = self.top / "new-work"

        with it("should create it on main with a first commit"):
            expect(Git(self.root).run("branch", "--show-current")).to(equal("main"))
            expect(Git(self.root).run("log", "--format=%s")).to(contain("Initial commit"))

        with it("should ignore what the CDD checkout ignores, committed"):
            ignored = (self.root / ".gitignore").read_text(encoding="utf-8")
            expect(ignored).to(contain(".sessions/main/session.log"))
            expect(Git(self.root).run("status", "--porcelain")).to(equal(""))

        with it("should say how to start the repository's own chat"):
            expect(self.answer).to(contain("start_session"))
            expect(self.answer).to(contain(str(self.root)))

        with it("should leave a repository there as it is when opened again"):
            again = self.repos.open("new-work", publish=False, install=False, start_chat=False)
            expect(again).to(contain("is a repository already, on main"))
            expect(again).to(contain(".gitignore already ignores"))

    with context("publishing a repository that has an origin already"):
        with before.each:
            self.root = _repository(self.top / "has-origin")
            self.origin = self.top / "origin.git"
            Git(self.top).run("init", "--bare", "-b", "main", str(self.origin))
            Git(self.root).run("remote", "add", "origin", str(self.origin))

        with it("should push main there instead of creating a GitHub repository"):
            answer = self.repos.open("has-origin", install=False, start_chat=False)
            expect(answer).to(contain("Pushed main to its origin"))
            expect(Git(self.origin).run("rev-parse", "main")).to(equal(Git(self.root).run("rev-parse", "HEAD")))

        with it("should say it is published once origin has main"):
            self.repos.open("has-origin", install=False, start_chat=False)
            expect(self.repos.open("has-origin", install=False, start_chat=False)).to(contain("Already published"))

    with context("opening a linked worktree as a repository"):
        with it("should refuse it"):
            Git(self.here).run("worktree", "add", "-b", "ticket-2", str(self.top / "wt"))
            expect(lambda: self.repos.open("wt", publish=False, install=False, start_chat=False)).to(raise_error(FolderIsAWorktreeError))

    with context("opening a repository without a name"):
        with it("should refuse"):
            expect(lambda: self.repos.open(" ", publish=False, install=False, start_chat=False)).to(raise_error(RepoNameRequiredError))

    with context("opening a repository with a visibility GitHub does not offer"):
        with it("should refuse, naming the visibility"):
            expect(lambda: self.repos.open("shop", visibility="secret", publish=True, install=False, start_chat=False)).to(
                raise_error(UnknownVisibilityError, contain("secret"))
            )

    with context("publishing a new repository on a machine without the GitHub CLI"):
        with it("should refuse, saying to install gh or open it without publishing"):
            with patch("space.repo.repos.shutil.which", return_value=None):
                opening = lambda: self.repos.open("shop", publish=True, install=False, start_chat=False)
                expect(opening).to(raise_error(PublishFailedError, contain("gh", "publish false")))

    with context("installing CDD into a new repository whose install fails"):
        with it("should refuse, naming the folder and what the install said"):
            failed = subprocess.CompletedProcess([], 1, stdout="", stderr="no module named harness")
            with patch("space.repo.repos.subprocess.run", return_value=failed):
                opening = lambda: self.repos.open("shop", publish=False, install=True, start_chat=False)
                expect(opening).to(raise_error(InstallFailedError, contain(".claude", "no module named harness")))
