"""validate-artifact-rules-test — passing examples satisfy the rule; failing examples violate it.

Story: Validate Artifacts Against Rule and Scanner
  Scenario 1: Passing examples satisfy rule and scanner  → agent emits PASS
  Scenario 2: Failing examples violate rule and scanner  → agent emits FAIL

Usage:
    pytest enforce/rules/validate-artifact-rules-test.py -v -s

Requires:
    cursor-agent on PATH and authenticated (`cursor-agent login`).
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import NamedTuple

import pytest

from agent_test import AgentResult, AgentTest  # provided by agent_test/ at repo root

_VERDICT_RE = re.compile(
    r"Rule:\s*[\w-]+\s*->\s*(PASS|FAIL)"                    # canonical:  Rule: x -> PASS
    r"|\*\*Result:\s*(PASS|FAIL)\*\*"                       # fallback:   **Result: PASS**
    r"|Validation result[:\s]+\**(PASS|FAIL)\**"            # fallback:   Validation result: **PASS**
    r"|\*\*Verdict\*\*[^`\n]*(PASS|FAIL|valid|invalid)",    # fallback:   **Verdict:** PASS / valid
    re.IGNORECASE,
)

RULES_ROOT  = Path(__file__).parent.parent / "examples" / "vehicle" / "rules"
SESSION_DIR = Path(__file__).parent / ".sessions"


# ===========================================================================
# CASE COLLECTION
# ===========================================================================

class ArtifactCase(NamedTuple):
    rule_name: str
    example_file: Path
    expected_verdict: str


def _collect_cases() -> list[ArtifactCase]:
    cases: list[ArtifactCase] = []
    for rule_dir in sorted(RULES_ROOT.iterdir()):
        if not rule_dir.is_dir():
            continue
        for label, verdict in (("pass", "PASS"), ("fail", "FAIL")):
            examples_dir = rule_dir / "examples" / label
            if not examples_dir.is_dir():
                continue
            for md in sorted(examples_dir.glob("*.md")):
                cases.append(ArtifactCase(rule_dir.name, md, verdict))
    return cases


_CASES = _collect_cases()


# ===========================================================================
# FIXTURES
# ===========================================================================

@pytest.fixture(scope="session")
def cdd_guidance() -> str:
    """Validate-specific guidance: agent-test.md (base) + validate.md."""
    return AgentTest().given_guidance(files=["validate.md"])


@pytest.fixture(scope="session", autouse=True)
def require_cursor_agent() -> None:
    AgentTest.assert_authenticated()


# ===========================================================================
# HELPERS
# ===========================================================================

def given_rule_and_example(rule_name: str, example_file: Path, workspace: Path) -> None:
    rule_dir = RULES_ROOT / rule_name
    assert rule_dir.is_dir(), f"Rule dir missing: {rule_dir}"
    assert example_file.is_file(), f"Example file missing: {example_file}"
    shutil.copytree(rule_dir, workspace / "rules" / rule_name, dirs_exist_ok=True)
    shutil.copy2(example_file, workspace / example_file.name)


def build_prompt(rule_name: str, example_file: Path) -> str:
    return f"Validate `{example_file.name}` using rule `{rule_name}`."


def then_assert_verdict(result: AgentResult, expected: str, *, label: str = "") -> None:
    match = _VERDICT_RE.search(result.stdout)
    if match:
        raw = next(g for g in match.groups() if g is not None)
        actual = "PASS" if raw.lower() in ("pass", "valid") else "FAIL"
    else:
        actual = None
    suffix = f" for {label}" if label else ""
    assert actual == expected, (
        f"Expected verdict {expected!r}{suffix}, got {actual!r}\n"
        f"Agent output:\n{result.stdout}"
    )


# ===========================================================================
# TESTS
# ===========================================================================

class TestValidateArtifactRules(AgentTest):
    @pytest.mark.parametrize(
        "case",
        _CASES,
        ids=[f"{c.rule_name}[{c.example_file.parent.name}/{c.example_file.name}]" for c in _CASES],
    )
    def test_examples_satisfy_or_violate_rule(
        self,
        case: ArtifactCase,
        cdd_guidance: str,
        tmp_path: Path,
    ):
        # Given
        given_rule_and_example(case.rule_name, case.example_file, tmp_path)

        # When
        result: AgentResult = self.when_agent_invoked(
            guidance=cdd_guidance,
            prompt=build_prompt(case.rule_name, case.example_file),
            workspace=tmp_path,
            session_file=SESSION_DIR / f"{case.rule_name}.json",
        )

        # Then
        then_assert_verdict(
            result,
            case.expected_verdict,
            label=f"{case.rule_name} [{case.example_file.parent.name}/{case.example_file.name}]",
        )
