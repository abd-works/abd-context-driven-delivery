"""CDD web domain access facts — read once from each file while the overlay records its nodes; the rules read them and open no file."""

from __future__ import annotations

import ast
import re

from cdd_guidance.patterns.source_text import SourceText

_TOOL_CALL = re.compile(r"\.call(?:<[^>]*>)?\(")
_ADAPTER_IMPORT = re.compile(r"""from\s+['"]@cdd/""")
_EXTENDS_ADAPTER = re.compile(r"\bclass\s+\w+\s+extends\s+\w+(?:Adapter|Tools)\b")
_STORE_IMPORT = re.compile(r"""from\s+['"]lowdb[^'"]*['"]""")
# File names an application would give its own copy of what the installer generates.
_HAND_WRITTEN_ADAPTER = re.compile(r"(?:-adapter|-tools|-connection-node|^cdd-connection)\.ts$")
_MARK = re.compile(r"@language_adapter\(")
# The annotation that publishes an operation on MCP, spelled `@mcp` or `@Mcp`; TypeScript reads what such an operation returns.
_OPERATION_ANNOTATION = "mcp"
_OPEN_RESULT = "dict[str, Any]"


def route_facts(text: str) -> dict:
    return {"tool_calls": SourceText(text).hits(_TOOL_CALL)}


def node_facts(text: str) -> dict:
    source = SourceText(text)
    reaches_cdd = bool(_ADAPTER_IMPORT.search(text))
    return {
        "tool_calls": source.hits(_TOOL_CALL),
        "reaches_cdd": reaches_cdd,
        "extends_adapter": bool(_EXTENDS_ADAPTER.search(text)),
        "store_imports": source.hits(_STORE_IMPORT) if reaches_cdd else [],
    }


def is_hand_written_adapter(file_name: str, text: str) -> bool:
    """A file named like generated code that reaches cdd; an adapter for anything else is the application's own port."""
    if not _HAND_WRITTEN_ADAPTER.search(file_name):
        return False
    return file_name.startswith("cdd-connection") or bool(_ADAPTER_IMPORT.search(text) or _TOOL_CALL.search(text))


def is_annotated(text: str) -> bool:
    return bool(_MARK.search(text))


def annotated_toolset_facts(text: str) -> dict:
    """[line, operation] for each MCP operation of an annotated toolset that answers an open ``dict[str, Any]``, which
    TypeScript then reads with no type. The decorators are read from the parsed file, so every spelling of the annotation and
    any number of other annotations above it count."""
    operations = [node for node in ast.walk(ast.parse(text)) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return {"open_results": [[node.lineno, node.name] for node in operations if _answers_open_dict(node) and _is_published(node)]}


def _answers_open_dict(operation: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return operation.returns is not None and ast.unparse(operation.returns) == _OPEN_RESULT


def _is_published(operation: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(_annotation_name(decorator).lower() == _OPERATION_ANNOTATION for decorator in operation.decorator_list)


def _annotation_name(decorator: ast.expr) -> str:
    """The name a decorator is written with: `Mcp` for `@Mcp`, `@Mcp(...)`, and `@mcp_server.Mcp`."""
    annotated = decorator.func if isinstance(decorator, ast.Call) else decorator
    if isinstance(annotated, ast.Attribute):
        return annotated.attr
    return annotated.id if isinstance(annotated, ast.Name) else ""
