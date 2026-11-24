"""The .gitignore a new repository starts with: what CDD writes into a project, and nothing of the person's own."""
import shutil
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from space.repo.new_repository import CDD_WRITTEN_PATTERNS, FolderInsideARepositoryError, NewRepository
from space.repo.repo import Repo


with description("a plain folder a session works in") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="cdd-plain-"))
        self.new = NewRepository(Repo(self.folder))

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("given the patterns for what CDD writes into a project"):
        with before.each:
            self.added = self.new.write_ignores()
            self.lines = (self.folder / ".gitignore").read_text(encoding="utf-8").splitlines()

        with it("should ignore CDD's install in each IDE's folder"):
            expect(self.lines).to(contain(".claude/", ".cursor/", ".kilo/"))

        with it("should ignore a session's working files"):
            expect(self.lines).to(contain(".sessions/main/session.log"))

        with it("should ignore no name the CDD checkout keeps for its own scratch files"):
            expect([line for line in self.lines if line in ("_*", "conf/*", "sandbox/", "count_all.py")]).to(equal([]))

        with it("should answer how many patterns it added"):
            expect(self.added).to(equal(len(CDD_WRITTEN_PATTERNS)))

        with context("given them again"):
            with it("should add nothing"):
                expect(self.new.write_ignores()).to(equal(0))

    with context("holding a .gitignore of its own"):
        with before.each:
            (self.folder / ".gitignore").write_text("dist/\n.claude/\n", encoding="utf-8")
            self.added = self.new.write_ignores()

        with it("should keep the person's lines first"):
            expect((self.folder / ".gitignore").read_text(encoding="utf-8").splitlines()[:2]).to(equal(["dist/", ".claude/"]))

        with it("should add only the patterns it lacks"):
            expect(self.added).to(equal(len(CDD_WRITTEN_PATTERNS) - 1))


with description("a plain folder inside another repository's checkout") as self:
    with before.each:
        self.outer = Path(tempfile.mkdtemp(prefix="cdd-outer-")).resolve()
        # A .git folder holding a HEAD is how a checkout's top is known; no git runs.
        (self.outer / ".git").mkdir()
        (self.outer / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        self.inner = self.outer / "sub" / "inner"
        self.inner.mkdir(parents=True)
        self.new = NewRepository(Repo(self.inner))

    with after.each:
        shutil.rmtree(self.outer, ignore_errors=True)

    with context("made a repository"):
        with it("should be refused, naming the repository that holds it"):
            expect(lambda: self.new.make_from_folder()).to(raise_error(FolderInsideARepositoryError, contain(str(self.outer))))

        with it("should write no .gitignore into it"):
            try:
                self.new.make_from_folder()
            except FolderInsideARepositoryError:
                pass
            expect((self.inner / ".gitignore").exists()).to(equal(False))
