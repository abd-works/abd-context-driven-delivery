"""Repos - the repositories CDD works on beside one another, in the folder ``~/.cdd/config.json`` keeps as
``repos_folder``. Opening one creates it when missing, on main, publishes it, installs CDD into its ``.claude``, ignores
what CDD writes into a project (``CDD_WRITTEN_PATTERNS``), and starts a chat of its own in it: a top-level chat, not one nested in the chat that
asked, where the person switches to or creates sessions as usual."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import noSessionLog, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.chat.chat import Chats, NewChat
from harness.installation.data_class import data_field
from harness.installation.files import command
from harness.installation.json_file import JsonFile
from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_annotations import long_call, mcp
from space.repo.new_repository import DEFAULT_BRANCH, NewRepository
from space.repo.repo import SERVED_CHECKOUTS, Repo

# The checkout serving these tools: its install script installs CDD.
_CDD_CHECKOUT = Path(__file__).resolve().parents[2]
_CONFIG_FILE = "config.json"
_REPOS_FOLDER = "repos_folder"
_VISIBILITIES = ("private", "public", "internal")
_INSTALL_SECONDS = 600
_PUBLISH_SECONDS = 180
# How much of a failed install's output its error carries: the end, where the reason is, short enough to read.
_INSTALL_FAILURE_CHARS = 2000


class RepoNameRequiredError(ValueError):
    """Raised when a repository is opened without a name."""

    def __init__(self) -> None:
        super().__init__("repository name is required, such as abd-cdd-hardening-workarea")


class NotAReposFolderError(ValueError):
    """Raised when the folder chosen to hold repositories is not a folder that is there."""

    def __init__(self, folder: Path) -> None:
        super().__init__(f"{folder} is not a folder; make it first or choose another")
        self.folder = folder


class UnknownVisibilityError(ValueError):
    def __init__(self, visibility: str) -> None:
        super().__init__(f"visibility must be one of {', '.join(_VISIBILITIES)}, not {visibility!r}")


class PublishFailedError(RuntimeError):
    """Raised when the GitHub CLI cannot create or push the repository; it carries what gh said."""


class InstallFailedError(RuntimeError):
    """Raised when installing CDD into the repository's .claude fails; it carries the install's output."""


class RepositoryChat:
    """A new top-level chat in the Claude desktop app on root, titled title, whose first prompt opens the CDD session
    called session there: a harness *NewChat* opened from chats. The app asks the person to confirm the folder and send
    that prompt."""

    def __init__(self, root: Path, title: str, session: str, chats: Chats) -> None:
        self._root = root
        self._title = title
        self._session = session
        self.chat: NewChat = chats.new_chat(str(root), self.first_prompt)

    @property
    def first_prompt(self) -> str:
        return f"Open the CDD session {self._session} in this folder: call sessions.switch with name {self._session}."

    @property
    def instructions(self) -> str:
        """What the agent is told when the link cannot be opened: how to start the chat itself."""
        return (
            f"Start a top-level chat on {self._root}: start_session with initiation user_asked, context fresh, "
            f"cwd {self._root}, use_worktree false, title {self._title!r}, and prompt {self.first_prompt!r}. Or open {self.chat.link}"
        )

    def open(self) -> str:
        """Hand the link to the desktop app; when the system cannot open it, say how to start the chat instead."""
        try:
            self.chat.open()
        except (OSError, subprocess.SubprocessError):
            return self.instructions
        return f"Opened a new chat on {self._root} in the Claude app: send its first prompt there to open the session {self._session}."

class CddConfig:
    """The person's own cdd settings, in ``~/.cdd/config.json``: one object, read whole and written whole."""

    def __init__(self, file: JsonFile) -> None:
        self.file = file

    @classmethod
    def in_home(cls, home: CddHome) -> CddConfig:
        """The settings file in home, ``config.json``."""
        return cls(JsonFile(home.folder / _CONFIG_FILE))

    def value(self, key: str) -> str:
        found = self.file.read().get(key)
        return found if isinstance(found, str) else ""

    def set(self, key: str, setting: str) -> None:
        self.file.write({**self.file.read(), key: setting})


class SiblingRepo:
    """One repository in the repos folder: a folder whose ``.git`` is a folder of its own, never a linked worktree's."""

    def __init__(self, repo: Repo) -> None:
        self.repo = repo

    @property
    @data_field
    def name(self) -> str:
        return self.repo.root.name

    @property
    @data_field
    def path(self) -> str:
        return str(self.repo.root)

    @property
    @data_field
    def branch(self) -> str:
        return self.repo.checkout.branch

    @property
    @data_field
    def is_published(self) -> bool:
        return self.repo.has_origin

    @property
    @data_field
    def has_cdd(self) -> bool:
        """Whether CDD is installed in its .claude."""
        return (self.repo.root / ".claude" / "commands").is_dir()

    @property
    def is_repository(self) -> bool:
        """Whether its folder is a repository of its own: its ``.git`` is a folder, not a linked worktree's file."""
        return self.repo.checkout.folder == self.repo.root and self.repo.is_main_clone


