"""{feature} — agent test for {feature}."""
from pathlib import Path

import pytest
from agentic_tdd import AgentTest, AgentResult, JudgeResult  # noqa: F401

# One session directory per test module — never share session files across modules.
_SESSION_DIR = Path(__file__).parent / ".sessions"
_SESSION_DIR.mkdir(parents=True, exist_ok=True)

# Workspace root used by cursor-agent; each test gets its own tmp_path.
_WORKSPACE = Path(__file__).parent


class Test{Feature}(AgentTest):
    """Tests for {feature}."""

    def test_{scenario}(self, tmp_path: Path) -> None:
        # ── Given ─────────────────────────────────────────────────────────────
        guidance = self.given_guidance()
        context = self.given_context(
            """\
{artifact content here}
"""
        )

        # ── When ──────────────────────────────────────────────────────────────
        result = self.when_agent_invoked(
            guidance=guidance,
            prompt="{task prompt}",
            context=context,
            workspace=tmp_path,
            session_file=_SESSION_DIR / "{feature}-{scenario}.json",
        )

        # ── Then ──────────────────────────────────────────────────────────────
        verdict = self.ai_judge(
            output=result.stdout,
            rubric="{judge rubric}",
            workspace=tmp_path,
            session_file=_SESSION_DIR / "{feature}-{scenario}-judge.json",
        )
        assert verdict.passed(), verdict.reason
