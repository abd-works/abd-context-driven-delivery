"""What the domain-driven TypeScript stack patterns (LERN, MERN) share."""

from __future__ import annotations

from cdd_guidance.patterns.pattern import Pattern


class DomainDrivenStack(Pattern):
    """Implementation fidelity for a domain-module-organized TypeScript stack on an already-designed vertical slice. The
    acceptance tests are written first, with Stories at acceptance_tests in TypeScript, and then the production code
    those tests drive."""

    # Shared by the stack patterns, each of which is a pattern of its own.
    pattern = ""
    default_workspace_folder = "packages"
