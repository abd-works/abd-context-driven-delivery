"""Installer — collect toolsets from the repo; install each tool on the installment."""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any, Callable, Iterable

from primitives.agent_tools.agent_tools import (
    AgentToolSet,
    InstallDestination,
    ToolSetCollection,
    agent_tool,
    agent_toolset,
)


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

    def __init__(self, ide: str, path: Path | str, toolset_ref: str = "") -> None:
        self.ide = ide
        self.path = Path(path)
        self.toolset_ref = toolset_ref

    def install(self, tool: Any) -> None:
        self.write(tool)

    def write(self, tool: Any) -> None:
        raise NotImplementedError


from primitives.harness_files.harness_files import MarkdownInstallation, skill


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
    _SKIP_DIRS = frozenset({"__pycache__", "examples", ".venv", "node_modules", ".git"})
    _ANNOTATIONS = frozenset(
        {"skill", "command", "rules", "mcp", "hook", "agent_tool", "agent_instructions"}
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
        self.repo = Path(repo).resolve() if repo is not None else Path(__file__).resolve().parents[2]
        self._state_file = state_file
        from primitives.hooks.hooks import HookInstallation
        from primitives.mcp.mcp_server import McpInstallation

        self._mcp = McpInstallation(self.ide, self.path)
        self._hook = HookInstallation(self.ide, self.path)
        self.nested_toolsets = ToolSetCollection()

    def collect_toolsets(self, repo: Path | None = None) -> list[Any]:
        """Parse the repo for toolset classes whose members carry install annotations."""
        root = (repo or self.repo).resolve()
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        toolsets: list[Any] = []
        seen: set[str] = set()
        for py_file in sorted(root.rglob("*.py")):
            if any(part in self._SKIP_DIRS for part in py_file.parts):
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

    def get_installations(self, tool: Any) -> list[Installation]:
        destinations = tool.destinations
        installations: list[Installation] = []
        mcp_mode = InstallDestination.MCP in destinations
        if mcp_mode:
            installations.append(self._mcp)
        for destination in (
            InstallDestination.SKILL,
            InstallDestination.COMMAND,
            InstallDestination.RULE,
        ):
            if destination in destinations:
                installations.append(
                    MarkdownInstallation(
                        self.ide, self.path, destination, mcp_mode=mcp_mode
                    )
                )
        if InstallDestination.HOOK in destinations:
            installations.append(self._hook)
        return installations

    def _install_toolset(self, toolset: Any) -> None:
        for tool in toolset.tools.values():
            for installation in self.get_installations(tool):
                installation.install(tool)

    @skill
    @agent_tool
    def install(self, toolsets: Iterable[Any] | None = None) -> Any:
        """Install annotated toolsets into the IDE path — skills, commands, rules, MCP, and hooks."""
        from primitives.hooks.hooks import HookInstallation
        from primitives.mcp.mcp_server import McpInstallation

        self._mcp = McpInstallation(self.ide, self.path)
        self._hook = HookInstallation(self.ide, self.path)
        if toolsets is None:
            toolsets = self.collect_toolsets()
        for item in toolsets:
            try:
                toolset = AgentToolSet.instantiate(item)
            except Exception:  # noqa: BLE001
                continue
            self._install_toolset(toolset)
            for child in toolset.nested_toolsets:
                self._install_toolset(child)
        self._state_file.write_text(
            json.dumps({"ide": self.ide, "path": str(self.path)}, indent=2) + "\n",
            encoding="utf-8",
        )
        return self._mcp


Installer.install._mcp = True


__all__ = ["Destination", "Installation", "Installer"]
