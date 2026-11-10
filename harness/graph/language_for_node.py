"""Map a graph node's source file to a code channel name."""

from __future__ import annotations

_DRAWIO = frozenset({".drawio", ".xml"})


def language_for_node(node) -> str | None:
    relative = (getattr(getattr(node, "source", None), "file", None) or "").lower()
    if not relative or relative in {".", ""}:
        if node.type in {"Module", "Package"}:
            return "graph"
        return None
    if relative.endswith((".ts", ".tsx")):
        return "typescript"
    if relative.endswith((".js", ".jsx", ".mjs")):
        return "javascript"
    if relative.endswith(".py"):
        return "python"
    if any(relative.endswith(ext) for ext in _DRAWIO):
        return "drawio"
    return "graph"
