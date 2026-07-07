"""Entry point referenced from stories/SKILL.md.

Run:

    python stories/src/skill/assemble_components.py \\
        --skill-root stories/ \\
        --fidelity exploration,specification \\
        --format md \\
        --phase generate

Outputs the manifest as JSON on stdout. Anomalies (unknown fidelity, missing
front matter, invalid YAML, etc.) are emitted as JSON on stderr but never
abort the run.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.CLI.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
