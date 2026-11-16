"""The CDD version a chat runs, read against the latest on origin main, so the chat bar can say when to update."""
from __future__ import annotations

import re
import tomllib
from enum import Enum
from pathlib import Path

from harness.agent_tools import agent_toolset
from harness.diagnostics.major_release import MajorRelease
from harness.diagnostics.test_runs import TestRunRecord, default_record_folder
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.data_class import data_field, language_adapter
from harness.installation.files import command
from harness.mcp.mcp_annotations import long_call, mcp
from harness.process.git import Git, RepoConnectError
from harness.process.github_cli import GitHubCli

# The checkout the cdd server runs its code from: the one whose version every chat it answers runs.
SERVED_CHECKOUT = Path(__file__).resolve().parents[2]
PYPROJECT = "pyproject.toml"
LATEST_BRANCH = "main"
# The version line of pyproject.toml's [project] table, the one line /version rewrites.
_VERSION_LINE = re.compile(r'^version\s*=\s*"[^"]*"', re.MULTILINE)
_VERSION_TEXT = re.compile(r'^\d+\.\d+(\.\d+)?$')
# Short enough that the fetch ends inside the cdd tool's own time limit, so a slow network reads the last fetch instead.
FETCH_SECONDS = 8


class VersionStanding(str, Enum):
    """How the version a chat runs stands against the latest on origin main."""

    CURRENT = "current"
    BEHIND_MINOR = "behind minor"
    BEHIND_MAJOR = "behind major"
    UNKNOWN = "unknown"


class VersionNotValid(ValueError):
    """A next version given to /version that is not numbers such as 0.2 or 0.2.1."""

    def __init__(self, text: str) -> None:
        super().__init__(f"{text!r} is not a version: give major and minor, such as 0.2, or major, minor and patch, such as 0.2.1")
        self.text = text


class Release:
    """A CDD version by its major and minor numbers, read from the ``version`` in ``pyproject.toml``; the patch number is
    left out, since a release moves the minor version."""

    def __init__(self, major: int, minor: int) -> None:
        self.major = major
        self.minor = minor

    @classmethod
    def from_pyproject(cls, text: str) -> Release:
        numbers = [int(part) for part in tomllib.loads(text)["project"]["version"].split(".")[:2]]
        return cls(*numbers, *([0] * (2 - len(numbers))))

    @property
    def label(self) -> str:
        return f"v{self.major}.{self.minor}"

    def standing_against(self, latest: Release) -> VersionStanding:
        if latest.major > self.major:
            return VersionStanding.BEHIND_MAJOR
        if latest.major == self.major and latest.minor > self.minor:
            return VersionStanding.BEHIND_MINOR
        return VersionStanding.CURRENT


