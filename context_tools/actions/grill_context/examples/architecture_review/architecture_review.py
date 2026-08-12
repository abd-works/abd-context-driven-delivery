"""architecture_review — shows GrillContext grilling a concrete architecture question."""
from __future__ import annotations

from grill_context.grill_context import GrillContext


class ArchitectureReview:
    """Example: run a context-grounded architecture interview for a given codebase."""

    def run(self, context_root: str, question: str) -> str:
        """Grill *question* against the context files found under *context_root*.

        Instantiates GrillContext rooted at the workspace, then fires
        grill_with_context so the interviewer reads every relevant context
        file before asking a single concept-grounded question.
        """
        grill = GrillContext(path=context_root)
        return grill.grill_with_context(plan=question)
