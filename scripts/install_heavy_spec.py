"""Install from the latest release, step 1, with real git: which version line the checkout's pyproject.toml ends with."""

import importlib.util
import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from harness.git.git import Git

_SCRIPT = Path(__file__).resolve().parent / "install.py"
_spec = importlib.util.spec_from_file_location("cdd_install_script_heavy", _SCRIPT)
install = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(install)

_RELEASE = "v1.2.0"


def _pyproject(version: str) -> str:
    return f'[project]\nname = "shop"\nversion = "{version}"\n'


with description("a checkout that installs from the latest release") as self:
    with before.each:
        self.checkout = Path(tempfile.mkdtemp(prefix="install-latest-")).resolve()
        self.pyproject = self.checkout / "pyproject.toml"
        self.git = Git(self.checkout)
        self.git.run("init", "-b", "main")
        self.pyproject.write_text(_pyproject("1.2.0"), encoding="utf-8")
        self.git.run("add", "-A")
        self.git.run("commit", "-m", "Release 1.2.0")
        self.git.run("tag", _RELEASE)
        self.script_checkout = install._REPO
        install._REPO = self.checkout

    with after.each:
        install._REPO = self.script_checkout
        shutil.rmtree(self.checkout, ignore_errors=True)

    with context("that is at the release, with its version line edited and not committed"):
        with before.each:
            self.pyproject.write_text(_pyproject("9.9.9"), encoding="utf-8")
            self.answer = install._match_release_version(_RELEASE)

        with it("should put the version line back to the release's"):
            expect(self.pyproject.read_text(encoding="utf-8")).to(equal(_pyproject("1.2.0")))

        with it("should say it set the version from the release"):
            expect(self.answer).to(contain("set from v1.2.0"))

    with context("that is past the release, with its own newer version committed"):
        with before.each:
            self.pyproject.write_text(_pyproject("1.3.0"), encoding="utf-8")
            self.git.run("commit", "-am", "Next version 1.3.0")
            self.answer = install._match_release_version(_RELEASE)

        with it("should keep its own committed version"):
            expect(self.pyproject.read_text(encoding="utf-8")).to(equal(_pyproject("1.3.0")))

        with it("should leave nothing modified"):
            expect(self.git.run("status", "--porcelain")).to(equal(""))

        with it("should say the checkout keeps its own version, past the release"):
            expect(self.answer).to(contain('version = "1.3.0"', "past v1.2.0"))
