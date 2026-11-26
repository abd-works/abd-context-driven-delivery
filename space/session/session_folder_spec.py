"""BDD spec for removing a session's folder: SessionFolder.remove (session_folder.py)."""

import shutil
import tempfile
from pathlib import Path

from expects import be_false, be_true, equal, expect
from mamba import after, before, context, description, it

from space.session import Sessions
from space.session import session_folder
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue

# shutil.rmtree as Python answers it, put back after each example that stands in for Windows.
REAL_RMTREE = shutil.rmtree


def _held_folder(real_rmtree):
    """shutil.rmtree as Windows answers it while another process has the folder itself open, as a file watcher does for
    a moment: every file inside goes, and removing the emptied folder is refused."""
    def rmtree(path, *args, **kwargs):
        folder = Path(path)
        for inner in folder.iterdir():
            real_rmtree(inner) if inner.is_dir() else inner.unlink()
        raise PermissionError(5, "Access is denied", str(folder))
    return rmtree


def _held_file(real_rmtree):
    """shutil.rmtree as Windows answers it while another process has a file inside open: nothing is removed."""
    def rmtree(path, *args, **kwargs):
        raise PermissionError(5, "Access is denied", str(Path(path) / "session.log"))
    return rmtree


with description("a session's folder that is removed") as self:
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name).resolve()
        Sessions(self.project).switch("pet-visits", self.project, create=True)
        self.session = Sessions(self.project).named("pet-visits")
        self.folder = self.session.record_folder

    with after.each:
        session_folder.shutil.rmtree = REAL_RMTREE
        self.tmp.cleanup()

    with context("that Windows holds open for a moment once its files are gone"):
        with before.each:
            session_folder.shutil.rmtree = _held_folder(REAL_RMTREE)
            self.session.folder.remove()

        with it("should leave none of its files behind"):
            expect(list(self.folder.rglob("*")) if self.folder.exists() else []).to(equal([]))

        with it("should no longer be held by its sessions"):
            expect("pet-visits" in [session.name for session in Sessions(self.project).all()]).to(be_false)

    with context("that still holds a file Windows refuses to remove"):
        with before.each:
            session_folder.shutil.rmtree = _held_file(REAL_RMTREE)
            self.session.folder.remove()

        with it("should no longer be held by its sessions all the same"):
            expect("pet-visits" in [session.name for session in Sessions(self.project).all()]).to(be_false)

        with it("should leave the file in a folder set aside, which is no session"):
            expect((self.folder.with_name(f"_removing-{self.folder.name}") / "session.json").is_file()).to(be_true)

    with context("that an earlier removal left a folder set aside under its name"):
        with before.each:
            self.left_behind = self.folder.with_name(f"_removing-{self.folder.name}")
            self.left_behind.mkdir()
            (self.left_behind / "progress-cache.json").write_text("{}", encoding="utf-8")
            self.session.folder.remove()

        with it("should remove the session's folder all the same"):
            expect(self.folder.exists()).to(be_false)

        with it("should remove what the earlier removal left behind"):
            expect(self.left_behind.exists()).to(be_false)

    with context("that holds a file whose path, once the folder is set aside, is longer than Windows allows"):
        with before.each:
            # A path of 255 characters: within the 260 Windows allows, and past it once _removing- is added.
            deep = self.folder / "e2e-test-results" / ("s" * 60)
            deep.mkdir(parents=True)
            name_length = 255 - len(str(deep)) - 1
            (deep / ("n" * (name_length - 4) + ".png")).write_bytes(b"")
            self.session.folder.remove()

        with it("should remove the folder and the file all the same"):
            expect([self.folder.exists(), self.folder.with_name(f"_removing-{self.folder.name}").exists()]).to(equal([False, False]))
