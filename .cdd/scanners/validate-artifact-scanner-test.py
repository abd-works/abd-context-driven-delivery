"""validate-artifact-scanner-test — passing examples satisfy the scanner; failing examples violate it.

Story: Validate Artifacts Against Rule and Scanner
  Scenario 1: Passing examples satisfy rule and scanner  → scanner exit 0
  Scenario 2: Failing examples violate rule and scanner  → scanner exit 1

Usage:
    pytest enforce/scanners/validate-artifact-scanner-test.py -v
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

import pytest

RULES_ROOT = Path(__file__).parent.parent / "examples" / "vehicle" / "rules"


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
# HELPERS
# ===========================================================================

def given_rule_scanner_and_examples(case: ScannerCase) -> None:
    assert case.scanner.exists(), f"Scanner missing: {case.scanner}"
    assert case.examples_dir.is_dir(), f"Examples dir missing: {case.examples_dir}"
    assert any(case.examples_dir.glob("*.md")), f"No .md files in: {case.examples_dir}"


def when_scanner_runs_against_examples(scanner: Path, examples_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(scanner), "--workspace", str(examples_dir)],
        capture_output=True,
        text=True,
    )


def then_scanner_reports_expected_violations(
    result: subprocess.CompletedProcess, expected: int, label: str, rule: str
) -> None:
    assert result.returncode == expected, (
        f"Rule '{rule}' [{label}]: expected exit {expected}, got {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


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
        given_rule_scanner_and_examples(case)

        # When
        result = when_scanner_runs_against_examples(case.scanner, case.examples_dir)

        # Then
        then_scanner_reports_expected_violations(result, case.expected_exit, label, case.rule_name)
