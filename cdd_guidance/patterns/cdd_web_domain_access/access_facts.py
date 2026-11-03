"""CDD web domain access facts — read once from each file while the overlay records its nodes; the rules read them and open no file."""

from __future__ import annotations

import re

_TOOL_CALL = re.compile(r"\.call(?:<[^>]*>)?\(")
_ADAPTER_IMPORT = re.compile(r"""from\s+['"]@cdd/""")
_EXTENDS_ADAPTER = re.compile(r"\bclass\s+\w+\s+extends\s+\w+(?:Adapter|Tools)\b")
_STORE_IMPORT = re.compile(r"""from\s+['"]lowdb[^'"]*['"]""")
# File names an application would give its own copy of what the installer generates.
_HAND_WRITTEN_ADAPTER = re.compile(r"(?:-adapter|-tools|-connection-node|^cdd-connection)\.ts$")
_MARK = re.compile(r"@language_adapter\(")
_OPEN_RESULT = re.compile(r"def\s+(\w+)\(self[^)]*\)\s*->\s*dict\[str,\s*Any\]")
_OPERATION_MARK = "@mcp"
_DECORATOR_LINES = 4


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _hits(pattern: re.Pattern[str], text: str) -> list[list]:
    return [[_line_of(text, match.start()), match.group(0).strip()] for match in pattern.finditer(text)]


def route_facts(text: str) -> dict:
    return {"tool_calls": _hits(_TOOL_CALL, text)}


def node_facts(text: str) -> dict:
    reaches_cdd = bool(_ADAPTER_IMPORT.search(text))
    return {
        "tool_calls": _hits(_TOOL_CALL, text),
        "reaches_cdd": reaches_cdd,
        "extends_adapter": bool(_EXTENDS_ADAPTER.search(text)),
        "store_imports": _hits(_STORE_IMPORT, text) if reaches_cdd else [],
    }


def is_hand_written_adapter(file_name: str, text: str) -> bool:
    """A file named like generated code that reaches cdd; an adapter for anything else is the application's own port."""
    if not _HAND_WRITTEN_ADAPTER.search(file_name):
        return False
    return file_name.startswith("cdd-connection") or bool(_ADAPTER_IMPORT.search(text) or _TOOL_CALL.search(text))


def is_marked(text: str) -> bool:
    return bool(_MARK.search(text))


def marked_toolset_facts(text: str) -> dict:
    return {"open_results": [[_line_of(text, match.start()), match.group(1)] for match in _OPEN_RESULT.finditer(text) if _reaches_typescript(text, match)]}


def _reaches_typescript(text: str, match: re.Match[str]) -> bool:
    """TypeScript reads what `to_json()` and an MCP operation return, and nothing else on the class."""
    if match.group(1) == "to_json":
        return True
    decorators = text[: match.start()].rsplit("\n", _DECORATOR_LINES)[1:]
    return _OPERATION_MARK in "\n".join(decorators)
