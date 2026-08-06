"""Python epic-helper emission for Clean Engineering ExampleFactories."""

from __future__ import annotations

import re
from typing import List, Sequence


def render_python_factory_imports(
    factories: Sequence[str],
    *,
    ce_module: str = "example_factories",
) -> List[str]:
    """Import lines for an epic helper. ``ce_module`` is the CE package/module path."""
    if not factories:
        return []
    lines = [
        f"# Example factories (clean_engineering) - adjust `{ce_module}` to match CE layout",
    ]
    for name in factories:
        lines.append(f"from {ce_module} import {name}")
    lines.append("")
    return lines


def render_python_factory_accessors(factories: Sequence[str]) -> List[str]:
    """Methods that construct factories; given_* helpers call these (not invent Fakes)."""
    if not factories:
        return []
    lines = [
        "    # -- Example factories - imported by tier test-helpers to build real collaborators --",
        "",
    ]
    for name in factories:
        method = _pascal_to_snake(name)
        lines.append(f"    def {method}(self) -> {name}:")
        lines.append(
            f'        """Return {name}; callers use factory methods for scenario objects."""'
        )
        lines.append(f"        return {name}()")
        lines.append("")
    return lines


def _pascal_to_snake(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
