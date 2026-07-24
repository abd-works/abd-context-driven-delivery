"""Markdown parse/render for Epic Example factories lines."""

from __future__ import annotations

import re
from typing import List, Sequence

from context_tools.stories.code.example_factories import normalize_factory_name


def render_md_factory_line(factories: Sequence[str]) -> str:
    if not factories:
        return ""
    linked = ", ".join(f"`{n}`" for n in factories)
    return f"Example factories: {linked}"


def parse_md_factory_line(line: str) -> List[str]:
    """Parse ``Example factories: `A`, `B` `` from markdown."""
    m = re.match(r"^Example factories:\s*(.+)$", line.strip(), re.IGNORECASE)
    if not m:
        return []
    return [
        normalize_factory_name(part.strip().strip("`"))
        for part in m.group(1).split(",")
        if part.strip()
    ]
