"""The metrics gate: a change may not make the code worse.

Measures the code before a change (a commit, usually the branch the change starts from) and after it (a checkout,
usually the working tree), then compares them metric by metric and names every function, class and module the change
pushed past a limit. It exits 1 when any guarded metric got worse, so a refactor that trades one problem for another
stops before it is committed.

Usage (run with the Python of a metrics venv, as measure_revision.py is):

    python metrics_gate.py --base <commit> --head <checkout folder> --node-tools <dir> [--report gate.md]

--base is a commit in the repository that holds --head; it is extracted with ``git archive`` into a temporary folder.
--head is the folder to judge, normally the working tree with the change in it.
"""
from __future__ import annotations

import argparse
import io
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from measure_revision import measure  # noqa: E402

LOWER, HIGHER = "lower", "higher"
# The folders measure_revision.py counts as production code. Extracting only these keeps a commit's archive short of
# Windows path limits, which the retired fixtures under .retired/ exceed.
MEASURED_FOLDERS = ("harness", "cdd_guidance", "space", "tools", "scripts")


@dataclass(frozen=True)
class Guard:
    """One metric the gate holds: where it sits in a measurement, which way is better, and the target to reach."""
    name: str
    path: str
    better: str
    target: float

    def value_in(self, summary: dict) -> float:
        value = summary
        for part in self.path.split("."):
            value = value[part]
        return value

    def got_worse(self, before: float, after: float) -> bool:
        return after > before if self.better == LOWER else after < before

    def meets_target(self, value: float) -> bool:
        return value <= self.target if self.better == LOWER else value >= self.target


# The metrics a change must not make worse, each with the target the refactor is working towards. The targets are
# set from common review limits and from where this code already stands: low enough to remove the worst problems,
# reachable in a few rounds. See code-metrics-trend.md for why each one matters.
GUARDS = (
    Guard("Functions with more than 10 paths", "python.functions_ccn_over_10", LOWER, 60),
    Guard("Functions with more than 20 paths", "python.functions_ccn_over_20", LOWER, 0),
    Guard("Functions that are hard to read (readability score above 15)", "python.functions_cognitive_over_15", LOWER, 30),
    Guard("Functions longer than 50 lines", "python.functions_nloc_over_50", LOWER, 0),
    Guard("Functions that take more than 5 parameters", "python.functions_params_over_5", LOWER, 15),
    Guard("Modules with a poor maintainability score (below 20)", "python.modules_mi_below_20", LOWER, 15),
    Guard("Lines in the longest module", "python.module_sloc.max", LOWER, 800),
    Guard("Total complexity of the most complex class", "python.wmc.max", LOWER, 100),
    Guard("Most methods in a single class", "python.nom.max", LOWER, 30),
    Guard("Average total complexity of a class", "python.wmc.mean", LOWER, 15),
    Guard("Share of classes doing several unrelated jobs", "python.classes_lcom4_over_1_share", LOWER, 0.40),
    Guard("Classes that depend on more than 14 other classes", "python.classes_cbo_over_14", LOWER, 25),
    Guard("Classes where one call can set off more than 50 methods", "python.classes_rfc_over_50", LOWER, 50),
    Guard("Most modules that import one single module", "python.module_fan_in.max", LOWER, 40),
    Guard("Folders that many depend on but are written as plain concrete code", "python.packages_distance_over_0_7", LOWER, 8),
    Guard("Modules caught in an import loop", "python.import_graph.runtime_imports.modules_in_cycles", LOWER, 0),
    Guard("Folders caught in an import loop", "python.import_graph.runtime_imports.packages_in_cycles", LOWER, 0),
    Guard("Copied lines, as a share of all lines", "python.duplication.duplicated_pct", LOWER, 0.30),
    Guard("Copied blocks of code", "python.duplication.clones", LOWER, 15),
    Guard("Groups of functions identical apart from their names", "python.function_clones.groups", LOWER, 0),
    Guard("Helper function names written separately in several modules", "python.function_clones.free_function_names_in_several_modules", LOWER, 5),
    Guard("Class names defined in more than one module", "shadow_models.class_names_in_several_modules", LOWER, 0),
    Guard("Pairs of unrelated classes holding the same fields", "shadow_models.identical_field_sets", LOWER, 0),
)

