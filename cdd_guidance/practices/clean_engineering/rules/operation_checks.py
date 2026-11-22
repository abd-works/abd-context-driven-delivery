"""Code-channel graph rules — read the facts each parsed Operation and OoadClass recorded on its graph node."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding

from cdd_guidance.practices.clean_engineering.reading.production_classes import parameters_of
from cdd_guidance.practices.clean_engineering.model.operation_metrics import StatementCount
from cdd_guidance.practices.clean_engineering.rules.operation_semantics import SEMANTIC_RULES
from cdd_guidance.practices.clean_engineering.rules import rule_numbers
from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

VAGUE_NAMES = {
    "thing",
    "stuff",
    "info",
    "data",
    "args_list",
    "params",
    "options",
    "misc",
    "obj",
    "payload",
}

# snake_case requires at least one underscore between words; plain `register` is not snake_case.
_SNAKE_CASE = re.compile(r"^_*[a-z][a-z0-9]*(_[a-z0-9]+)+_*$")
_CAMEL_CASE = re.compile(r"^_*[a-z]+[A-Z][a-zA-Z0-9]*$")
_DUNDER = re.compile(r"^__[a-z]+__$")
_SKIP_OP_NAMES = frozenset(
    {
        "constructor",
        "__init__",
        "setUp",
        "tearDown",
        "setUpClass",
        "tearDownClass",
        "setUpModule",
    }
)
_STATIC_FACTORY_NAMES = frozenset({"instance", "create"})
# Static factories beyond name patterns (creation / mapping helpers): `now` makes a new value for this moment, as
# `datetime.now` does, and `every` makes each value a class allows, such as `IdeLayout.every()`. A global accessor
# such as `current` is not one: it hands out ambient state, which `hold-state-on-the-object-not-in-parameters` replaces
# with an object the caller holds.
_STATIC_FACTORY_EXTRA_NAMES = frozenset({"fromRequest", "now", "every"})
_CAMEL_FROM_FACTORY = re.compile(r"^from[A-Z]")
# The operations React calls on a component class itself, which it requires to be static.
_REACT_STATIC_OPERATIONS = frozenset({"getDerivedStateFromError", "getDerivedStateFromProps"})
_SCRIPT_SUFFIXES = (".ts", ".tsx", ".js", ".jsx")
_LOAD_FACTORY = re.compile(r"^load(?:[A-Z_].*)?$")
# The names a return type spells: `list[CatalogPractice]` spells `list` and `CatalogPractice`.
_TYPE_NAME = re.compile(r"[A-Za-z_]\w*")
# The words a type's name is made of: `HookPayload` is `Hook` and `Payload`, `hook_payload` is `hook` and `payload`.
_TYPE_WORD = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+")


_VAGUE_PARAMETER_NAMES = frozenset({"options", "opts", "config", "settings"})

GENERIC_NAMES = {
    "info",
    "thing",
    "stuff",
    "temp",
    "tmp",
    "val",
    "obj",
    "item",
    "foo",
    "bar",
    "baz",
    "misc",
    "blob",
    "value",
}


class UseExplicitDependencies(ProductionCodeRule):
    """A collaborator a constructor builds that its caller cannot hand it. The parser leaves out what a caller can
    replace or what the class owns: a failure it raises, a parameter's default, a part built from its own state. This
    rule passes values, failures, and collections (``ProductionClasses.is_value``), the peers an Entity composes, and a part
    the owner builds once and keeps: a class of the program's own that is no outside collaborator. An outside
    collaborator is a class the program does not declare, such as a library's client, or one whose name says it reaches
    outside the object (a repository, service, client, gateway, file, connection, or other process): the caller has to
    be able to hand it a different one. The build keeps the first such collaborator on the class
    (``constructs_collaborator``)."""

    slug = "use-explicit-dependencies"
    # Requires a judge: whether a part the class builds is an outside collaborator is read from what the part is; the check goes by its name and where it is declared.
    requires_judge = True
    node_types = ("OoadClass",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        built = node.get_fact("constructs_collaborator") or ""
        return [Finding(node, message) for message in ([f"Class '{node.name}' constructs '{built}' inside its constructor."] if built else [])]


class OperationMeasureRule(ProductionCodeRule):
    """Measures each operation body the graph records: every Operation node, and each Property node a getter backs,
    whose node records the getter's measurements."""

    node_types = ("Operation", "Property")

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        """A field is no operation: one a constructor assigns sits inside the constructor, whose measures are not its."""
        if node.type == "Property" and not node.get_fact("is_property"):
            return []
        return [Finding(node, message) for message in self.measure(node)]

    def measure(self, operation: "Node") -> list[str]:
        return []


