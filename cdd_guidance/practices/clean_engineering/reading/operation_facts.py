"""The facts each operation keeps about the other operations and classes of the graph: the operation whose body it
copies, exactly or nearly, and whether the failure it raises without a message writes its own."""

from __future__ import annotations

import ast
import textwrap
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.clean_engineering.reading.folder_facts import record_fact
from cdd_guidance.practices.clean_engineering.reading.near_copies import MIN_LINES, NearCopies
from cdd_guidance.practices.source_code import CODE_LANGUAGES

if TYPE_CHECKING:
    from harness.graph.graph import Node, PracticeNodes

    from cdd_guidance.practices.clean_engineering.reading.production_classes import ProductionClasses

# A share is kept as a whole percentage.
_PERCENT = 100


def qualified_name(operation: "Node") -> str:
    """How a fact across files names an operation: `Class.operation`, or the function's name alone for a function a
    file declares outside any class."""
    owner = str(operation.get_fact("owner") or "")
    return operation.name if not owner or owner == MODULE_FUNCTION_HOLDER else f"{owner}.{operation.name}"


def code_operations(in_graph: "PracticeNodes") -> list["Node"]:
    """The operations of the production code the graph read: neither a spec's or test support's, nor one a model
    document describes, which has no body to compare."""
    suffixes = {suffix for language in CODE_LANGUAGES for suffix in language.suffixes}
    return [
        node for node in in_graph.nodes("Operation")
        if not in_graph.practice.reading.test_code.is_test_code(node.source.file) and PurePosixPath(node.source.file or "").suffix in suffixes
    ]


def file_qualified_name(operation: "Node") -> str:
    """How a fact across files names an operation with its file, `shop/cart.py: Cart.total`, so two classes of one name
    in different files stay apart."""
    return f"{operation.source.file}: {qualified_name(operation)}"


class BodyCopies:
    """Production operations whose bodies are the same as one read before them (``duplicate_of``: that operation's
    name), or nearly the same (``near_copy_of``: its name, its file, and the percentage of their code they share). A copy
    with a renamed variable or one changed line is still a second place the same fix has to go. Each body is reported
    once: a near copy is looked for only among the operations no exact copy names."""

    def __init__(self, in_graph: "PracticeNodes") -> None:
        self._operations = code_operations(in_graph)

    def record(self) -> None:
        exact = self._exact_copies()
        near: dict[str, list] = {}
        for copy, original, shared in NearCopies([node for node in self._operations if node.node_id not in exact]).pairs():
            near[copy.node_id] = [original.name, original.source.file, round(_PERCENT * shared)]
        for operation in self._operations:
            record_fact(operation, "duplicate_of", exact.get(operation.node_id, ""))
            record_fact(operation, "near_copy_of", near.get(operation.node_id, []))

    def _exact_copies(self) -> dict[str, str]:
        """Each operation whose body has the same fingerprint as one before it, with the name of that one."""
        seen: dict[str, str] = {}
        copies: dict[str, str] = {}
        for operation in [node for node in self._operations if self._compared(node)]:
            fingerprint = operation.get_fact("body_fingerprint", "")
            if fingerprint in seen:
                copies[operation.node_id] = seen[fingerprint]
            else:
                seen[fingerprint] = operation.name
        return copies

    def _compared(self, operation: "Node") -> bool:
        """An operation whose body is long enough to copy, and is more than its class's configuration."""
        counted = bool(operation.get_fact("body_fingerprint", "")) and operation.get_fact("line_count", 0) >= MIN_LINES
        return counted and not self._configures_only(operation)

    def _configures_only(self, operation: "Node") -> bool:
        """True for a body that is one call given only literal values, such as a pattern's
        `super().__init__(format="typescript", default_workspace_folder="harness")`: each class's own configuration,
        not logic one function could hold."""
        call = self._sole_call(operation.get_fact("body_text") or "")
        return call is not None and all(isinstance(value, ast.Constant) for value in [*call.args, *(keyword.value for keyword in call.keywords)])

    def _sole_call(self, body: str) -> ast.Call | None:
        """The call a Python body makes as its one statement, its docstring aside; none for any other body."""
        try:
            statements = ast.parse(textwrap.dedent(body)).body
        except SyntaxError:
            return None
        code = [item for item in statements if not (isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant))]
        sole = code[0] if len(code) == 1 else None
        return sole.value if isinstance(sole, ast.Expr) and isinstance(sole.value, ast.Call) else None


class FailureMessages:
    """Whether the failure each operation raises without a message writes its own (``exception_gives_own_message``): a
    failure the program declares whose constructor hands its base the message carries that context however it is
    raised."""

    def __init__(self, in_graph: "PracticeNodes", classes: "ProductionClasses") -> None:
        self._in_graph = in_graph
        self._classes = classes

    def record(self) -> None:
        for operation in self._in_graph.nodes("Operation"):
            exception = operation.get_fact("exception_without_message", "")
            record_fact(operation, "exception_gives_own_message", bool(exception) and self._classes.gives_own_message(exception))
