"""Repos - the repositories CDD works on beside one another, in the folder ``~/.cdd/config.json`` keeps as
``repos_folder``. Opening one creates it when missing, on main, publishes it, installs CDD into its ``.claude``, ignores
what the CDD checkout ignores, and starts a chat of its own in it: a top-level chat, not one nested in the chat that
asked, where the person switches to or creates sessions as usual."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import noSessionLog, tool_subject
from harness.installation.data_class import data_field
from harness.installation.files import command
from harness.installation.json_file import JsonFile
from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_server import long_call, mcp
from harness.process.git import Git
from space.repo.repo import Repo

# The checkout serving these tools: its .gitignore is what a new repository ignores, and its install script installs CDD.
_CDD_CHECKOUT = Path(__file__).resolve().parents[2]
_CONFIG_FILE = "config.json"
_REPOS_FOLDER = "repos_folder"
_DEFAULT_BRANCH = "main"
_VISIBILITIES = ("private", "public", "internal")
# Where a new chat opens in the Claude desktop app: the person confirms the folder and sends the first prompt.
_NEW_CHAT_LINK = "claude://code/new"
_FIRST_PROMPT = "Open this folder's CDD main session: call sessions.switch with name main."
_GITIGNORE_HEADER = "# Ignored as the CDD checkout ignores (written by repos.open)"
_INSTALL_SECONDS = 600
_PUBLISH_SECONDS = 180


class RepoNameRequiredError(ValueError):
    """Raised when a repository is opened without a name."""

    def __init__(self) -> None:
        super().__init__("repository name is required, such as abd-cdd-hardening-workarea")


class NotAReposFolderError(ValueError):
    """Raised when the folder chosen to hold repositories is not a folder that is there."""

    def __init__(self, folder: Path) -> None:
        super().__init__(f"{folder} is not a folder; make it first or choose another")
        self.folder = folder


class FolderIsAWorktreeError(ValueError):
    """Raised when the repository named is a linked worktree of another one: it is opened through its ticket, not as a
    repository of its own."""

    def __init__(self, folder: Path) -> None:
        super().__init__(f"{folder} is a linked worktree of another repository, not a repository of its own")
        self.folder = folder


class PathIsAFileError(ValueError):
    """Raised when the folder a chat is to open on is a file: it cannot be made a folder without losing the file."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"{path} is a file, not a folder; choose a folder")
        self.path = path


class UnknownVisibilityError(ValueError):
    def __init__(self, visibility: str) -> None:
        super().__init__(f"visibility must be one of {', '.join(_VISIBILITIES)}, not {visibility!r}")


class PublishFailedError(RuntimeError):
    """Raised when the GitHub CLI cannot create or push the repository; it carries what gh said."""


class InstallFailedError(RuntimeError):
    """Raised when installing CDD into the repository's .claude fails; it carries the install's output."""


class CddConfig:
    """The person's own cdd settings, in ``~/.cdd/config.json``: one object, read whole and written whole."""

    def __init__(self, home: CddHome | None = None) -> None:
        self.file = JsonFile((home or CddHome()).folder / _CONFIG_FILE)

    def value(self, key: str) -> str:
        found = self.file.read().get(key)
        return found if isinstance(found, str) else ""

    def set(self, key: str, value: str) -> None:
        self.file.write({**self.file.read(), key: value})


