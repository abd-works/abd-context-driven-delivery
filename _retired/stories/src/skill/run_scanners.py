"""run_scanners.py — run every applicable scanner against a workspace.

Usage (agent calls this during the validate phase):

    python stories/src/skill/run_scanners.py \\
        --workspace <path>   \\
        --rules-root stories/rules

Exit 0  — all scanners passed (or were skipped).
Exit 1  — one or more violations found.

Output (stdout): one JSON object per line, one per violation:
    {"rule": "...", "message": "...", "location": "...", "severity": "...", "hint": "..."}

Summary (stderr):
    # run_scanners: N scanner(s) run, M violation(s)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

_READS_RE = re.compile(r"reads\s*=\s*\(([^)]+)\)")


def _scanner_reads(scanner_path: Path) -> set[str]:
    try:
        text = scanner_path.read_text(encoding="utf-8")
    except OSError:
        return {"story_map"}
    m = _READS_RE.search(text)
    if not m:
        return {"story_map"}
    kinds = set(re.findall(r'"([^"]+)"', m.group(1)))
    return kinds or {"story_map"}


def _detect_workspace_kinds(root: Path) -> set[str]:
    kinds: set[str] = set()
    if (root / "story-map.md").exists() or (root / "story-graph.json").exists():
        kinds.add("story_map")
    if any(
        (root / name).exists()
        for name in ("thin-slicing.md", "thin-slice.md", "thin-slices.md", "increments.md")
    ):
        kinds.add("increments")
    scenarios_dir = root / "scenarios"
    if scenarios_dir.is_dir() and any(scenarios_dir.rglob("*.md")):
        kinds.add("scenarios")
    if any(root.rglob("story-context.md")):
        kinds.add("story_contexts")
    tests_dir = root / "tests"
    if tests_dir.is_dir() and any(
        f.suffix in {".ts", ".tsx", ".js", ".py", ".java"}
        for f in tests_dir.rglob("*") if f.is_file()
    ):
        kinds.add("test_suites")
    return kinds


def _discover_rule_dirs(rules_root: Path) -> list[Path]:
    """Return every direct sub-directory of rules_root that looks like a rule."""
    return sorted(
        d for d in rules_root.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def _scanner_for_rule(rule_dir: Path) -> Path | None:
    """Return the scanner script inside rule_dir, or None if there isn't one."""
    candidates = sorted(rule_dir.glob("*-scanner.py"))
    return candidates[0] if candidates else None


def _run_one(scanner: Path, workspace: Path) -> tuple[int, list[dict], str]:
    proc = subprocess.run(
        [sys.executable, str(scanner), "--workspace", str(workspace)],
        capture_output=True,
        text=True,
    )
    violations: list[dict] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            violations.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return proc.returncode, violations, proc.stderr.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run all applicable scanners against a workspace")
    parser.add_argument("--workspace", required=True, help="Path to workspace root")
    parser.add_argument(
        "--rules-root",
        default=str(Path(__file__).resolve().parents[3] / "stories" / "rules"),
        help="Path to rules directory (default: stories/rules relative to repo root)",
    )
    args = parser.parse_args(argv)

    workspace = Path(args.workspace).resolve()
    rules_root = Path(args.rules_root).resolve()

    present_kinds = _detect_workspace_kinds(workspace)
    rule_dirs = _discover_rule_dirs(rules_root)

    total_run = 0
    total_skip = 0
    total_no_scanner = 0
    total_violations = 0

    for rule_dir in rule_dirs:
        rule = rule_dir.name
        scanner = _scanner_for_rule(rule_dir)

        if scanner is None:
            total_no_scanner += 1
            sys.stdout.write(f"# rule {rule}: NO_SCANNER\n")
            sys.stdout.flush()
            continue

        reads = _scanner_reads(scanner)
        if not reads.issubset(present_kinds):
            total_skip += 1
            missing = reads - present_kinds
            sys.stdout.write(f"# rule {rule}: SKIP  — workspace missing {', '.join(sorted(missing))}\n")
            sys.stdout.flush()
            continue

        total_run += 1
        _, violations, _stderr = _run_one(scanner, workspace)
        for v in violations:
            sys.stdout.write(json.dumps(v) + "\n")
            sys.stdout.flush()
            total_violations += 1

        tag = "FAIL" if violations else "PASS"
        msgs = "; ".join(v.get("message", "") for v in violations[:2])
        detail = f"  — {msgs}" if msgs else ""
        sys.stdout.write(f"# scan {rule}: {tag}{detail}\n")
        sys.stdout.flush()

    sys.stdout.write(
        f"# run_scanners: {total_run} run, {total_skip} skipped, "
        f"{total_no_scanner} no-scanner, {total_violations} violation(s)\n"
    )
    sys.stdout.flush()
    return 1 if total_violations > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
