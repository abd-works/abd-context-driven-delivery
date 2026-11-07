"""What every builder shares: guidance for building a new part of CDD in this repository."""

from __future__ import annotations

from harness.guidance.guidance import PracticeGuidance


class Builder(PracticeGuidance):
    """Guidance for building a new part of CDD, such as a toolset or a practice. A builder writes into this repository
    itself, so it works from the repository's root rather than a practice folder."""

    default_workspace_folder: str = "."
