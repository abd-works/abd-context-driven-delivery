"""Sessions - the work sessions of one checkout, kept in its ``.sessions`` folder, and which of them is open."""

from __future__ import annotations

from pathlib import Path

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import tool_subject
from harness.installation.files import command
from harness.mcp.mcp_server import mcp
from space.repo.repo import Repo
from space.session.session import COMPLETE_FOLDER, MAIN_SESSION_NAME, SESSION_FILE, Session, name_of
from space.work_state import WorkState, project_folder

BACKLOG_FOLDER = "_backlog"
# Folders in `.sessions` whose names start with this are the ones the sessions share, such as the backlog.
_SHARED_FOLDER_MARK = "_"


class SessionNameRequiredError(ValueError):
    """Raised when switch-session has no name and ``.sessions/session.json`` has no session or branch."""

    def __init__(self) -> None:
        super().__init__(
            "session name is required: pass name, or switch to a branch first so "
            "the session can take its name"
        )


@agent_toolset
class Sessions:
    """The work sessions of one checkout: open ones in ``.sessions/{name}/``, closed ones in ``.sessions/_complete/``,
    and the one saved as open in ``.sessions/session.json``. ``main`` works on the whole repository and is open when no
    other is. The open session is read from that file each time it is asked for, so a switch or a close made by another
    chat or by the hook server is seen at once."""

    def __init__(self, project: Path | str | None = None) -> None:
        self.project = Path(project).resolve() if project is not None else project_folder()
        self.root = Repo(self.project).checkout_folder

    @classmethod
    @tool_subject
    def of_project(cls, project: Path) -> Sessions:
        """The sessions of the checkout holding project, the project the running call names."""
        return cls(project)

    @property
    def folder(self) -> Path:
        """The `.sessions` folder that holds the sessions and what they share on the board."""
        return WorkState(self.root).sessions_folder

    @property
    def backlog_folder(self) -> Path:
        """Where sessions wait before work starts, and where a session moved back is held."""
        return self.folder / BACKLOG_FOLDER

    def folder_of(self, name: str) -> Path:
        """The folder of the session called name. A ticket on the board lives in the main checkout's ``.sessions``, so
        a chat in the ticket's linked worktree logs there too and the board shows its work. Each checkout keeps its own
        main session."""
        preferred = self.folder / name
        candidates = [preferred]
        if name != MAIN_SESSION_NAME:
            candidates.insert(0, WorkState(Repo(self.root).primary_root()).sessions_folder / name)
        return next((folder for folder in candidates if (folder / SESSION_FILE).is_file()), preferred)

    def all(self) -> list[Session]:
        """The work sessions, open ones first then closed: not main, and not the folders the sessions share."""
        return [self.load(folder) for folder in self._work_session_folders()]

    def _work_session_folders(self) -> list[Path]:
        if not self.folder.is_dir():
            return []
        open_folders = [folder for folder in sorted(self.folder.iterdir()) if folder.is_dir() and self._is_work_session(folder.name)]
        closed = self.folder / COMPLETE_FOLDER
        closed_folders = sorted(folder for folder in closed.iterdir() if folder.is_dir()) if closed.is_dir() else []
        return open_folders + closed_folders

    @staticmethod
    def _is_work_session(name: str) -> bool:
        return bool(name) and name != MAIN_SESSION_NAME and not name.startswith(_SHARED_FOLDER_MARK)

    def named(self, name: str) -> Session | None:
        """The work session called name, open before closed; none when there is none. Only that session's folder is
        read, so a tool that names one session does not load every other."""
        if not self._is_work_session(name):
            return None
        found = next((folder for folder in (self.folder / name, self.folder / COMPLETE_FOLDER / name) if folder.is_dir()), None)
        return self.load(found) if found is not None else None

    def load(self, folder: Path) -> Session:
        """The session kept in folder, read without opening it."""
        return Session.load(folder, self.root)

    @property
    def open_name(self) -> str:
        """The name of the session saved as open; main when none is."""
        return WorkState(self.root).session or MAIN_SESSION_NAME

    @property
    def saved(self) -> Session:
        """The session saved as open, read from its folder without being held, so each reader sees a switch or a close
        made elsewhere at once."""
        return self.load(self.folder_of(self.open_name))

    def create(self, name: str, workpath: Path, *, title: str = "", scope: str = "", parent: str = "") -> Session:
        """A new session called name, working in workpath, with the title, scope, and parent a board ticket shows saved
        in its ``session.json``; it is not opened, because a session made for later, such as a board ticket, is not the
        one being worked on."""
        session = Session(self.root)
        session.name = name_of(name)
        session.workpath = Path(workpath).resolve()
        session.session_path = self.folder / session.name
        session.save()
        session.save_fields(**{key: value for key, value in (("title", title), ("scope", scope), ("parent", parent)) if value})
        session.log.seed_first_loop()
        return session

    def open(self, session: Session, workpath: Path | None = None) -> Session:
        """Make session the open session of this checkout, working in workpath when one is given."""
        if workpath is not None:
            session.workpath = Path(workpath).resolve()
        session.save()
        WorkState(self.root).session = "" if session.name == MAIN_SESSION_NAME else session.name
        return session

    @mcp
    @command(name="current-session")
    @agent_tool
    def current(self) -> Session:
        """The open session of this project; the main session, which works on the whole repository, when none is named."""
        return self.saved

    @mcp
    @command(name="switch-session")
    @agent_tool
    def switch(self, name: str = "", workpath: Path | None = None) -> str:
        """Open the session called ``name``, creating its folder when missing, and save it as the open session of this project. Returns how to keep its log.

        ``name`` defaults to ``session`` in ``.sessions/session.json``, then to the saved ``branch``.
        ``workpath`` is the folder it works in; a new session works in the project's folder when none is given.
        Does not touch branches or worktrees."""
        wanted = self._name_to_switch_to(name)
        folder = self.folder_of(wanted)
        is_kept = (folder / SESSION_FILE).is_file()
        session = self.load(folder) if is_kept else self.create(wanted, workpath if workpath is not None else self.project)
        return self.open(session, workpath).log.instructions()

    def _name_to_switch_to(self, name: str) -> str:
        state = WorkState(self.root)
        branch = state.branch
        cleaned = name_of(name or state.session or (branch.name if branch is not None else ""))
        if not cleaned:
            raise SessionNameRequiredError()
        return cleaned

    def close(self, session: Session) -> None:
        """Close session: when it is the open one, main becomes the open session."""
        if session.name != self.open_name:
            return
        WorkState(self.root).session = ""
