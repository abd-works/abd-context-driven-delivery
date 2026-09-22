"""Scan action kit and shared scanner engine: path + files, violations."""

from __future__ import annotations

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

_LAZY = {
    "Scan": (".scan", "Scan"),
    "ScanReport": (".scan", "ScanReport"),
    "SKIP_DIR_NAMES": (".scanner", "SKIP_DIR_NAMES"),
    "Scanner": (".scanner", "Scanner"),
    "ScannerCollection": (".scanner_collection", "ScannerCollection"),
    "ScannerReport": (".scanner_collection", "ScannerReport"),
    "ScannerRunner": (".scanner_runner", "ScannerRunner"),
    "Violation": (".violation", "Violation"),
}


def __getattr__(name: str):
    if name == "run_scanner_main":
        from .scanner_runner import ScannerRunner

        return ScannerRunner.run_scanner_main
    spec = _LAZY.get(name)
    if spec is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr = spec
    from importlib import import_module

    return getattr(import_module(module_name, __name__), attr)
