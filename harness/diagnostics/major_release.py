"""A major release of CDD: never on red, it raises the major version, tags it, and publishes a GitHub release whose notes
are the commits and the stories completed since the release before."""
from __future__ import annotations

import re
import tempfile
from pathlib import Path

from harness.diagnostics.test_runs import RunOutcome, TestRunRecord, TestTier
from harness.installation.data_class import data_field
from harness.process.git import Git, RepoConnectError
from harness.process.github_cli import GitHubCli

PYPROJECT = "pyproject.toml"
TAG_PATTERN = "v*"
# Where a ticket's session folder moves when its ticket is complete: each folder added there is a completed story.
COMPLETE_SESSIONS = ".sessions/_complete"
_VERSION_LINE = re.compile(r'^version\s*=\s*"([^"]*)"', re.MULTILINE)
# The release tiers, in the order /release runs them.
RELEASE_TIERS = (TestTier.E2E, TestTier.HEAVY)
# How much of a commit hash release notes show: enough to find the commit, short enough to read.
SHORT_COMMIT_CHARS = 12


class ReleaseOnRed(RuntimeError):
    """A release asked for while a release tier's latest run did not pass on the commit being released."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("Not released, the tests are not green on this commit: " + "; ".join(problems)
                         + ". Run each tier with python -m harness.diagnostics.test_runs <tier> . and fix what fails until both pass.")
        self.problems = problems


class ReleaseNotes:
    """The commits and the completed stories between the previous release tag and HEAD. With no release tag yet, the
    previous release is the last commit that changed pyproject.toml, where /version last set the version."""

    def __init__(self, git: Git) -> None:
        self._git = git

    @property
    def previous_release(self) -> str:
        """The previous release's tag, or the commit the notes start after; empty when there is neither."""
        try:
            return self._git.run("describe", "--tags", "--abbrev=0", "--match", TAG_PATTERN)
        except RepoConnectError:
            return self._git.run("log", "-1", "--format=%H", "--", PYPROJECT)

    @property
    def commits(self) -> list[str]:
        """Each commit's subject since the previous release, oldest first, merges left out."""
        listed = self._git.run("log", "--no-merges", "--reverse", "--format=%s", *self._range())
        return [line for line in listed.splitlines() if line.strip()]

    @property
    def completed_stories(self) -> list[str]:
        """The tickets whose session folder moved to .sessions/_complete since the previous release."""
        added = self._git.run("diff", "--name-only", "--diff-filter=A", *self._range(), "--", COMPLETE_SESSIONS) if self.previous_release else ""
        names = [Path(path).relative_to(COMPLETE_SESSIONS).parts[0] for path in added.splitlines() if path.startswith(COMPLETE_SESSIONS + "/")]
        return list(dict.fromkeys(names))

    def text(self, version: str) -> str:
        since = self.previous_release
        lines = [f"# CDD {version}", "", f"Since {since[:SHORT_COMMIT_CHARS] if since else 'the first commit'}."]
        lines += ["", "## Completed stories", ""] + ([f"- {name}" for name in self.completed_stories] or ["- none"])
        lines += ["", "## Commits", ""] + ([f"- {subject}" for subject in self.commits] or ["- none"])
        return "\n".join(lines) + "\n"

    def _range(self) -> list[str]:
        since = self.previous_release
        return [f"{since}..HEAD"] if since else ["HEAD"]


class MajorRelease:
    """The next major release of the checkout git runs in: previewed until it is published, which writes the version,
    commits and pushes it, tags it, and creates the GitHub release."""

    def __init__(self, git: Git, github_cli: GitHubCli, test_runs: TestRunRecord) -> None:
        self._project = Path(git.folder)
        self._git = git
        self._github_cli = github_cli
        self._test_runs = test_runs
        self._notes = ReleaseNotes(git)
        self.url = ""
        self.is_published = False
        self._published_notes = ""

    def check_green(self) -> MajorRelease:
        """Refuse with ReleaseOnRed unless the latest e2e and heavy runs passed on HEAD."""
        head = self._git.run("rev-parse", "HEAD")
        problems = [problem for problem in (self._problem_with(tier, head) for tier in RELEASE_TIERS) if problem]
        if problems:
            raise ReleaseOnRed(problems)
        return self

    def _problem_with(self, tier: TestTier, head: str) -> str:
        """Why the tier's latest run does not allow a release on head; empty when it passed on head."""
        run = self._test_runs.latest(tier)
        if run is None:
            return f"{tier.value} has not run"
        if run.outcome is not RunOutcome.PASSED:
            return f"{tier.value}'s latest run is {run.outcome.value}"
        if run.commit != head:
            return f"{tier.value} last passed on {run.commit[:9]}, not on HEAD {head[:9]}"
        return ""

    def publish(self) -> MajorRelease:
        """Write the version, commit pyproject.toml alone, push, tag v<version>, push the tag, and create the release."""
        self.check_green()
        notes = self.notes
        tag = self.tag
        file = self._project / PYPROJECT
        file.write_text(_VERSION_LINE.sub(f'version = "{self.version}"', file.read_text(encoding="utf-8"), count=1), encoding="utf-8")
        self._git.run("commit", "-m", f"Release {tag}", "--", PYPROJECT)
        self._git.run("push", "origin", "HEAD")
        self._git.run("tag", "-a", tag, "-m", f"Release {tag}")
        self._git.run("push", "origin", tag)
        with tempfile.TemporaryDirectory(prefix="cdd-release-") as folder:
            notes_file = Path(folder) / "notes.md"
            notes_file.write_text(notes, encoding="utf-8")
            answer = self._github_cli.run("release", "create", tag, "--title", f"CDD {tag}", "--notes-file", str(notes_file), "--verify-tag")
        self.url = answer.strip().splitlines()[-1] if answer.strip() else ""
        self._published_notes = notes
        self.is_published = True
        return self

    @property
    @data_field
    def version(self) -> str:
        """The next major version, such as 2.0.0 after 1.4.2."""
        current = _VERSION_LINE.search((self._project / PYPROJECT).read_text(encoding="utf-8")).group(1)
        if self.is_published:
            return current
        return f"{int(current.split('.')[0]) + 1}.0.0"

    @property
    @data_field
    def tag(self) -> str:
        return f"v{self.version}"

    @property
    @data_field
    def notes(self) -> str:
        """The release notes, the commits and completed stories since the previous release."""
        return self._published_notes or self._notes.text(self.tag)

    @property
    @data_field
    def release_url(self) -> str:
        """The release's page on the repository, once published."""
        return self.url

    @property
    @data_field
    def published(self) -> bool:
        return self.is_published
