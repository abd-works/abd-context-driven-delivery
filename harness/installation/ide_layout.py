"""IdeLayout - where one IDE reads what an install writes, and the file shapes it reads."""
from __future__ import annotations

import os
import sys
from pathlib import Path


class IdeLayout:
    """How one IDE lays out the folder CDD installs into: the folder's name in a project, where its slash commands and
    rules go, and the shape of a rule file. Every per-IDE choice an install makes reads it here, so supporting another
    IDE means adding it here."""

    DEFAULT_IDE = "Cursor"
    # The open project as Cursor and VS Code spell it inside a user-level MCP server entry.
    PROJECT_FOLDER = "${workspaceFolder}"
    _FOLDERS = {"Cursor": ".cursor", "VS Code": ".github", "Kilo": ".kilo", "Claude": ".claude"}
    # The file an IDE other than Claude Code reads its MCP servers from, in its settings folder or its install folder.
    MCP_CONFIG_NAME = "mcp.json"
    # The folders an install writes guidance into inside an IDE's folder, with the kind of guidance each holds.
    _GUIDANCE_FOLDERS = {"skills": "skill", "rules": "rule", "agents": "agent"}

    def __init__(self, ide: str) -> None:
        self.ide = ide

    @classmethod
    def every(cls) -> list[IdeLayout]:
        """The layout of each IDE CDD installs into."""
        return [cls(ide) for ide in cls._FOLDERS]

    @classmethod
    def installed_guidance_kind(cls, path: str) -> str:
        """skill, rule, or agent for a path inside a folder an install writes that guidance into, such as
        ``.cursor/rules/`` or ``.claude/skills/``, in any IDE's folder; empty for any other path. A hook that logs or
        toasts a file asks this, so every IDE's folders are known in one place."""
        posix = str(path).replace("\\", "/").lower()
        found = (kind for folder in cls._FOLDERS.values() for name, kind in cls._GUIDANCE_FOLDERS.items() if f"/{folder}/{name}/" in posix)
        return next(found, "")

    @property
    def folder_name(self) -> str:
        """The folder in a project the IDE reads, such as ``.cursor``."""
        return self._FOLDERS.get(self.ide, self._FOLDERS[self.DEFAULT_IDE])

    @property
    def is_claude_code(self) -> bool:
        return self.ide == "Claude"

    @property
    def rule_suffix(self) -> str:
        """Claude Code reads rules as ``.md``; the other IDEs as ``.mdc``."""
        return ".md" if self.is_claude_code else ".mdc"

    @property
    def commands_folder(self) -> str:
        """VS Code reads slash commands as prompts."""
        return "prompts" if self.ide == "VS Code" else "commands"

    @property
    def nests_skills(self) -> bool:
        """Claude Code only finds ``skills/<name>/SKILL.md``, so its skill folders are one level deep."""
        return not self.is_claude_code

    @property
    def scopes_rules_by_paths(self) -> bool:
        """Claude Code scopes a rule by ``paths``; the other IDEs by ``globs`` and ``alwaysApply``."""
        return self.is_claude_code

    @property
    def runs_hooks(self) -> bool:
        """Claude Code hooks are not wired yet, so its install carries no hook channel."""
        return not self.is_claude_code

    @property
    def user_settings_folder(self) -> Path | None:
        """The IDE's user settings folder, where it keeps the MCP servers every project sees; none for an IDE without
        one."""
        if self.ide == "VS Code":
            return self._vscode_user_folder()
        return Path.home() / self._FOLDERS[self.ide] if self.ide in ("Cursor", "Claude") else None

    @property
    def user_mcp_config(self) -> Path | None:
        """The file the IDE reads its user-level MCP servers from: Claude Code's ``~/.claude.json``, else ``mcp.json`` in
        its settings folder."""
        if self.is_claude_code:
            return Path.home() / ".claude.json"
        folder = self.user_settings_folder
        return folder / self.MCP_CONFIG_NAME if folder is not None else None

    @property
    def mcp_servers_key(self) -> str:
        """The key an MCP config lists its servers under: VS Code's ``servers``, every other IDE's ``mcpServers``."""
        return "servers" if self.ide == "VS Code" else "mcpServers"

    @property
    def names_mcp_transport(self) -> bool:
        """Whether an MCP server entry names its transport in ``type``; Cursor reads the transport from the entry's URL."""
        return self.ide != "Cursor"

    def _vscode_user_folder(self) -> Path:
        if sys.platform == "win32":
            appdata = os.environ.get("APPDATA")
            base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
        return base / "Code" / "User"
