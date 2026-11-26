"""Repo.make_repository - a plain folder a session works in made a git repository on main, with real git."""
import shutil
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.git.git import Git
from space.repo.new_repository import FolderInsideARepositoryError, NewRepository
from space.repo.repo import Repo


def _plain_folder(folder: Path) -> Path:
    """A plain folder as a chat works in one: a file of its own, CDD installed into its .claude, and a session."""
    (folder / ".claude" / "skills").mkdir(parents=True)
    (folder / ".claude" / "skills" / "skill.md").write_text("skill\n", encoding="utf-8")
    (folder / ".sessions" / "main").mkdir(parents=True)
    (folder / ".sessions" / "main" / "session.log").write_text("log\n", encoding="utf-8")
    (folder / "notes.md").write_text("notes\n", encoding="utf-8")
    return folder


# Files of the person's own that the CDD checkout's housekeeping lines (``_*``, ``conf/*``, ``sandbox/``) would hide.
_OWN_FILES = ["_config.yml", "conf/settings.yaml", "count_all.py", "pages/_app.tsx", "sandbox/try.py"]


def _with_own_files(folder: Path) -> Path:
    for name in _OWN_FILES:
        (folder / name).parent.mkdir(parents=True, exist_ok=True)
        (folder / name).write_text("mine\n", encoding="utf-8")
    return folder


with description("a plain folder a session works in") as self:
    with before.each:
        self.folder = _plain_folder(Path(tempfile.mkdtemp(prefix="cdd-plain-")).resolve())
        self.repo = Repo(self.folder)

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("made a git repository"):
        with before.each:
            self.answer = self.repo.make_repository()

        with it("should be a repository on main"):
            expect([self.repo.is_clone, self.repo.current_branch.name]).to(equal([True, "main"]))

        with it("should commit the folder's own files with a README"):
            expect(Git(self.folder).run("ls-files").splitlines()).to(equal([".gitignore", "README.md", "notes.md"]))

        with it("should leave CDD's install and the session's working files out of the first commit"):
            expect(Git(self.folder).run("ls-files")).not_to(contain(".claude"))

        with it("should leave nothing uncommitted"):
            expect(Git(self.folder).run("status", "--porcelain")).to(equal(""))

        with it("should say what it did"):
            expect(self.answer).to(contain("on main with a first commit"))

        with context("made one again"):
            with it("should leave the repository as it is"):
                expect(self.repo.make_repository()).to(contain("is a repository already, on main"))

    with context("holding files named as the CDD checkout names its own scratch files"):
        with before.each:
            _with_own_files(self.folder)
            self.repo.make_repository()

        with it("should commit each of them, since only what CDD writes into a project is ignored"):
            expect(Git(self.folder).run("ls-files").splitlines()).to(equal(sorted([".gitignore", "README.md", "notes.md", *_OWN_FILES])))

        with it("should leave none of them ignored"):
            expect(Git(self.folder).run("status", "--porcelain", "--ignored")).not_to(contain("conf/"))


with description("a folder made a git repository") as self:
    with before.each:
        self.top = Path(tempfile.mkdtemp(prefix="cdd-new-repo-")).resolve()

    with after.each:
        shutil.rmtree(self.top, ignore_errors=True)

    with context("that does not exist yet"):
        with before.each:
            self.folder = self.top / "brand-new"
            self.answer = NewRepository(Repo(self.folder)).make_from_folder().sentence

        with it("should make the folder a repository on main"):
            expect(Git(self.folder).run("rev-parse", "--abbrev-ref", "HEAD")).to(equal("main"))

        with it("should commit its .gitignore and a README"):
            expect(Git(self.folder).run("ls-files").splitlines()).to(equal([".gitignore", "README.md"]))

        with it("should say it created it"):
            expect(self.answer).to(contain("on main with a first commit"))

    with context("inside a subfolder of another repository"):
        with before.each:
            self.outer = _plain_folder(self.top / "outer")
            Repo(self.outer).make_repository()
            self.inner = self.outer / "sub" / "inner"
            self.inner.mkdir(parents=True)
            (self.inner / "a.txt").write_text("a\n", encoding="utf-8")

        with it("should be refused, naming the repository that holds it"):
            expect(lambda: NewRepository(Repo(self.inner)).make_from_folder()).to(raise_error(FolderInsideARepositoryError, contain(str(self.outer))))

        with it("should leave the outer repository able to add the subfolder's files"):
            try:
                NewRepository(Repo(self.inner)).make_from_folder()
            except FolderInsideARepositoryError:
                pass
            Git(self.outer).run("add", "-A")
            expect(Git(self.outer).run("ls-files")).to(contain("sub/inner/a.txt"))
