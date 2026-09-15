"""Layer 1 fixture host — co-located markdown beside this module."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from primitives.markdown import Markdown, markdown


@dataclass(frozen=True)
class ContextGuidanceStub:
    module_dir: Path


class SampleToolHost:
    domain_slug = "sample_tool"
    toolset_name = "sample_tool"

    def __init__(self, module_dir: Path | None = None) -> None:
        root = module_dir or Path(__file__).resolve().parent
        self.module_dir = root
        self.context_guidance = ContextGuidanceStub(root)

    @markdown
    def guidance(self) -> str:
        """Guidance section body."""

    def read_guidance_via_markdown(self) -> str:
        return Markdown.from_label(self, "guidance").extract()
