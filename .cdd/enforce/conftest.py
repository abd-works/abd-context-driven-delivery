"""conftest.py — add repo root to sys.path so agent_test/ is importable."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[1]  # enforce/ → repo root
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
