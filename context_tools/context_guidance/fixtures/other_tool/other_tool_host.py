"""Isolation fixture — same label, different module_dir."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from primitives.markdown import markdown


@dataclass(frozen=True)
class ContextGuidanceStub:
    module_dir: Path


class OtherToolHost:
    domain_slug = "other_tool"
    toolset_name = "other_tool"

    def __init__(self, module_dir: Path | None = None) -> None:
        root = module_dir or Path(__file__).resolve().parent
        self.module_dir = root
        self.context_guidance = ContextGuidanceStub(root)

    @markdown
    def guidance(self) -> str:
        """Guidance section body."""
