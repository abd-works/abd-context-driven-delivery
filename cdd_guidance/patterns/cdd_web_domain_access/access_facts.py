"""CDD web domain access facts — read once from each file while the overlay records its nodes; the rules read them and open no file."""

from __future__ import annotations

import ast
import re
from pathlib import Path

from cdd_guidance.practices.clean_engineering.model.operation_metrics import SourceText

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


class AccessFile:
    """One file that may reach the CDD domain from outside Python, read once, with the SourceText that gives each match
    in it the line it starts on: a route, a node tier, a hand-written adapter, or an annotated toolset. Which of those it
    is, and the facts its rules read, are its operations."""

    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.text = text
        self._source = SourceText(text)

    @classmethod
    def at(cls, path: Path) -> AccessFile:
        """The file at path, read now."""
        return cls(path.name, path.read_text(encoding="utf-8", errors="replace"))

    def tier(self) -> tuple[str, dict] | None:
        """The DDD node type this file becomes and the facts it carries; none for a file that does not reach the domain."""
        if self.name.endswith("-routes.ts"):
            return "AccessRoute", self.route_facts()
        if self.is_hand_written_adapter():
            return "AccessHandWrittenAdapter", {}
        if self.name.endswith("-node.ts"):
            return "AccessNode", self.node_facts()
        if self.name.endswith(".py") and self.is_annotated():
            return "AccessAnnotatedToolset", self.annotated_toolset_facts()
        return None

    def route_facts(self) -> dict:
        return {"tool_calls": self._source.hits(_TOOL_CALL)}

    def node_facts(self) -> dict:
        reaches_cdd = bool(_ADAPTER_IMPORT.search(self.text))
        return {
            "tool_calls": self._source.hits(_TOOL_CALL),
            "reaches_cdd": reaches_cdd,
            "extends_adapter": bool(_EXTENDS_ADAPTER.search(self.text)),
            "store_imports": self._source.hits(_STORE_IMPORT) if reaches_cdd else [],
        }

    def is_hand_written_adapter(self) -> bool:
        """A file named like generated code that reaches cdd; an adapter for anything else is the application's own port."""
        if not _HAND_WRITTEN_ADAPTER.search(self.name):
            return False
        return self.name.startswith("cdd-connection") or bool(_ADAPTER_IMPORT.search(self.text) or _TOOL_CALL.search(self.text))

    def is_annotated(self) -> bool:
        return bool(_MARK.search(self.text))

    def annotated_toolset_facts(self) -> dict:
        """[line, operation] for each MCP operation of an annotated toolset that answers an open ``dict[str, Any]``, which
        TypeScript then reads with no type. The decorators are read from the parsed file, so every spelling of the
        annotation and any number of other annotations above it count."""
        operations = [node for node in ast.walk(ast.parse(self.text)) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        return {"open_results": [[node.lineno, node.name] for node in operations if self._answers_open_dict(node) and self._is_published(node)]}

    def _answers_open_dict(self, operation: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        return operation.returns is not None and ast.unparse(operation.returns) == _OPEN_RESULT

    def _is_published(self, operation: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        return any(self._annotation_name(decorator).lower() == _OPERATION_ANNOTATION for decorator in operation.decorator_list)

    def _annotation_name(self, decorator: ast.expr) -> str:
        """The name a decorator is written with: `Mcp` for `@Mcp`, `@Mcp(...)`, and `@mcp_server.Mcp`."""
        annotated = decorator.func if isinstance(decorator, ast.Call) else decorator
        if isinstance(annotated, ast.Attribute):
            return annotated.attr
        return annotated.id if isinstance(annotated, ast.Name) else ""
