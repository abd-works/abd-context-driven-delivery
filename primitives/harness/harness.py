"""Harness — ide + path, write_deploy onto Deployment."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from primitives.harness.deployment import Deployment
from primitives.harness.registry import Registry

_STATE_NAME = ".deploy-state.json"
_DEFAULT_PATHS = {
    "Cursor": ".cursor",
    "VS Code": ".github",
    "Kilo": ".kilo",
}


class Harness:
    def __init__(self, ide: str | None = None, path: str | Path | None = None) -> None:
        state_file = Path(__file__).resolve().parent / _STATE_NAME
        if ide is None and path is None and state_file.is_file():
            data = json.loads(state_file.read_text(encoding="utf-8"))
            ide = data.get("ide")
            path = data.get("path")
        self.ide = ide or "Cursor"
        self.path = Path(path) if path is not None else Path(_DEFAULT_PATHS.get(self.ide, ".cursor"))
        self.deployment = Deployment(self.ide, self.path)
        self._state_file = state_file

    def write_deploy(self, hosts: Iterable[Any] | None = None) -> None:
        entries = list(hosts) if hosts is not None else Registry.load()
        for host in entries:
            self.deployment.deploy(host)
        self._state_file.write_text(
            json.dumps({"ide": self.ide, "path": str(self.path)}, indent=2) + "\n",
            encoding="utf-8",
        )
