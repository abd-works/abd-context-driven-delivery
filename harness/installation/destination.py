"""What install reads from a toolset beside its destinations: the Installation that writes one destination's files, the
channel a module registers with its server, and the tools a server skipped. The omission annotations that keep a member
out of install or the catalog (``@noDeploy``, ``@noCatalog``) are in harness/annotations; the data annotations are in
data_class.py."""
from __future__ import annotations

import functools
import logging
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from harness.agent_tools.agent_tools import AgentTool
from harness.annotations.annotation import DestinationKind
from harness.installation.ide_layout import IdeLayout
from harness.installation.repository_toolsets import RepositoryToolsets

if TYPE_CHECKING:
    from harness.installation.install_record import InstallRecord
    from harness.installation.install_target import InstallTarget

_logger = logging.getLogger(__name__)


def is_temporary(folder: Path) -> bool:
    """Whether folder is in the system's temporary folder, as a spec's install is: such an install keeps its record and
    its MCP entry in the folder itself, so it never touches the person's own."""
    try:
        temp = _resolved_temp()
        resolved = Path(folder).resolve()
    except OSError:
        return False
    return resolved == temp or temp in resolved.parents


@functools.cache
def _resolved_temp() -> Path:
    """The system's temporary folder, resolved once: it does not move while a process runs, and resolving a path on
    Windows asks the file system for every folder in it."""
    return Path(tempfile.gettempdir()).resolve()


class InstallPlace:
    """Where one install writes: the IDE folder with its layout (*InstallTarget*), the record of every file the install
    wrote there (*InstallRecord*), and the repository being installed, which names the folders its guidance is kept in
    (none for an install made for no repository). Every channel of one install writes through one place."""

    def __init__(self, target: InstallTarget, record: InstallRecord, repository: RepositoryToolsets | None = None) -> None:
        self.target = target
        self.install_record = record
        self.repository = repository
        self.is_temporary = target.is_temporary
        """Whether the install writes into a temporary folder, as a spec's install does."""

    @classmethod
    def into(cls, target: InstallTarget, repository: RepositoryToolsets | None = None) -> InstallPlace:
        """A place writing into target that keeps its own record of the folder, for a writer outside an install run,
        such as the catalog working out where a skill goes."""
        from harness.installation.install_record import InstallRecord

        return cls(target, InstallRecord(target), repository)

    @property
    def layout(self) -> IdeLayout:
        return self.target.layout

    @property
    def path(self) -> Path:
        return self.target.path

    @property
    def repo(self) -> Path | None:
        """The repository being installed; none for an install made for no repository."""
        return self.repository.root if self.repository is not None else None

    def wrote(self, written: Path) -> None:
        """Keep written, a file the install wrote, in the install record."""
        self.install_record.track(written)

    def relative_folder(self, install_folder: Path) -> Path:
        """The folder a toolset installs from, such as its practice's folder, from the repository it is in."""
        folder = self._guidance_source_folder(Path(install_folder))
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


class Installation(InstallPlace):
    """Writes one channel's files into one IDE folder: ``install(tool)`` writes what tool publishes there; a subclass
    names its ``destination``, the *DestinationKind* that is its channel, and defines ``write``."""

    destination: ClassVar[DestinationKind | None] = None

    def install(self, tool: AgentTool) -> None:
        self.write(tool)

    def write(self, tool: AgentTool) -> None:
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


class StandUp:
    """What a channel's server answered when an install stood it up over what was installed: the tools it serves, and
    the tools it skipped so it could serve the rest."""

    def __init__(self, tools: list[str], skipped: SkippedTools) -> None:
        self.tools = tools
        self.skipped = skipped

    @property
    def notice(self) -> str:
        """The lines that name each skipped tool; empty when nothing was skipped."""
        return self.skipped.notice


class ChannelServer:
    """The server a channel's installed files point the IDE at, as an install handles it: stood up in the install's
    process over what was installed, to check it loads (`stand_up`), then started (`ensure_running`). The cdd server is
    one; the hook channel has none, since the hook command starts the hook daemon on the first event."""

    stood_up: StandUp | None = None

    def stand_up(self) -> StandUp:
        """Stand the server up over what was installed, in this process, and answer what it serves and skipped."""
        raise NotImplementedError

    def ensure_running(self) -> list[str]:
        """Start the server when none answers; one line for each thing started, saying how it runs."""
        raise NotImplementedError

    @property
    def runs_this_process(self) -> bool:
        """Whether this process is the server, as it is when an install runs as one of the cdd server's tool calls."""
        return False


class RegisteredChannel(Installation):
    """A channel a module registers with the Installer, beside the file channels: the MCP channel and the hook channel.
    harness/mcp and harness/hooks each define one and register it with ``SERVER_CHANNELS.register`` when they are
    imported, so the Installer runs every registered channel without importing them. A channel whose files point the IDE
    at a server holds it (`server`); the hook channel holds none."""

    # Toolset classes every install publishes through this channel beside the repository's own, such as the hooks
    # that start the cdd server.
    toolsets: tuple[type, ...] = ()
    server: ChannelServer | None = None

    @classmethod
    def create(cls, target: InstallTarget, record: InstallRecord, repository: RepositoryToolsets | None = None) -> RegisteredChannel:
        """The installation of this channel into target, with the collaborators its server needs; the Installer makes
        every registered channel this way. A channel that needs none is made as it is."""
        return cls(target, record, repository)

    @classmethod
    def into(cls, target: InstallTarget, repository: RepositoryToolsets | None = None) -> RegisteredChannel:
        """The installation of this channel into target that keeps its own record of the folder, for a writer outside
        an install run."""
        from harness.installation.install_record import InstallRecord

        return cls.create(target, InstallRecord(target), repository)

    def accepts(self, tool: AgentTool) -> bool:
        """Whether tool is written through this installation: install publishes it to this channel."""
        return tool.is_published_to(self.destination)

    @property
    def published(self) -> list[str]:
        """The names this installation published, such as the MCP operations it enrolled, sorted."""
        raise NotImplementedError

    def write_once_recorded(self) -> None:
        """Write what the channel writes once every tool is recorded, such as the IDE's MCP entry; most write nothing."""

    def status(self) -> list[str]:
        """One line for each fact the install report gives about the channel, such as whether its server is running."""
        raise NotImplementedError
