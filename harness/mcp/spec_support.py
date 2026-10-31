"""Spec support: a throwaway user home, and a real stdio MCP host that records its pid there."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from harness.installation.installer import Installer
from harness.mcp.mcp_server import HostPid

_REPO_ROOT = Path(__file__).resolve().parents[2]


class UserHome:
    """Points HOME, USERPROFILE and APPDATA at a temp folder so specs never touch the user's own config."""

    _KEYS = ("HOME", "USERPROFILE", "APPDATA")

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-user-home-"))
        self._prior = {key: os.environ.get(key) for key in self._KEYS}

    def enter(self) -> Path:
        os.environ["HOME"] = str(self.root)
        os.environ["USERPROFILE"] = str(self.root)
        os.environ["APPDATA"] = str(self.root / "AppData" / "Roaming")
        return self.root

    def leave(self) -> None:
        for key, value in self._prior.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        shutil.rmtree(self.root, ignore_errors=True)


class StdioMcpHost:
    """The host an IDE would spawn: ``start_host.py`` on stdio, claiming its pid in ``ide_path``."""

    TOOLSETS = "harness.guidance.fixtures.agentic_ops.agentic_ops:SampleMcpOps"
    CLAIM_SECONDS = 60

    def __init__(self, ide_path: Path) -> None:
        self.ide_path = ide_path
        self._process: subprocess.Popen | None = None

    def start(self) -> None:
        self.ide_path.mkdir(parents=True, exist_ok=True)
        env = {
            **os.environ,
            "PYTHONPATH": Installer(repo=_REPO_ROOT).pythonpath(),
            "CDD_IDE_PATH": str(self.ide_path),
            "CDD_PROJECT": str(_REPO_ROOT),
            "MCP_TOOLSET_REFS": self.TOOLSETS,
        }
        script = _REPO_ROOT / "harness" / "mcp" / "scripts" / "start_host.py"
        self._process = subprocess.Popen(
            [sys.executable, "-u", str(script)],
            cwd=str(_REPO_ROOT),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._wait_for_claim()

    def stop(self) -> None:
        if self._process is None:
            return
        self._process.kill()
        self._process.wait()
        self._process = None

    def _wait_for_claim(self) -> None:
        pid = HostPid.from_ide(self.ide_path)
        deadline = time.time() + self.CLAIM_SECONDS
        while time.time() < deadline:
            if pid.is_running():
                return
            time.sleep(0.25)
        self.stop()
        raise RuntimeError(f"MCP host never claimed its pid in {self.ide_path}")
