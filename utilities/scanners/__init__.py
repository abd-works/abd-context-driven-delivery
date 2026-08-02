"""Shared scanner infrastructure: named rules, path + files, violations."""

from __future__ import annotations

from .scan import Scan
from .scanner import SKIP_DIR_NAMES, Scanner
from .scanner_collection import ScannerCollection, ScannerReport
from .scanner_runner import ScannerRunner
from .violation import Violation

__all__ = [
    "Scan",
    "SKIP_DIR_NAMES",
    "Scanner",
    "ScannerCollection",
    "ScannerReport",
    "ScannerRunner",
    "Violation",
]
