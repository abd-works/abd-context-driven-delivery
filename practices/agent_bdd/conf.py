"""Agent BDD runtime configuration - local secrets and import paths."""
from __future__ import annotations

import importlib.util
import os
import sys
import types
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _PKG_ROOT.parent.parent
_SECRETS_FILE = _PKG_ROOT / "conf" / ".secrets"


class AgentBddConf:
    """Load secrets and keep hyphenated folders importable for agent BDD."""

    def __init__(self, secrets_file: Path | None = None) -> None:
        self._secrets_file = secrets_file or _SECRETS_FILE
        self._repo_root = _REPO_ROOT

    def load_secrets(self) -> None:
        """Load KEY=VALUE lines into os.environ without overwriting existing vars."""
        if not self._secrets_file.is_file():
            return
        for raw in self._secrets_file.read_text(encoding="utf-8").splitlines():
            self._apply_secret_line(raw)

    def _apply_secret_line(self, raw: str) -> None:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            return
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key and value and not os.environ.get(key):
            os.environ[key] = value

    def ensure_import_paths(self) -> None:
        """Make repo root and category dirs importable without shadowing the MCP SDK."""
        from installation.installer import Installer

        Installer(repo=self._repo_root).ensure_import_path()

    def ensure_hyphenated_import(self, module_name: str, file_path: Path) -> None:
        """Register a module whose folder uses hyphens instead of underscores."""
        if module_name in sys.modules:
            return
        self._ensure_package_parents(module_name)
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load {module_name!r} from {file_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

    def _ensure_package_parents(self, module_name: str) -> None:
        parts = module_name.split(".")
        for index in range(1, len(parts)):
            package_name = ".".join(parts[:index])
            if package_name in sys.modules:
                continue
            package = types.ModuleType(package_name)
            package.__path__ = []  # type: ignore[attr-defined]
            sys.modules[package_name] = package

    def configure(self) -> None:
        self.load_secrets()
        self.ensure_import_paths()


AgentBddConf().configure()
