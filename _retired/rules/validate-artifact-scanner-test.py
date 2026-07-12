"""validate-artifact-scanner-test — passing examples satisfy the scanner; failing examples violate it.

Story: Validate Artifacts Against Scanner
  Scenario 1: Passing examples satisfy scanner  → scanner exit 0
  Scenario 2: Failing examples violate scanner  → scanner exit 1

Usage:
    pytest enforce/validate-artifact-scanner-test.py -v
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

import pytest

RULES_ROOT = Path(__file__).parent / "examples" / "vehicle" / "rules"


# ===========================================================================
# CASE COLLECTION
# ===========================================================================

class ScannerCase(NamedTuple):
    rule_name: str
    scanner: Path
    examples_dir: Path
    expected_exit: int


def _collect_cases() -> list[ScannerCase]:
    cases: list[ScannerCase] = []
    for rule_dir in sorted(RULES_ROOT.iterdir()):
        if not rule_dir.is_dir():
            continue
        scanner = rule_dir / f"{rule_dir.name}-scanner.py"
        if not scanner.exists():
            continue
        for label, expected_exit in (("pass", 0), ("fail", 1)):
            examples_dir = rule_dir / "examples" / label
            if examples_dir.is_dir():
                cases.append(ScannerCase(
                    rule_name=rule_dir.name,
                    scanner=scanner,
                    examples_dir=examples_dir,
                    expected_exit=expected_exit,
                ))
    return cases


_CASES = _collect_cases()


# ===========================================================================
# TESTS
# ===========================================================================

class TestValidateArtifactScanner:
    @pytest.mark.parametrize(
        "case",
        _CASES,
        ids=[f"{c.rule_name}[{'pass' if c.expected_exit == 0 else 'fail'}]" for c in _CASES],
    )
    def test_examples_satisfy_or_violate_scanner(self, case: ScannerCase):
        label = "pass" if case.expected_exit == 0 else "fail"

        # Given
        assert case.scanner.exists(), f"Scanner missing: {case.scanner}"
        assert case.examples_dir.is_dir(), f"Examples dir missing: {case.examples_dir}"
        assert any(case.examples_dir.glob("*.md")), f"No .md files in: {case.examples_dir}"

        # When
        result = subprocess.run(
            [sys.executable, str(case.scanner), "--workspace", str(case.examples_dir)],
            capture_output=True,
            text=True,
        )

        # Then
        assert result.returncode == case.expected_exit, (
            f"Rule '{case.rule_name}' [{label}]: expected exit {case.expected_exit}, got {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
