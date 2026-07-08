"""test_use_given_when_then — agent correctly identifies tests that follow Given/When/Then.

Each example under examples/use-given-when-then/ has:
  context/   — input files given to the agent
  expected/
    expected.md  — what the agent should output
    rubric.md    — qualitative judge criteria (falls back to AgentTest.default_rubric)
  actual/        — written after each run
    output.md    — what the agent actually produced
    verdict.md   — judge verdict and reason
"""
from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import pytest

from agentic_tdd import AgentTest, JudgeResult  # noqa: F401

_EXAMPLES_DIR = Path(__file__).parent / "examples" / "use-given-when-then"
_SESSION_DIR  = Path(__file__).parent / ".sessions"
_SESSION_DIR.mkdir(parents=True, exist_ok=True)

_PROMPT = (
    "Does the test below follow the Given / When / Then pattern using AgentTest helpers "
    "(`given_guidance`, `when_agent_invoked`, and either `ai_judge` or a direct assertion "
    "on `result.stdout`)? Reply PASS if it does, FAIL if it does not."
)


class Example(NamedTuple):
    name: str
    context_dir: Path
    expected_dir: Path
    actual_dir: Path


def _collect() -> list[Example]:
    return [
        Example(
            name=d.name,
            context_dir=d / "context",
            expected_dir=d / "expected",
            actual_dir=d / "actual",
        )
        for d in sorted(_EXAMPLES_DIR.iterdir())
        if d.is_dir() and (d / "context").is_dir() and (d / "expected").is_dir()
    ]


_EXAMPLES = _collect()


class TestUseGivenWhenThen(AgentTest):

    @pytest.fixture(scope="session", autouse=True)
    def require_cursor_agent(self):
        self.assert_authenticated()

    @pytest.mark.parametrize("example", _EXAMPLES, ids=[e.name for e in _EXAMPLES])
    def test_example(self, example: Example, tmp_path: Path) -> None:
        # Given
        context_text = "\n\n".join(
            f.read_text(encoding="utf-8")
            for f in sorted(example.context_dir.iterdir())
            if f.is_file()
        )
        expected = (example.expected_dir / "expected.md").read_text(encoding="utf-8").strip()
        rubric_file = example.expected_dir / "rubric.md"
        rubric = (
            rubric_file.read_text(encoding="utf-8").strip()
            if rubric_file.is_file()
            else self.default_rubric
        )

        guidance = self.given_guidance()
        context  = self.given_context(context_text)

        # When
        result = self.when_agent_invoked(
            guidance=guidance,
            prompt=_PROMPT,
            context=context,
            workspace=tmp_path,
            session_file=_SESSION_DIR / f"use-gwt-{example.name}.json",
        )

        # Then
        verdict: JudgeResult = self.ai_judge(
            output=result.stdout,
            rubric=f"{rubric}\n\nExpected:\n{expected}",
            workspace=tmp_path,
            session_file=_SESSION_DIR / f"use-gwt-{example.name}-judge.json",
        )

        self.write_actual(example.actual_dir, output=result.stdout, verdict=verdict)

        assert verdict.passed(), verdict.reason
