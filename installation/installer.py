"""Installer — collect toolsets from the repo; install each tool on the installment."""
from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Iterable

InstallTracker = Callable[[Path], None]


class Destination:
    """Base annotation to define the installation destination of a tool. Subclasses annotate the member."""

    flag = ""

    def annotate(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        setattr(fn, self.flag, True)
        name = getattr(self, "name", None)
        if name is not None:
            setattr(fn, f"{self.flag}_name", name)
        return fn

    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        return self.annotate(fn)


class Installation:
    """``install(tool)`` writes the channel; subclass ``write``."""

    channel = ""

    def __init__(
        self,
        ide: str,
        path: Path | str,
        toolset_ref: str = "",
        repo: Path | str | None = None,
    ) -> None:
        self.ide = ide
        self.path = Path(path)
        self.toolset_ref = toolset_ref
        self.repo = Path(repo).resolve() if repo is not None else None
        self._install_tracker: InstallTracker | None = None

    def track_write(self, dest: Path) -> None:
        if self._install_tracker is not None:
            self._install_tracker(dest)

    def folder_for(self, toolset: Any) -> Path:
        """Repo-relative package folder the toolset already knows (practice dir, fidelity leaf)."""
        raw = getattr(toolset, "install_folder", None)
        if raw is None:
            slug = getattr(toolset, "slug", None) or "toolset"
            return Path(str(slug))
        folder = Path(raw)
        repo = self.repo
        if repo is None:
            return folder
        try:
            return folder.resolve().relative_to(repo)
        except ValueError:
            return Path(folder.name)

    def install(self, tool: Any) -> None:
        self.write(tool)

    def write(self, tool: Any) -> None:
        raise NotImplementedError


from harness.agent_tools.agent_tools import (
    AgentToolSet,
    InstallDestination,
    ToolSetCollection,
    agent_tool,
    agent_toolset,
)
from installation.harness_files.harness_files import MarkdownInstallation, Skill
from installation.mcp.mcp_server import Mcp


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
    _CATALOG_DIRS = ("harness", "tools", "practices", "actions")
    _SKIP_FILE_NAMES = frozenset({"conftest.py"})
    _SKIP_FILE_SUFFIXES = ("_spec.py", "_test.py")
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
        state_file = Path(__file__).resolve().parent / self._STATE_NAME
        if ide is None and path is None and state_file.is_file():
            data = json.loads(state_file.read_text(encoding="utf-8"))
            ide = data.get("ide")
            path = data.get("path")
        self.ide = ide or "Cursor"
        self.path = (
            Path(path)
            if path is not None
            else Path(self._DEFAULT_PATHS.get(self.ide, ".cursor"))
        )
        self.repo = Path(repo).resolve() if repo is not None else Path(__file__).resolve().parents[1]
        self._state_file = state_file
        from installation.hooks.hooks import HookInstallation
        from installation.mcp.mcp_server import McpInstallation

        self.ensure_import_path(self.repo)
        self._mcp = McpInstallation(self.ide, self.path, repo=self.repo)
        self._hook = HookInstallation(self.ide, self.path, repo=self.repo)
        self.nested_toolsets = ToolSetCollection()
        self._installed_paths: list[str] = []

    @classmethod
    def import_path_entries(cls, repo: Path | str) -> list[str]:
        """Repo root plus catalog folders. Never includes ``installation/`` (that shadows the MCP SDK)."""
        root = Path(repo).resolve()
        entries = [str(root)]
        for name in cls._CATALOG_DIRS:
            folder = root / name
            if folder.is_dir():
                entries.append(str(folder))
        return entries

    @classmethod
    def pythonpath(cls, repo: Path | str) -> str:
        return os.pathsep.join(cls.import_path_entries(repo))

    @classmethod
    def ensure_import_path(cls, repo: Path | str) -> None:
        entries = cls.import_path_entries(repo)
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
        toolsets: list[Any] = []
        seen: set[str] = set()
        for py_file in sorted(root.rglob("*.py")):
            if self._skip_collect_path(py_file):
                continue
            try:
                tree_ast = ast.parse(py_file.read_text(encoding="utf-8"))
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            module = self._module_name(py_file, root)
            if not module:
                continue
            for node in tree_ast.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                if not self._class_is_installable(node):
                    continue
                ref = f"{module}:{node.name}"
                if ref in seen:
                    continue
                seen.add(ref)
                toolsets.append(ref)
        return toolsets

    def _skip_collect_path(self, py_file: Path) -> bool:
        try:
            rel_parts = py_file.resolve().relative_to(self.repo.resolve()).parts
        except ValueError:
            rel_parts = py_file.parts
        if any(part.startswith(".") for part in rel_parts[:-1]):
            return True
        if any(part.lower() in self._SKIP_DIRS for part in py_file.parts):
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
        installation._install_tracker = self._track_write

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

    def get_installations(self, tool: Any) -> list[Installation]:
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
                markdown = MarkdownInstallation(
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
            for installation in self.get_installations(tool):
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
        from installation.hooks.hooks import HookInstallation
        from installation.mcp.mcp_server import McpInstallation

        self.clean()
        self._installed_paths = []
        self.ensure_import_path(self.repo)
        self._mcp = McpInstallation(self.ide, self.path, repo=self.repo)
        self._hook = HookInstallation(self.ide, self.path, repo=self.repo)
        if toolsets is None:
            toolsets = self.collect_toolsets()
        for item in toolsets:
            try:
                toolset = AgentToolSet.instantiate(item)
            except Exception:  # noqa: BLE001
                continue
            self._install_toolset(toolset)
            nested = getattr(toolset, "nested_toolsets", None)
            if not nested:
                continue
            for child in nested:
                self._install_toolset(child)
        self._save_state()
        self._mcp.standup()
        diagnosis = self._mcp.diagnose()
        notice = diagnosis.get("notice") or ""
        if notice:
            print(notice, file=sys.stderr)
        self._hook.standup()
        hook_diagnosis = self._hook.diagnose()
        hook_notice = hook_diagnosis.get("notice") or ""
        if hook_notice:
            print(hook_notice, file=sys.stderr)
        return self._mcp


__all__ = ["Destination", "Installation", "Installer"]
