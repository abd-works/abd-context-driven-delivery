"""Agent BDD runtime configuration — local secrets and import paths."""
from __future__ import annotations

import importlib.util
import os
import sys
import types
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _PKG_ROOT.parent
_SECRETS_FILE = _PKG_ROOT / "conf" / ".secrets"


def load_secrets(path: Path | None = None) -> None:
    """Load KEY=VALUE lines into os.environ without overwriting existing vars."""
    secrets = path or _SECRETS_FILE
    if not secrets.is_file():
        return
    for raw in secrets.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key and value and not os.environ.get(key):
            os.environ[key] = value


def ensure_import_paths() -> None:
    """Make repo root importable for tools, agents, and generator modules."""
    entry = str(_REPO_ROOT)
    if entry not in sys.path:
        sys.path.insert(0, entry)


def ensure_hyphenated_import(module_name: str, file_path: Path) -> None:
    """Register a module whose folder uses hyphens (e.g. clean-code/clean_code.py)."""
    if module_name in sys.modules:
        return
    parts = module_name.split(".")
    for index in range(1, len(parts)):
        package_name = ".".join(parts[:index])
        if package_name not in sys.modules:
            package = types.ModuleType(package_name)
            package.__path__ = []  # type: ignore[attr-defined]
            sys.modules[package_name] = package
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {module_name!r} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)


def configure() -> None:
    load_secrets()
    ensure_import_paths()


configure()
