"""The CDD version a chat runs, read against the latest on origin main, so the chat bar can say when to update."""
from __future__ import annotations

import tomllib
from enum import Enum
from pathlib import Path

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.data_class import data_field, language_adapter
from harness.mcp.mcp_annotations import mcp
from harness.process.git import Git, RepoConnectError

# The checkout the cdd server runs its code from: the one whose version every chat it answers runs.
SERVED_CHECKOUT = Path(__file__).resolve().parents[2]
PYPROJECT = "pyproject.toml"
LATEST_BRANCH = "main"
# Short enough that the fetch ends inside the cdd tool's own time limit, so a slow network reads the last fetch instead.
FETCH_SECONDS = 8


class VersionStanding(str, Enum):
    """How the version a chat runs stands against the latest on origin main."""

    CURRENT = "current"
    BEHIND_MINOR = "behind minor"
    BEHIND_MAJOR = "behind major"
    UNKNOWN = "unknown"


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

    def __init__(self, checkout: Path | str, git: Git | None = None) -> None:
        self._checkout = Path(checkout)
        self._git = git or Git(self._checkout)
        self._fetch_problem = ""

    @classmethod
    @tool_subject
    def load(cls, *, project: Path | str) -> CddVersion:
        """The version of the code the cdd server runs, whichever project the call names: every chat it answers runs it."""
        return cls(SERVED_CHECKOUT)

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
