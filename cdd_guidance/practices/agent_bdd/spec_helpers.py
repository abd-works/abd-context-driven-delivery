"""Shared helpers for agent BDD specs: where a spec's repository and agent sessions are, the assertions on a run's
response specs repeat, and the prompt and rubric a generate-and-judge step uses. Import from
``cdd_guidance.practices.agent_bdd.spec_helpers``; the steps that need the agent are on the block ``agent(...)`` yields.
"""
from __future__ import annotations

from pathlib import Path

from expects import be_true, equal, expect

from cdd_guidance.practices.agent_bdd.agent_bdd_common import RunResponse

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def repo_root_from(file: str | Path, *, parents: int = 2) -> Path:
    """Resolve the abd-context-driven-delivery root from a spec file path."""
    return Path(file).resolve().parents[parents]


def sessions_dir(spec_file: str | Path, *, folder: str = ".agent_bdd_sessions") -> Path:
    """Session JSON directory under .context/ in the spec's package."""
    return Path(spec_file).resolve().parent / ".context" / folder


# ---------------------------------------------------------------------------
# Response assertions
# ---------------------------------------------------------------------------


def expect_ok_action(
    response: RunResponse,
    action: str,
    *,
    require_instructions: bool = True,
) -> None:
    """Assert ``ok``, matching ``action``, and optionally non-empty instructions."""
    expect(response.ok).to(be_true)
    expect(response.action).to(equal(action))
    if require_instructions:
        expect(response.instructions is not None).to(be_true)


def expect_instructions_contain(
    response: RunResponse,
    *needles: str,
    case_insensitive: bool = True,
) -> None:
    """Assert every needle appears in ``response.instructions``."""
    text = str(response.instructions or "")
    haystack = text.lower() if case_insensitive else text
    for needle in needles:
        probe = needle.lower() if case_insensitive else needle
        expect(probe in haystack).to(be_true)


def generate_similar_prompt(pass_path: str | Path) -> str:
    """Ask the agent to generate something similar to the passing fixture."""
    location = Path(pass_path).as_posix()
    return (
        f"Read {location}. Generate a similar successful result — the same kind of "
        "artifact, close in shape and content, not a copy. Hold this generate for "
        "human review."
    )


def generate_similar_rubric(pass_path: str | Path) -> str:
    """AI-judge rubric: generated output is close to the passing fixture."""
    location = Path(pass_path).as_posix()
    return (
        f"The output is a similar successful result to {location}: same kind of "
        "artifact, close in shape and intent, not an unrelated rewrite."
    )
