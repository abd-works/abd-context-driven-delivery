"""/release and the test cadence over their real boundaries: git in a throwaway repository with a bare origin, the gh
command line, and scripts/test.ps1 run by PowerShell in a background process. release_spec.py and
test_runs_spec.py are their stubbed twins.

gh is run for real without publishing: a release on GitHub is public, so the release here is created through a gh that
records it, and the real gh is asked only what publishes nothing."""
import subprocess
import shutil
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from expects import be_none, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.diagnostics.release import CddRelease, ReleaseAlreadyTagged
from harness.diagnostics.test_runs import RunOutcome, TestCadence, TestRun, TestRunRecord, TestRunner, TestTier, main_checkout
from harness.git.git import Git
from harness.diagnostics.github_cli import GitHubCli, GitHubCliError

# How long the background run of a stand-in test.ps1 has to record its result.
RECORDED_SECONDS = 60


def git(folder: Path, *args: str) -> str:
    return Git(folder).run(*args)


def throwaway_repository(root: Path) -> Path:
    """A checkout on main of a bare origin, its first release tagged v1.0.0, two commits and one completed story since,
    then the version raised to 1.4.0 as /version does."""
    origin, checkout = root / "origin.git", root / "checkout"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(checkout)], check=True, capture_output=True)
    for setting in (("user.name", "Spec"), ("user.email", "spec@example.invalid"), ("commit.gpgsign", "false"), ("tag.gpgsign", "false")):
        git(checkout, "config", *setting)
    git(checkout, "checkout", "-q", "-b", "main")
    (checkout / "pyproject.toml").write_text('[project]\nname = "cdd"\nversion = "1.0.0"\n', encoding="utf-8")
    git(checkout, "add", "pyproject.toml")
    git(checkout, "commit", "-q", "-m", "First release")
    git(checkout, "tag", "-a", "v1.0.0", "-m", "Release v1.0.0")
    (checkout / "board.py").write_text("board = 1\n", encoding="utf-8")
    git(checkout, "add", "board.py")
    git(checkout, "commit", "-q", "-m", "Fix the board")
    story = checkout / ".sessions" / "_complete" / "release-cadence"
    story.mkdir(parents=True)
    (story / "session.json").write_text("{}", encoding="utf-8")
    git(checkout, "add", ".sessions")
    git(checkout, "commit", "-q", "-m", "sessions: release-cadence moves to _complete")
    (checkout / "pyproject.toml").write_text('[project]\nname = "cdd"\nversion = "1.4.0"\n', encoding="utf-8")
    git(checkout, "commit", "-q", "-m", "Version v1.4", "--", "pyproject.toml")
    git(checkout, "push", "-q", "origin", "main", "--follow-tags")
    return checkout


class RecordingGh:
    """gh as far as GitHub: it keeps the release it was asked to create and answers its link."""

    def __init__(self) -> None:
        self.ran: list[tuple[str, ...]] = []
        self.notes = ""

    def run(self, *args: str) -> str:
        self.ran.append(args)
        self.notes = Path(args[args.index("--notes-file") + 1]).read_text(encoding="utf-8")
        return f"https://github.com/owner/cdd/releases/tag/{args[2]}"


with description("a release of a throwaway repository") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="release-heavy-"))
        self.checkout = throwaway_repository(self.root)
        self.record = TestRunRecord(self.root / "home")
        head = git(self.checkout, "rev-parse", "HEAD")
        for tier in (TestTier.E2E, TestTier.HEAVY):
            self.record.save(TestRun(tier, head, datetime.now(timezone.utc), RunOutcome.PASSED))
        self.gh = RecordingGh()
        self.release = CddRelease(Git(self.checkout), self.gh, self.record)

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("previewed"):
        with it("should list the commits since v1.0.0 and not before"):
            expect(self.release.notes).to(contain("- Fix the board"))
            expect(self.release.notes).not_to(contain("First release"))

        with it("should list the story completed since v1.0.0"):
            expect(self.release.notes).to(contain("## Completed stories\n\n- release-cadence"))

    with context("published"):
        with before.each:
            self.release.publish()

        with it("should push the version /version set to origin main, unchanged"):
            expect(git(self.root / "origin.git", "show", "main:pyproject.toml")).to(contain('version = "1.4.0"'))

        with it("should commit nothing"):
            expect(git(self.checkout, "log", "-1", "--format=%s")).to(equal("Version v1.4"))

        with it("should push the tag on the commit the tests passed on"):
            expect(git(self.root / "origin.git", "rev-list", "-n", "1", "v1.4.0")).to(equal(git(self.checkout, "rev-parse", "HEAD")))

        with it("should create the release on that tag with the notes"):
            expect((self.gh.ran[0][2], self.gh.notes)).to(equal(("v1.4.0", self.release.notes)))

        with it("should refuse to release the same version again"):
            expect(lambda: self.release.publish()).to(raise_error(ReleaseAlreadyTagged))


with description("the gh command line") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="gh-heavy-"))
        subprocess.run(["git", "init", "-q", str(self.folder)], check=True)

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    with it("should answer its version"):
        expect(GitHubCli(self.folder).run("--version")).to(contain("gh version"))

    with it("should refuse a release in a repository GitHub does not know, naming the command"):
        expect(lambda: GitHubCli(self.folder).run("release", "list")).to(raise_error(GitHubCliError, contain("gh release list failed")))


with description("a tier run by the real runner") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="test-runner-heavy-"))
        self.checkout = throwaway_repository(self.root)
        (self.checkout / "scripts").mkdir()
        (self.checkout / "scripts" / "test.ps1").write_text(
            'param([string]$Suite)\nWrite-Host "ran $Suite"\nWrite-Host "1 examples failed"\nexit 1\n', encoding="utf-8")
        self.record = TestRunRecord(self.root / "home")

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with it("should answer test.ps1's exit code and output"):
        expect(TestRunner().run(TestTier.HEAVY, self.checkout)).to(equal((1, "ran heavy\n1 examples failed\n")))

    with it("should be run in the repository's own folder while it has main checked out"):
        expect(main_checkout(self.checkout)).to(equal(Path(git(self.checkout, "rev-parse", "--show-toplevel"))))

    with it("should not run in a worktree on another branch"):
        worktree = self.root / "worktree"
        git(self.checkout, "worktree", "add", "-q", "-b", "feature", str(worktree))
        (worktree / "scripts").mkdir(exist_ok=True)
        (worktree / "scripts" / "test.ps1").write_text("exit 0\n", encoding="utf-8")
        git(self.checkout, "checkout", "-q", "-b", "other")
        expect(main_checkout(worktree)).to(be_none)

    with it("should record a new failure from its background process"):
        TestCadence(self.checkout, self.record).start_due()
        deadline = time.monotonic() + RECORDED_SECONDS
        while time.monotonic() < deadline and self.record.latest(TestTier.E2E).outcome is RunOutcome.RUNNING:
            time.sleep(0.2)
        run = self.record.latest(TestTier.E2E)
        expect((run.state, run.is_new_failure, run.summary)).to(equal(("failed", True, "ran e2e\n1 examples failed")))
