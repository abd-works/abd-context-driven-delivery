"""Scan action kit and shared scanner engine: named rules, path + files, violations."""

from __future__ import annotations

from .scan import Scan, ScanReport
from .scanner import SKIP_DIR_NAMES, Scanner
from .scanner_collection import ScannerCollection, ScannerReport
from .scanner_runner import ScannerRunner
from .violation import Violation

run_scanner_main = ScannerRunner.run_scanner_main

__all__ = [
    "Scan",
    "ScanReport",
    "SKIP_DIR_NAMES",
    "Scanner",
    "ScannerCollection",
    "ScannerReport",
    "ScannerRunner",
    "Violation",
    "run_scanner_main",
]
