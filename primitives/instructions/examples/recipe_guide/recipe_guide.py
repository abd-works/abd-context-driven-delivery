# @toolset-manifest python -m tools manifest primitives.instructions.examples.recipe_guide:RecipeGuide
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Demonstrates all three @instruction forms: inline prose, section slot, and file slot."""
from __future__ import annotations

import inspect
from pathlib import Path

from primitives.actions.action import agent_instructions, agentic_toolset
from primitives.instructions import Instruction, instruction
from tools.tool import resource, agent_tool


@agentic_toolset
class RecipeGuide:
    """Collect and draft recipes - brainstorm ideas, then write step-by-step recipes."""

    def __init__(self, cuisine: str) -> None:
        self._cuisine = cuisine
        self._drafts: list[str] = []
        super().__init__()

    @property
    def module_dir(self) -> Path:
        """Directory of this module — used by @instruction slots to locate markdown files."""
        return Path(inspect.getfile(type(self))).resolve().parent

    # -- resources: observable state -------------------------------------------

    @property
    @resource
    def cuisine(self) -> str:
        """The cuisine style this guide covers."""
        return self._cuisine

    @property
    @resource
    def draft_count(self) -> int:
        """Number of drafted recipes so far."""
        return len(self._drafts)

    # -- tools: callable by the AI ---------------------------------------------

    @agent_tool
    def add_draft(self, recipe: str) -> str:
        """Save a recipe draft."""
        self._drafts.append(recipe)
        return f"Draft saved: {recipe}"

    @agent_tool
    def read_drafts(self) -> str:
        """Return all saved drafts as a numbered list."""
        if not self._drafts:
            return "No drafts yet."
        return "\n".join(f"{i + 1}. {d}" for i, d in enumerate(self._drafts))

    # -- instruction slots -----------------------------------------------------

    # Form B - named slot -> section in recipe_guide.md
    #   "technique" -> _section_heading_for_name -> "Technique"
    #   matches ## Technique in recipe_guide.md (same slug as this file)
    @instruction
    def technique(self) -> Instruction: ...

    # Form C - named slot with explicit label -> standalone file
    #   label="plating-rules" -> resolves to plating-rules.md beside this package
    @instruction(label="plating-rules")
    def plating(self) -> Instruction: ...

    # -- actions ---------------------------------------------------------------

    # Form A - inline prose: each string literal in the body IS instruction text.
    #   {{expr}} substitutions are rendered against the live instance before the AI sees them.
    @agent_instructions
    def brainstorm(self, theme: str) -> str:
        """List 5 recipe ideas for {{theme}} using {{self.cuisine}} techniques."""
        """For each idea write a one-sentence description and name the key ingredient."""
        self.add_draft()
        return f"Brainstormed ideas for {theme}"

    # Using named slots: technique (section) and plating (file) are expanded inline.
    @agent_instructions
    def draft_recipe(self, name: str) -> str:
        """Draft a complete recipe called {{name}}."""
        self.technique()   # -> expands # Technique section from recipe_guide.md
        self.plating()     # -> expands plating-rules.md
        self.add_draft()
        return f"Drafted: {name}"
