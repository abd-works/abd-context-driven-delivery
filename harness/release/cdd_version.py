"""The CDD version a chat runs, read against the latest release on origin (its newest ``v*`` tag), so the chat bar can
say when to update."""
from __future__ import annotations

import re
from pathlib import Path

from harness.agent_tools import agent_toolset
from harness.release.project_version import PYPROJECT, ProjectVersion, Version, VersionStanding
from harness.release.release import CddRelease
from harness.release.test_runs import TestRunRecord, default_record_folder
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.data_class import data_field, language_adapter
from harness.installation.files import command
from harness.mcp.mcp_annotations import long_call, mcp
from harness.git.git import Git, RepoConnectError
from harness.release.github_cli import GitHubCli

# The checkout the cdd server runs its code from: the one whose version every chat it answers runs.
SERVED_CHECKOUT = Path(__file__).resolve().parents[2]
# A release is a tag such as v2.0.0 that /release pushes; commits on main after it are not released.
_VERSION_TEXT = re.compile(r'^\d+\.\d+(\.\d+)?$')
# Short enough that the fetch ends inside the cdd tool's own time limit, so a slow network reads the last fetch instead.
FETCH_SECONDS = 8


class VersionNotValid(ValueError):
    """A next version given to /version that is not numbers such as 0.2 or 0.2.1."""

    def __init__(self, text: str) -> None:
        super().__init__(f"{text!r} is not a version: give major and minor, such as 0.2, or major, minor and patch, such as 0.2.1")
        self.text = text


@language_adapter(language="typescript")
@agent_toolset
class CddVersion:
    """Say which CDD version a chat runs and how it stands against the latest release on origin, so the chat bar's
    version badge can show it green, yellow, or red and offer the update."""

    def __init__(self, git: Git, project_git: Git | None = None, release: CddRelease | None = None) -> None:
        """git runs in the CDD checkout whose version the chat runs; project_git runs in the repository /version and
        /release write the next version in, commit it in, and push from, the one the chat works in, the checkout itself
        when none is named. release is that repository's release of the version /version set, which gh publishes and which reads the
        results the tiers /release runs record."""
        self._checkout = Path(git.folder)
        self._git = git
        self._project_git = project_git or git
        self._project = Path(self._project_git.folder)
        self._release = release
        self._fetch_problem = ""

    @classmethod
    @tool_subject
    def load(cls, *, project: Path | str) -> CddVersion:
        """The version of the code the cdd server runs, whichever project the call names: every chat it answers runs it.
        The next version is set in the project the call names."""
        return cls(Git(SERVED_CHECKOUT), Git(project))

    # Its fetch waits on origin, which can pass the server's ten-second wait on a busy machine.
    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def check(self) -> CddVersion:
        """Fetch origin's release tags, then answer the version this chat runs, the latest release, and how the two
        stand. When origin cannot be reached, the latest is the newest release tag as it was last fetched."""
        try:
            self._git.run("fetch", "--tags", "origin", timeout=FETCH_SECONDS)
        except RepoConnectError as unreachable:
            self._fetch_problem = str(unreachable)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def read(self) -> CddVersion:
        """Answer the version this chat runs, read from disk now, against the latest release tag as last fetched,
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
        project = ProjectVersion.of(self._project)
        written = self._next_version_from(version, project.version)
        project.write(written)
        self._project_git.run("commit", "-m", f"Version v{written}", "--", PYPROJECT)
        self._project_git.run("push", "origin", "HEAD")
        return self

    # Its publish pushes, tags, and waits on GitHub.
    @long_call
    @command(name="release")
    @mcp
    @agent_tool
    def release(self, publish: bool = False) -> CddRelease:
        """Release the CDD version in pyproject.toml, never on red. /version sets the number; this tags and publishes
        it, changing no file. A version already released is refused: run /version first.
        1. Run the e2e tier, then the heavy tier, each to its end in the background from the repository's folder with
           the main checkout's Python: `.venv/Scripts/python -m harness.release.test_runs e2e .`, then the same
           with heavy. Each records its result in the cdd home. When a tier fails, find the cause, fix it, commit, and
           run that tier again, then the other, until both pass on the same commit.
        2. Call this with publish false. It refuses with ReleaseOnRed unless the latest e2e and heavy runs passed on
           HEAD, and with ReleaseAlreadyTagged when the version already has its tag; otherwise it answers the version and
           its release notes: the commits and the completed stories
           since the previous release tag. It changes nothing.
        3. Show the person the version and the notes, and ask before publishing, since publishing creates a public
           GitHub release.
        4. On their yes, call this with publish true. It pushes HEAD, tags it v<version> and pushes the tag, and runs
           gh release create with the notes.
        5. Hand the person release_url, the release's page on the repository."""
        release = self._release or CddRelease(self._project_git, GitHubCli(self._project), TestRunRecord(default_record_folder(), self._project))
        return release.publish() if publish else release.check_green()

    def _next_version_from(self, version: str, current: Version) -> str:
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
        """The latest release, such as v2.0, from origin's newest v* tag; empty when no release tag has been fetched."""
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
            return f"CDD {running}. The latest release on origin is unknown: {self._fetch_problem or 'no release tag has been fetched'}"
        if standing is VersionStanding.CURRENT:
            return f"CDD {running} is the latest release."
        size = "major" if standing is VersionStanding.BEHIND_MAJOR else "minor"
        return f"CDD {running} is behind the {latest} release, a {size} update. Press to update and reinstall."

    @property
    def _running(self) -> Version:
        return ProjectVersion.of(self._checkout).version

    @property
    def _latest(self) -> Version | None:
        """The newest release tag fetched, by version, not by date; None when there is none."""
        try:
            tags = self._git.run("tag", "--list", "v*", "--sort=-v:refname")
        except RepoConnectError:
            return None
        return next((release for release in map(Version.from_tag, tags.splitlines()) if release is not None), None)
