"""The CDD version a chat runs, read against the latest on origin main, as the chat bar's version badge shows it.

Git is stubbed at the one boundary *CddVersion* runs it through, so this spec reaches no network."""
import shutil
import tempfile
from pathlib import Path

from expects import be_true, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.mcp.mcp_annotations import LongCall
from harness.diagnostics.cdd_version import CddVersion, VersionNotValid, VersionStanding
from harness.process.git import RepoConnectError


def pyproject(version: str) -> str:
    return f'[project]\nname = "abd-context-driven-delivery"\nversion = "{version}"\n'


class OriginStub:
    """Git in a checkout whose origin main holds pyproject.toml at one version, or that origin cannot be reached."""

    def __init__(self, latest: str | None, is_reachable: bool = True) -> None:
        self._latest = latest
        self._is_reachable = is_reachable
        self.ran: list[tuple[str, ...]] = []

    def run(self, *args: str, timeout: float | None = None) -> str:
        self.ran.append(args)
        if args[0] == "fetch" and not self._is_reachable:
            raise RepoConnectError("Cannot connect git: git fetch origin main failed: could not resolve host.")
        if args[0] == "show" and self._latest is None:
            raise RepoConnectError("Cannot connect git: git show origin/main:pyproject.toml failed: unknown revision.")
        return pyproject(self._latest) if args[0] == "show" else ""


with description("the CDD version a chat runs") as self:
    with before.each:
        self.checkout = Path(tempfile.mkdtemp(prefix="cdd-version-"))
        (self.checkout / "pyproject.toml").write_text(pyproject("0.1.0"), encoding="utf-8")

    with after.each:
        shutil.rmtree(self.checkout, ignore_errors=True)

    def checked(self, origin: OriginStub) -> CddVersion:
        self.origin = origin
        return CddVersion(self.checkout, git=origin).check()

    with context("checked"):
        with it("should fetch origin main before reading its version"):
            self.checked(OriginStub("0.1.0"))
            expect(self.origin.ran[0]).to(equal(("fetch", "origin", "main")))

        with it("should be answered when it comes back, since its fetch waits on origin"):
            expect(LongCall.annotates(CddVersion.check)).to(be_true)

        with it("should name its version by major and minor"):
            expect(self.checked(OriginStub("0.1.0")).version).to(equal("v0.1"))

    with context("that origin main holds the same version"):
        with it("should read current"):
            expect(self.checked(OriginStub("0.1.3")).standing).to(equal(VersionStanding.CURRENT))

    with context("that origin main holds a newer minor version"):
        with it("should read behind by a minor version"):
            expect(self.checked(OriginStub("0.2.0")).standing).to(equal(VersionStanding.BEHIND_MINOR))

        with it("should say which version is latest and that pressing the badge updates"):
            expect(self.checked(OriginStub("0.2.0")).summary).to(contain("v0.2", "update and reinstall"))

    with context("that origin main holds a newer major version"):
        with it("should read behind by a major version"):
            expect(self.checked(OriginStub("1.0.0")).standing).to(equal(VersionStanding.BEHIND_MAJOR))

    with context("that origin main cannot be reached"):
        with it("should read the version origin main had when last fetched"):
            expect(self.checked(OriginStub("0.2.0", is_reachable=False)).standing).to(equal(VersionStanding.BEHIND_MINOR))

    with context("that origin main has never been fetched and cannot be reached"):
        with it("should read unknown"):
            expect(self.checked(OriginStub(None, is_reachable=False)).standing).to(equal(VersionStanding.UNKNOWN))

        with it("should say why the latest version is unknown"):
            expect(self.checked(OriginStub(None, is_reachable=False)).summary).to(contain("could not resolve host"))


with description("the next CDD version") as self:
    with before.each:
        self.project = Path(tempfile.mkdtemp(prefix="cdd-next-version-"))
        (self.project / "pyproject.toml").write_text(pyproject("0.1.0") + '\n[tool.setuptools]\npackages = []\n', encoding="utf-8")
        self.subject = CddVersion(self.project, git=OriginStub("0.1.0"), project=self.project)

    with after.each:
        shutil.rmtree(self.project, ignore_errors=True)

    def written(self) -> str:
        return (self.project / "pyproject.toml").read_text(encoding="utf-8")

    with context("set with no version given"):
        with it("should raise the minor version in pyproject.toml"):
            self.subject.set_next()
            expect(self.written()).to(contain('version = "0.2.0"'))

    with context("set to a version given by major and minor"):
        with it("should write that version in pyproject.toml"):
            self.subject.set_next("1.0")
            expect(self.written()).to(contain('version = "1.0.0"'))

        with it("should leave the rest of pyproject.toml as it was"):
            self.subject.set_next("1.0")
            expect(self.written()).to(contain("[tool.setuptools]\npackages = []"))

    with context("set to text that is not a version"):
        with it("should refuse it, naming the text"):
            expect(lambda: self.subject.set_next("next")).to(raise_error(VersionNotValid, contain("next")))
