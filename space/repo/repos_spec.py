"""Repos - the repositories kept beside one another, and opening one in a chat of its own."""
import shutil
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.mcp.cdd_home import CddHome
from harness.process.git import Git
from space.repo.repos import CddConfig, FolderIsAWorktreeError, NotAReposFolderError, Repos, RepoNameRequiredError


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
        self.repos = Repos(self.here, CddConfig(self.home))

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
            expect(Repos(self.here, CddConfig(self.home)).folder).to(equal(chosen.resolve()))

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

    with context("opening a linked worktree as a repository"):
        with it("should refuse it"):
            Git(self.here).run("worktree", "add", "-b", "ticket-2", str(self.top / "wt"))
            expect(lambda: self.repos.open("wt", publish=False, install=False, start_chat=False)).to(raise_error(FolderIsAWorktreeError))

    with context("opening a repository without a name"):
        with it("should refuse"):
            expect(lambda: self.repos.open(" ", publish=False, install=False, start_chat=False)).to(raise_error(RepoNameRequiredError))
