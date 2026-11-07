"""IdeLayout - where one IDE reads what an install writes, and the file shapes it reads."""
from __future__ import annotations


class IdeLayout:
    """How one IDE lays out the folder CDD installs into: the folder's name in a project, where its slash commands and
    rules go, and the shape of a rule file. Every per-IDE choice an install makes reads it here, so supporting another
    IDE means adding it here."""

    DEFAULT_IDE = "Cursor"
    _FOLDERS = {"Cursor": ".cursor", "VS Code": ".github", "Kilo": ".kilo", "Claude": ".claude"}

    def __init__(self, ide: str) -> None:
        self.ide = ide

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
