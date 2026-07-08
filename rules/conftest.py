"""conftest.py — add agentic-tdd/ to sys.path so agentic_tdd is importable."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[1]  # enforce/ → repo root
_AGENT_TDD = _REPO_ROOT / "agentic-tdd"
if str(_AGENT_TDD) not in sys.path:
    sys.path.insert(0, str(_AGENT_TDD))
