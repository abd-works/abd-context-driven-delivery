"""Skill-inject hook — delegates to ``dispatch.py``."""

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    subprocess.run(
        [sys.executable, str(_REPO_ROOT / "primitives/hooks/dispatch.py")],
        stdin=sys.stdin,
        check=False,
    )
