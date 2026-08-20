"""Shared helpers for BDD specs that assert a fail/pass scan fixture pair.

Mistake specs should call these rather than inventing a parallel eval harness.
"""
from __future__ import annotations

from pathlib import Path

from expects import be_false, be_true, expect

from scanners.scan import Scan, ScanReport


def _scan_report(
    scan: Scan,
    path: str | Path,
    *,
    rule: str | None,
    root: str | Path | None,
) -> ScanReport:
    file_path = Path(path)
    scan_root = Path(root) if root is not None else file_path.parent
    return ScanReport.from_scan(
        scan.scan([str(file_path)], root=str(scan_root), rule=rule)
    )


def expect_scan_fails(
    scan: Scan,
    path: str | Path,
    *,
    rule: str | None = None,
    root: str | Path | None = None,
) -> None:
    expect(_scan_report(scan, path, rule=rule, root=root).ok).to(be_false)


def expect_scan_passes(
    scan: Scan,
    path: str | Path,
    *,
    rule: str | None = None,
    root: str | Path | None = None,
) -> None:
    expect(_scan_report(scan, path, rule=rule, root=root).ok).to(be_true)
