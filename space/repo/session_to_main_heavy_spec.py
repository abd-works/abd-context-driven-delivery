"""BDD spec: a session's work taken to main, merged in the clone or pushed to origin, as the chat bar's Merge to main
and Push to main do. Real git, on a clone with an origin beside it."""
import shutil
import subprocess
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from space.repo.built_once import BuiltOnce  # noqa: E402
from space.repo.repo import Repo  # noqa: E402

SESSION_BRANCH = "session/demo"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def _clone_with_origin(root: Path) -> None:
    origin = root / "origin.git"
    clone = root / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True, capture_output=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, capture_output=True)
    _git(clone, "config", "user.email", "session@test")
    _git(clone, "config", "user.name", "session")
    _git(clone, "checkout", "-q", "-b", "main")
    (clone / ".gitignore").write_text(".sessions/\n", encoding="utf-8")
    _git(clone, "add", ".gitignore")
    _git(clone, "commit", "-q", "-m", "seed")
    _git(clone, "push", "-q", "origin", "main")


_REPOSITORIES = BuiltOnce("session-to-main-spec-", _clone_with_origin)


def _clone_of_master(root: Path) -> None:
    """A clone of an origin whose default branch is master, as a repository made before git named it main."""
    origin = root / "origin.git"
    seed = root / "seed"
    subprocess.run(["git", "init", "-q", "-b", "master", str(seed)], check=True, capture_output=True)
    _git(seed, "config", "user.email", "session@test")
    _git(seed, "config", "user.name", "session")
    (seed / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(seed, "add", "-A")
    _git(seed, "commit", "-q", "-m", "seed")
    subprocess.run(["git", "clone", "-q", "--bare", str(seed), str(origin)], check=True, capture_output=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(root / "clone")], check=True, capture_output=True)
    _git(root / "clone", "config", "user.email", "session@test")
    _git(root / "clone", "config", "user.name", "session")


_MASTER_REPOSITORIES = BuiltOnce("session-to-master-spec-", _clone_of_master)


def _files_on(root: Path, ref: str) -> list[str]:
    return _git(root, "ls-tree", "-r", "--name-only", ref).splitlines()


# (E) Steer Sessions
# (S) Person --> Push Session To Main From Chat Bar
with description("a session's work taken to main") as self:
    with before.each:
        self.tmp = _REPOSITORIES.copy()
        self.origin, self.clone = self.tmp / "origin.git", self.tmp / "clone"

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with context("from the session's own worktree, with work not committed"):
        with before.each:
            self.tree = self.tmp / "clone-demo"
            _git(self.clone, "worktree", "add", "-q", "-b", SESSION_BRANCH, str(self.tree))
            (self.tree / "work.txt").write_text("work\n", encoding="utf-8")

        with context("that is merged to main"):
            with before.each:
                self.landed = Repo(self.tree).merge_to_main()

            with it("should commit the work on the session's branch"):
                expect(_files_on(self.tree, SESSION_BRANCH)).to(contain("work.txt"))

            with it("should hold the work on main in the clone"):
                expect(_files_on(self.clone, "main")).to(contain("work.txt"))

            with it("should leave main on origin without the work"):
                expect(_files_on(self.origin, "main")).not_to(contain("work.txt"))

            with it("should leave the worktree on the session's branch"):
                expect(_git(self.tree, "rev-parse", "--abbrev-ref", "HEAD")).to(equal(SESSION_BRANCH))

            with it("should answer the commit main is on"):
                expect(self.landed.sha).to(equal(_git(self.clone, "rev-parse", "main")))

        with context("and the clone's own changes not committed, such as the session's log written in main"):
            with before.each:
                (self.clone / "seed.txt").write_text("seed\ntool repo.merge_to_main\n", encoding="utf-8")
                Repo(self.tree).merge_to_main()

            with it("should hold the clone's changes on main beside the work"):
                expect(_git(self.clone, "show", "main:seed.txt")).to(contain("tool repo.merge_to_main"))

        with context("that is pushed to main"):
            with before.each:
                Repo(self.tree).push_to_main()

            with it("should hold the work on main on origin"):
                expect(_files_on(self.origin, "main")).to(contain("work.txt"))

            with it("should push the session's branch to origin"):
                expect(_files_on(self.origin, SESSION_BRANCH)).to(contain("work.txt"))

    with context("from the clone itself, with the session's branch checked out"):
        with before.each:
            _git(self.clone, "checkout", "-q", "-b", SESSION_BRANCH)
            (self.clone / "work.txt").write_text("work\n", encoding="utf-8")

        with context("that is merged to main"):
            with before.each:
                Repo(self.clone).merge_to_main()

            with it("should hold the work on main"):
                expect(_files_on(self.clone, "main")).to(contain("work.txt"))

            with it("should leave the clone on the session's branch"):
                expect(_git(self.clone, "rev-parse", "--abbrev-ref", "HEAD")).to(equal(SESSION_BRANCH))

    with context("from main itself, with work not committed"):
        with before.each:
            (self.clone / "work.txt").write_text("work\n", encoding="utf-8")

        with context("that is pushed to main"):
            with before.each:
                Repo(self.clone).push_to_main()

            with it("should push the work to main on origin"):
                expect(_files_on(self.origin, "main")).to(contain("work.txt"))


with description("a session's work taken to the default branch of a repository whose default is master") as self:
    with before.each:
        self.tmp = _MASTER_REPOSITORIES.copy()
        self.origin, self.clone = self.tmp / "origin.git", self.tmp / "clone"
        self.tree = self.tmp / "clone-demo"
        _git(self.clone, "worktree", "add", "-q", "-b", SESSION_BRANCH, str(self.tree))
        (self.tree / "work.txt").write_text("work\n", encoding="utf-8")

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with context("that is pushed to main"):
        with before.each:
            Repo(self.tree).push_to_main()

        with it("should push the work to master on origin"):
            expect(_files_on(self.origin, "master")).to(contain("work.txt"))

        with it("should make no main branch on origin"):
            expect(_git(self.origin, "branch", "--list", "main")).to(equal(""))

# (E) Steer Sessions
# (S) Person --> Push Work From Chat Bar
with description("a session's work pushed on its own branch") as self:
    with before.each:
        self.tmp = _REPOSITORIES.copy()
        self.origin, self.clone = self.tmp / "origin.git", self.tmp / "clone"
        self.tree = self.tmp / "clone-demo"
        _git(self.clone, "worktree", "add", "-q", "-b", SESSION_BRANCH, str(self.tree))
        (self.tree / "work.txt").write_text("work\n", encoding="utf-8")
        Repo(self.tree).push_work()

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with it("should push the work on the session's branch to origin"):
        expect(_files_on(self.origin, SESSION_BRANCH)).to(contain("work.txt"))

    with it("should leave main without the work"):
        expect(_files_on(self.origin, "main")).not_to(contain("work.txt"))
