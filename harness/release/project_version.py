"""ProjectVersion and Version. A project's version, kept in the ``version`` line of its ``pyproject.toml``, and a CDD
version by its major and minor numbers."""
from __future__ import annotations

import re
from enum import Enum
from pathlib import Path

PYPROJECT = "pyproject.toml"
VERSION_LINE = re.compile(r'^version\s*=\s*"([^"]*)"', re.MULTILINE)
RELEASE_TAG = re.compile(r'^v(\d+)\.(\d+)(\.\d+)?$')


class VersionStanding(str, Enum):
    """How the version a chat runs stands against the latest release."""

    CURRENT = "current"
    BEHIND_MINOR = "behind minor"
    BEHIND_MAJOR = "behind major"
    UNKNOWN = "unknown"


class Version:
    """A CDD version by its major and minor numbers; the patch number is left out, since a release moves the minor
    version."""

    def __init__(self, major: int, minor: int) -> None:
        self.major = major
        self.minor = minor

    @classmethod
    def from_text(cls, text: str) -> Version:
        """The version written as text such as 1.5.0, as a project's version line writes it."""
        numbers = [int(part) for part in text.split(".")[:2]]
        return cls(*numbers, *([0] * (2 - len(numbers))))

    @classmethod
    def from_tag(cls, tag: str) -> Version | None:
        """The version a tag such as v2.0.0 names, or None when the tag is not a release."""
        numbers = RELEASE_TAG.match(tag.strip())
        return cls(int(numbers.group(1)), int(numbers.group(2))) if numbers else None

    @property
    def label(self) -> str:
        return f"v{self.major}.{self.minor}"

    def standing_against(self, latest: Version) -> VersionStanding:
        if latest.major > self.major:
            return VersionStanding.BEHIND_MAJOR
        if latest.major == self.major and latest.minor > self.minor:
            return VersionStanding.BEHIND_MINOR
        return VersionStanding.CURRENT


class ProjectVersion:
    """The version of the project whose ``pyproject.toml`` this is: the one reader and writer of its version line."""

    def __init__(self, pyproject: Path) -> None:
        self.file = Path(pyproject)

    @classmethod
    def of(cls, project: Path) -> ProjectVersion:
        """The version of the project in the folder project."""
        return cls(Path(project) / PYPROJECT)

    def read(self) -> str:
        """The version as its line writes it, such as 1.5.0."""
        return VERSION_LINE.search(self.file.read_text(encoding="utf-8")).group(1)

    def write(self, version: str) -> None:
        """Write version, such as 1.6.0, in place of the version line's, leaving every other line as it is."""
        text = self.file.read_text(encoding="utf-8")
        self.file.write_text(VERSION_LINE.sub(f'version = "{version}"', text, count=1), encoding="utf-8")

    @property
    def version(self) -> Version:
        return Version.from_text(self.read())
