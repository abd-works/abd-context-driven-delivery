"""Installer — collect toolsets from the repo; install each tool on the installment."""
from __future__ import annotations

import ast
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

from installation.destination import Installation
from harness.agent_tools.agent_tools import (
    AgentToolSet,
    InstallDestination,
    agent_tool,
    agent_toolset,
)
from installation.files import FileInstallation, Skill
from harness.hooks.hooks import Hook
from harness.mcp.mcp_server import Mcp


@agent_toolset
class Installer:
    """Collect installable toolsets; then install each tool."""

    domain_slug = "installer"
    _STATE_NAME = ".install-state.json"
    _DEFAULT_PATHS = {
        "Cursor": ".cursor",
        "VS Code": ".github",
        "Kilo": ".kilo",
    }
    _SKIP_DIRS = frozenset(
        {
            "__pycache__",
            "examples",
            "example",
            "fixtures",
            "fixture",
            "tests",
            ".venv",
            "node_modules",
            ".git",
            "harness",
        }
    )
    _CATALOG_DIRS = ("tools", "practices", "actions")
    _SKIP_FILE_NAMES = frozenset({"conftest.py"})
    _SKIP_FILE_SUFFIXES = ("_spec.py", "_test.py")
    _SKIP_ROOT_TOOLSET_NAMES = frozenset(
        {"RulesCollection", "MarkdownCollection", "GuidanceCollection"}
    )
    _ANNOTATIONS = frozenset(
        {
            "Skill",
            "Command",
            "Rules",
            "Agent",
            "AgentGuidance",
            "Mcp",
            "Hook",
            "Hooks",
            "agent_tool",
            "agent_instructions",
        }
    )

    def __init__(
        self,
        ide: str | None = None,
        path: str | Path | None = None,
        repo: str | Path | None = None,
    ) -> None:
        self.repo = Path(repo).resolve() if repo is not None else Path(__file__).resolve().parents[1]
        shared_state = Path(__file__).resolve().parent / self._STATE_NAME
        if ide is None and path is None and shared_state.is_file():
            data = json.loads(shared_state.read_text(encoding="utf-8"))
            ide = data.get("ide")
            stored = data.get("path")
            if stored and Path(stored).exists() and not self._is_ephemeral_install_path(stored):
                path = stored
        self.ide = ide or "Cursor"
        default_path = self.repo / self._DEFAULT_PATHS.get(self.ide, ".cursor")
        self.path = Path(path) if path is not None else default_path
        if self._is_ephemeral_install_path(self.path):
            self._state_file = self.path / self._STATE_NAME
        else:
            self._state_file = shared_state
        from harness.mcp.mcp_server import McpInstallation

        self.ensure_import_path()
        self._mcp = McpInstallation(self.ide, self.path, repo=self.repo)
        self._hook: Any = None
        self._installed_paths: list[str] = []

    def _is_ephemeral_install_path(self, path: Path | str) -> bool:
        try:
            resolved = Path(path).resolve()
            temp = Path(tempfile.gettempdir()).resolve()
            return resolved == temp or temp in resolved.parents
        except OSError:
            return False

    def import_path_entries(self, repo: Path | str | None = None) -> list[str]:
        """Repo root plus tools, practices, and actions. Never ``installation/`` or ``harness/`` (those shadow the MCP SDK)."""
        root = Path(repo).resolve() if repo is not None else self.repo
        entries = [str(root)]
        for name in self._CATALOG_DIRS:
            folder = root / name
            if folder.is_dir():
                entries.append(str(folder))
        return entries

    def pythonpath(self, repo: Path | str | None = None) -> str:
        return os.pathsep.join(self.import_path_entries(repo))

    def ensure_import_path(self, repo: Path | str | None = None) -> None:
        entries = self.import_path_entries(repo)
        root = entries[0]
        if root not in sys.path:
            sys.path.insert(0, root)
        for entry in entries[1:]:
            if entry not in sys.path:
                sys.path.insert(0, entry)

    def collect_toolsets(self, repo: Path | None = None) -> list[Any]:
        """Parse the repo for toolset classes whose members carry install annotations."""
        root = (repo or self.repo).resolve()
        self.ensure_import_path(root)
        seen: set[str] = set()
        toolsets: list[Any] = []
        for py_file in sorted(root.rglob("*.py")):
            if self._skip_collect_path(py_file):
                continue
            for ref in self._toolset_refs_in_file(py_file, root):
                if ref in seen:
                    continue
                seen.add(ref)
                toolsets.append(ref)
        return toolsets

    def _toolset_refs_in_file(self, py_file: Path, root: Path) -> list[str]:
        try:
            tree_ast = ast.parse(py_file.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            return []
        module = self._module_name(py_file, root)
        if not module:
            return []
        refs: list[str] = []
        for node in tree_ast.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if node.name in self._SKIP_ROOT_TOOLSET_NAMES:
                continue
            if not self._class_is_installable(node):
                continue
            refs.append(f"{module}:{node.name}")
        return refs

    def _skip_collect_path(self, py_file: Path) -> bool:
        try:
            rel_parts = py_file.resolve().relative_to(self.repo.resolve()).parts
        except ValueError:
            rel_parts = py_file.parts
        if any(part.startswith(".") for part in rel_parts[:-1]):
            return True
        if rel_parts[:2] == ("harness", "knowledge_graph"):
            pass
        elif any(part.lower() in self._SKIP_DIRS for part in py_file.parts):
            return True
        name = py_file.name
        if name in self._SKIP_FILE_NAMES:
            return True
        if name.startswith("test_") and name.endswith(".py"):
            return True
        return name.endswith(self._SKIP_FILE_SUFFIXES)

    def _annotation_id(self, node: ast.expr) -> str | None:
        target = node.func if isinstance(node, ast.Call) else node
        if isinstance(target, ast.Name):
            return target.id
        if isinstance(target, ast.Attribute):
            return target.attr
        return None

    def _class_is_installable(self, class_def: ast.ClassDef) -> bool:
        if any(self._annotation_id(dec) == "agent_toolset" for dec in class_def.decorator_list):
            return True
        for item in class_def.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if any(self._annotation_id(dec) in self._ANNOTATIONS for dec in item.decorator_list):
                return True
        return False

    def _module_name(self, py_file: Path, root: Path) -> str | None:
        try:
            rel = py_file.resolve().relative_to(root.resolve())
        except ValueError:
            return None
        if rel.stem == "__init__":
            parts = list(rel.parts[:-2]) + [rel.parent.name]
        else:
            parts = list(rel.parts[:-1]) + [rel.stem]
        return ".".join(parts)

    def _track_write(self, dest: Path) -> None:
        try:
            rel = dest.resolve().relative_to(self.path.resolve())
        except ValueError:
            return
        normalized = str(rel).replace("\\", "/")
        if normalized not in self._installed_paths:
            self._installed_paths.append(normalized)

    def _bind_install_tracker(self, installation: Installation) -> None:
        installation.bind_tracker(self._track_write)

    def _load_state(self) -> dict[str, Any]:
        if not self._state_file.is_file():
            return {}
        try:
            return json.loads(self._state_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_state(self) -> None:
        payload = {
            "ide": self.ide,
            "path": str(self.path),
            "installed_files": self._installed_paths,
        }
        self._state_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def _prune_empty_parents(self, file_path: Path) -> None:
        stop_at = {self.path / name for name in ("skills", "rules", "commands", "prompts")}
        parent = file_path.parent
        while parent not in stop_at and parent != self.path:
            if not parent.is_dir() or any(parent.iterdir()):
                break
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent

    def installations_for(self, tool: Any) -> list[Installation]:
        destinations = tool.destinations
        installations: list[Installation] = []
        mcp_mode = InstallDestination.MCP in destinations
        if mcp_mode:
            self._bind_install_tracker(self._mcp)
            installations.append(self._mcp)
        for destination in (
            InstallDestination.SKILL,
            InstallDestination.COMMAND,
            InstallDestination.RULE,
        ):
            if destination in destinations:
                markdown = FileInstallation(
                    self.ide,
                    self.path,
                    destination,
                    mcp_mode=mcp_mode,
                    repo=self.repo,
                )
                self._bind_install_tracker(markdown)
                installations.append(markdown)
        if InstallDestination.HOOK in destinations:
            self._bind_install_tracker(self._hook)
            installations.append(self._hook)
        return installations

    def _install_toolset(self, toolset: Any) -> None:
        for tool in toolset.tools.values():
            for installation in self.installations_for(tool):
                installation.install(tool)

    @Mcp
    @Skill
    @agent_tool
    def clean(self) -> list[str]:
        """Remove files written by the previous install for this IDE path."""
        state = self._load_state()
        install_path = Path(str(state.get("path", self.path)))
        if str(install_path.resolve()) != str(self.path.resolve()):
            return []
        removed: list[str] = []
        for rel in state.get("installed_files", []):
            dest = install_path / rel
            if Path(rel).name == "mcp.json":
                continue
            if not dest.is_file():
                continue
            dest.unlink()
            removed.append(rel)
            self._prune_empty_parents(dest)
        return removed

    @Mcp
    @Skill
    @agent_tool
    def install(self, toolsets: Iterable[Any] | None = None) -> Any:
        """Install annotated toolsets into the IDE path — skills, commands, rules, MCP, and hooks. Runs clean first."""
        self.clean()
        self._installed_paths = []
        self.ensure_import_path()
        self._reset_channels()
        self._install_all(toolsets)
        self._save_state()
        self._standup_channels()
        self.ensure_mcp_host()
        return self._mcp

    def _reset_channels(self) -> None:
        from harness.hooks.hooks import HookInstallation
        from harness.mcp.mcp_server import McpInstallation

        self._mcp = McpInstallation(self.ide, self.path, repo=self.repo)
        self._hook = HookInstallation(self.ide, self.path, repo=self.repo)

    def _install_all(self, toolsets: Iterable[Any] | None) -> None:
        if toolsets is None:
            toolsets = self.collect_toolsets()
        for item in toolsets:
            try:
                toolset = AgentToolSet.instantiate(item)
            except Exception as error:  # noqa: BLE001
                print(f"install skipped {item}: {error}", file=sys.stderr)
                continue
            self._install_toolset(toolset)
            for child in toolset.child_toolsets():
                self._install_toolset(child)

    def _standup_channels(self) -> None:
        self._mcp.standup()
        self._print_channel_notice(self._mcp.diagnose())
        self._hook.standup()
        self._print_channel_notice(self._hook.diagnose())

    def _print_channel_notice(self, diagnosis: dict[str, Any]) -> None:
        notice = diagnosis.get("notice") or ""
        if notice:
            print(notice, file=sys.stderr)

    def ensure_mcp_host(self, payload: dict[str, Any] | None = None) -> str:
        from harness.mcp.mcp_server import McpInstallation

        return McpInstallation(self.ide, self.path, repo=self.repo).ensure_cursor_host()

    @Hook("sessionStart")
    def ensure_mcp_host_on_session_start(self, payload: dict[str, Any] | None = None) -> str:
        return self.ensure_mcp_host(payload)

    @Hook("afterAgentResponse")
    def ensure_mcp_host_after_agent_response(
        self, payload: dict[str, Any] | None = None
    ) -> str:
        return self.ensure_mcp_host(payload)


__all__ = ["Installation", "Installer"]
