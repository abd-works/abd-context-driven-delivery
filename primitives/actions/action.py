# @toolset-manifest python -m tools manifest primitives.actions.agent_with_actions:AgentWithActions
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.format python
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Action expansion - orchestration recipes that never execute, only instruct."""
from __future__ import annotations

import ast
import inspect
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TypeAlias

_PARAM_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")
_SELF_PLACEHOLDER = re.compile(r"\{\{self\.(\w+)\}\}")


from tools.types import (
    ManifestDocument,
    RunRequestDocument,
    RunResponseDocument,
    SignatureEntry,
)

ContextDocument: TypeAlias = dict[str, Any]
ArgumentDocument: TypeAlias = dict[str, Any]
ActionExpansion: TypeAlias = dict[str, Any]


def _get_or_create_singleton(cls: type) -> Any:
    """Return the cached singleton for *cls*, creating it on first call."""
    if cls._instance is None:
        cls._instance = cls()
    return cls._instance


@dataclass(frozen=True)
class _ActionExpandRequest:
    action_func: Callable[..., Any]
    toolset_path: str
    context: ContextDocument
    arguments: ArgumentDocument
    tool_callables: dict[str, Callable[..., Any]]
    instance: Any | None = None


@dataclass(frozen=True)
class _ActionRunRequest:
    request: RunRequestDocument
    toolset_path: str
    action_name: str
    context: ContextDocument
    arguments: ArgumentDocument
    instance: Any


@dataclass(frozen=True)
class _InstructionBuildRequest:
    """Bundles all inputs needed to build the instruction text for one action expansion."""

    body: "_ActionBody"
    toolset_path: str
    context: dict[str, Any]
    arguments: dict[str, Any]
    parameter_names: set[str]
    tool_callables: dict[str, Callable[..., Any]]
    instance: Any | None = None


@dataclass(frozen=True)
class _RunOutput:
    """Bundles the expansion result and run-request metadata for building a run response."""

    toolset_path: Any
    action_name: Any
    arguments: dict[str, Any]
    instance: Any
    expanded: dict[str, Any]


@dataclass(frozen=True)
class _ScanRequest:
    """Bundles all inputs needed to scan one action body for disallowed member access."""

    body: "ast.Module"
    allowed_names: set[str]
    all_providers: set[str]
    class_name: str
    action_name: str
    base_line: int


@dataclass(frozen=True)
class _BodySlots:
    """Groups the four sets of allowed member kinds in a toolset body walk."""

    instruction_slots: "frozenset[str]"
    action_slots: "frozenset[str]"
    tool_names: set[str]
    resource_names: set[str]


@dataclass(frozen=True)
class _WalkContext:
    """Immutable context for walking a single action body."""

    instance: Any
    current_action: str
    visited: "frozenset[tuple[str, str]]"
    defining_class: "type | None"
    slots: _BodySlots


class _ProseAccumulator:
    """Mutable state that collects prose and tool steps during a body walk."""

    def __init__(self) -> None:
        self.prose: list[str] = []
        self.tool_steps: list[str] = []
        self.seen_prose: set[str] = set()

    def merge(self, new_prose: "list[str]", new_tools: "list[str]") -> None:
        """Merge new_prose (deduped) and new_tools into this accumulator."""
        self.tool_steps.extend(new_tools)
        for part in new_prose:
            if part and part not in self.seen_prose:
                self.prose.append(part)
                self.seen_prose.add(part)

    def add_text(self, text: str) -> None:
        """Add text to prose when non-empty and not already seen."""
        if text and text not in self.seen_prose:
            self.prose.append(text)
            self.seen_prose.add(text)


from primitives.instructions import (
    _expand_docstring,
    _inline,
    instruction_slot_names,
)
from tools.tool import _SignatureReader, resource, Toolset


class AgenticToolset(Toolset):
    """Base for toolsets that declare @action methods. Adds the mode resource.

    Inherit from this instead of Toolset when your class uses @action.
    Use @agentic_toolset as the class decorator (parallel to @toolset).

    mode lives on the callee, not the caller — it governs every call into this
    instance's actions, whether the call is ``self.action()`` (same instance)
    or ``self.other_agentic_toolset().action()`` (cross-instance).

    mode values
    -----------
    action  (default) — calls into this instance's actions expand inline into the caller's instructions.
    tool    — list the called action in tools (like a tool call); defer its body instead of inlining it.
    """

    _mode: str = "action"

    @property
    @resource
    def mode(self) -> str:
        """Execution mode for @action calls into this instance (self or cross-instance).
        action = expand inline; tool = list action in tools, defer its body."""
        return self._mode

    @mode.setter
    def mode(self, new_mode: str) -> None:
        if new_mode not in ("action", "tool"):
            raise ValueError(f"mode must be 'action' or 'tool', got {new_mode!r}")
        self._mode = new_mode


class ActionValidationError(Exception):
    def __init__(
        self,
        message: str,
        *,
        class_name: str,
        action_name: str,
        lineno: int | None = None,
    ) -> None:
        location = f"{class_name}.{action_name}"
        if lineno is not None:
            location = f"{location}:{lineno}"
        super().__init__(f"{location} - {message}")
        self._class_name = class_name
        self._action_name = action_name
        self._lineno = lineno

    @property
    def class_name(self) -> str:
        return self._class_name

    @property
    def action_name(self) -> str:
        return self._action_name

    @property
    def lineno(self) -> int | None:
        return self._lineno


@dataclass(frozen=True)
class _ActionBody:
    prose_parts: tuple[str, ...]
    tool_steps: tuple[str, ...]
    result_template: str

#to do: move static methods to class methods; clean enginnerring rules should test for this
def _action_slot_names(toolset_cls: type) -> frozenset[str]:
    names: set[str] = set()
    for name, member in inspect.getmembers(toolset_cls, predicate=inspect.isfunction):
        if getattr(member, "_is_action", False):
            names.add(name)
    return frozenset(names)




def _self_member_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "self":
            return func.attr
        return None
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
        return node.attr
    return None


def _cross_instance_call(node: ast.AST) -> tuple[str, str] | None:
    """Match ``self.<provider>().<member>()`` or ``self.<provider>.<member>()``.

    The call boundary is the *member* being invoked (the actual tool/action) —
    getting to the provider instance is just a reference and may be either a
    zero-arg method call or a plain attribute/property access.
    """
    if not isinstance(node, ast.Call):
        return None
    if not isinstance(node.func, ast.Attribute):
        return None
    member = node.func.attr
    provider_node = node.func.value
    provider_attr = provider_node.func if isinstance(provider_node, ast.Call) else provider_node
    if not isinstance(provider_attr, ast.Attribute):
        return None
    if not isinstance(provider_attr.value, ast.Name) or provider_attr.value.id != "self":
        return None
    return provider_attr.attr, member


class _ActionBodyScanner(ast.NodeVisitor):
    """Visits an @action body, checking only step-level ``self.*`` references.

    A call *boundary* (``self.<member>()``, or a cross-instance
    ``self.<provider>().<member>()``) is a step and must resolve to an allowed
    name. Once a boundary is recognised, its arguments are not descended into —
    they are plain data (e.g. ``slug=self.domain_slug``), not further steps.
    """

    def __init__(self, scan_req: "_ScanRequest") -> None:
        self._req = scan_req

    def _check_member(self, member_name: str, node: ast.AST) -> None:
        req = self._req
        if member_name in req.allowed_names or member_name in req.all_providers:
            return
        raise ActionValidationError(
            f"self.{member_name} is not a @tool, @instruction, @action, or @resource",
            class_name=req.class_name,
            action_name=req.action_name,
            lineno=req.base_line + node.lineno - 1,
        )

    def visit_Call(self, node: ast.Call) -> None:
        if _cross_instance_call(node) is not None:
            return  # cross-instance call boundary; member checked at expansion time
        member_name = _self_member_name(node)
        if member_name is not None:
            self._check_member(member_name, node)
            return  # arguments are data, not steps - do not descend into them
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        member_name = _self_member_name(node)
        if member_name is not None:
            self._check_member(member_name, node)
            return
        self.generic_visit(node)


class _ActionValidator:
    """Validates @action bodies reference only allowed members."""

    _instance: _ActionValidator | None = None

    @staticmethod
    def _is_resource_property(member: Any) -> bool:
        """Return True when member is a property whose getter has _is_resource=True."""
        return (
            isinstance(member, property)
            and member.fget is not None
            and getattr(member.fget, "_is_resource", False)
        )

    @staticmethod
    def _cross_instance_providers(body: ast.Module) -> set[str]:
        providers: set[str] = set()
        for node in ast.walk(body):
            cross = _cross_instance_call(node)
            if cross is not None:
                providers.add(cross[0])
        return providers

    @staticmethod
    def _for_each_providers(body: ast.Module) -> set[str]:
        """Collect provider method names used as iterables in for-each action bodies.

        Recognises the pattern::

            for <var> in self.<provider>():
                <var>.<action>()

        The provider name is added to the allowed-names set so the validator does
        not reject ``self.<provider>()`` as an unrecognised member call.
        """
        providers: set[str] = set()
        for node in ast.walk(body):
            if not isinstance(node, ast.For):
                continue
            iter_member = _self_member_name(node.iter)
            if iter_member is not None:
                providers.add(iter_member)
        return providers

    @classmethod
    def instance(cls) -> _ActionValidator:
        return _get_or_create_singleton(cls)

    def validate_class(self, toolset_cls: type) -> None:
        allowed = self._allowed_names(toolset_cls)
        for name, member in inspect.getmembers(toolset_cls, predicate=inspect.isfunction):
            if not getattr(member, "_is_action", False):
                continue
            self.validate_action(toolset_cls.__name__, name, member, allowed)

    def _scan_action_body(self, scan_req: _ScanRequest) -> None:
        """Walk the body and raise ActionValidationError for any disallowed member access.

        Only call *boundaries* (``self.<member>()`` and cross-instance calls) are
        validated as steps — call *arguments* are data, evaluated for real once the
        action runs, not a separate step the agent needs to resolve. So a value like
        ``self.domain_slug`` passed as ``slug=self.domain_slug`` is never itself
        required to be a @tool / @instruction / @action / @resource.
        """
        _ActionBodyScanner(scan_req).visit(scan_req.body)

    def validate_action(
        self,
        class_name: str,
        action_name: str,
        action_func: Callable[..., Any],
        allowed_names: set[str],
    ) -> None:
        body = self._parse_source(action_func)
        all_providers = self._cross_instance_providers(body) | self._for_each_providers(body)
        self._scan_action_body(_ScanRequest(
            body=body,
            allowed_names=allowed_names,
            all_providers=all_providers,
            class_name=class_name,
            action_name=action_name,
            base_line=action_func.__code__.co_firstlineno,
        ))

    def _allowed_names(self, toolset_cls: type) -> set[str]:
        return (
            self._tool_names(toolset_cls)
            | set(instruction_slot_names(toolset_cls))
            | set(_action_slot_names(toolset_cls))
            | self._resource_names(toolset_cls)
        )

    def _tool_names(self, toolset_cls: type) -> set[str]:
        names: set[str] = set()
        for name, member in inspect.getmembers(toolset_cls, predicate=inspect.isfunction):
            if getattr(member, "_is_tool", False):
                names.add(name)
        return names

    def _resource_names(self, toolset_cls: type) -> set[str]:
        """Allow @resource properties (incl. bases) in action bodies."""
        names: set[str] = set()
        for cls in toolset_cls.__mro__:
            if cls is object:
                continue
            names.update(name for name, member_val in cls.__dict__.items() if self._is_resource_property(member_val))
        return names

    def _parse_source(self, action_func: Callable[..., Any]) -> ast.Module:
        source = textwrap.dedent(inspect.getsource(action_func))
        return ast.parse(source)

    def _self_tool_name(self, node: ast.Call) -> str | None:
        return _self_member_name(node)



class _ActionExpander:
    """Expands @action bodies into instructions for a calling agent."""

    _instance: _ActionExpander | None = None

    @staticmethod
    def _visit_key(instance: Any, action_name: str, defining_class: type | None = None) -> tuple[str, str]:
        cls = defining_class if defining_class is not None else type(instance)
        return cls.__qualname__, action_name

    @staticmethod
    def _find_parent_action(
        own_class: type,
        method_name: str,
        after_class: type | None,
        own_func: Callable[..., Any],
    ) -> "tuple[Callable[..., Any], type] | None":
        """Walk the MRO slice after *after_class* and return the first ``@action`` found."""
        past_anchor = after_class is None
        for klass in own_class.__mro__:
            if not past_anchor:
                past_anchor = (klass is after_class)
                continue
            if method_name not in klass.__dict__:
                continue
            func = klass.__dict__[method_name]
            if after_class is None and func is own_func:
                continue
            if callable(func) and getattr(func, "_is_action", False):
                return func, klass
        return None

    @staticmethod
    def _fetch_class_method(own_class: type, method_name: str) -> "Callable[..., Any] | None":
        """Raw __dict__ lookup — returns the stored callable or None."""
        return own_class.__dict__.get(method_name)

    @staticmethod
    def _own_class_func(
        instance: Any, method_name: str
    ) -> "tuple[type, Callable[..., Any]] | None":
        """Return ``(own_class, own_func)`` for *method_name* on *instance*, or None."""
        own_class = type(instance)
        own_func = _ActionExpander._fetch_class_method(own_class, method_name)
        return None if own_func is None else (own_class, own_func)

    @staticmethod
    def _check_and_advance_visited(
        instance: Any, current_action: str, defining_class: "type | None",
        visited: "frozenset[tuple[str, str]]",
    ) -> "frozenset[tuple[str, str]]":
        """Raise ActionValidationError for recursive calls; otherwise extend visited."""
        visit_key = _ActionExpander._visit_key(instance, current_action, defining_class)
        if visit_key in visited:
            raise ActionValidationError(
                f"recursive @action call: {current_action}",
                class_name=type(instance).__name__,
                action_name=current_action,
            )
        return visited | {visit_key}

    @staticmethod
    def _is_leading_docstring(statement: "ast.stmt", already_skipped: bool) -> bool:
        """Return True when statement is the first bare string literal (the docstring)."""
        return (
            not already_skipped
            and isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        )

    @staticmethod
    def _member_call_attr(call_node: "ast.AST", var_name: str) -> "str | None":
        """Return the attribute name if call_node is ``var_name.attr(...)``, else None."""
        if not isinstance(call_node, ast.Call):
            return None
        func = call_node.func
        if not isinstance(func, ast.Attribute):
            return None
        if not isinstance(func.value, ast.Name) or func.value.id != var_name:
            return None
        return func.attr

    @staticmethod
    def _super_call_name(node: ast.AST) -> str | None:
        """Return the method name if node is a bare ``super().method(...)`` call, else None."""
        if not isinstance(node, ast.Call):
            return None
        func = node.func
        if not isinstance(func, ast.Attribute):
            return None
        receiver = func.value
        if not isinstance(receiver, ast.Call):
            return None
        if not isinstance(receiver.func, ast.Name):
            return None
        if receiver.func.id != "super":
            return None
        return func.attr

    @staticmethod
    def _is_ellipsis_expr(node: ast.AST) -> bool:
        return isinstance(node, ast.Constant) and node.value is Ellipsis

    @staticmethod
    def _is_empty_action_body(function_def: ast.FunctionDef) -> bool:
        """True when the body has no steps - only docstring, ``...``, ``pass``, and/or ``return``.

        Empty bodies auto-delegate to the same-named parent ``@action`` when one exists
        (implicit ``super().method()``). Explicit ``super()`` or any ``self.*`` step means
        the body is not empty and is expanded as written.
        """
        for statement in function_def.body:
            if isinstance(statement, (ast.Pass, ast.Return)):
                continue
            if isinstance(statement, ast.Expr):
                expr_value = statement.value
                if isinstance(expr_value, ast.Constant) and isinstance(expr_value.value, str):
                    continue
                if _ActionExpander._is_ellipsis_expr(expr_value):
                    continue
                return False
            return False
        return True

    @staticmethod
    def _result_template_from(function_def: ast.FunctionDef, expander: "_ActionExpander") -> str:
        for statement in function_def.body:
            if isinstance(statement, ast.Return):
                return expander._expression_text(statement.value, set())
        return ""

    @staticmethod
    def _resolve_super_func(
        instance: Any,
        method_name: str,
        *,
        after_class: type | None = None,
    ) -> "tuple[Callable[..., Any], type] | None":
        """Walk the MRO to find the next parent ``@action`` for *method_name*.

        When *after_class* is None, skip the instance's own definition (identity check).
        When *after_class* is set, skip until after that class, then take the next ``@action``.
        Returns ``(func, defining_class)`` or ``None``.
        """
        pair = _ActionExpander._own_class_func(instance, method_name)
        if pair is None:
            return None
        own_class, own_func = pair
        return _ActionExpander._find_parent_action(own_class, method_name, after_class, own_func)

    def __init__(self) -> None:
        self._reader = _SignatureReader.instance()
        self._validator = _ActionValidator.instance()

    @classmethod
    def instance(cls) -> _ActionExpander:
        return _get_or_create_singleton(cls)

    def parse_body(
        self,
        action_func: Callable[..., Any],
        instance: Any | None = None,
    ) -> _ActionBody:
        if instance is not None:
            return self._parse_body_resolved(action_func, instance)
        return self._parse_body_static(action_func)

    def _require_static_function_def(
        self, action_func: Callable[..., Any]
    ) -> ast.FunctionDef:
        """Parse *action_func* source and return its FunctionDef, or raise."""
        module = self._validator._parse_source(action_func)
        function_def = module.body[0]
        if not isinstance(function_def, ast.FunctionDef):
            raise ActionValidationError(
                "action body is not a function",
                class_name=action_func.__qualname__,
                action_name=action_func.__name__,
            )
        return function_def

    def _process_static_expr(
        self,
        statement: ast.Expr,
        steps: list[str],
        prose: list[str],
        seen_prose: set[str],
    ) -> None:
        """Process one Expr statement: collect tool step or prose text."""
        call_val = statement.value
        if isinstance(call_val, ast.Call):
            tool_name = self._validator._self_tool_name(call_val)
            if tool_name:
                steps.append(tool_name)
                return
            if self._super_call_name(call_val) is not None:
                return
        text = self._expression_text(call_val, set())
        if text and text not in seen_prose:
            prose.append(text)
            seen_prose.add(text)

    def _collect_call_tool(self, statement: ast.stmt, steps: list[str]) -> None:
        """Append the tool name from a bare Call statement when it is a self-member call."""
        tool_name = self._validator._self_tool_name(statement)  # type: ignore[arg-type]
        if tool_name:
            steps.append(tool_name)

    def _collect_static_prose(self, fdef: ast.FunctionDef) -> tuple[list[str], set[str]]:
        """Seed prose and seen-set from the function docstring."""
        prose: list[str] = []
        seen: set[str] = set()
        docstring = ast.get_docstring(fdef)
        if docstring:
            prose.append(docstring.strip())
            seen.add(docstring.strip())
        return prose, seen

    def _handle_static_stmt(
        self, stmt: ast.stmt, prose: list[str], seen: set[str], steps: list[str]
    ) -> str:
        """Dispatch a single statement; return a result-template if it is a Return."""
        if isinstance(stmt, ast.Return):
            return self._expression_text(stmt.value, set())
        if isinstance(stmt, ast.Expr):
            self._process_static_expr(stmt, steps, prose, seen)
        elif isinstance(stmt, ast.Call):
            self._collect_call_tool(stmt, steps)
        return ""

    def _walk_static_body(
        self, fdef: ast.FunctionDef, prose: list[str], seen: set[str], steps: list[str]
    ) -> str:
        """Walk statement list and return the result-template string (may be empty)."""
        result_template = ""
        for stmt in fdef.body:
            found = self._handle_static_stmt(stmt, prose, seen, steps)
            if found:
                result_template = found
        return result_template

    def _parse_body_static(self, action_func: Callable[..., Any]) -> _ActionBody:
        fdef = self._require_static_function_def(action_func)
        prose, seen = self._collect_static_prose(fdef)
        steps: list[str] = []
        result_template = self._walk_static_body(fdef, prose, seen, steps) or f"Instructions for {action_func.__name__}"
        return _ActionBody(prose_parts=tuple(prose), tool_steps=tuple(steps), result_template=result_template)

    def _resolve_parent_result_template(
        self, action_func: Callable[..., Any], instance: Any
    ) -> str:
        """Return the result template from the parent @action for empty-body delegation."""
        resolved = self._resolve_super_func(instance, action_func.__name__)
        if resolved is None:
            return ""
        parent_func, _ = resolved
        parent_module = self._validator._parse_source(parent_func)
        parent_fdef = parent_module.body[0]
        if isinstance(parent_fdef, ast.FunctionDef):
            return self._result_template_from(parent_fdef, self)
        return ""

    def _parse_body_resolved(self, action_func: Callable[..., Any], instance: Any) -> _ActionBody:
        module = self._validator._parse_source(action_func)
        function_def = module.body[0]
        if not isinstance(function_def, ast.FunctionDef):
            return self._parse_body_static(action_func)
        prose, tool_steps = self._walk_body(instance, function_def, current_action=action_func.__name__)
        prose = self._inject_focus(action_func, instance, prose)
        result_template = self._result_template_from(function_def, self)
        if not result_template and self._is_empty_action_body(function_def):
            result_template = self._resolve_parent_result_template(action_func, instance)
        if not result_template:
            result_template = f"Instructions for {action_func.__name__}"
        return _ActionBody(
            prose_parts=tuple(prose),
            tool_steps=tuple(tool_steps),
            result_template=result_template,
        )

    def _focus_file_path(
        self, module_dir: Path, focus_group: str, filter_value: str
    ) -> "Path | None":
        """Resolve the flat focus file path; return None when absent or overridden by a dir."""
        if (module_dir / focus_group / filter_value).is_dir():
            return None
        candidate = module_dir / focus_group / f"{filter_value}.md"
        return candidate if candidate.is_file() else None

    def _load_focus_text(self, focus_path: Path) -> str:
        """Load the raw UTF-8 text of a focus file (I/O only)."""
        return focus_path.read_text(encoding="utf-8")

    def _read_focus_file(self, focus_path: Path) -> str | None:
        """Return stripped focus content, or None when the file is empty."""
        return self._load_focus_text(focus_path).strip() or None

    def _append_focus_content(
        self, module_dir: Path, focus_entries: list[tuple[str, str]], instance: Any,
        result: list[str], seen: set[str],
    ) -> None:
        """Append content from each flat focus file not already in *seen*."""
        for focus_group, filter_key in focus_entries:
            filter_value = getattr(instance, filter_key, None)
            if not filter_value:
                continue
            focus_path = self._focus_file_path(module_dir, focus_group, filter_value)
            if focus_path is None:
                continue
            content = self._read_focus_file(focus_path)
            if content and content not in seen:
                result.append(content)
                seen.add(content)

    def _inject_focus(
        self, action_func: Callable[..., Any], instance: Any, prose: list[str]
    ) -> list[str]:
        """Append focus-group file content to prose when @focus is on the action."""
        focus_entries = _mro_action_focus_entries(type(instance), action_func.__name__, action_func)
        if not focus_entries:
            return prose
        module_dir = Path(inspect.getfile(type(instance))).parent
        result = list(prose)
        self._append_focus_content(module_dir, focus_entries, instance, result, set(prose))
        return result

    def _build_body_slots(self, toolset_cls: type) -> _BodySlots:
        """Build the four allowed-member sets for a toolset class."""
        return _BodySlots(
            instruction_slots=instruction_slot_names(toolset_cls),
            action_slots=_action_slot_names(toolset_cls),
            tool_names=self._validator._tool_names(toolset_cls),
            resource_names=self._validator._resource_names(toolset_cls),
        )

    def _parse_parent_fdef(self, parent_func: Callable[..., Any]) -> "ast.FunctionDef | None":
        """Parse parent_func source and return its FunctionDef, or None."""
        parent_module = self._validator._parse_source(parent_func)
        parent_fdef = parent_module.body[0]
        return parent_fdef if isinstance(parent_fdef, ast.FunctionDef) else None

    def _add_docstring_prose(
        self, function_def: ast.FunctionDef, ctx: _WalkContext, acc: _ProseAccumulator
    ) -> None:
        """Expand and add the action docstring to *acc*."""
        docstring = ast.get_docstring(function_def)
        action_func = getattr(type(ctx.instance), ctx.current_action)
        doc_text = docstring.strip() if docstring and docstring.strip() else ctx.current_action
        acc.add_text(_expand_docstring(doc_text, action_func, instance=ctx.instance))

    def _walk_nested_action(
        self, action_name: str, instance: Any, visited: "frozenset[tuple[str, str]]",
        acc: _ProseAccumulator,
    ) -> None:
        """Expand action_name on instance and merge results into acc."""
        action_func = getattr(type(instance), action_name)
        module = self._validator._parse_source(action_func)
        function_def = module.body[0]
        if not isinstance(function_def, ast.FunctionDef):
            return
        nested_prose, nested_tools = self._walk_body(instance, function_def, current_action=action_name, visited=visited)
        acc.merge(nested_prose, nested_tools)

    def _describe_resource(self, member: str, instance: Any, acc: _ProseAccumulator) -> None:
        """Inline a @resource value and its docstring into acc."""
        resource_value = getattr(instance, member)
        prop = getattr(type(instance), member, None)
        getter = prop.fget if isinstance(prop, property) else None
        doc = _expand_docstring((getter.__doc__ or "").strip(), getter, instance=instance) if getter else ""
        text = f"Resource `{member}` = {resource_value!r}."
        acc.add_text(text + '\n\n' + doc if doc else text)

    def _expand_action_call(
        self, member: str, target_instance: Any, visited: "frozenset[tuple[str, str]]",
        acc: _ProseAccumulator,
    ) -> None:
        """Expand an action call (self or cross-instance) into acc, unless mode=tool.

        ``mode`` lives on the *callee* (``target_instance``), not the caller, so
        it governs every call to that instance's actions — self calls included.
        mode=tool lists the action as a deferred tool step so the agent invokes
        it as its own step later; inner tools stay inside that deferred expansion.
        """
        if getattr(target_instance, "mode", "action") == "tool":
            acc.tool_steps.append(member)
            return
        self._walk_nested_action(member, target_instance, visited, acc)

    def _walk_for_each_body(
        self, stmt: ast.For, var_name: str, target_item: Any,
        visited: "frozenset[tuple[str, str]]", acc: _ProseAccumulator,
    ) -> None:
        """Dispatch each member call on target_item found inside the for-each body."""
        target_cls = type(target_item)
        target_actions = _action_slot_names(target_cls)
        target_tools = self._validator._tool_names(target_cls)
        for body_stmt in stmt.body:
            if not isinstance(body_stmt, ast.Expr):
                continue
            member_attr = self._member_call_attr(body_stmt.value, var_name)
            if member_attr is None:
                continue
            if member_attr in target_actions:
                self._walk_nested_action(member_attr, target_item, visited, acc)
            elif member_attr in target_tools:
                acc.tool_steps.append(member_attr)

    def _walk_for_each_statement(self, stmt: ast.For, ctx: _WalkContext, acc: _ProseAccumulator) -> None:
        """Expand: ``for <var> in self.<provider>(): <var>.<action>()``."""
        iter_node, loop_var = stmt.iter, stmt.target
        if not (isinstance(loop_var, ast.Name) and isinstance(iter_node, ast.Call)):
            return
        iter_member = _self_member_name(iter_node)
        if iter_member is None:
            return
        items = getattr(ctx.instance, iter_member)()
        for target_item in items:
            self._walk_for_each_body(stmt, loop_var.id, target_item, ctx.visited, acc)

    @staticmethod
    def _is_sub_agent_tool(toolset_cls: type, member: str) -> bool:
        """True when member is a @sub_agent tool (``_is_tool`` is suppressed)."""
        func = getattr(toolset_cls, member, None)
        return callable(func) and getattr(func, "_is_sub_agent", False)

    @staticmethod
    def _resolve_provider(instance: Any, provider_name: str) -> Any:
        """Resolve ``self.<provider_name>`` to the companion instance it refers to.

        A provider reference just gets you to the instance that owns the tool
        or action being called next (the outer call in the source) — it is
        not itself the call boundary. It may be spelled either way:
        a zero-arg method (``self.workspace()``) or a property/plain
        attribute that already holds the built instance (``self.workspace``).
        """
        raw = getattr(instance, provider_name)
        if getattr(type(raw), "_is_toolset", False):
            return raw
        return raw() if callable(raw) else raw

    def _walk_cross_instance_statement(
        self, expr_node: ast.AST, ctx: _WalkContext, acc: _ProseAccumulator
    ) -> bool:
        """Handle cross-instance action/tool calls; return True when handled.

        Actions expand inline (unless target ``mode == "tool"``). Tools and
        ``@sub_agent`` tools are listed as tool steps — their instructions stay
        on the tool, not inlined into the caller's markdown.
        """
        cross = _cross_instance_call(expr_node)
        if not cross:
            return False
        provider_name, member = cross
        target_instance = self._resolve_provider(ctx.instance, provider_name)
        target_cls = type(target_instance)
        if member in _action_slot_names(target_cls):
            self._expand_action_call(member, target_instance, ctx.visited, acc)
        elif member in self._validator._tool_names(target_cls) or self._is_sub_agent_tool(
            target_cls, member
        ):
            acc.tool_steps.append(member)
        return True

    def _walk_self_member_statement(self, member: str, ctx: _WalkContext, acc: _ProseAccumulator) -> None:
        """Handle ``self.<member>`` references: actions, instructions, tools, and resources."""
        if member in ctx.slots.action_slots:
            if member != ctx.current_action:
                self._expand_action_call(member, ctx.instance, ctx.visited, acc)
            return
        if member in ctx.slots.instruction_slots:
            acc.add_text(_inline(ctx.instance, member))
            return
        if member in ctx.slots.tool_names:
            acc.tool_steps.append(member)
            return
        if member in ctx.slots.resource_names:
            self._describe_resource(member, ctx.instance, acc)

    def _walk_super_statement(self, ctx: _WalkContext, acc: _ProseAccumulator) -> None:
        """Handle ``super().method()`` calls by inlining the parent action's body."""
        resolved = self._resolve_super_func(ctx.instance, ctx.current_action, after_class=ctx.defining_class)
        if resolved is None:
            return
        parent_func, parent_cls = resolved
        parent_fdef = self._parse_parent_fdef(parent_func)
        if parent_fdef is None:
            return
        nested_prose, nested_tools = self._walk_body(
            ctx.instance, parent_fdef, current_action=ctx.current_action,
            visited=ctx.visited, defining_class=parent_cls,
        )
        acc.merge(nested_prose, nested_tools)

    def _dispatch_statement(self, statement: "ast.stmt", ctx: _WalkContext, acc: _ProseAccumulator) -> None:
        """Route one non-skip statement to the appropriate walk handler."""
        if isinstance(statement, ast.For):
            self._walk_for_each_statement(statement, ctx, acc)
            return
        expr_node = statement.value if isinstance(statement, ast.Expr) else statement
        if self._walk_cross_instance_statement(expr_node, ctx, acc):
            return
        member = _self_member_name(expr_node)
        if member:
            self._walk_self_member_statement(member, ctx, acc)
            return
        if self._super_call_name(expr_node) is not None:
            self._walk_super_statement(ctx, acc)
            return
        if isinstance(statement, ast.Expr):
            acc.add_text(self._expression_text(statement.value, set()))

    def _walk_statements(self, function_def: ast.FunctionDef, ctx: _WalkContext, acc: _ProseAccumulator) -> None:
        """Iterate function_def.body and dispatch each statement."""
        skipped_docstring = False
        for statement in function_def.body:
            if isinstance(statement, ast.Return):
                continue
            if isinstance(statement, ast.Expr) and self._is_ellipsis_expr(statement.value):
                continue
            if self._is_leading_docstring(statement, skipped_docstring):
                skipped_docstring = True
                continue
            self._dispatch_statement(statement, ctx, acc)

    def _walk_body(
        self, instance: Any, function_def: ast.FunctionDef, *,
        current_action: str, visited: "frozenset[tuple[str, str]] | None" = None,
        defining_class: "type | None" = None,
    ) -> "tuple[list[str], list[str]]":
        new_visited = self._check_and_advance_visited(instance, current_action, defining_class, visited or frozenset())
        ctx = _WalkContext(
            instance=instance, current_action=current_action, visited=new_visited,
            defining_class=defining_class, slots=self._build_body_slots(type(instance)),
        )
        acc = _ProseAccumulator()
        self._add_docstring_prose(function_def, ctx, acc)
        if self._is_empty_action_body(function_def):
            self._walk_super_statement(ctx, acc)
        else:
            self._walk_statements(function_def, ctx, acc)
        return acc.prose, acc.tool_steps

    def _make_build_request(
        self, body: _ActionBody, request: _ActionExpandRequest, parameter_names: set[str]
    ) -> _InstructionBuildRequest:
        """Assemble an _InstructionBuildRequest from an expand request and parsed body."""
        return _InstructionBuildRequest(
            body=body, toolset_path=request.toolset_path, context=request.context,
            arguments=request.arguments, parameter_names=parameter_names,
            tool_callables=request.tool_callables, instance=request.instance,
        )

    def _build_expansion_result(
        self, body: _ActionBody, request: _ActionExpandRequest, parameter_names: set[str]
    ) -> ActionExpansion:
        """Build the final expansion dict from a parsed body and request."""
        result = self._substitute(
            body.result_template, request.arguments, parameter_names, instance=request.instance
        )
        instructions = self._build_instructions(self._make_build_request(body, request, parameter_names))
        return {"result": result, "instructions": instructions, "tools": list(dict.fromkeys(body.tool_steps))}

    def expand(self, request: _ActionExpandRequest) -> ActionExpansion:
        body = self.parse_body(request.action_func, request.instance)
        self._log_expansion(request, body.tool_steps)
        parameter_names = set(self._reader.simple_parameters(request.action_func))
        return self._build_expansion_result(body, request, parameter_names)

    def _should_log_expansion(self, request: _ActionExpandRequest) -> bool:
        """Return True when the expansion should be recorded in the session log."""
        from sessions import is_logged, member_is_logged

        action_name = request.action_func.__name__
        if request.instance is not None:
            return member_is_logged(type(request.instance), action_name)
        return is_logged(request.action_func)

    def _build_expansion_log_payload(
        self, request: _ActionExpandRequest, tool_steps: tuple[str, ...]
    ) -> dict[str, Any]:
        """Build the session-log payload dict for one action expansion."""
        action_name = request.action_func.__name__
        return {
            "request": {
                "action": action_name, "arguments": request.arguments,
                "context": request.context, "tools": list(tool_steps),
            },
            "response": {"expanded": True},
        }

    def _log_expansion(self, request: _ActionExpandRequest, tool_steps: tuple[str, ...]) -> None:
        if not self._should_log_expansion(request):
            return
        from sessions import SessionLog, summarize_mapping
        action_name = request.action_func.__name__
        SessionLog.instance().append(
            kind="expansion", toolset=request.toolset_path, name=action_name,
            summary=summarize_mapping({"tools": ",".join(tool_steps)}), ok=True,
            payload=self._build_expansion_log_payload(request, tool_steps),
        )

    def _build_yaml_block(self, toolset_path: Any, context: dict[str, Any]) -> list[str]:
        """Return the YAML fence block lines for a tools-run invocation."""
        lines = [
            "Every tool call uses this shape - set `tool` and `arguments`, pipe to CLI:",
            "", "```yaml", f"toolset: {toolset_path}", "context:",
        ]
        for key, context_value in context.items():
            lines.append(f"  {key}: {context_value}")
        lines += ["tool: <tool name>", "arguments:", "  <if needed>", "```", ""]
        return lines

    def _build_tool_hint_lines(
        self, body: _ActionBody, tool_callables: dict[str, Callable[..., Any]]
    ) -> list[str]:
        """Return the numbered tool-step hint lines for suggested flow."""
        lines = ["Suggested flow (repeat and reorder as the story needs):", ""]
        for index, tool_name in enumerate(body.tool_steps, start=1):
            lines.append(f"{index}. tool: {tool_name}")
            hint = self._argument_hint(tool_callables.get(tool_name))
            if hint:
                lines.append("   arguments:")
                lines.append(f"     {hint}")
            lines.append("")
        return lines

    def _build_instructions(self, build_request: _InstructionBuildRequest) -> str:
        body = build_request.body
        arguments, parameter_names, instance = (
            build_request.arguments, build_request.parameter_names, build_request.instance
        )
        lines: list[str] = []
        for part in body.prose_parts:
            lines.append(self._substitute(part, arguments, parameter_names, instance=instance))
            lines.append("")
        lines.extend(self._build_yaml_block(build_request.toolset_path, build_request.context))
        lines.append("Run: python -m tools run -")
        lines.append("")
        lines.extend(self._build_tool_hint_lines(body, build_request.tool_callables))
        lines.append("Read `resources` from each response before choosing the next tool.")
        return "\n".join(lines).strip()

    def _argument_hint(self, tool_func: Callable[..., Any] | None) -> str | None:
        if tool_func is None:
            return None
        parameters = self._reader.simple_parameters(tool_func)
        if not parameters:
            return None
        hints = [f"{name}: <value>" for name in parameters]
        return "\n     ".join(hints)

    def _replace_self_attrs(self, template: str, instance: Any | None) -> str:
        """Expand {{self.attr}} placeholders from *instance* attributes."""
        def replace_self(match: re.Match[str]) -> str:
            attr = match.group(1)
            placeholder = "{{self." + attr + "}}"
            if instance is None or not hasattr(instance, attr):
                raise ValueError(
                    f"missing instance attribute {attr!r} for placeholder {placeholder}"
                )
            return str(getattr(instance, attr))

        return _SELF_PLACEHOLDER.sub(replace_self, template)

    def _replace_params(
        self,
        template: str,
        arguments: dict[str, Any],
        parameter_names: set[str],
    ) -> str:
        """Expand {{param}} placeholders from declared *arguments*; leave unknown tokens as-is."""
        def replace_param(match: re.Match[str]) -> str:
            name = match.group(1)
            if name not in parameter_names:
                # Not a declared parameter - embedded template content, leave untouched.
                return match.group(0)
            if name not in arguments:
                raise ValueError(
                    f"missing argument {name!r} for placeholder {{{{{name}}}}}"
                )
            return str(arguments[name])

        return _PARAM_PLACEHOLDER.sub(replace_param, template)

    def _substitute(
        self,
        template: str,
        arguments: dict[str, Any],
        parameter_names: set[str],
        *,
        instance: Any | None = None,
    ) -> str:
        """Expand {{param}} from arguments and {{self.attr}} from instance.

        Only substitutes {{name}} when ``name`` is a declared parameter.
        Unknown {{tokens}} that appear inside embedded template content are
        left as-is rather than raising - they are not action parameters.
        Raises only when a declared parameter has no matching argument value.
        """
        rendered = self._replace_self_attrs(template, instance)
        rendered = self._replace_params(rendered, arguments, parameter_names)
        return rendered

    def _expression_text(self, node: ast.expr | None, _parameters: set[str]) -> str:
        if node is None:
            return ""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value.strip()
        if isinstance(node, ast.JoinedStr):
            return self._joined_string(node)
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == "self":
                return "{{self." + node.attr + "}}"
        if isinstance(node, ast.Name):
            return "{{" + node.id + "}}"
        return ast.unparse(node)

    def _joined_string(self, node: ast.JoinedStr) -> str:
        parts: list[str] = []
        for str_value in node.values:
            if isinstance(str_value, ast.Constant) and isinstance(str_value.value, str):
                parts.append(str_value.value)
            elif isinstance(str_value, ast.FormattedValue):
                parts.append(self._expression_text(str_value.value, set()))
        return "".join(parts)