class SiblingRepo:
    """One repository in the repos folder: a folder whose ``.git`` is a folder of its own, never a linked worktree's."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder

    @property
    @data_field
    def name(self) -> str:
        return self.folder.name

    @property
    @data_field
    def path(self) -> str:
        return str(self.folder)

    @property
    @data_field
    def branch(self) -> str:
        return Git(self.folder).run("branch", "--show-current") if Git(self.folder).succeeds("rev-parse", "--git-dir") else ""

    @property
    @data_field
    def is_published(self) -> bool:
        return Git(self.folder).succeeds("remote", "get-url", "origin")

    @property
    @data_field
    def has_cdd(self) -> bool:
        """Whether CDD is installed in its .claude."""
        return (self.folder / ".claude" / "commands").is_dir()

    @staticmethod
    def is_one(folder: Path) -> bool:
        return (folder / ".git").is_dir()


@agent_toolset
class Repos:
    """The repositories in the repos folder, each a sibling of the others; opening one gives it its own chat."""

    def __init__(self, project: Path | str, config: CddConfig | None = None) -> None:
        # The checkout the calling chat works in: by default the repos folder is the folder its main clone sits in.
        self.project = Path(project).resolve()
        self.config = config or CddConfig()

    @classmethod
    @tool_subject
    def load(cls, *, project: Path | str) -> Repos:
        """The repositories beside the checkout of project, the folder the calling chat works in."""
        return cls(project)

    @property
    def folder(self) -> Path:
        """The folder holding the repositories: the one chosen with ``/repos-folder``, else the folder the calling
        chat's main clone sits in, which for a CDD worktree such as abd-cdd-x is the folder beside abd-context-driven-delivery."""
        chosen = self.config.value(_REPOS_FOLDER)
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
        self.config.set(_REPOS_FOLDER, str(folder))
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
        return [SiblingRepo(child) for child in sorted(folder.iterdir(), key=lambda f: f.name.lower()) if child.is_dir() and SiblingRepo.is_one(child)]

    @long_call
    @mcp
    @command(name="open-repo")
    @agent_tool
    @noSessionLog
    def open(
        self, name: str, folder: str = "", visibility: str = "private", publish: bool = True, install: bool = True, start_chat: bool = True
    ) -> str:
        """Open the repository called name in a chat of its own, on main. folder is where it is kept, by default the
        repos folder (/repos-folder). A repository not there yet is created: git init on main with a first commit.
        publish creates it on GitHub with the gh CLI when it has no origin; visibility is private (the default), public,
        or internal. With install, CDD is installed into its .claude; its .gitignore gets every line the CDD checkout's has.
        start_chat opens a new top-level Claude chat on the folder; the person sends its first prompt, which opens the
        repository's main session. Ask the person for visibility before publishing, offering private as the default."""
        cleaned = (name or "").strip()
        if not cleaned:
            raise RepoNameRequiredError()
        if visibility not in _VISIBILITIES:
            raise UnknownVisibilityError(visibility)
        root = (Path(folder).expanduser().resolve() if folder else self.folder) / cleaned
        steps = [self._create(root), self._ignore_as_cdd_does(root)]
        if publish:
            steps.append(self._publish(root, visibility))
        if install:
            steps.append(self._install_cdd(root))
        steps.append(self._open_chat(root, cleaned) if start_chat else self._chat_instructions(root, cleaned))
        return "\n".join(f"- {step}" for step in steps if step)

    @mcp
    @command(name="open-folder")
    @agent_tool
    @noSessionLog
    def open_folder(self, path: str, start_chat: bool = True) -> str:
        """Open the folder at path, any folder on disk, in a chat of its own, as it is, making it first when it is not
        there yet: no repository is created, nothing is published or installed, and a folder that is not a git
        repository stays one. start_chat opens a new top-level Claude chat on it; the person sends its first prompt,
        which opens the folder's main session. With no git there, its tickets get no worktree or chat of their own."""
        root = Path(path).expanduser().resolve()
        if root.is_file():
            raise PathIsAFileError(root)
        root.mkdir(parents=True, exist_ok=True)
        return self._open_chat(root, root.name) if start_chat else self._chat_instructions(root, root.name)

    def _create(self, root: Path) -> str:
        if (root / ".git").is_file():
            raise FolderIsAWorktreeError(root)
        if SiblingRepo.is_one(root):
            branch = Git(root).run("branch", "--show-current")
            if branch != _DEFAULT_BRANCH:
                return f"{root} is a repository already, on {branch or 'no branch'}; the new chat opens it as it is."
            return f"{root} is a repository already, on {_DEFAULT_BRANCH}."
        root.mkdir(parents=True, exist_ok=True)
        git = Git(root)
        git.run("init", "-b", _DEFAULT_BRANCH)
        readme = root / "README.md"
        if not readme.exists():
            readme.write_text(f"# {root.name}\n", encoding="utf-8")
        git.run("add", "-A")
        git.run("commit", "-m", "Initial commit")
        return f"Created {root} on {_DEFAULT_BRANCH} with a first commit."

    def _ignore_as_cdd_does(self, root: Path) -> str:
        """Add to root's .gitignore every line of the CDD checkout's that it lacks, and commit it."""
        source = _CDD_CHECKOUT / ".gitignore"
        if not source.is_file():
            return "The CDD checkout has no .gitignore to copy."
        target = root / ".gitignore"
        have = target.read_text(encoding="utf-8").splitlines() if target.is_file() else []
        present = {line.strip() for line in have}
        wanted = [line for line in source.read_text(encoding="utf-8").splitlines() if line.strip() and line.strip() not in present]
        if not [line for line in wanted if not line.lstrip().startswith("#")]:
            return ".gitignore already ignores what the CDD checkout ignores."
        text = "\n".join([*have, *([""] if have else []), _GITIGNORE_HEADER, *wanted]) + "\n"
        target.write_text(text, encoding="utf-8")
        Repo.of_project(root).commit([str(target)], "Ignore what the CDD checkout ignores", untracked=True)
        return f"Added {len(wanted)} lines to .gitignore from the CDD checkout's, and committed them."

    def _publish(self, root: Path, visibility: str) -> str:
        repo = Repo.of_project(root)
        if repo.has_origin:
            if repo.needs_push():
                repo.push_upstream()
                return "Pushed main to its origin."
            return f"Already published: {Git(root).run('remote', 'get-url', 'origin')}."
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
        return f"Published as a {visibility} GitHub repository: {Git(root).run('remote', 'get-url', 'origin')}."

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
            raise InstallFailedError(f"installing CDD into {root / '.claude'} failed: {(answer.stderr or answer.stdout).strip()[-2000:]}")
        return f"Installed CDD into {root / '.claude'}."

    def _chat_link(self, root: Path) -> str:
        return f"{_NEW_CHAT_LINK}?folder={quote(str(root), safe='')}&q={quote(_FIRST_PROMPT, safe='')}"

    def _open_chat(self, root: Path, name: str) -> str:
        """Open a new top-level chat on root in the Claude desktop app. The app asks the person to confirm the folder and
        send the first prompt; when the link cannot be opened, the agent is told to start the chat itself."""
        link = self._chat_link(root)
        try:
            if sys.platform == "win32":
                os.startfile(link)  # noqa: S606 - the link names the desktop app's own scheme
            else:
                subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", link], check=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            return self._chat_instructions(root, name)
        return f"Opened a new chat on {root} in the Claude app: send its first prompt there to open the main session."

    def _chat_instructions(self, root: Path, name: str) -> str:
        return (
            f"Start a top-level chat on {root}: start_session with initiation user_asked, context fresh, cwd {root}, "
            f"use_worktree false, title {name!r}, and prompt {_FIRST_PROMPT!r}. Or open {self._chat_link(root)}"
        )

