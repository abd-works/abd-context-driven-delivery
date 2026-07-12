"""Ad-hoc: run only the `01-shaping` coarse case.

Everything else — .secrets loading, cursor-agent path resolution, stderr
capture — now lives in `stories/src/skill/evals/eval.py`. This shim only
narrows the case set so you don't wait for all five cases when iterating
on shaping.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent  # stories/
sys.path.insert(0, str(HERE / "src" / "skill" / "evals"))

import eval as E  # noqa: E402  (side effect: loads stories/conf/.secrets)

CASE = "01-shaping"

if not os.environ.get("CURSOR_API_KEY"):
    sys.exit(
        "CURSOR_API_KEY not set. Fill it in stories/conf/.secrets or export it "
        "in the shell before running."
    )

_orig_discover = E.discover_coarse_cases
E.discover_coarse_cases = lambda: [c for c in _orig_discover() if c.name == CASE]

run_dir = E._create_run_dir()
report = E.Report(
    started_at=datetime.now(timezone.utc).isoformat(),
    mode="coarse",
)
report.coarse_results = E.run_coarse_cases(model=None, verbose=True, run_dir=run_dir)
E._write_report(report, run_dir)
print(f"\nReport: {run_dir}")
