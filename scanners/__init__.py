"""Shared scanner infrastructure: named rules, path + files, violations."""

from __future__ import annotations

from .scanner import Scanner
from .scanner_collection import ScannerCollection, ScannerReport
from .scanner_runner import execute_scan, run_scanner_main, violations_exit_code
from .violation import Violation

__all__ = [
    "Scanner",
    "ScannerCollection",
    "ScannerReport",
    "Violation",
    "execute_scan",
    "run_scanner_main",
    "violations_exit_code",
]
