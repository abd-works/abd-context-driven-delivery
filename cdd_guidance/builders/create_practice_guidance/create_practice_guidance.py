"""CreatePracticeGuidance — scaffold new PracticeGuidance domains under cdd_guidance/practices/."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset

from cdd_guidance.builders.builder import Builder


@agent_toolset
class CreatePracticeGuidance(Builder):
    """Scaffold a new practice: its PracticeGuidance class, its markdown, templates, and examples."""
