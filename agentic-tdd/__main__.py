"""Entry point — run as: python agentic-tdd/__main__.py <command> [args]."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentic_tdd import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
