"""AgentGuidance — later. HarnessTool subclass; generate is not implemented yet."""

from __future__ import annotations

from typing import Any

from harness.harness_tool import HarnessTool


class AgentGuidance(HarnessTool):
    def generate(self, source: Any = None, roots: list[Path] | None = None) -> HarnessTool:
        raise NotImplementedError("later")
