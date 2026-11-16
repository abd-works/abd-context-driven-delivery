"""/release: a major release of CDD, never on red, tagged and published as a GitHub release with notes.

Git and gh are stubbed at the boundary *MajorRelease* runs them through, and the test runs are seeded in a record, so
nothing here runs a tier, git or gh. major_release_heavy_spec.py releases a throwaway repository with real git and gh."""
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from expects import be_true, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.diagnostics.cdd_version import CddVersion
from harness.diagnostics.major_release import MajorRelease, ReleaseOnRed
from harness.diagnostics.test_runs import RunOutcome, TestRun, TestRunRecord, TestTier
from harness.process.git import RepoConnectError

HEAD = "f00dfeed1234"
STARTED = datetime(2026, 11, 15, 9, 0, tzinfo=timezone.utc)


class GitStub:
    """A checkout at HEAD whose previous release is tagged v1.0.0, or untagged, with commits and completed stories since."""

    def __init__(self, folder: Path, tag: str = "v1.0.0") -> None:
        self.folder = folder
        self.tag = tag
        self.ran: list[tuple[str, ...]] = []

    def run(self, *args: str, **_: object) -> str:
        self.ran.append(args)
        if args[0] == "rev-parse":
            return HEAD
        if args[0] == "describe":
            if not self.tag:
                raise RepoConnectError("Cannot connect git: git describe failed: No names found.")
            return self.tag
        if args[:2] == ("log", "-1"):
            return "beef0001"
        if args[0] == "log":
            return "Add the release command\nFix the board"
        if args[0] == "diff":
            return ".sessions/_complete/release-cadence/session.json\n.sessions/_complete/release-cadence/session.log\n.sessions/_complete/tdd-practice/session.json"
        return ""


class GhStub:
    def __init__(self) -> None:
        self.ran: list[tuple[str, ...]] = []
        self.notes = ""

    def run(self, *args: str) -> str:
        self.ran.append(args)
        self.notes = Path(args[args.index("--notes-file") + 1]).read_text(encoding="utf-8")
        return "https://github.com/owner/cdd/releases/tag/v2.0.0"


with description("a major release") as self:
    with before.each:
        self.project = Path(tempfile.mkdtemp(prefix="major-release-"))
        (self.project / "pyproject.toml").write_text('[project]\nname = "cdd"\nversion = "1.4.2"\n', encoding="utf-8")
        self.record = TestRunRecord(self.project / "home")
        self.git = GitStub(self.project)
        self.gh = GhStub()

    with after.each:
        shutil.rmtree(self.project, ignore_errors=True)

    def ran(self, tier: TestTier, outcome: RunOutcome = RunOutcome.PASSED, commit: str = HEAD) -> None:
        self.record.save(TestRun(tier, commit, STARTED, outcome))

    def green(self) -> None:
        self.ran(TestTier.E2E)
        self.ran(TestTier.HEAVY)

    def version(self) -> CddVersion:
        return CddVersion(self.git, self.git, MajorRelease(self.git, self.gh, self.record))

    with context("previewed with e2e and heavy green on HEAD"):
        with before.each:
            self.green()
            self.release = self.version().release()

        with it("should be the next major version"):
            expect(self.release.version).to(equal("2.0.0"))

        with it("should list the commits since the previous release tag"):
            expect(self.release.notes).to(contain("- Fix the board"))

        with it("should list each completed story once"):
            expect(self.release.notes.count("- release-cadence")).to(equal(1))

        with it("should change nothing"):
            expect(self.gh.ran + [args for args in self.git.ran if args[0] in ("commit", "push", "tag")]).to(equal([]))

    with context("with no release tag yet"):
        with it("should take the notes from the last version change of pyproject.toml"):
            self.git.tag = ""
            self.green()
            self.version().release().notes
            expect(self.git.ran).to(contain(("log", "--no-merges", "--reverse", "--format=%s", "beef0001..HEAD")))

    with context("that heavy failed"):
        with it("should refuse on red"):
            self.ran(TestTier.E2E)
            self.ran(TestTier.HEAVY, RunOutcome.FAILED)
            expect(lambda: self.version().release(publish=True)).to(raise_error(ReleaseOnRed, contain("heavy's latest run is failed")))

    with context("that e2e passed on an older commit"):
        with it("should refuse on red"):
            self.ran(TestTier.E2E, commit="0ldc0mmit")
            self.ran(TestTier.HEAVY)
            expect(lambda: self.version().release()).to(raise_error(ReleaseOnRed, contain("e2e last passed on 0ldc0mmit")))

    with context("that e2e has not run"):
        with it("should refuse on red"):
            self.ran(TestTier.HEAVY)
            expect(lambda: self.version().release()).to(raise_error(ReleaseOnRed, contain("e2e has not run")))

    with context("published"):
        with before.each:
            self.green()
            self.release = self.version().release(publish=True)

        with it("should write the major version in pyproject.toml"):
            expect((self.project / "pyproject.toml").read_text(encoding="utf-8")).to(contain('version = "2.0.0"'))

        with it("should commit pyproject.toml alone, push, tag, and push the tag, in that order"):
            changed = [args for args in self.git.ran if args[0] in ("commit", "push", "tag")]
            expect(changed).to(equal([
                ("commit", "-m", "Release v2.0.0", "--", "pyproject.toml"),
                ("push", "origin", "HEAD"),
                ("tag", "-a", "v2.0.0", "-m", "Release v2.0.0"),
                ("push", "origin", "v2.0.0"),
            ]))

        with it("should create the GitHub release on its tag"):
            expect(self.gh.ran[0][:3]).to(equal(("release", "create", "v2.0.0")))

        with it("should publish the notes"):
            expect(self.gh.notes).to(contain("- Add the release command"))

        with it("should keep the notes it published"):
            expect(self.release.notes).to(equal(self.gh.notes))

        with it("should hand back the release link"):
            expect(self.release.release_url).to(equal("https://github.com/owner/cdd/releases/tag/v2.0.0"))

        with it("should read as published"):
            expect(self.release.published).to(be_true)