def operation_label(operation: "Node") -> str:
    """How a message names the measured operation: `Operation 'load'`, or `Property 'total'` for a getter."""
    return f"{operation.type} '{operation.name}'"


class KeepOperationsSmall(OperationMeasureRule):
    """Counts the statements of the body, as the rule says: a call, list, or string written over several lines is one
    statement, and the signature and docstring are none. An operation whose body the graph did not keep, such as one a
    model document declares, is measured by its lines."""

    slug = "keep-operations-small-focused"
    code_fidelity_only = True

    @property
    def limit(self) -> int:
        return rule_numbers.MOST_STATEMENTS

    def measure(self, operation: "Node") -> list[str]:
        python = str(operation.source.file or "").endswith(".py")
        statements = StatementCount(operation.get_fact("body_text") or "", python).count()
        if statements is None:
            return self._measure_lines(operation)
        if statements <= self.limit:
            return []
        return [f"{operation_label(operation)} is {statements} statements (max {self.limit})."]

    def _measure_lines(self, operation: "Node") -> list[str]:
        size = self._line_count(operation)
        if size <= self.limit:
            return []
        return [f"{operation_label(operation)} is {size} lines (max {self.limit})."]

    def _line_count(self, operation: "Node") -> int:
        """The parser's count, read from the node's own facts (an ancestor's count is another member's); for a node
        without one, the lines its source span covers."""
        span = operation.source.end_line - operation.source.start_line + 1
        return operation.facts.get("line_count") or (span if span > 1 else 0)


class SimplifyControlFlow(OperationMeasureRule):
    slug = "simplify-control-flow"
    code_fidelity_only = True

    @property
    def limit(self) -> int:
        return rule_numbers.MOST_NESTED_LEVELS

    def measure(self, operation: "Node") -> list[str]:
        if operation.name.startswith("register") and operation.name.endswith("Route"):
            return []
        if operation.name.startswith("create") and operation.name.endswith("Routes"):
            return []
        depth = operation.get_fact("max_control_flow_depth", 0) or 0
        if depth <= self.limit:
            return []
        return [f"{operation_label(operation)} nests control flow {depth} levels deep (max {self.limit})."]


class UseExceptionsProperly(ProductionCodeRule):
    """A spec catches every exception on purpose, to prove what a call raises, so only production code is judged."""

    slug = "use-exceptions-properly"
    code_fidelity_only = True
    node_types = OperationMeasureRule.node_types

    def check_production(self, operation: "Node", context: "RuleCheckContext") -> list[Finding]:
        if not operation.get_fact("has_bare_catch"):
            return []
        return [Finding(operation, f"{operation_label(operation)} catches every exception (a bare except, or except Exception that never re-raises).")]


class NeverSwallowExceptions(ProductionCodeRule):
    slug = "never-swallow-exceptions"
    code_fidelity_only = True
    node_types = OperationMeasureRule.node_types

    def check_production(self, operation: "Node", context: "RuleCheckContext") -> list[Finding]:
        if not operation.get_fact("swallows_exceptions"):
            return []
        return [Finding(operation, f"{operation_label(operation)} swallows a caught failure or hands back a fallback in its place.")]


