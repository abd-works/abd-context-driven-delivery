"""The folder an install is told to write into: kept as an absolute path, refused when it is empty or a file."""
import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.installation.ide_layout import IdeLayout
from harness.installation.install_target import InstallTarget, NotAnInstallFolder


with description("the folder an install is told to write into") as self:
    with context("named from the current directory"):
        with it("should be kept as the whole path, so a later run from another directory finds it"):
            expect(InstallTarget(IdeLayout("Claude"), ".claude").path).to(equal(Path.cwd() / ".claude"))

    with context("named with nothing"):
        with it("should be refused"):
            expect(lambda: InstallTarget(IdeLayout("Claude"), "")).to(raise_error(NotAnInstallFolder))

        with it("should be refused saying the path is empty"):
            try:
                InstallTarget(IdeLayout("Claude"), "")
            except NotAnInstallFolder as refusal:
                expect(str(refusal)).to(contain("empty"))

    with context("that is a file"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp(prefix="install-target-"))
            self.file = self.folder / "README.md"
            self.file.write_text("mine\n", encoding="utf-8")

        with after.each:
            shutil.rmtree(self.folder, ignore_errors=True)

        with it("should be refused"):
            expect(lambda: InstallTarget(IdeLayout("Claude"), self.file)).to(raise_error(NotAnInstallFolder))

        with it("should be refused naming the file"):
            try:
                InstallTarget(IdeLayout("Claude"), self.file)
            except NotAnInstallFolder as refusal:
                expect(str(refusal)).to(contain("README.md", "is a file"))

        with it("should keep the path given on the refusal"):
            try:
                InstallTarget(IdeLayout("Claude"), self.file)
            except NotAnInstallFolder as refusal:
                expect(refusal.path).to(equal(self.file))

    with context("whose parent folder does not exist"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp(prefix="install-target-"))
            self.mistyped = self.folder / "does" / "not" / "exist" / ".github"

        with after.each:
            shutil.rmtree(self.folder, ignore_errors=True)

        with it("should be refused, naming the folder that is missing"):
            expect(lambda: InstallTarget(IdeLayout("VS Code"), self.mistyped)).to(
                raise_error(NotAnInstallFolder, contain(str(self.folder / "does" / "not" / "exist"), "does not exist"))
            )

        with it("should make no folder"):
            try:
                InstallTarget(IdeLayout("VS Code"), self.mistyped)
            except NotAnInstallFolder:
                pass
            expect((self.folder / "does").exists()).to(equal(False))

    with context("missing, in a folder that exists"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp(prefix="install-target-"))

        with after.each:
            shutil.rmtree(self.folder, ignore_errors=True)

        with it("should be taken, since an install makes the IDE folder itself"):
            expect(InstallTarget(IdeLayout("Claude"), self.folder / ".claude").path).to(equal(self.folder / ".claude"))
