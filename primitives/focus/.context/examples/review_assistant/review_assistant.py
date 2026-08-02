# @toolset-manifest python -m tools manifest primitives.focus.examples.review_assistant:ReviewAssistant
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Example showing @focus on an @action — injects fidelity-specific guidance at runtime."""
from __future__ import annotations

import inspect
from pathlib import Path

from primitives.actions.action import action
from primitives.focus import focus
from tools.tool import resource, tool, toolset


@toolset
class ReviewAssistant:
    """Review code or documents with guidance tuned to the active fidelity level.

    @focus(focus="fidelities") appends fidelities/{fidelity}.md to the review
    action's prose before the AI sees it. Switch fidelity at construction time
    to get development or production guidance.
    """

    def __init__(self, fidelity: str = "development") -> None:
        self._fidelity = fidelity
        self._findings: list[str] = []
        super().__init__()

    @property
    def module_dir(self) -> Path:
        """Directory of this module — @focus resolves fidelity files relative to here."""
        return Path(inspect.getfile(type(self))).resolve().parent

    @property
    @resource
    def fidelity(self) -> str:
        """Active fidelity level (development or production)."""
        return self._fidelity

    @property
    @resource
    def finding_count(self) -> int:
        """Number of review findings recorded so far."""
        return len(self._findings)

    @tool
    def record_finding(self, finding: str) -> str:
        """Record a review finding."""
        self._findings.append(finding)
        return f"Finding recorded: {finding}"

    @tool
    def read_findings(self) -> str:
        """Return all recorded findings as a numbered list."""
        if not self._findings:
            return "No findings yet."
        return "\n".join(f"{i + 1}. {f}" for i, f in enumerate(self._findings))

    # @focus appends fidelities/{fidelity}.md to this action's prose.
    # The filter_key defaults to "fidelity" (strip trailing 's' from "fidelities").
    @focus(focus="fidelities")
    @action
    def review(self, subject: str) -> str:
        """Review {{subject}} and record every issue found."""
        """Use record_finding for each issue. Read findings when done."""
        self.record_finding()
        self.read_findings()
        return f"Review of {subject} complete"