class ProvideMeaningfulContext(ProductionCodeRule):
    slug = "provide-meaningful-context"
    code_fidelity_only = True
    node_types = ("Operation",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        for raw in node.get_fact("unnamed_literal_numbers", []):
            return [Finding(node, f"Operation '{node.name}' uses the unnamed number {raw}.")]
        return []


class AvoidVagueParameterNames(ProductionCodeRule):
    """A placeholder name passes when the parameter's type names it: in `payload: HookPayload` the type says which
    payload the caller supplies, so the name hides nothing."""

    slug = "avoid-vague-parameter-names"
    # Requires a judge: whether a parameter's name is vague is read from what it carries; the check matches a word list.
    requires_judge = True
    node_types = ("Parameter", "Operation")

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        if node.type == "Parameter":
            if node.name.lower() in VAGUE_NAMES and not self._named_by_type(node.name, node.get_fact("type_hint", "")):
                return [Finding(node, f"Parameter '{node.name}' is vague. Use a domain-specific name.")]
            return []
        for parameter in parameters_of(node):
            lowered = parameter.name.lower()
            vague = lowered in VAGUE_NAMES or lowered in _VAGUE_PARAMETER_NAMES
            if vague and not self._named_by_type(parameter.name, parameter.get_fact("type_hint", "")):
                return [Finding(node, f"Parameter '{parameter.name}' in '{node.name}' is vague.")]
        return []

    def _named_by_type(self, name: str, type_hint: str) -> bool:
        """True when a type the hint names has the parameter's name as one of its words: `HookPayload` for `payload`,
        `RenderOptions` for `options`."""
        words = {word.lower() for type_name in _TYPE_NAME.findall(type_hint or "") for word in _TYPE_WORD.findall(type_name)}
        return name.strip("_").lower() in words


# A Claude Code mod hands every hook its engine as `$`, the name the mod API documents, so a reader knows it on sight.
_CONVENTIONAL_PARAMETER_NAMES = frozenset({"$"})


class UseIntentionRevealingNames(ProductionCodeRule):
    """Judged on each parameter, which the graph reads for every operation's signature, so a name is reported once,
    where it is written."""

    slug = "use-intention-revealing-names"
    # Requires a judge: whether a name says why the thing exists is read from the name in its place; the check goes by its length.
    requires_judge = True
    node_types = ("Parameter",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        if not re.match(r"^[\w$]+$", node.name) or node.name in _CONVENTIONAL_PARAMETER_NAMES:
            return []
        operation = node.get_fact("operation_name", "")
        if self._setter_parameter(node):
            return []
        if operation == "text" and node.name in {"value", "rawField"}:
            return []
        if node.name == "value" and operation == "asyncRoute":
            return []
        if len(node.name) < 3 or node.name.lower() in GENERIC_NAMES:
            return [Finding(node, f"Parameter '{node.name}' does not reveal intent.")]
        return []

    def _setter_parameter(self, node: "Node") -> bool:
        """`value` in a setter, TypeScript's `set email(value)` or Python's `@email.setter`: the property names the
        intent."""
        return node.name == "value" and bool(node.get_fact("property_setter"))


class UseConsistentNaming(ProductionCodeRule):
    slug = "use-consistent-naming"
    # Requires a judge: whether two words name one concept is read from what they mean; the check matches word lists.
    requires_judge = True
    node_types = ("OoadClass",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        snake_names: list[str] = []
        camel_names: list[str] = []
        for shape in node.get_fact("operation_shapes", []):
            name = shape["name"]
            if not name or name in _SKIP_OP_NAMES or _DUNDER.match(name) or name.startswith("_"):
                continue
            if _CAMEL_CASE.match(name):
                camel_names.append(name)
            elif _SNAKE_CASE.match(name):
                snake_names.append(name)
        if not snake_names or not camel_names:
            return []
        minority = camel_names if len(camel_names) <= len(snake_names) else snake_names
        style = "camelCase" if minority is camel_names else "snake_case"
        return [Finding(node, f"Operation '{minority[0]}' uses {style} while other operations on '{node.name}' "
            "use the other convention.")]


class PreferInstanceOperations(ProductionCodeRule):
    slug = "prefer-instance-operations"
    code_fidelity_only = True
    node_types = ("Operation",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        is_static = bool(node.get_fact("is_static"))
        is_classmethod = bool(node.get_fact("is_classmethod"))
        if not is_static and not is_classmethod:
            return []
        if self._allows_static_factory_operation(node.name) or self._makes_its_own_class(node) or self._react_static(node):
            return []
        kind = "classmethod" if is_classmethod else "staticmethod"
        return [Finding(node, f"Operation '{node.name}' is a {kind}; prefer an instance operation.")]

    def _allows_static_factory_operation(self, name: str) -> bool:
        if name in _STATIC_FACTORY_NAMES or name in _STATIC_FACTORY_EXTRA_NAMES:
            return True
        if name.startswith("from_"):
            return True
        if _CAMEL_FROM_FACTORY.match(name):
            return True
        return _LOAD_FACTORY.match(name) is not None

    def _react_static(self, operation: "Node") -> bool:
        """A static operation React calls on a component class, such as `getDerivedStateFromError`: React requires it
        to be static, so the class cannot make it an instance operation."""
        script = str(operation.source.file or "").endswith(_SCRIPT_SUFFIXES)
        return script and operation.name in _REACT_STATIC_OPERATIONS

    def _makes_its_own_class(self, operation: "Node") -> bool:
        """A factory: a class-level operation that makes its own class from what it is given, such as
        `for_project(root) -> ProjectApproach`, `every(folder) -> list[Practice]`, or `-> Self`; no instance exists yet
        to call it on. One that takes nothing, such as `current() -> Board`, hands out a global instance, which a caller
        should hold instead."""
        if not parameters_of(operation):
            return False
        spelled = set(_TYPE_NAME.findall(str(operation.get_fact("return_type") or "")))
        return bool(spelled & {operation.get_fact("owner", ""), "Self"})


class UsePropertyNotAccessor(ProductionCodeRule):
    slug = "use-property-not-accessor"
    node_types = ("Operation",)

    _PREFIXES = ("calculate_", "compute_", "get_")

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        if node.get_fact("is_property"):
            return []
        if not any(node.name.startswith(prefix) for prefix in self._PREFIXES):
            return []
        if parameters_of(node):
            return []
        owner = node.get_fact("owner", "")
        return [Finding(node, f"Operation '{node.name}' on '{owner}' looks like a getter; use a property.")]


class EliminateDuplication(PracticeGraphRule):
    """Production operations whose bodies are the same, or nearly the same: a copy with a renamed variable or one
    changed line is still a second place the same fix has to go. The build keeps on each copy the operation it copies
    (``duplicate_of``, ``near_copy_of``)."""

    slug = "eliminate-duplication"
    node_types = ("Operation",)

    def check_practice(self, context: "RuleCheckContext") -> list[Finding]:
        hits: list[Finding] = []
        for operation in context.nodes("Operation"):
            original = operation.get_fact("duplicate_of") or ""
            near = operation.get_fact("near_copy_of") or []
            if original:
                hits.append(Finding(operation, f"Operation '{operation.name}' duplicates the body of '{original}'."))
            elif near:
                hits.append(Finding(operation, self._near_copy_message(operation, near)))
        return hits

    def _near_copy_message(self, operation: "Node", near: list) -> str:
        name, file, percent = near
        return (
            f"Operation '{operation.name}' nearly duplicates '{name}' ({file}): "
            f"{percent}% of their code is the same. Give the shared logic one function."
        )


CODE_RULES: tuple[PracticeGraphRule, ...] = (
    UseExplicitDependencies(),
    UseConsistentNaming(),
    KeepOperationsSmall(),
    SimplifyControlFlow(),
    UseExceptionsProperly(),
    NeverSwallowExceptions(),
    ProvideMeaningfulContext(),
    AvoidVagueParameterNames(),
    UseIntentionRevealingNames(),
    PreferInstanceOperations(),
    UsePropertyNotAccessor(),
    EliminateDuplication(),
) + SEMANTIC_RULES