@agent_toolset
class Repos:
    """The repositories in the repos folder, each a sibling of the others; opening one gives it its own chat."""

    def __init__(self, project: Path | str, cdd_config: CddConfig) -> None:
        # The checkout the calling chat works in: by default the repos folder is the folder its main clone sits in.
        self.project = Path(project).resolve()
        self.cdd_config = cdd_config

    @classmethod
    @tool_subject
    def load(cls, *, project: Path | str) -> Repos:
        """The repositories beside the checkout of project, the folder the calling chat works in."""
        return cls(project, CddConfig.in_home(CddHome()))

    @property
    def folder(self) -> Path:
        """The folder holding the repositories: the one chosen with ``/repos-folder``, else the folder the calling
        chat's main clone sits in, which for a CDD worktree such as abd-cdd-x is the folder beside abd-context-driven-delivery."""
        chosen = self.cdd_config.value(_REPOS_FOLDER)
        if chosen:
            return Path(chosen)
        return Repo.of_project(self.project).main_clone.root.parent

    @mcp
    @command(name="repos-folder")
    @agent_tool
    @noSessionLog
    def set_folder(self, path: str) -> str:
        """Choose the folder new and existing repositories are kept in, such as C:\\dev; repos.siblings lists the
        repositories there and repos.open creates new ones there. Kept in ~/.cdd/config.json as repos_folder."""
        folder = Path(path).expanduser().resolve()
        if not folder.is_dir():
            raise NotAReposFolderError(folder)
        self.cdd_config.set(_REPOS_FOLDER, str(folder))
        return f"Repositories are kept in {folder}."

    @mcp
    @command(name="repos")
    @agent_tool
    @noSessionLog
    def siblings(self) -> list[SiblingRepo]:
        """The repositories in the repos folder, each with its branch, whether it is published, and whether CDD is
        installed in it. Linked worktrees, such as a ticket's, are left out: they belong to the repository they branch."""
        folder = self.folder
        if not folder.is_dir():
            return []
        children = sorted((child for child in folder.iterdir() if child.is_dir()), key=lambda child: child.name.lower())
        siblings = (SiblingRepo(SERVED_CHECKOUTS.at(child.resolve())) for child in children)
        return [sibling for sibling in siblings if sibling.is_repository]

    @long_call
    @mcp
    @command(name="open-repo")
    @agent_tool
    @noSessionLog
    def open(
        self, name: str, folder: str = "", visibility: str = "private", publish: bool = True, install: bool = True, start_chat: bool = True,
        call: ToolCall | None = None,
    ) -> str:
        """Open the repository called name in a chat of its own, on main. folder is where it is kept, by default the
        repos folder (/repos-folder). A repository not there yet is created: git init on main with a first commit.
        publish creates it on GitHub with the gh CLI when it has no origin; visibility is private (the default), public,
        or internal. With install, CDD is installed into its .claude; its .gitignore gets what CDD writes into a project (CDD_WRITTEN_PATTERNS) and nothing else.
        start_chat opens a new top-level Claude chat on the folder; the person sends its first prompt, which opens the
        repository's main session. Ask the person for visibility before publishing, offering private as the default."""
        cleaned = self._checked_name(name, visibility)
        root = (Path(folder).expanduser().resolve() if folder else self.folder) / cleaned
        new = NewRepository(SERVED_CHECKOUTS.at(root))
        steps = [new.create().sentence]
        ignored = new.ignore_as_cdd_does()
        steps.append(f"Added {ignored} lines to .gitignore for what CDD writes into a project, and committed them." if ignored else ".gitignore already ignores what CDD writes into a project.")
        steps += [self._publish(root, visibility)] if publish else []
        steps += [self._install_cdd(root)] if install else []
        # A new repository's main session is the session of the branch it is created on.
        chat = RepositoryChat(root, cleaned, DEFAULT_BRANCH, Chats.load(call))
        steps.append(chat.open() if start_chat else chat.instructions)
        return "\n".join(f"- {step}" for step in steps if step)

    def _checked_name(self, name: str, visibility: str) -> str:
        """name trimmed, refused when empty, as is a visibility GitHub does not offer."""
        cleaned = (name or "").strip()
        if not cleaned:
            raise RepoNameRequiredError()
        if visibility not in _VISIBILITIES:
            raise UnknownVisibilityError(visibility)
        return cleaned

    def _publish(self, root: Path, visibility: str) -> str:
        repo = Repo.of_project(root)
        if repo.has_origin:
            if repo.origin.needs_push():
                repo.origin.push_upstream()
                return "Pushed main to its origin."
            return f"Already published: {repo.git.run('remote', 'get-url', 'origin')}."
        gh = shutil.which("gh")
        if gh is None:
            raise PublishFailedError("the GitHub CLI (gh) is not installed; install it, or open the repository with publish false")
        answer = subprocess.run(
            [gh, "repo", "create", root.name, f"--{visibility}", "--source", str(root), "--remote", "origin", "--push"],
            cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=_PUBLISH_SECONDS, check=False,
            stdin=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if answer.returncode != 0:
            raise PublishFailedError(f"gh repo create failed: {(answer.stderr or answer.stdout).strip()}")
        return f"Published as a {visibility} GitHub repository: {repo.git.run('remote', 'get-url', 'origin')}."

    def _install_cdd(self, root: Path) -> str:
        """Install CDD's skills, commands, agents and rules into root/.claude with the serving checkout's install script,
        in a process of its own, as the chat bar's Run install does."""
        script = _CDD_CHECKOUT / "scripts" / "install.py"
        answer = subprocess.run(
            [sys.executable, str(script), "--ide", "Claude", "--path", str(root / ".claude")],
            cwd=_CDD_CHECKOUT, capture_output=True, text=True, encoding="utf-8", timeout=_INSTALL_SECONDS, check=False,
            stdin=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if answer.returncode != 0:
            raise InstallFailedError(f"installing CDD into {root / '.claude'} failed: {(answer.stderr or answer.stdout).strip()[-_INSTALL_FAILURE_CHARS:]}")
        return f"Installed CDD into {root / '.claude'}."


