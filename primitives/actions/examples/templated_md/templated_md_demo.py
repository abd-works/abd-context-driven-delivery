# @toolset-manifest python -m tools manifest primitives.actions.examples.templated_md_demo:TemplatedMdDemo
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""Example action whose instructions load from an md file with {{}} templating."""
from __future__ import annotations

from primitives.actions.action import agent_instructions, agentic_toolset


@agentic_toolset
class TemplatedMdDemo:
    """Demo toolset for md instruction templating."""

    def __init__(self, label: str) -> None:
        self.label = label
        super().__init__()

    @agent_instructions
    def greet(self, name: str) -> str:
        """greet_instructions"""
        return f"Greeted {name}"
