"""Shared scanner infrastructure: named rules, path + files, violations."""

from __future__ import annotations

from .scan import Scan
from .scanner import SKIP_DIR_NAMES, Scanner, filter_scan_files, is_skipped_path
from .scanner_collection import ScannerCollection, ScannerReport
from .scanner_runner import execute_scan, run_scanner_main, violations_exit_code
from .violation import Violation

__all__ = [
    "Scan",
    "SKIP_DIR_NAMES",
    "Scanner",
    "ScannerCollection",
    "ScannerReport",
    "Violation",
    "execute_scan",
    "filter_scan_files",
    "is_skipped_path",
    "run_scanner_main",
    "violations_exit_code",
]
