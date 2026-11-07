"""Agent BDD runtime configuration - local secrets and import paths."""
from __future__ import annotations

import os
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent
# The checkout: agent_bdd sits in cdd_guidance/practices.
_REPO_ROOT = _PKG_ROOT.parents[2]
_SECRETS_FILE = _PKG_ROOT / "conf" / ".secrets"


class AgentBddConf:
    """Load the agent's secrets and import paths into the process that runs agent specs; nothing loads them on import."""

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
        from harness.installation.installer import Installer

        Installer(repo=self._repo_root).ensure_import_path()

    def configure(self) -> None:
        self.load_secrets()
        self.ensure_import_paths()

