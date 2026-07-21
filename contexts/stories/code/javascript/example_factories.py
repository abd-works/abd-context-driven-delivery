"""JavaScript epic-helper emission for Clean Engineering ExampleFactories."""

from __future__ import annotations

from typing import List, Sequence


def render_js_factory_imports(
    factories: Sequence[str],
    *,
    ce_module: str = "../example-factories.js",
) -> List[str]:
    if not factories:
        return []
    names = ", ".join(factories)
    return [
        "// Example factories (clean_engineering) — adjust path to match CE layout",
        f"import {{ {names} }} from '{ce_module}';",
        "",
    ]


def render_js_factory_accessors(factories: Sequence[str]) -> List[str]:
    if not factories:
        return []
    lines = [
        "  // Example factories (explore/spec → fake; tier specs → isolated|production)",
        "",
    ]
    for name in factories:
        method = _pascal_to_camel(name)
        lines.append(f"  {method}() {{")
        lines.append(f"    return new {name}();")
        lines.append("  }")
        lines.append("")
    return lines


def _pascal_to_camel(name: str) -> str:
    if not name:
        return name
    return name[0].lower() + name[1:]
