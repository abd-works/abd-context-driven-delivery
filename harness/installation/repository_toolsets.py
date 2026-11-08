"""The toolsets one repository defines, found by reading its source, and the import path that loads them."""
from __future__ import annotations

import ast
import logging
import os
import sys
from pathlib import Path
from typing import Iterable

from harness.agent_tools.agent_tools import ToolsetReference
from harness.annotations.name import Name

logger = logging.getLogger(__name__)


class ToolsetUnloadable(Exception):
    """A toolset the repository's source defines whose module cannot be imported, or does not define it."""

    def __init__(self, reference: str, cause: Exception) -> None:
        super().__init__(f"{reference}: {type(cause).__name__}: {cause}")
        self.reference = reference
        self.cause = cause


class RepositoryToolsets:
    """*RepositoryToolsets* finds every toolset class in one repository by reading its source, without importing it,
    and puts the folders that load those classes on the import path. The installer, the hook server, and the MCP host
    each read the repository this way, so the three publish the same toolsets.

    A class is a toolset when it carries ``@agent_toolset`` or a member carries a publication annotation (``@skill``,
    ``@mcp``, ``@Hook``, ...). Folders of examples, fixtures, tests, and retired code are skipped, and so are specs.
    """

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
            "_retired",
            ".retired",
        }
    )
    # The packages under these folders import by their own names (``from validate.validate import ...``). This is the one
    # list of a checkout's import folders: the installer, the hook server, the cdd server's environment (CddHome), and
    # the catalog generator all read it through ``pythonpath``; ``pyproject.toml`` repeats it, since it cannot read code.
    IMPORT_FOLDERS = (
        "tools",
        "cdd_guidance/practices",
        "cdd_guidance/actions",
        "cdd_guidance/patterns",
        "cdd_guidance/builders",
    )
    _SKIP_FILE_NAMES = frozenset({"conftest.py"})
    _SKIP_FILE_SUFFIXES = ("_spec.py", "_test.py")
    # The annotations install reads on members, by name, because it reads the source without importing it. An annotation is matched
    # by its snake-case name, so its class name (``Mcp``) and its lowercase alias (``mcp``) both count.
    ANNOTATIONS = frozenset(
        {"skill", "command", "rules", "mcp", "hook", "hooks", "agent_tool", "agent_instructions"}
    )

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).resolve()
        self.unloadable: list[ToolsetUnloadable] = []

    @classmethod
    def of_running_checkout(cls) -> RepositoryToolsets:
        """The toolsets of the CDD checkout this code was imported from, the code a hook server or a probe runs, whichever
        project its call came from. This is the one place that works the checkout out from where the framework sits."""
        return cls(Path(__file__).resolve().parents[2])

    def import_path_entries(self) -> list[str]:
        """The repository root, then tools and the guidance packages under ``cdd_guidance``. Never ``harness/``, which
        would shadow the MCP SDK's ``mcp``; the collection walk still reads ``harness/``."""
        entries = [str(self.root)]
        for name in self.IMPORT_FOLDERS:
            folder = self.root / name
            if folder.is_dir():
                entries.append(str(folder))
        return entries

    def pythonpath(self) -> str:
        return os.pathsep.join(self.import_path_entries())

    def pycache_prefix(self) -> str:
        """One bytecode folder for this checkout, which keeps ``__pycache__`` out of the source tree."""
        return str(self.root / ".pycache")

    def use_for_this_process(self) -> None:
        """Import this checkout's modules in the running process, with their bytecode kept in its one folder. A process
        started by path rather than through ``pythonpath()``, such as the IDE's hook command, calls it first."""
        os.environ["PYTHONPYCACHEPREFIX"] = self.pycache_prefix()
        sys.pycache_prefix = self.pycache_prefix()
        self.ensure_import_path()

    def ensure_import_path(self) -> None:
        entries = self.import_path_entries()
        if entries[0] not in sys.path:
            sys.path.insert(0, entries[0])
        for entry in entries[1:]:
            if entry not in sys.path:
                sys.path.insert(0, entry)

    def classes(self) -> list[type]:
        """The class of every toolset the repository defines, each module imported, in folder order. A toolset that
        cannot be loaded is left out and kept in ``unloadable`` with its cause, so each reader decides whether it stops
        or serves the rest. A module that keeps something the framework declares a seam for, such as the sessions a
        tool call opens, registers it when it is imported, so a process that loads these classes has every
        registration the repository makes."""
        self.unloadable = []
        found: list[type] = []
        for reference in self.collect():
            try:
                found.append(ToolsetReference(reference).toolset_class)
            # A toolset's module is the repository's own code; any failure importing it is that toolset's failure.
            except Exception as error:  # noqa: BLE001
                logger.exception("could not load toolset %s", reference)
                self.unloadable.append(ToolsetUnloadable(reference, error))
        return found

    def collect(self) -> list[str]:
        """The ``module:Class`` reference of every toolset class in the repository, each once, in folder order."""
        self.ensure_import_path()
        found: dict[str, None] = {}
        for py_file in self._collected_files():
            found.update(dict.fromkeys(self._toolset_refs_in_file(py_file)))
        return list(found)

    def _toolset_refs_in_file(self, py_file: Path) -> list[str]:
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            return []
        module = self._module_name(py_file)
        if not module:
            return []
        return [
            str(ToolsetReference.in_module(module, node.name))
            for node in tree.body
            if isinstance(node, ast.ClassDef)
            and not self._is_hosted_only(node)
            and self._class_is_installable(node)
        ]

    def _collected_files(self) -> Iterable[Path]:
        skip = {name.lower() for name in self._SKIP_DIRS}
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [name for name in sorted(dirnames) if not name.startswith(".") and name.lower() not in skip]
            for name in sorted(filenames):
                path = Path(dirpath) / name
                if name.endswith(".py") and not self._skipped(path):
                    yield path

    def _skipped(self, py_file: Path) -> bool:
        try:
            folders = py_file.resolve().relative_to(self.root).parts[:-1]
        except ValueError:
            folders = py_file.parts[:-1]
        if any(part.startswith(".") or part.lower() in self._SKIP_DIRS for part in folders):
            return True
        name = py_file.name
        if name in self._SKIP_FILE_NAMES or (name.startswith("test_") and name.endswith(".py")):
            return True
        return name.endswith(self._SKIP_FILE_SUFFIXES)

    def _annotation_id(self, node: ast.expr) -> str | None:
        target = node.func if isinstance(node, ast.Call) else node
        if isinstance(target, ast.Name):
            return target.id
        if isinstance(target, ast.Attribute):
            return target.attr
        return None

    def _is_hosted_only(self, class_def: ast.ClassDef) -> bool:
        """Whether the class is annotated ``@hosted_only``: its tools run only through what holds it."""
        return any(self._annotation_id(dec) == "hosted_only" for dec in class_def.decorator_list)

    def _class_is_installable(self, class_def: ast.ClassDef) -> bool:
        if any(self._annotation_id(dec) == "agent_toolset" for dec in class_def.decorator_list):
            return True
        return any(
            Name(self._annotation_id(dec) or "").snake in self.ANNOTATIONS
            for item in class_def.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            for dec in item.decorator_list
        )

    def _module_name(self, py_file: Path) -> str | None:
        try:
            rel = py_file.resolve().relative_to(self.root)
        except ValueError:
            return None
        if rel.stem == "__init__":
            parts = list(rel.parts[:-2]) + [rel.parent.name]
        else:
            parts = list(rel.parts[:-1]) + [rel.stem]
        return ".".join(parts)
