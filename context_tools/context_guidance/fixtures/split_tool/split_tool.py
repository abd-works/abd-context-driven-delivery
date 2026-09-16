"""Split on-disk layout: section files beside the module."""
from __future__ import annotations

from context_tools.context_guidance.guidance import PracticeGuidance


class SplitPracticeGuidance(PracticeGuidance):
    domain_slug = "split_tool"
    default_format = "markdown"
    name = None
