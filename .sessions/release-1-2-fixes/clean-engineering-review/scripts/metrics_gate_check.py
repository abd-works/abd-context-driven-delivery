"""Checks of the metrics gate's comparison, on hand-made measurements, so they need none of the measuring tools.

    python metrics_gate_check.py

Each check prints its name and passes or fails; the script exits 1 when one fails. The gate itself is slow (minutes:
it measures two whole checkouts), so these checks hold the comparison, and a real run against two commits shows the
measuring (see the docstring of metrics_gate.py).
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metrics_gate import GUARDS, report  # noqa: E402


def measurement(**changes) -> dict:
    """A measurement holding every guarded metric at 1 and no offenders, with `changes` ({"a.b": value}) applied."""
    summary: dict = {}
    for guard in GUARDS:
        place = summary
        *folders, last = guard.path.split(".")
        for part in folders:
            place = place.setdefault(part, {})
        place[last] = 1
    for path, value in changes.items():
        place = summary
        *folders, last = path.split(".")
        for part in folders:
            place = place[part]
        if value is None:
            del place[last]
        else:
            place[last] = value
    summary["offenders"] = {key: {} for key in (
        "functions_over_10_paths", "functions_hard_to_read", "functions_over_50_lines", "functions_over_5_parameters",
        "classes_depending_on_over_14", "classes_with_unrelated_jobs", "classes_total_complexity", "classes_methods",
        "modules_lines")}
    summary["file_digests"] = {"harness/a.py": "1", "harness/files_app/app/b.ts": "1"}
    return summary


def a_change_made_only_in_typescript_is_judged():
    before = measurement()
    after = measurement(**{"typescript.functions_ccn_over_10": 2})
    after["file_digests"]["harness/files_app/app/b.ts"] = "2"
    text, failed = report(before, after)
    assert failed, text
    assert "| TypeScript functions with more than 10 paths | 1 | 2 |" in text, text


def the_report_names_how_many_production_files_the_change_touched():
    before = measurement()
    after = copy.deepcopy(before)
    after["file_digests"]["harness/files_app/app/b.ts"] = "2"
    after["file_digests"]["harness/c.py"] = "1"
    text, _ = report(before, after)
    assert "Production files this change touched: 2 (1 Python, 1 TypeScript): 1 added, 0 removed, 1 edited." in text, text


def a_change_touching_no_production_file_says_so():
    text, failed = report(measurement(), measurement())
    assert not failed, text
    assert "Production files this change touched: 0 (0 Python, 0 TypeScript)" in text, text


def a_metric_one_side_could_not_measure_fails_the_gate():
    text, failed = report(measurement(), measurement(**{"typescript.duplication": None}))
    assert failed, text
    assert "| Copied blocks of TypeScript code | 1 | None | 15 | ⚠️ not measured |" in text, text


def a_typescript_function_pushed_past_a_limit_is_named():
    before = measurement()
    after = measurement()
    after["offenders"]["functions_over_10_paths"]["harness/files_app/app/b.ts:render"] = 12
    text, failed = report(before, after)
    assert failed, text
    assert "new: `harness/files_app/app/b.ts:render` (12 paths)" in text, text


CHECKS = (
    a_change_made_only_in_typescript_is_judged,
    the_report_names_how_many_production_files_the_change_touched,
    a_change_touching_no_production_file_says_so,
    a_metric_one_side_could_not_measure_fails_the_gate,
    a_typescript_function_pushed_past_a_limit_is_named,
)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    failures = 0
    for check in CHECKS:
        name = check.__name__.replace("_", " ")
        try:
            check()
            print(f"passed: {name}")
        except AssertionError as error:
            failures += 1
            print(f"FAILED: {name}\n{error}\n")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