# Limits on a single function, class or module. A change may not push anything new past one, nor make anything
# already past one bigger.
LIMITS = {
    "functions_over_10_paths": "paths",
    "functions_hard_to_read": "readability score",
    "functions_over_50_lines": "lines",
    "functions_over_5_parameters": "parameters",
    "classes_depending_on_over_14": "classes depended on",
    "classes_with_unrelated_jobs": "unrelated groups of methods",
}
# Sizes that may not grow on the biggest items: a class's total complexity above 100 or methods above 30, and a
# module above 800 lines.
GROWTH = {
    "classes_total_complexity": ("total complexity", 100),
    "classes_methods": ("methods", 30),
    "modules_lines": ("lines", 800),
}


def measured_commit(repository: Path, commit: str, node_tools: Path | None) -> dict:
    """The measurement of a commit, extracted from the repository without touching any checkout."""
    archive = subprocess.run(["git", "-C", str(repository), "archive", commit, *MEASURED_FOLDERS],
                             capture_output=True, check=True).stdout
    folder = Path(tempfile.mkdtemp(prefix="gate-"))
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(folder, filter="data")
    return measure(folder, commit, node_tools)


def worse_items(before: dict, after: dict) -> list[str]:
    """Every function, class or module the change pushed past a limit or made bigger while past it."""
    found = []
    for key, unit in LIMITS.items():
        for item, value in after["offenders"][key].items():
            earlier = before["offenders"][key].get(item)
            if earlier is None:
                found.append(f"new: `{item}` ({value} {unit})")
            elif value > earlier:
                found.append(f"bigger: `{item}` ({earlier} → {value} {unit})")
    for key, (unit, limit) in GROWTH.items():
        for item, value in after["offenders"][key].items():
            earlier = before["offenders"][key].get(item, 0)
            if value > limit and value > earlier:
                found.append(f"past {limit} {unit}: `{item}` ({earlier} → {value})")
    return found


def report(before: dict, after: dict) -> tuple[str, bool]:
    lines = ["| Metric | Before | After | Target | Verdict |", "|---|---|---|---|---|"]
    failed = False
    for guard in GUARDS:
        was, now = guard.value_in(before), guard.value_in(after)
        if guard.got_worse(was, now):
            verdict, failed = "🔴 worse", True
        elif now != was:
            verdict = "🟢 better"
        else:
            verdict = "⚪ unchanged"
        target = "✅ met" if guard.meets_target(now) else f"{guard.target}"
        lines.append(f"| {guard.name} | {was} | {now} | {target} | {verdict} |")
    items = worse_items(before, after)
    if items:
        failed = True
        lines += ["", "**Functions, classes and modules this change made worse:**", *[f"- {item}" for item in items]]
    lines.insert(0, "## Metrics gate: " + ("FAILED, this change makes the code worse" if failed else "passed") + "\n")
    return "\n".join(lines), failed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, help="the commit the change starts from")
    parser.add_argument("--head", type=Path, required=True, help="the checkout with the change in it")
    parser.add_argument("--repository", type=Path, default=None, help="the repository holding --base; by default --head")
    parser.add_argument("--node-tools", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None, help="also write the report to this file")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    head = args.head.resolve()
    node_tools = args.node_tools.resolve() if args.node_tools else None
    before = measured_commit((args.repository or head).resolve(), args.base, node_tools)
    after = measure(head, "head", node_tools)
    text, failed = report(before, after)
    print(text)
    if args.report:
        args.report.write_text(text, encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
