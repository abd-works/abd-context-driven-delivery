"""Installer — collect toolsets from the repo; install each tool on the installment."""
from __future__ import annotations

import ast
import json
import os
import shutil
import stat
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Iterable

from harness.installation.destination import Installation, noCatalog
from harness.agent_tools.agent_tools import (
    AgentToolSet,
    InstallDestination,
    agent_instructions,
    agent_tool,
    agent_toolset,
)
from harness.installation.files import FileInstallation, Skill
from harness.hooks.hooks import Hook
from harness.markdown import markdown
from harness.mcp.mcp_server import Mcp


@noCatalog
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
            ".pycache",
            "examples",
            "_examples",
            "example",
            "fixtures",
            "fixture",
            "tests",
            ".venv",
            "node_modules",
            ".git",
            "retired",
        }
    )
    _CATALOG_DIRS = (
        "tools",
        "cdd_guidance/practices",
        "cdd_guidance/actions",
        "cdd_guidance/patterns",
        "cdd_guidance/builders",
    )
    _SKIP_FILE_NAMES = frozenset({"conftest.py"})
    _SKIP_FILE_SUFFIXES = ("_spec.py", "_test.py")
    _SKIP_ROOT_TOOLSET_NAMES = frozenset(
        {
            "RulesCollection",
            "MarkdownCollection",
            "GuidanceCollection",
            "PracticeGuidance",
            "FidelityGuidance",
        }
    )
    _DEPLOYED_CHANNELS = ("toolset", "skill", "command", "rules", "mcp", "hook", "agent")
    _GREEN_SURFACE_CHANGE = 0.10
    _YELLOW_SURFACE_CHANGE = 0.50
    _DIAGNOSTICS_LOG = "diagnostics.json"
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
        self.repo = Path(repo).resolve() if repo is not None else Path(__file__).resolve().parents[2]
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
        self._deployed_toolsets: list[str] = []
        self.diagnosis: list[str] = []

    def _is_ephemeral_install_path(self, path: Path | str) -> bool:
        try:
            resolved = Path(path).resolve()
            temp = Path(tempfile.gettempdir()).resolve()
            return resolved == temp or temp in resolved.parents
        except OSError:
            return False

    def import_path_entries(self, repo: Path | str | None = None) -> list[str]:
        """Repo root plus tools and the guidance packages under ``cdd_guidance``. Never ``harness/`` (that shadows the MCP SDK). The deploy walk still parses ``harness/``."""
        root = Path(repo).resolve() if repo is not None else self.repo
        entries = [str(root)]
        for name in self._CATALOG_DIRS:
            folder = root / name
            if folder.is_dir():
                entries.append(str(folder))
        return entries

    def pythonpath(self, repo: Path | str | None = None) -> str:
        return os.pathsep.join(self.import_path_entries(repo))

    def pycache_prefix(self, repo: Path | str | None = None) -> str:
        """One bytecode directory for this checkout. Keeps ``__pycache__`` out of the source tree."""
        root = Path(repo).resolve() if repo is not None else self.repo
        return str(root / ".pycache")

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
        for py_file in self._iter_collect_files(root):
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

    def _iter_collect_files(self, root: Path) -> Iterable[Path]:
        skip = {name.lower() for name in self._SKIP_DIRS}
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                name
                for name in sorted(dirnames)
                if not name.startswith(".") and name.lower() not in skip
            ]
            for name in sorted(filenames):
                if not name.endswith(".py"):
                    continue
                path = Path(dirpath) / name
                if self._skip_collect_path(path):
                    continue
                yield path

    def _skip_collect_path(self, py_file: Path) -> bool:
        try:
            rel_parts = py_file.resolve().relative_to(self.repo.resolve()).parts
        except ValueError:
            rel_parts = py_file.parts
        if any(part.startswith(".") for part in rel_parts[:-1]):
            return True
        if any(part.lower() in self._SKIP_DIRS for part in rel_parts):
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
        stop_at = {self.path / name for name in ("skills", "rules", "commands", "prompts", "agents")}
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
            if Path(rel).name in {"mcp.json", self._DIAGNOSTICS_LOG}:
                continue
            if not dest.is_file():
                continue
            dest.unlink()
            removed.append(rel)
            self._prune_empty_parents(dest)
        self._prune_empty_skill_dirs()
        return removed

    def _prune_empty_skill_dirs(self) -> None:
        skills = self.path / "skills"
        if not skills.is_dir():
            return
        for dirpath, _dirnames, _filenames in os.walk(skills, topdown=False):
            folder = Path(dirpath)
            if folder == skills:
                continue
            try:
                next(folder.iterdir())
            except StopIteration:
                try:
                    folder.rmdir()
                except OSError:
                    pass

    def _rmtree(self, path: Path) -> None:
        def onerror(func: Any, target: str, _exc: Any) -> None:
            os.chmod(target, stat.S_IWRITE)
            func(target)

        shutil.rmtree(path, onerror=onerror)

    def _remove_legacy_underscore_skills(self) -> None:
        skills = self.path / "skills"
        if not skills.is_dir():
            return
        for dirpath, dirnames, _filenames in os.walk(skills):
            root = Path(dirpath)
            for name in list(dirnames):
                kebab = name.replace("_", "-")
                if kebab == name or not (root / kebab).exists():
                    continue
                twin = root / name
                if twin.is_dir():
                    self._rmtree(twin)

    @Mcp
    @Skill
    @agent_tool
    def install(
        self,
        toolsets: Iterable[Any] | None = None,
        replace: bool = True,
    ) -> Any:
        """Install annotated toolsets into the IDE path — skills, commands, rules, MCP, and hooks. ``replace`` wipes files from the previous install first."""
        if replace:
            self.clean()
            self._installed_paths = []
        else:
            self._installed_paths = [
                rel
                for rel in self._load_state().get("installed_files", [])
                if (self.path / rel).is_file()
            ]
        self.ensure_import_path()
        self._reset_channels()
        self._install_all(toolsets)
        self._install_agents()
        self._remove_legacy_underscore_skills()
        self._prune_empty_skill_dirs()
        self._save_state()
        self._standup_channels()
        self.ensure_mcp_host()
        self.diagnosis = self.diagnose_after_install()
        for report in self.diagnosis:
            if report.startswith("!"):
                print(report, file=sys.stderr)
        return self._mcp

    def _install_agents(self) -> None:
        """Copy cdd_guidance/agents into the IDE agents folder. The source stays on cdd_guidance."""
        source = self.repo / "cdd_guidance" / "agents"
        if not source.is_dir():
            return
        for path in sorted(source.glob("*.md")):
            dest = self.path / "agents" / f"{self._agent_name(path)}.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            self._track_write(dest)

    def _agent_name(self, path: Path) -> str:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            return path.stem
        for line in text.splitlines()[1:]:
            if line.strip() == "---":
                break
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip()
                if name:
                    return name
        return path.stem

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
                self._remember_toolset(item, toolset)
                self._install_toolset(toolset)
                for child in toolset.child_toolsets():
                    self._install_toolset(child)
            except Exception as error:
                raise RuntimeError(f"install failed for {item}") from error

    def _standup_channels(self) -> None:
        self._mcp.standup()
        self._print_channel_notice(self._mcp.diagnose())
        self._hook.standup()
        self._print_channel_notice(self._hook.diagnose())
        if not self._is_ephemeral_install_path(self.path) and not self._mcp_host_is_this_process():
            self.ensure_runtimes()

    def ensure_runtimes(self) -> dict[str, Any]:
        """Start the hook daemon and MCP host; fail if either stays down."""
        hook_pid = self._ensure_hook_runtime()
        mcp = self._ensure_mcp_runtime()
        print(
            f"hook server pid={hook_pid} mcp host={mcp}",
            file=sys.stderr,
        )
        return {"hook": "running", "mcp": mcp}

    def _ensure_hook_runtime(self) -> int | None:
        from harness.hooks.hook_daemon import HookDaemon
        from harness.hooks.hook_server import HookServer

        HookServer.ensure(self.repo)
        live = HookDaemon().live_address(HookServer.state_path(self.repo))
        if live is None:
            raise RuntimeError("install failed: hook server is not running")
        return live[2]

    def _ensure_mcp_runtime(self) -> str:
        from harness.mcp.mcp_server import McpInstallation

        installation = McpInstallation(self.ide, self.path, repo=self.repo)
        status = installation.ensure_cursor_host()
        if installation.cursor_host_is_running():
            return "running"
        deadline = time.time() + 20
        while time.time() < deadline:
            if installation.cursor_host_is_running():
                return "running"
            time.sleep(0.25)
        raise RuntimeError(f"install failed: MCP host is not running ({status})")

    def _print_channel_notice(self, diagnosis: dict[str, Any]) -> None:
        notice = diagnosis.get("notice") or ""
        if notice:
            print(notice, file=sys.stderr)

    def _remember_toolset(self, item: Any, toolset: Any) -> None:
        if isinstance(item, str):
            ref = item
        else:
            cls = type(toolset)
            ref = f"{cls.__module__}:{cls.__name__}"
        if ref not in self._deployed_toolsets:
            self._deployed_toolsets.append(ref)

    def diagnose_after_install(self) -> list[str]:
        """Record install-channel diagnostics only; guidance probes use ``/guidance-diagnostics``."""
        report = str(self.diagnose_install())
        records = [
            {"name": "diagnose_install", "report": report, "color": self._color_in(report)}
        ]
        self._append_install_log(records)
        return [report]

    @agent_instructions
    def diagnose_install(self) -> str:
        """Compare this install with the last diagnostics.json entry and report counts, or what changed."""
        actual = self._deployed_channels()
        last = self._baseline_channels()
        baseline = last if last is not None else {name: [] for name in self._DEPLOYED_CHANNELS}
        added, removed = self._channel_delta(actual, baseline)
        color = (
            "green"
            if last is None
            else self._surface_color(self._surface_change(added, removed, actual, baseline))
        )
        body = "\n".join(
            part
            for part in (
                self._compare_report(actual, baseline, added, removed),
                self._runtime_status_report(),
            )
            if part.strip()
        )
        if color != "red":
            return self._colored_report(color, body)
        return self._colored_report(color, f"!\n{body}\n{self.diagnose_instructions()}")

    def _surface_change(
        self,
        added: dict[str, list[str]],
        removed: dict[str, list[str]],
        actual: dict[str, list[str]],
        baseline: dict[str, list[str]],
    ) -> float:
        changed = sum(len(items) for items in added.values())
        changed += sum(len(items) for items in removed.values())
        total = 0
        for name in self._DEPLOYED_CHANNELS:
            total += len(actual.get(name, [])) + len(baseline.get(name, []))
        if total == 0:
            return 0.0
        return changed / total

    def _surface_color(self, ratio: float) -> str:
        if ratio <= self._GREEN_SURFACE_CHANGE:
            return "green"
        if ratio <= self._YELLOW_SURFACE_CHANGE:
            return "yellow"
        return "red"

    def _color_in(self, report: str) -> str:
        for line in report.splitlines():
            if line in {"green", "yellow", "red"}:
                return line
        return "green"

    def _colored_report(self, color: str, body: str) -> str:
        if body.startswith("!"):
            rest = body[1:].lstrip("\n")
            return f"!\n{color}\n{rest}"
        return f"{color}\n{body}"

    def _compare_report(
        self,
        actual: dict[str, list[str]],
        baseline: dict[str, list[str]],
        added: dict[str, list[str]],
        removed: dict[str, list[str]],
    ) -> str:
        lines = ["installed"]
        for name in self._DEPLOYED_CHANNELS:
            previous = len(baseline.get(name, []))
            current = len(actual.get(name, []))
            lines.append(f"{name} {previous} -> {current} (delta {current - previous})")
        for name in self._DEPLOYED_CHANNELS:
            for item in added.get(name, []):
                lines.append(f"new {name}: {item}")
            for item in removed.get(name, []):
                lines.append(f"deleted {name}: {item}")
        return "\n".join(lines)

    def _channel_delta(
        self,
        actual: dict[str, list[str]],
        baseline: dict[str, list[str]],
    ) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
        added: dict[str, list[str]] = {}
        removed: dict[str, list[str]] = {}
        for name in self._DEPLOYED_CHANNELS:
            got = set(actual.get(name, []))
            expected = set(baseline.get(name, []))
            extra = sorted(got - expected)
            missing = sorted(expected - got)
            if extra:
                added[name] = extra
            if missing:
                removed[name] = missing
        return added, removed

    def _baseline_channels(self) -> dict[str, list[str]] | None:
        path = self._diagnostics_log()
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        installs = data.get("installs") or []
        if not installs:
            return None
        return self._channels_from_entry(installs[-1])

    def _channels_from_entry(self, entry: dict[str, Any]) -> dict[str, list[str]]:
        channels: dict[str, list[str]] = {}
        for name in self._DEPLOYED_CHANNELS:
            field = entry.get(name) or {}
            items = field.get("items") if isinstance(field, dict) else field
            channels[name] = [str(item) for item in items or []]
        return channels

    def _diagnostics_log(self) -> Path:
        return self.path / self._DIAGNOSTICS_LOG

    def _append_install_log(self, records: list[dict[str, str]]) -> None:
        path = self._diagnostics_log()
        installs: list[dict[str, Any]] = []
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            installs = list(data.get("installs") or [])
        channels = self._deployed_channels()
        color = "green"
        for record in records:
            if record["color"] == "red":
                color = "red"
                break
            if record["color"] == "yellow":
                color = "yellow"
        entry: dict[str, Any] = {"color": color, "diagnostics": records}
        for name in self._DEPLOYED_CHANNELS:
            items = channels.get(name, [])
            entry[name] = {"count": len(items), "items": items}
        installs.append(entry)
        data: dict[str, Any] = {}
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
        data["installs"] = installs
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def write_diagnostics_section(self, section: str, payload: dict[str, Any]) -> None:
        """Add or replace one top-level section in diagnostics.json. Install history stays."""
        path = self._diagnostics_log()
        data: dict[str, Any] = {}
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
        current = data.get(section)
        if isinstance(payload, dict):
            merged = dict(current) if isinstance(current, dict) else {}
            merged.update(payload)
            child_colors = [
                value.get("color")
                for value in merged.values()
                if isinstance(value, dict) and value.get("color") in {"green", "yellow", "red"}
            ]
            if child_colors:
                merged["color"] = (
                    "red"
                    if "red" in child_colors
                    else "yellow"
                    if "yellow" in child_colors
                    else "green"
                )
            data[section] = merged
        else:
            data[section] = payload
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def _deployed_channels(self) -> dict[str, list[str]]:
        return {
            "toolset": list(self._deployed_toolsets),
            "skill": self._markdown_names("skills", "SKILL.md"),
            "command": self._command_names(),
            "rules": self._rule_names(),
            "mcp": self._mcp_names(),
            "hook": self._hook_names(),
            "agent": self._markdown_names("agents", "*.md"),
        }

    def _markdown_names(self, folder_name: str, file_name: str) -> list[str]:
        folder = self.path / folder_name
        if not folder.is_dir():
            return []
        if file_name == "SKILL.md":
            names = {path.parent.name for path in folder.rglob(file_name)}
        else:
            names = {path.stem for path in folder.rglob(file_name)}
        return sorted(names)

    def _command_names(self) -> list[str]:
        names = set(self._markdown_names("commands", "*.md"))
        names.update(self._markdown_names("prompts", "*.md"))
        return sorted(names)

    def _rule_names(self) -> list[str]:
        folder = self.path / "rules"
        if not folder.is_dir():
            return []
        return sorted(path.stem for path in folder.rglob("*.mdc"))

    def _mcp_names(self) -> list[str]:
        operations = getattr(self._mcp, "mcp_operations", None) or []
        names = [str(getattr(op, "mcp_name", "")) for op in operations if getattr(op, "mcp_name", "")]
        if names:
            return sorted(names)
        stored = self._load_state().get("mcp") or []
        return sorted(str(name) for name in stored)

    def _hook_names(self) -> list[str]:
        dest = self.path / "hook-handlers.json"
        if not dest.is_file():
            return []
        try:
            data = json.loads(dest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return sorted(
            str(item.get("operation") or item.get("event") or "")
            for item in data.get("handlers") or []
            if item.get("operation") or item.get("event")
        )

    def _mcp_host_is_this_process(self) -> bool:
        from harness.mcp.mcp_server import HostPid

        return HostPid.from_ide(self.path).is_this_process

    def _mcp_host_is_running(self) -> bool:
        from harness.mcp.mcp_server import McpInstallation

        return McpInstallation(self.ide, self.path, repo=self.repo).cursor_host_is_running()

    def _hook_server_status(self) -> tuple[bool, int | None]:
        from harness.hooks.hook_daemon import HookDaemon
        from harness.hooks.hook_server import HookServer

        live = HookDaemon().live_address(HookServer.state_path(self.repo))
        if live is None:
            return False, None
        return True, live[2]

    def _registered_hook_events(self) -> list[str]:
        dest = self.path / "hooks.json"
        if not dest.is_file():
            return []
        try:
            data = json.loads(dest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        hooks = data.get("hooks")
        if not isinstance(hooks, dict):
            return []
        return sorted(str(name) for name in hooks if name)

    def _registered_hook_operations(self) -> list[str]:
        dest = self.path / "hook-handlers.json"
        if not dest.is_file():
            return []
        try:
            data = json.loads(dest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        names = {
            str(item.get("operation") or "")
            for item in data.get("handlers") or []
            if item.get("operation")
        }
        return sorted(name for name in names if name)

    def _runtime_status_report(self) -> str:
        mcp = "running" if self._mcp_host_is_running() else "not running"
        hook_live, hook_pid = self._hook_server_status()
        hook = f"running (pid {hook_pid})" if hook_live else "not running"
        events = self._registered_hook_events()
        operations = self._registered_hook_operations()
        lines = [
            f"mcp host: {mcp}",
            f"hook server: {hook}",
        ]
        if events:
            lines.append(f"hooks registered (events): {', '.join(events)}")
        else:
            lines.append("hooks registered (events): none")
        if operations:
            lines.append(f"hook handlers (operations): {', '.join(operations)}")
        else:
            lines.append("hook handlers (operations): none")
        return "\n".join(lines)

    @markdown("install")
    def install_instructions(self) -> str:
        """Install instructions."""

    @markdown("clean")
    def clean_instructions(self) -> str:
        """Clean instructions."""

    @markdown("diagnose_install")
    def diagnose_install_instructions(self) -> str:
        """Diagnose-install instructions."""

    @markdown("ensure_runtimes")
    def runtime_instructions(self) -> str:
        """Runtime instructions."""

    @agent_instructions
    def diagnose_instructions(self) -> str:
        """How to diagnose an install whose deployed counts do not match."""
        self.install_instructions
        self.clean_instructions
        self.diagnose_install_instructions
        self.runtime_instructions
        return str(self.diagnose_install_instructions).strip()

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