def action(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a method as an agent orchestration recipe; body is expanded, never executed."""
    func._is_action = True
    return func


def _build_merged_agentic_class(cls: type) -> type:
    """Create the merged AgenticToolset subclass, set metadata attributes, and return it."""
    merged = type(
        cls.__name__,
        (cls, AgenticToolset),
        {
            k: attr_value
            for k, attr_value in vars(cls).items()
            if k not in ("__dict__", "__weakref__")
        },
    )
    merged.__doc__ = cls.__doc__
    merged.__module__ = cls.__module__
    merged.__qualname__ = cls.__qualname__
    merged._is_toolset = True  # type: ignore[attr-defined]
    return merged


def agentic_toolset(cls: type) -> type:
    """Mark an action-bearing class as agentic; merges AgenticToolset (adds mode resource).

    @toolset stays ignorant of actions and is unchanged.
    """
    if getattr(cls, "_is_toolset", False):
        return cls
    if issubclass(cls, Toolset):
        raise TypeError(
            f"{cls.__name__} must use @agentic_toolset or @toolset — "
            "do not subclass Toolset or AgenticToolset directly"
        )
    merged = _build_merged_agentic_class(cls)
    from sessions import inherit_annotations_from_bases
    from tools.extensions import ToolsetExtensions

    inherit_annotations_from_bases(merged)
    ToolsetExtensions.instance().validate_toolset(merged)
    return merged


@dataclass(frozen=True)
class Action:
    """One orchestration recipe on a toolset - expanded into instructions, never executed."""

    name: str
    callable: Callable[..., Any]
    owner: type | None = None

    @property
    def instructions(self) -> str:
        return _SignatureReader.instance().member_instructions(self.callable)

    def _build_focus_entry(self) -> list[dict[str, str]]:
        """Build the manifest focus list from this action's focus entries."""
        focus_entries = _mro_action_focus_entries(self.owner, self.name, self.callable)
        return [{"group": focus_group, "filter_key": filter_key} for focus_group, filter_key in focus_entries]

    def _build_signature_extras(self) -> "SignatureEntry":
        """Build the optional fields (focus, instructions, parameters, returns) for the signature."""
        reader = _SignatureReader.instance()
        extras: SignatureEntry = {}
        focus = self._build_focus_entry()
        if focus:
            extras["focus"] = focus
        if self.instructions:
            extras["instructions"] = self.instructions
        parameters = reader.simple_parameters(self.callable)
        if parameters:
            extras["parameters"] = parameters
        returns = reader.simple_return_type(self.callable)
        if returns:
            extras["returns"] = returns
        return extras

    @property
    def signature_entry(self) -> SignatureEntry:
        body = _ActionExpander.instance().parse_body(self.callable)
        entry: SignatureEntry = {"kind": "action", "tools": list(dict.fromkeys(body.tool_steps))}
        entry.update(self._build_signature_extras())
        return entry

    def add_to_signature(self, signature: ManifestDocument) -> None:
        signature[self.name] = self.signature_entry


def _focus_entries_from_func(func: Callable[..., Any]) -> list[tuple[str, str]]:
    """Return the ``_focus_entries`` list from a single callable (no MRO walk)."""
    target = getattr(func, "__func__", func)
    return list(getattr(target, "_focus_entries", []) or [])


def _class_dict_entry(klass: type, name: str) -> "Any":
    """Return the raw entry for *name* in *klass*'s __dict__, or None."""
    return klass.__dict__.get(name)


def _raw_mro_class_funcs(owner: type, name: str) -> "list[tuple[type, Any]]":
    """Gather ``(class, raw_entry)`` pairs from the MRO where *name* exists in __dict__."""
    return [(klass, _class_dict_entry(klass, name)) for klass in owner.__mro__ if name in klass.__dict__]


def _mro_action_funcs(owner: type, name: str) -> "list[Callable[..., Any]]":
    """Return each ``@action`` callable found in *owner*'s MRO for *name*."""
    funcs: list[Callable[..., Any]] = []
    for _klass, func in _raw_mro_class_funcs(owner, name):
        if not callable(func):
            continue
        target = getattr(func, "__func__", func)
        if getattr(target, "_is_action", False):
            funcs.append(func)
    return funcs


def _collect_mro_focus_entries(owner: type, name: str) -> list[tuple[str, str]]:
    """Collect unique ``_focus_entries`` for @action *name* across *owner*'s MRO."""
    entries: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for func in _mro_action_funcs(owner, name):
        for entry in _focus_entries_from_func(func):
            if entry not in seen:
                entries.append(entry)
                seen.add(entry)
    return entries


def _mro_action_focus_entries(
    owner: type | None,
    name: str,
    action_func: Callable[..., Any],
) -> list[tuple[str, str]]:
    """Collect ``_focus_entries`` from the action and its base definitions (MRO)."""
    if owner is None:
        return _focus_entries_from_func(action_func)
    return _collect_mro_focus_entries(owner, name)


def _discover_actions(instance: "Toolset") -> "dict[str, Action]":
    discovered: dict[str, Action] = {}
    owner = type(instance)
    for name, member in inspect.getmembers(owner, predicate=inspect.isfunction):
        if getattr(member, "_is_action", False):
            discovered[name] = Action(
                name=name,
                callable=getattr(instance, name),
                owner=owner,
            )
    return discovered


def _has_actions(instance: "Toolset") -> bool:
    return bool(_discover_actions(instance))


class _ActionRunner:
    """Invokes one action from a parsed run request."""

    _instance: _ActionRunner | None = None

    def __init__(self) -> None:
        from tools.tool import _ManifestYaml
        self._expander = _ActionExpander.instance()
        self._yaml = _ManifestYaml.instance()

    @classmethod
    def instance(cls) -> _ActionRunner:
        return _get_or_create_singleton(cls)

    def validate_toolset(self, toolset_cls: type) -> None:
        _ActionValidator.instance().validate_class(toolset_cls)

    def _expand_action(
        self,
        action_entry: "Action",
        request: _ActionRunRequest,
    ) -> dict[str, Any]:
        """Call the expander for *action_entry* and return the expanded dict."""
        return self._expander.expand(
            _ActionExpandRequest(
                action_func=action_entry.callable,
                toolset_path=str(request.toolset_path),
                context=request.context,
                arguments=request.arguments,
                tool_callables={
                    name: tool.callable for name, tool in request.instance.tools.items()
                },
                instance=request.instance,
            )
        )

    def _try_expand_action(
        self, action_entry: "Action", request: _ActionRunRequest
    ) -> dict[str, Any]:
        """Expand *action_entry* and translate any exception into a RunError."""
        from tools.tool import RunError
        try:
            return self._expand_action(action_entry, request)
        except Exception as exc:
            raise RunError(
                str(exc),
                response={"ok": False, "action": str(request.action_name), "error": str(exc)},
            ) from exc

    def invoke_action(self, request: _ActionRunRequest) -> RunResponseDocument:
        from tools.tool import RunError
        action_name = str(request.action_name)
        if action_name not in request.instance.actions:
            raise RunError(
                f"unknown action {action_name!r}",
                response={"ok": False, "action": action_name, "error": "unknown action"},
            )
        expanded = self._try_expand_action(request.instance.actions[action_name], request)
        return self._build_response(request.request, _RunOutput(
            toolset_path=request.toolset_path, action_name=request.action_name,
            arguments=request.arguments, instance=request.instance, expanded=expanded,
        ))

    def _build_response(
        self,
        request: dict[str, Any],
        output: _RunOutput,
    ) -> dict[str, Any]:
        from tools.tool import _ManifestYaml
        response: dict[str, Any] = {
            "ok": True,
            "toolset": str(output.toolset_path),
            "action": str(output.action_name),
            "result": output.expanded["result"],
            "instructions": output.expanded["instructions"],
            "arguments": _ManifestYaml.instance().serialize_value(output.arguments),
            "tools": output.expanded["tools"],
        }
        if request.get("include_resources", True):
            response["resources"] = _ManifestYaml.instance().serialize_value(output.instance.resources)
        return response


