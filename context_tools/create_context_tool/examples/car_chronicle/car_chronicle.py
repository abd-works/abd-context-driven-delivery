"""Minimal BaseContextTool subclass example for generator specs."""

from __future__ import annotations

from context_tools.base.base_context_tool import BaseContextTool


class CarChronicle(BaseContextTool):
    """# Instructions"""

    def __init__(self, path: str | None = None, session: str | None = None) -> None:
        super().__init__(path=path, session=session)
