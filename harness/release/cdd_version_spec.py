"""The CDD version a chat runs, read against the latest release on origin (its newest v* tag), as the chat bar's version badge shows it.

Git is stubbed at the one boundary *CddVersion* runs it through, so this spec reaches no network."""
import shutil
import tempfile
from pathlib import Path

from expects import be_true, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.mcp.mcp_annotations import LongCall
from harness.release.cdd_version import CddVersion, VersionNotValid
from harness.release.project_version import VersionStanding
from harness.git.git import RepoConnectError


def pyproject(version: str) -> str:
    return f'[project]\nname = "abd-context-driven-delivery"\nversion = "{version}"\n'


class OriginStub:
    """Git in a checkout whose fetched tags hold one latest release, newest first as ``--sort=-v:refname`` lists them,
    or none; or whose origin cannot be reached."""

    def __init__(self, latest: str | None, is_reachable: bool = True, folder: Path = Path(), tags: list[str] | None = None) -> None:
        self.folder = folder
        self._tags = tags if tags is not None else ([f"v{latest}"] if latest else [])
        self._is_reachable = is_reachable
        self.ran: list[tuple[str, ...]] = []

    def run(self, *args: str, timeout: float | None = None) -> str:
        self.ran.append(args)
        if args[0] == "fetch" and not self._is_reachable:
            raise RepoConnectError("Cannot connect git: git fetch --tags origin failed: could not resolve host.")
        return "\n".join(self._tags) if args[0] == "tag" else ""


with description("the CDD version a chat runs") as self:
    with before.each:
        self.checkout = Path(tempfile.mkdtemp(prefix="cdd-version-"))
        (self.checkout / "pyproject.toml").write_text(pyproject("0.1.0"), encoding="utf-8")

    with after.each:
        shutil.rmtree(self.checkout, ignore_errors=True)

    def checked(self, origin: OriginStub) -> CddVersion:
        self.origin = origin
        origin.folder = self.checkout
        return CddVersion(origin).check()

    with context("checked"):
        with it("should fetch origin's tags before reading the latest release"):
            self.checked(OriginStub("0.1.0"))
            expect(self.origin.ran[0]).to(equal(("fetch", "--tags", "origin")))

        with it("should read the latest release from the release tags, newest version first"):
            _ = self.checked(OriginStub("0.1.0")).latest
            expect(self.origin.ran).to(contain(("tag", "--list", "v*", "--sort=-v:refname")))

        with it("should be answered when it comes back, since its fetch waits on origin"):
            expect(LongCall.annotates(CddVersion.check)).to(be_true)

        with it("should name its version by major and minor"):
            expect(self.checked(OriginStub("0.1.0")).version).to(equal("v0.1"))

    with context("with a patch number"):
        with before.each:
            (self.checkout / "pyproject.toml").write_text(pyproject("0.1.2"), encoding="utf-8")

        with it("should name its version by major, minor and patch"):
            expect(self.checked(OriginStub("0.1.2")).version).to(equal("v0.1.2"))

        with it("should read current against the same patch release"):
            expect(self.checked(OriginStub("0.1.2")).standing).to(equal(VersionStanding.CURRENT))

    # The chat bar reads it after every turn, so a version changed on disk shows at once without asking origin each time.
    with context("read again without fetching"):
        with before.each:
            self.origin = OriginStub("0.2.0", folder=self.checkout)
            (self.checkout / "pyproject.toml").write_text(pyproject("0.2.0"), encoding="utf-8")
            self.read = CddVersion(self.origin).read()

        with it("should not fetch origin"):
            expect([args[0] for args in self.origin.ran]).not_to(contain("fetch"))

        with it("should name the version now on disk"):
            expect(self.read.version).to(equal("v0.2"))

        with it("should read against the latest release tag as last fetched"):
            expect(self.read.standing).to(equal(VersionStanding.CURRENT))

    with context("that the latest release is the same version"):
        with it("should read current"):
            expect(self.checked(OriginStub("0.1.0")).standing).to(equal(VersionStanding.CURRENT))

    with context("that the latest release is a newer patch of the same version"):
        with it("should read behind by a patch version"):
            expect(self.checked(OriginStub("0.1.3")).standing).to(equal(VersionStanding.BEHIND_PATCH))

        with it("should name the latest release with its patch number"):
            expect(self.checked(OriginStub("0.1.3")).latest).to(equal("v0.1.3"))

        with it("should say the patch release is latest and that pressing the badge updates"):
            expect(self.checked(OriginStub("0.1.3")).summary).to(contain("v0.1.3", "a patch update", "update and reinstall"))

    with context("that the latest release is a newer minor version"):
        with it("should read behind by a minor version"):
            expect(self.checked(OriginStub("0.2.0")).standing).to(equal(VersionStanding.BEHIND_MINOR))

        with it("should say which version is latest and that pressing the badge updates"):
            expect(self.checked(OriginStub("0.2.0")).summary).to(contain("v0.2", "update and reinstall"))

    with context("that the latest release is a newer major version"):
        with it("should read behind by a major version"):
            expect(self.checked(OriginStub("1.0.0")).standing).to(equal(VersionStanding.BEHIND_MAJOR))

    # Only a tag /release pushed is a release; other tags, such as design-system-setup or v-next, are not.
    with context("that origin also holds tags that are not releases"):
        with it("should read the newest release tag among them"):
            expect(self.checked(OriginStub(None, tags=["v-next", "v0.3.0", "v0.2.0"])).latest).to(equal("v0.3"))

    with context("that origin cannot be reached"):
        with it("should read the latest release tag as last fetched"):
            expect(self.checked(OriginStub("0.2.0", is_reachable=False)).standing).to(equal(VersionStanding.BEHIND_MINOR))

    with context("that no release tag has been fetched and origin cannot be reached"):
        with it("should read unknown"):
            expect(self.checked(OriginStub(None, is_reachable=False)).standing).to(equal(VersionStanding.UNKNOWN))

        with it("should say why the latest version is unknown"):
            expect(self.checked(OriginStub(None, is_reachable=False)).summary).to(contain("could not resolve host"))


with description("the next CDD version") as self:
    with before.each:
        self.project = Path(tempfile.mkdtemp(prefix="cdd-next-version-"))
        (self.project / "pyproject.toml").write_text(pyproject("0.1.0") + '\n[tool.setuptools]\npackages = []\n', encoding="utf-8")
        self.project_git = OriginStub("0.1.0", folder=self.project)
        self.subject = CddVersion(OriginStub("0.1.0", folder=self.project), self.project_git)

    with after.each:
        shutil.rmtree(self.project, ignore_errors=True)

    def written(self) -> str:
        return (self.project / "pyproject.toml").read_text(encoding="utf-8")

    with context("set with no version given"):
        with it("should commit pyproject.toml alone, naming the new version"):
            self.subject.set_next()
            expect(self.project_git.ran).to(contain(("commit", "-m", "Version v0.2.0", "--", "pyproject.toml")))

        with it("should push that commit to origin, so the next version is the latest there"):
            self.subject.set_next()
            expect(self.project_git.ran[-1]).to(equal(("push", "origin", "HEAD")))

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

    with context("set to a version given by major, minor and patch"):
        with it("should commit it naming the whole version, patch included"):
            self.subject.set_next("0.1.1")
            expect(self.project_git.ran).to(contain(("commit", "-m", "Version v0.1.1", "--", "pyproject.toml")))

    with context("set to text that is not a version"):
        with it("should refuse it, naming the text"):
            expect(lambda: self.subject.set_next("next")).to(raise_error(VersionNotValid, contain("next")))
