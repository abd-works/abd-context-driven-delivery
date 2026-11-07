"""Minimal PracticeGuidance example for generator specs."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class CarChronicle(PracticeGuidance):
    """Write a driving chronicle: a markdown log of trips in the car's own voice."""
