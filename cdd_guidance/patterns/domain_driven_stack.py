"""What the domain-driven TypeScript stack patterns (LERN, MERN) share."""

from __future__ import annotations

from harness.guidance.guidance import PracticeGuidance


class DomainDrivenStack(PracticeGuidance):
    """Implementation fidelity for a domain-module-organized TypeScript stack on an already-designed vertical slice. The
    acceptance tests are written first, with Stories at acceptance_tests in TypeScript, and then the production code
    those tests drive."""

    def __init__(self) -> None:
        super().__init__(format="typescript", default_workspace_folder="packages")