@language_adapter(language="typescript")
@agent_toolset
class CddVersion:
    """Say which CDD version a chat runs and how it stands against the latest on origin main, so the chat bar's version
    badge can show it green, yellow, or red and offer the update."""

    def __init__(self, checkout: Path | str, git: Git | None = None, project: Path | str | None = None, project_git: Git | None = None,
                 github_cli: GitHubCli | None = None, test_runs: TestRunRecord | None = None) -> None:
        """checkout is the CDD checkout whose version the chat runs; project is the repository /version and /release
        write the next version in, commit it in, and push from, the one the chat works in. github_cli publishes a release, and
        test_runs is where the tiers /release runs record their results."""
        self._checkout = Path(checkout)
        self._project = Path(project) if project is not None else self._checkout
        self._git = git or Git(self._checkout)
        self._project_git = project_git or Git(self._project)
        self._github_cli = github_cli
        self._test_runs = test_runs
        self._fetch_problem = ""

    @classmethod
    @tool_subject
    def load(cls, *, project: Path | str) -> CddVersion:
        """The version of the code the cdd server runs, whichever project the call names: every chat it answers runs it.
        The next version is set in the project the call names."""
        return cls(SERVED_CHECKOUT, project=project)

    # Its fetch waits on origin, which can pass the server's ten-second wait on a busy machine.
    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def check(self) -> CddVersion:
        """Fetch origin main, then answer the version this chat runs, the latest on origin main, and how the two stand.
        When origin cannot be reached, the latest is the version origin main had when it was last fetched."""
        try:
            self._git.run("fetch", "origin", LATEST_BRANCH, timeout=FETCH_SECONDS)
        except RepoConnectError as unreachable:
            self._fetch_problem = str(unreachable)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def read(self) -> CddVersion:
        """Answer the version this chat runs, read from disk now, against the version origin main had when last fetched,
        without fetching. The chat bar reads it after every turn, so a changed version shows at once without asking
        origin on each turn; ``check`` fetches."""
        return self

    @command(name="version")
    @mcp
    @agent_tool
    def set_next(self, version: str = "") -> CddVersion:
        """Set the next CDD version in the repository's pyproject.toml, then commit that file alone and push the branch
        to origin, so the version is the latest there at once: the version given, such as 0.2 or 1.0.1, or with none
        given the next minor version. Nothing raises the version by itself; run this when a change is a release. Then
        tell the person the version it wrote and pushed."""
        file = self._project / PYPROJECT
        text = file.read_text(encoding="utf-8")
        next_version = self._next_version_from(version, Release.from_pyproject(text))
        file.write_text(_VERSION_LINE.sub(f'version = "{next_version}"', text, count=1), encoding="utf-8")
        self._project_git.run("commit", "-m", f"Version {Release.from_pyproject(file.read_text(encoding='utf-8')).label}", "--", PYPROJECT)
        self._project_git.run("push", "origin", "HEAD")
        return self

    # Its publish pushes, tags, and waits on GitHub.
    @long_call
    @command(name="release")
    @mcp
    @agent_tool
    def release(self, publish: bool = False) -> MajorRelease:
        """Release the next major CDD version, such as 2.0.0 after 1.4, never on red.
        1. Run the e2e tier, then the heavy tier, each to its end in the background from the repository's folder with
           the main checkout's Python: `.venv/Scripts/python -m harness.diagnostics.test_runs e2e .`, then the same
           with heavy. Each records its result in the cdd home. When a tier fails, find the cause, fix it, commit, and
           run that tier again, then the other, until both pass on the same commit.
        2. Call this with publish false. It refuses with ReleaseOnRed unless the latest e2e and heavy runs passed on
           HEAD, and otherwise answers the next version and its release notes: the commits and the completed stories
           since the previous release tag. It changes nothing.
        3. Show the person the version and the notes, and ask before publishing, since publishing creates a public
           GitHub release.
        4. On their yes, call this with publish true. It raises the major version in pyproject.toml, commits that file
           alone and pushes, tags the commit v<version> and pushes the tag, and runs gh release create with the notes.
        5. Hand the person release_url, the release's page on the repository."""
        release = MajorRelease(self._project, self._project_git, self._github_cli or GitHubCli(self._project),
                               self._test_runs or TestRunRecord(default_record_folder()))
        return release.publish() if publish else release.check_green()

    def _next_version_from(self, version: str, current: Release) -> str:
        if not version.strip():
            return f"{current.major}.{current.minor + 1}.0"
        given = version.strip().removeprefix("v")
        if not _VERSION_TEXT.match(given):
            raise VersionNotValid(version)
        return given if given.count(".") == 2 else f"{given}.0"

    @property
    @data_field
    def version(self) -> str:
        """The version this chat runs, such as v0.1."""
        return self._running.label

    @property
    @data_field
    def latest(self) -> str:
        """The version on origin main, such as v0.2; empty when origin main has never been fetched."""
        latest = self._latest
        return latest.label if latest is not None else ""

    @property
    @data_field
    def standing(self) -> VersionStanding:
        latest = self._latest
        return self._running.standing_against(latest) if latest is not None else VersionStanding.UNKNOWN

    @property
    @data_field
    def summary(self) -> str:
        """What the badge's tooltip says."""
        running, latest, standing = self.version, self.latest, self.standing
        if standing is VersionStanding.UNKNOWN:
            return f"CDD {running}. The latest version on origin {LATEST_BRANCH} is unknown: {self._fetch_problem}"
        if standing is VersionStanding.CURRENT:
            return f"CDD {running} is the latest on origin {LATEST_BRANCH}."
        size = "major" if standing is VersionStanding.BEHIND_MAJOR else "minor"
        return f"CDD {running} is behind {latest} on origin {LATEST_BRANCH}, a {size} update. Press to update and reinstall."

    @property
    def _running(self) -> Release:
        return Release.from_pyproject((self._checkout / PYPROJECT).read_text(encoding="utf-8"))

    @property
    def _latest(self) -> Release | None:
        try:
            return Release.from_pyproject(self._git.run("show", f"origin/{LATEST_BRANCH}:{PYPROJECT}"))
        except RepoConnectError:
            return None
