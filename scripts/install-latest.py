"""Merge the latest release (origin's newest v* tag) and reinstall CDD on it, restarting every server: ``scripts/install.py --from-latest``, with any other
arguments passed on. The ``/install-latest`` command runs this."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

INSTALL_SCRIPT = Path(__file__).resolve().parent / "install.py"

if __name__ == "__main__":
    command = [sys.executable, str(INSTALL_SCRIPT), "--from-latest", *sys.argv[1:]]
    raise SystemExit(subprocess.run(command, cwd=INSTALL_SCRIPT.parents[1], check=False).returncode)
