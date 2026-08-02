#!/usr/bin/env python3
"""Run one scanner: workspace path, file list, named rule -> violations."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Callable, Type

from scanners.scanner import Scanner
from scanners.violation import Violation


class ScannerRunner:
    """Utility operations for running a scanner from the command line."""

    @staticmethod
    def execute_scan(
        scanner_class: Type[Any],
        rule: str,
        root: Path,
        files: list[Path],
    ) -> list[Violation]:
        scanner = scanner_class(rule)
        return scanner.scan(root, Scanner.filter_scan_files(files))

    @staticmethod
    def print_violations(violations: list[Violation]) -> None:
        for violation in violations:
            print(violation.to_dict(), file=sys.stderr)

    @staticmethod
    def violations_exit_code(violations: list[Violation]) -> int:
        if not violations:
            return 0
        ScannerRunner.print_violations(violations)
        return 1

    @staticmethod
    def run_scanner_main(
        scanner_class: Type[Any],
        rule: str,
        collect_files: Callable[[Path], list[Path]],
        argv: list[str] | None = None,
    ) -> int:
        parser = argparse.ArgumentParser(description="Run one scanner")
        parser.add_argument(
            "--workspace",
            type=Path,
            default=Path.cwd(),
            help="Project root (default: cwd).",
        )
        args = parser.parse_args(argv)
        root = args.workspace.resolve()
        files = collect_files(root)
        violations = ScannerRunner.execute_scan(scanner_class, rule, root, files)
        return ScannerRunner.violations_exit_code(violations)
