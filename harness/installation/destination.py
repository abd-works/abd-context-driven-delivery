"""What install reads from a toolset beside its destinations: the omission annotations that keep a member out of install
or the catalog, the Installation that writes one destination's files and its server kind, and the tools a server
skipped. The data annotations are in data_class.py."""
from __future__ import annotations

import logging
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from harness.annotations.annotation import OmissionAnnotation
from harness.installation.ide_layout import IdeLayout
from harness.installation.repository_toolsets import RepositoryToolsets

_logger = logging.getLogger(__name__)

InstallTracker = Callable[[Path], None]


class NoCatalog(OmissionAnnotation):
    """Omit this class or operation from the catalog.

    Install and deploy ignore this annotation. Use it when the behavior is real
    but not ready to show in the catalog.
    """

    flag = "_no_catalog"


class NoDeploy(OmissionAnnotation):
    """Omit this operation from install.

    Skill, command, MCP, and hook annotations on the same operation do not write
    files. The catalog can still list it.
    """

    flag = "_no_deploy"
    omits_install = True


noCatalog = NoCatalog
noDeploy = NoDeploy


def is_temporary(folder: Path) -> bool:
    """Whether folder is in the system's temporary folder, as a spec's install is: such an install keeps its record and
    its MCP entry in the folder itself, so it never touches the person's own."""
    try:
        temp = Path(tempfile.gettempdir()).resolve()
        resolved = Path(folder).resolve()
    except OSError:
        return False
    return resolved == temp or temp in resolved.parents


class Installation:
    """Writes one channel's files into one IDE folder: ``install(tool)`` writes what tool publishes there; a subclass
    defines ``write``. It is made with the install's *IdeLayout*, so every channel of one install reads one layout."""

    channel = ""

    def __init__(self, layout: IdeLayout, path: Path | str, repo: Path | str | None = None) -> None:
        self.layout = layout
        self.path = Path(path)
        self.repo = Path(repo).resolve() if repo is not None else None
        self.repository = RepositoryToolsets(self.repo) if self.repo is not None else None
        """The repository being installed, which names the folders its guidance is kept in; none for an install made
        for no repository."""
        self.is_temporary = is_temporary(self.path)
        """Whether this installation writes into a temporary folder, as a spec's install does."""
        self._install_tracker: InstallTracker | None = None

    def track_writes_with(self, tracker: InstallTracker) -> None:
        self._install_tracker = tracker

    def track_write(self, dest: Path) -> None:
        if self._install_tracker is not None:
            self._install_tracker(dest)

    def folder_for(self, toolset: Any) -> Path:
        """Repo-relative package folder the toolset already knows (practice dir, fidelity leaf)."""
        folder = self._guidance_source_folder(Path(toolset.install_folder))
        repo = self.repo
        if repo is None:
            return folder
        try:
            relative = folder.resolve().relative_to(repo)
        except ValueError:
            return Path(folder.name)
        return self._guidance_source_folder(relative)

    def _guidance_source_folder(self, folder: Path) -> Path:
        """Installed skills stay at practices/ and actions/, under the guidance package."""
        if folder.parts[:1] == (RepositoryToolsets.GUIDANCE_FOLDER,):
            rest = folder.parts[1:]
            return Path(*rest) if rest else Path(".")
        return folder

    def install(self, tool: Any) -> None:
        self.write(tool)

    def write(self, tool: Any) -> None:
        raise NotImplementedError


class SkippedTool(Exception):
    """One published tool, handler, or toolset a server skipped so it could serve the rest: its toolset could not be
    loaded, its name or arguments were wrong, or it raised while answering."""

    def __init__(self, tool: str, reason: str, cause: BaseException | None = None) -> None:
        super().__init__(f"{tool}: {reason}")
        self.tool = tool
        self.reason = reason
        self.cause = cause


class SkippedTools:
    """What one server skipped while it stood up or answered, so it kept serving the rest: the cdd server's tools, the
    hook server's handlers. A diagnosis reports them, and the notice names them for whoever started the server."""

    def __init__(self, server: str, kind: str) -> None:
        self._server = server
        self._kind = kind
        self._items: list[SkippedTool] = []

    def skip(self, tool: str, error: BaseException) -> None:
        """Record tool as skipped because of error, with its traceback in the log."""
        skipped = error if isinstance(error, SkippedTool) else SkippedTool(tool, str(error), error)
        self._items.append(skipped)
        _logger.error("%s standup exception: skipped %s: %s", self._server, skipped.tool, skipped.reason, exc_info=skipped.cause)

    def clear(self) -> None:
        self._items.clear()

    @property
    def as_data(self) -> list[dict[str, str]]:
        """Each skipped tool and why, as a diagnosis reports it."""
        return [{"tool": item.tool, "reason": item.reason} for item in self._items]

    @property
    def notice(self) -> str:
        """The lines that name each skipped tool; empty when nothing was skipped."""
        if not self._items:
            return ""
        lines = [f"{self._server} standup skipped illegitimate {self._kind} and continued:"]
        lines.extend(f"- {item.tool}: {item.reason}" for item in self._items)
        return "\n".join(lines)

    def notify(self) -> None:
        """Print the notice for whoever started the server, when something was skipped."""
        if self._items:
            print(self.notice, file=sys.stderr)


class ServerInstallation(Installation):
    """An installation whose files point the IDE at a server process: the MCP entry at the cdd server, the hook entries
    at the hook server. Beside writing its files it stands that server up over what was installed to check it loads,
    starts it, and reports it. harness/mcp and harness/hooks each define one and register it with
    ``Installer.installs_through`` when they are imported, so the Installer runs every server channel without
    importing them."""

    # Toolset classes every install publishes through this channel beside the repository's own, such as the hooks
    # that start the cdd server.
    toolsets: tuple[type, ...] = ()

    def accepts(self, tool: Any) -> bool:
        """Whether tool is written through this installation: it is annotated for this channel."""
        return self.channel in tool.destinations

    @property
    def published(self) -> list[str]:
        """The names this installation published, such as the MCP operations it enrolled, sorted."""
        raise NotImplementedError

    def standup(self) -> Any:
        """Stand the server up over what was installed, in this process, to check it loads."""
        raise NotImplementedError

    def diagnose(self) -> dict[str, Any]:
        """What the stood-up server answers about itself, with a ``notice`` naming anything it skipped."""
        raise NotImplementedError

    def ensure_running(self) -> dict[str, str]:
        """Start the server when none answers, and say how it runs, keyed by what it is."""
        raise NotImplementedError

    def status(self) -> list[str]:
        """One line for each fact the install report gives about the server, such as whether it is running."""
        raise NotImplementedError

    def serves_this_process(self) -> bool:
        """Whether this process is the server, as it is when an install runs as one of the cdd server's tool calls."""
        return False
