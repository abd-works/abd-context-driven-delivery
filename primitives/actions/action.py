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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, TypeAlias

_PARAM_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")
_SELF_PLACEHOLDER = re.compile(r"\{\{self\.(\w+)\}\}")

# Sentinel for wrapper static_kwargs: resolve to the concrete toolset owner's module dir
# at manifest time (e.g. @sketch on Context.sketch -> context_tools/bdd when owner is Bdd).
OWNER_MODULE_DIR = "@owner"

from tools.types import (
    ManifestDocument,
    RunRequestDocument,
    RunResponseDocument,
    SignatureEntry,
)

ContextDocument: TypeAlias = dict[str, Any]
ArgumentDocument: TypeAlias = dict[str, Any]
ActionExpansion: TypeAlias = dict[str, Any]

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


from primitives.instructions import (
    _expand_docstring,
    _inline,
    instruction_slot_names,
)
from tools.tool import _SignatureReader


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
        self.class_name = class_name
        self.action_name = action_name
        self.lineno = lineno


@dataclass(frozen=True)
class _ActionBody:
    prose_parts: tuple[str, ...]
    tool_steps: tuple[str, ...]
    result_template: str


def _action_slot_names(toolset_cls: type) -> frozenset[str]:
    names: set[str] = set()
    for name, member in inspect.getmembers(toolset_cls, predicate=inspect.isfunction):
        if getattr(member, "_is_action", False):
            names.add(name)
    return frozenset(names)


@dataclass(frozen=True)
class _WrapperSpec:
    """One wrapping decorator's contribution to a chained action.

    ``chained_action`` is a real ``@action``-marked callable whose body
    the framework expands and prepends to the base action at expansion time.
    No preamble strings - the chained action *is* the instruction.

    ``static_kwargs`` are fixed parameters the decorator supplies to the
    chained action (e.g. ``agent_dir`` for ``@sketch``). They are surfaced
    in the manifest chain entry so the AI knows what to pass.
    """

    name: str
    chained_action: "Callable[..., Any]"
    static_kwargs: dict = field(default_factory=dict)


def _own_action_wrapper_specs(action_func: Callable[..., Any]) -> tuple[_WrapperSpec, ...]:
    """Return wrapper specs registered directly on this callable (no MRO)."""
    target = getattr(action_func, "__func__", action_func)
    specs = getattr(target, "_action_wrapper_specs", None) or ()
    return tuple(specs)


def _mro_action_wrapper_specs(owner: type, name: str) -> tuple[_WrapperSpec, ...]:
    """Resolve action wrappers across ``owner``'s MRO for method ``name``.

    The most-derived ``@action`` keeps its own wrappers. Wrapper names declared on
    base definitions of the same method and missing from the child are prepended
    so base annotations stay outer - overrides inherit action annotations automatically.
    """
    defining: Callable[..., Any] | None = None
    for klass in owner.__mro__:
        func = klass.__dict__.get(name)
        if func is None or not callable(func):
            continue
        target = getattr(func, "__func__", func)
        if getattr(target, "_is_action", False):
            defining = target
            break
    if defining is None:
        return ()

    result = list(_own_action_wrapper_specs(defining))
    seen = {spec.name for spec in result}
    past_defining = False
    for klass in owner.__mro__:
        func = klass.__dict__.get(name)
        if func is None or not callable(func):
            continue
        target = getattr(func, "__func__", func)
        if not past_defining:
            if target is defining:
                past_defining = True
            continue
        if target is defining:
            continue
        if not getattr(target, "_is_action", False):
            continue
        inherited: list[_WrapperSpec] = []
        for spec in _own_action_wrapper_specs(target):
            if spec.name not in seen:
                inherited.append(spec)
                seen.add(spec.name)
        if inherited:
            result = inherited + result
    return tuple(result)


def _action_wrapper_specs(
    action_func: Callable[..., Any],
    *,
    owner: type | None = None,
    name: str | None = None,
) -> tuple[_WrapperSpec, ...]:
    """Return wrapper specs for an action, in execution order (top-down).

    When ``owner`` is provided, include wrappers inherited from base ``@action``
    definitions of the same method. Without ``owner``, return only specs on
    ``action_func`` itself.
    """
    if owner is not None:
        method_name = name or getattr(action_func, "__name__", None)
        if method_name:
            return _mro_action_wrapper_specs(owner, method_name)
    return _own_action_wrapper_specs(action_func)


def _action_wrapper_names(
    action_func: Callable[..., Any],
    *,
    owner: type | None = None,
    name: str | None = None,
) -> tuple[str, ...]:
    """Return names of wrapping decorators for an action, in execution order."""
    return tuple(spec.name for spec in _action_wrapper_specs(action_func, owner=owner, name=name))


def require_action(func: Callable[..., Any], decorator_name: str) -> None:
    """Guard: ensure a chainable-action decorator's target is already ``@action``-marked.

    Chainable decorators (``@sketch``, ``@grill_with_context``, ...) must be applied on top
    of ``@action``. This helper centralises the guard so each decorator raises a consistent
    TypeError instead of duplicating the check.
    """
    if not getattr(func, "_is_action", False):
        raise TypeError(
            f"@{decorator_name} must decorate an @action method; got {func.__name__!r} "
            f"which is not marked as an action. Apply @action first, then @{decorator_name}."
        )


def add_action_wrapper(
    func: Callable[..., Any],
    name: str,
    chained_action: "Callable[..., Any]",
    static_kwargs: dict | None = None,
) -> None:
    """Register a wrapping decorator on an ``@action`` method.

    ``chained_action`` is a real ``@action``-marked callable. At expansion
    time, ``_ActionExpander`` calls ``_parse_body_static(chained_action)`` and
    prepends the resulting prose to the base action's expanded body - no
    preamble strings, no builders, no slots. The chained action's own
    instructions *are* the wrapper's contribution.

    Prepends to ``_action_wrapper_specs`` and rebuilds ``_action_wrappers``
    from it. Prepending matches Python's inner-first decoration order so a
    top-declared decorator ends up first in the spec list - declaration order
    equals execution order.
    """
    spec = _WrapperSpec(name=name, chained_action=chained_action, static_kwargs=static_kwargs or {})
    specs = list(getattr(func, "_action_wrapper_specs", None) or [])
    specs.insert(0, spec)
    func._action_wrapper_specs = specs  # type: ignore[attr-defined]
    func._action_wrappers = [s.name for s in specs]  # type: ignore[attr-defined]


def _resolve_wrapper_static_kwargs(
    static_kwargs: dict,
    owner: type | None,
) -> dict:
    """Resolve sentinel values in wrapper static_kwargs for manifest chain exposure."""
    if not static_kwargs:
        return {}
    resolved = dict(static_kwargs)
    if resolved.get("agent_dir") == OWNER_MODULE_DIR:
        if owner is None:
            resolved.pop("agent_dir", None)
        else:
            try:
                resolved["agent_dir"] = str(Path(inspect.getfile(owner)).resolve().parent)
            except (TypeError, OSError):
                resolved.pop("agent_dir", None)
    return resolved


def _owner_class_for_action(action_func: Callable[..., Any]) -> type | None:
    """Return the class that defines ``action_func``, or None if unknown."""
    qualname = getattr(action_func, "__qualname__", "") or ""
    if "." not in qualname:
        return None
    class_name = qualname.rsplit(".", 1)[0].split(".")[-1]
    module = inspect.getmodule(action_func)
    if module is None:
        return None
    owner = getattr(module, class_name, None)
    if owner is None or not isinstance(owner, type):
        return None
    return owner


def _instance_for_action(action_func: Callable[..., Any]) -> Any | None:
    """Best-effort construct the toolset that owns ``action_func`` for nested expansion.

    Used when expanding a chained wrapper action so in-method calls
    (e.g. ``self._grill_context().grill_with_context(...)``) resolve.
    """
    owner = _owner_class_for_action(action_func)
    if owner is None:
        return None
    try:
        return owner()
    except TypeError:
        return None


def _wrapper_expand_instance(
    chained_action: Callable[..., Any],
    host: Any | None,
) -> Any | None:
    """Instance used to expand a chained wrapper action.

    Prefer the host when it already merges the chained action's owning kit
    (``isinstance(host, Owner)``) so resources like ``active`` reflect the
    live run. Otherwise construct a fresh owner instance (engagement engines).
    """
    owner = _owner_class_for_action(chained_action)
    if host is not None and owner is not None and isinstance(host, owner):
        return host
    return _instance_for_action(chained_action)


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
    if not isinstance(node, ast.Call):
        return None
    if not isinstance(node.func, ast.Attribute):
        return None
    member = node.func.attr
    provider_call = node.func.value
    if not isinstance(provider_call, ast.Call):
        return None
    if not isinstance(provider_call.func, ast.Attribute):
        return None
    if not isinstance(provider_call.func.value, ast.Name) or provider_call.func.value.id != "self":
        return None
    return provider_call.func.attr, member


def _visit_key(instance: Any, action_name: str, defining_class: type | None = None) -> tuple[str, str]:
    cls = defining_class if defining_class is not None else type(instance)
    return cls.__qualname__, action_name


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


def _is_ellipsis_expr(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value is Ellipsis


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
            value = statement.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                continue
            if _is_ellipsis_expr(value):
                continue
            return False
        return False
    return True


def _result_template_from(function_def: ast.FunctionDef, expander: "_ActionExpander") -> str:
    for statement in function_def.body:
        if isinstance(statement, ast.Return):
            return expander._expression_text(statement.value, set())
    return ""


def _resolve_super_func(
    instance: Any,
    method_name: str,
    *,
    after_class: type | None = None,
) -> "tuple[Callable[..., Any], type] | None":
    """Walk the MRO to find the next parent ``@action`` for *method_name*.

    When *after_class* is None, skip the instance's own definition (identity check -
    subclasses may override the same function; look up the concrete host type first
    more than one MRO entry). When *after_class* is set (nested ``super()`` / empty-body
    walk), skip until after that class, then take the next ``@action``.
    Returns ``(func, defining_class)`` or ``None``.
    """
    own_class = type(instance)
    own_func = own_class.__dict__.get(method_name)
    if own_func is None:
        return None
    past_anchor = after_class is None
    for klass in own_class.__mro__:
        if not past_anchor:
            if klass is after_class:
                past_anchor = True
            continue
        if method_name not in klass.__dict__:
            continue
        func = klass.__dict__[method_name]
        if after_class is None and func is own_func:
            continue
        if callable(func) and getattr(func, "_is_action", False):
            return func, klass
    return None


def _cross_instance_providers(body: ast.Module) -> set[str]:
    providers: set[str] = set()
    for node in ast.walk(body):
        cross = _cross_instance_call(node)
        if cross is not None:
            providers.add(cross[0])
    return providers


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


class _ActionValidator:
    """Validates @action bodies reference only allowed members."""

    _instance: _ActionValidator | None = None

    @classmethod
    def instance(cls) -> _ActionValidator:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def validate_class(self, toolset_cls: type) -> None:
        allowed = self._allowed_names(toolset_cls)
        for name, member in inspect.getmembers(toolset_cls, predicate=inspect.isfunction):
            if not getattr(member, "_is_action", False):
                continue
            self.validate_action(toolset_cls.__name__, name, member, allowed)

    def validate_action(
        self,
        class_name: str,
        action_name: str,
        action_func: Callable[..., Any],
        allowed_names: set[str],
    ) -> None:
        body = self._parse_source(action_func)
        cross_providers = _cross_instance_providers(body)
        for_providers = _for_each_providers(body)
        all_providers = cross_providers | for_providers
        base_line = action_func.__code__.co_firstlineno
        for node in ast.walk(body):
            if _cross_instance_call(node) is not None:
                continue
            member_name = _self_member_name(node)
            if member_name is None:
                continue
            if member_name not in allowed_names and member_name not in all_providers:
                raise ActionValidationError(
                    f"self.{member_name} is not a @tool, @instruction, @action, or @resource",
                    class_name=class_name,
                    action_name=action_name,
                    lineno=base_line + node.lineno - 1,
                )

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
            for name, member in cls.__dict__.items():
                if isinstance(member, property) and member.fget is not None:
                    if getattr(member.fget, "_is_resource", False):
                        names.add(name)
        return names

    def _parse_source(self, action_func: Callable[..., Any]) -> ast.Module:
        source = textwrap.dedent(inspect.getsource(action_func))
        return ast.parse(source)

    def _self_tool_name(self, node: ast.Call) -> str | None:
        return _self_member_name(node)


def _resolve_chain_placeholders(part: str, next_name: str, prev_name: str) -> str:
    """Substitute {{next}} and {{prev}} in wrapper prose for the resolved stage names."""
    if not part:
        return part
    result = part.replace("{{next}}", next_name)
    if prev_name:
        result = result.replace("{{prev}}", prev_name)
    return result


def _chain_navigation(next_name: str, prev_name: str) -> list[str]:
    """Return framework-injected navigation hints for a wrapper in a chain.

    These are emitted automatically - individual actions must not repeat them.
    When run standalone (no chain), this returns an empty list.
    """
    hints: list[str] = []
    hints.append(f"When done, proceed to {next_name}.")
    if prev_name:
        hints.append(f"If the user wants to revise assumptions, return to {prev_name}.")
    return hints


class _ActionExpander:
    """Expands @action bodies into instructions for a calling agent."""

    _instance: _ActionExpander | None = None

    def __init__(self) -> None:
        self._reader = _SignatureReader.instance()
        self._validator = _ActionValidator.instance()

    @classmethod
    def instance(cls) -> _ActionExpander:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def parse_body(
        self,
        action_func: Callable[..., Any],
        instance: Any | None = None,
    ) -> _ActionBody:
        if instance is not None:
            return self._parse_body_resolved(action_func, instance)
        return self._parse_body_static(action_func)

    def _parse_body_static(self, action_func: Callable[..., Any]) -> _ActionBody:
        module = self._validator._parse_source(action_func)
        function_def = module.body[0]
        if not isinstance(function_def, ast.FunctionDef):
            raise ActionValidationError(
                "action body is not a function",
                class_name=action_func.__qualname__,
                action_name=action_func.__name__,
            )
        prose: list[str] = []
        steps: list[str] = []
        result_template = ""
        seen_prose: set[str] = set()
        specs = list(_action_wrapper_specs(action_func))
        for index, spec in enumerate(specs):
            next_name = specs[index + 1].name if index + 1 < len(specs) else action_func.__name__
            prev_name = specs[index - 1].name if index > 0 else ""
            wrapper_body = self._parse_body_static(spec.chained_action)
            for part in wrapper_body.prose_parts:
                resolved = _resolve_chain_placeholders(part, next_name, prev_name)
                if resolved and resolved not in seen_prose:
                    prose.append(resolved)
                    seen_prose.add(resolved)
            for hint in _chain_navigation(next_name, prev_name):
                if hint not in seen_prose:
                    prose.append(hint)
                    seen_prose.add(hint)
        docstring = ast.get_docstring(function_def)
        if docstring:
            prose.append(docstring.strip())
            seen_prose.add(docstring.strip())
        for statement in function_def.body:
            if isinstance(statement, ast.Return):
                result_template = self._expression_text(statement.value, set())
                continue
            if isinstance(statement, ast.Expr):
                if isinstance(statement.value, ast.Call):
                    tool_name = self._validator._self_tool_name(statement.value)
                    if tool_name:
                        steps.append(tool_name)
                        continue
                    if _super_call_name(statement.value) is not None:
                        continue
                text = self._expression_text(statement.value, set())
                if text and text not in seen_prose:
                    prose.append(text)
                    seen_prose.add(text)
                continue
            if isinstance(statement, ast.Call):
                tool_name = self._validator._self_tool_name(statement)
                if tool_name:
                    steps.append(tool_name)
        if not result_template:
            result_template = f"Instructions for {action_func.__name__}"
        return _ActionBody(
            prose_parts=tuple(prose),
            tool_steps=tuple(steps),
            result_template=result_template,
        )

    def _parse_body_resolved(self, action_func: Callable[..., Any], instance: Any) -> _ActionBody:
        module = self._validator._parse_source(action_func)
        function_def = module.body[0]
        if not isinstance(function_def, ast.FunctionDef):
            return self._parse_body_static(action_func)
        prose, tool_steps = self._walk_body(
            instance,
            function_def,
            current_action=action_func.__name__,
        )
        wrapper_prose: list[str] = []
        specs = list(
            _action_wrapper_specs(
                action_func,
                owner=type(instance),
                name=action_func.__name__,
            )
        )
        for index, spec in enumerate(specs):
            next_name = specs[index + 1].name if index + 1 < len(specs) else action_func.__name__
            prev_name = specs[index - 1].name if index > 0 else ""
            wrapper_instance = _wrapper_expand_instance(spec.chained_action, instance)
            if wrapper_instance is not None:
                wrapper_body = self._parse_body_resolved(
                    spec.chained_action, wrapper_instance
                )
            else:
                wrapper_body = self._parse_body_static(spec.chained_action)
            for part in wrapper_body.prose_parts:
                resolved = _resolve_chain_placeholders(part, next_name, prev_name)
                if resolved and resolved not in prose and resolved not in wrapper_prose:
                    wrapper_prose.append(resolved)
            for hint in _chain_navigation(next_name, prev_name):
                if hint not in prose and hint not in wrapper_prose:
                    wrapper_prose.append(hint)
        if wrapper_prose:
            prose = [*wrapper_prose, *prose]
        prose = self._inject_focus(action_func, instance, prose)
        result_template = _result_template_from(function_def, self)
        if not result_template and _is_empty_action_body(function_def):
            resolved = _resolve_super_func(instance, action_func.__name__)
            if resolved is not None:
                parent_func, _parent_cls = resolved
                parent_module = self._validator._parse_source(parent_func)
                parent_fdef = parent_module.body[0]
                if isinstance(parent_fdef, ast.FunctionDef):
                    result_template = _result_template_from(parent_fdef, self)
        if not result_template:
            result_template = f"Instructions for {action_func.__name__}"
        return _ActionBody(
            prose_parts=tuple(prose),
            tool_steps=tuple(tool_steps),
            result_template=result_template,
        )

    def _inject_focus(
        self,
        action_func: Callable[..., Any],
        instance: Any,
        prose: list[str],
    ) -> list[str]:
        """Append focus-group content when @focus is on an @action.

        Folder layout ({group}/{filter}/) is loaded via @instruction slots with the
        same focus - do not dump the folder here. Legacy flat {group}/{filter}.md
        files are still appended when present.
        """
        focus_entries = _mro_action_focus_entries(
            type(instance), action_func.__name__, action_func
        )
        if not focus_entries:
            return prose
        module_dir = Path(inspect.getfile(type(instance))).parent
        result = list(prose)
        seen = set(prose)
        for focus_group, filter_key in focus_entries:
            filter_value = getattr(instance, filter_key, None)
            if not filter_value:
                continue
            focus_dir = module_dir / focus_group / filter_value
            if focus_dir.is_dir():
                continue
            candidate = module_dir / focus_group / f"{filter_value}.md"
            if not candidate.is_file():
                continue
            content = candidate.read_text(encoding="utf-8").strip()
            if content and content not in seen:
                result.append(content)
                seen.add(content)
        return result

    def _walk_body(
        self,
        instance: Any,
        function_def: ast.FunctionDef,
        *,
        current_action: str,
        visited: frozenset[tuple[str, str]] | None = None,
        defining_class: type | None = None,
    ) -> tuple[list[str], list[str]]:
        visited = visited or frozenset()
        visit_key = _visit_key(instance, current_action, defining_class)
        if visit_key in visited:
            raise ActionValidationError(
                f"recursive @action call: {current_action}",
                class_name=type(instance).__name__,
                action_name=current_action,
            )
        visited = visited | {visit_key}
        toolset_cls = type(instance)
        instruction_slots = instruction_slot_names(toolset_cls)
        action_slots = _action_slot_names(toolset_cls)
        tool_names = self._validator._tool_names(toolset_cls)
        resource_names = self._validator._resource_names(toolset_cls)

        prose: list[str] = []
        tool_steps: list[str] = []
        seen_prose: set[str] = set()

        docstring = ast.get_docstring(function_def)
        action_func = getattr(toolset_cls, current_action)
        # No docstring -> same as docstring equal to the method name (instruction lookup label).
        doc_text = docstring.strip() if docstring and docstring.strip() else current_action
        expanded = _expand_docstring(doc_text, action_func, instance=instance)
        if expanded and expanded not in seen_prose:
            prose.append(expanded)
            seen_prose.add(expanded)

        if _is_empty_action_body(function_def):
            resolved = _resolve_super_func(
                instance, current_action, after_class=defining_class
            )
            if resolved is not None:
                parent_func, parent_cls = resolved
                parent_module = self._validator._parse_source(parent_func)
                parent_fdef = parent_module.body[0]
                if isinstance(parent_fdef, ast.FunctionDef):
                    nested_prose, nested_tools = self._walk_body(
                        instance,
                        parent_fdef,
                        current_action=current_action,
                        visited=visited,
                        defining_class=parent_cls,
                    )
                    for part in nested_prose:
                        if part and part not in seen_prose:
                            prose.append(part)
                            seen_prose.add(part)
                    tool_steps.extend(nested_tools)
            return prose, tool_steps

        for statement in function_def.body:
            if isinstance(statement, ast.Return):
                continue
            expr_node = statement.value if isinstance(statement, ast.Expr) else statement
            if isinstance(statement, ast.Expr) and _is_ellipsis_expr(statement.value):
                continue
            # For-each expansion: for <var> in self.<provider>(): <var>.<action>()
            # The provider is called at expansion time to get the list of target instances.
            # Each instance's named action (or tool) is then expanded/appended inline.
            if isinstance(statement, ast.For):
                iter_node = statement.iter
                loop_var = statement.target
                if isinstance(loop_var, ast.Name) and isinstance(iter_node, ast.Call):
                    iter_member = _self_member_name(iter_node)
                    if iter_member is not None:
                        items = getattr(instance, iter_member)()
                        var_name = loop_var.id
                        for item in items:
                            for body_stmt in statement.body:
                                if not isinstance(body_stmt, ast.Expr):
                                    continue
                                body_call = body_stmt.value
                                if not isinstance(body_call, ast.Call):
                                    continue
                                func = body_call.func
                                if not (
                                    isinstance(func, ast.Attribute)
                                    and isinstance(func.value, ast.Name)
                                    and func.value.id == var_name
                                ):
                                    continue
                                member_name = func.attr
                                target_cls = type(item)
                                target_actions = _action_slot_names(target_cls)
                                target_tools = self._validator._tool_names(target_cls)
                                if member_name in target_actions:
                                    nested_prose, nested_tools = self._walk_nested_action(
                                        item, member_name, visited
                                    )
                                    for part in nested_prose:
                                        if part and part not in seen_prose:
                                            prose.append(part)
                                            seen_prose.add(part)
                                    tool_steps.extend(nested_tools)
                                elif member_name in target_tools:
                                    tool_steps.append(member_name)
                continue
            cross = _cross_instance_call(expr_node)
            if cross:
                provider_method, member = cross
                target_instance = getattr(instance, provider_method)()
                target_cls = type(target_instance)
                target_actions = _action_slot_names(target_cls)
                target_tools = self._validator._tool_names(target_cls)
                if member in target_actions:
                    nested_prose, nested_tools = self._walk_nested_action(
                        target_instance, member, visited
                    )
                    for part in nested_prose:
                        if part and part not in seen_prose:
                            prose.append(part)
                            seen_prose.add(part)
                    tool_steps.extend(nested_tools)
                elif member in target_tools:
                    tool_steps.append(member)
                continue
            member = _self_member_name(expr_node)
            if member:
                if member in action_slots and member != current_action:
                    nested_prose, nested_tools = self._walk_nested_action(instance, member, visited)
                    for part in nested_prose:
                        if part and part not in seen_prose:
                            prose.append(part)
                            seen_prose.add(part)
                    tool_steps.extend(nested_tools)
                elif member in instruction_slots:
                    text = _inline(instance, member)
                    if text and text not in seen_prose:
                        prose.append(text)
                        seen_prose.add(text)
                elif member in tool_names:
                    tool_steps.append(member)
                elif member in resource_names:
                    value = getattr(instance, member)
                    prop = getattr(type(instance), member, None)
                    getter = prop.fget if isinstance(prop, property) else None
                    doc = ""
                    if getter is not None:
                        doc = _expand_docstring(
                            (getter.__doc__ or "").strip(), getter, instance=instance
                        )
                    text = f"Resource `{member}` = {value!r}."
                    if doc:
                        text = text + '\n\n' + doc
                    if text not in seen_prose:
                        prose.append(text)
                        seen_prose.add(text)
                continue
            super_method = _super_call_name(expr_node)
            if super_method is not None:
                resolved = _resolve_super_func(
                    instance, super_method, after_class=defining_class
                )
                if resolved is not None:
                    parent_func, parent_cls = resolved
                    parent_module = self._validator._parse_source(parent_func)
                    parent_fdef = parent_module.body[0]
                    if isinstance(parent_fdef, ast.FunctionDef):
                        nested_prose, nested_tools = self._walk_body(
                            instance,
                            parent_fdef,
                            current_action=super_method,
                            visited=visited,
                            defining_class=parent_cls,
                        )
                        for part in nested_prose:
                            if part and part not in seen_prose:
                                prose.append(part)
                                seen_prose.add(part)
                        tool_steps.extend(nested_tools)
                continue
            if isinstance(statement, ast.Expr):
                text = self._expression_text(statement.value, set())
                if text and text not in seen_prose:
                    prose.append(text)
                    seen_prose.add(text)

        return prose, tool_steps

    def _walk_nested_action(
        self,
        instance: Any,
        action_name: str,
        visited: frozenset[tuple[str, str]],
    ) -> tuple[list[str], list[str]]:
        action_func = getattr(type(instance), action_name)
        module = self._validator._parse_source(action_func)
        function_def = module.body[0]
        if not isinstance(function_def, ast.FunctionDef):
            return [], []
        return self._walk_body(
            instance,
            function_def,
            current_action=action_name,
            visited=visited,
        )

    def expand(self, request: _ActionExpandRequest) -> ActionExpansion:
        body = self.parse_body(request.action_func, request.instance)
        self._log_expansion(request, body.tool_steps)
        parameter_names = set(self._reader.simple_parameters(request.action_func))
        result = self._substitute(
            body.result_template,
            request.arguments,
            parameter_names,
            instance=request.instance,
        )
        instructions = self._build_instructions(
            body=body,
            toolset_path=request.toolset_path,
            context=request.context,
            arguments=request.arguments,
            parameter_names=parameter_names,
            tool_callables=request.tool_callables,
            instance=request.instance,
        )
        return {
            "result": result,
            "instructions": instructions,
            "tools": list(dict.fromkeys(body.tool_steps)),
        }

    def _log_expansion(
        self,
        request: _ActionExpandRequest,
        tool_steps: tuple[str, ...],
    ) -> None:
        from sessions import SessionLog, is_logged, member_is_logged, summarize_mapping

        action_name = request.action_func.__name__
        if request.instance is not None:
            if not member_is_logged(type(request.instance), action_name):
                return
        elif not is_logged(request.action_func):
            return
        slog = SessionLog.instance()
        slog.append(
            kind="expansion",
            toolset=request.toolset_path,
            name=action_name,
            summary=summarize_mapping({"tools": ",".join(tool_steps)}),
            ok=True,
            payload={
                "request": {
                    "action": action_name,
                    "arguments": request.arguments,
                    "context": request.context,
                    "tools": list(tool_steps),
                },
                "response": {"expanded": True},
            },
        )

    def _build_instructions(
        self,
        *,
        body: _ActionBody,
        toolset_path: str,
        context: dict[str, Any],
        arguments: dict[str, Any],
        parameter_names: set[str],
        tool_callables: dict[str, Callable[..., Any]],
        instance: Any | None = None,
    ) -> str:
        lines: list[str] = []
        for part in body.prose_parts:
            lines.append(
                self._substitute(part, arguments, parameter_names, instance=instance)
            )
            lines.append("")
        lines.append(
            "Every tool call uses this shape - set `tool` and `arguments`, pipe to CLI:"
        )
        lines.append("")
        lines.append("```yaml")
        lines.append(f"toolset: {toolset_path}")
        lines.append("context:")
        for key, value in context.items():
            lines.append(f"  {key}: {value}")
        lines.append("tool: <tool name>")
        lines.append("arguments:")
        lines.append("  <if needed>")
        lines.append("```")
        lines.append("")
        lines.append("Run: python -m tools run -")
        lines.append("")
        lines.append("Suggested flow (repeat and reorder as the story needs):")
        lines.append("")
        for index, tool_name in enumerate(body.tool_steps, start=1):
            lines.append(f"{index}. tool: {tool_name}")
            hint = self._argument_hint(tool_callables.get(tool_name))
            if hint:
                lines.append("   arguments:")
                lines.append(f"     {hint}")
            lines.append("")
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
        def replace_self(match: re.Match[str]) -> str:
            attr = match.group(1)
            placeholder = "{{self." + attr + "}}"
            if instance is None or not hasattr(instance, attr):
                raise ValueError(
                    f"missing instance attribute {attr!r} for placeholder {placeholder}"
                )
            return str(getattr(instance, attr))

        rendered = _SELF_PLACEHOLDER.sub(replace_self, template)

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

        rendered = _PARAM_PLACEHOLDER.sub(replace_param, rendered)
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
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                parts.append(self._expression_text(value.value, set()))
        return "".join(parts)


def action(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a method as an agent orchestration recipe; body is expanded, never executed."""
    func._is_action = True
    return func


@dataclass(frozen=True)
class Action:
    """One orchestration recipe on a toolset - expanded into instructions, never executed."""

    name: str
    callable: Callable[..., Any]
    owner: type | None = None

    @property
    def instructions(self) -> str:
        return _SignatureReader.instance().member_instructions(self.callable)

    @property
    def signature_entry(self) -> SignatureEntry:
        reader = _SignatureReader.instance()
        body = _ActionExpander.instance().parse_body(self.callable)
        entry: SignatureEntry = {
            "kind": "action",
            "tools": list(dict.fromkeys(body.tool_steps)),
        }
        specs = list(
            _action_wrapper_specs(self.callable, owner=self.owner, name=self.name)
        )
        if specs:
            chain: list = []
            for spec in specs:
                kwargs = _resolve_wrapper_static_kwargs(spec.static_kwargs, self.owner)
                if kwargs:
                    chain.append({"name": spec.name, **kwargs})
                else:
                    chain.append(spec.name)
            entry["chain"] = chain
        focus_entries = _mro_action_focus_entries(self.owner, self.name, self.callable)
        if focus_entries:
            entry["focus"] = [{"group": g, "filter_key": k} for g, k in focus_entries]
        if self.instructions:
            entry["instructions"] = self.instructions
        parameters = reader.simple_parameters(self.callable)
        if parameters:
            entry["parameters"] = parameters
        returns = reader.simple_return_type(self.callable)
        if returns:
            entry["returns"] = returns
        return entry

    def add_to_signature(self, signature: ManifestDocument) -> None:
        signature[self.name] = self.signature_entry


def _mro_action_focus_entries(
    owner: type | None,
    name: str,
    action_func: Callable[..., Any],
) -> list[tuple[str, str]]:
    """Collect ``_focus_entries`` from the action and its base definitions (MRO)."""
    if owner is None:
        return list(getattr(getattr(action_func, "__func__", action_func), "_focus_entries", []) or [])
    entries: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for klass in owner.__mro__:
        func = klass.__dict__.get(name)
        if func is None or not callable(func):
            continue
        target = getattr(func, "__func__", func)
        if not getattr(target, "_is_action", False):
            continue
        for entry in getattr(target, "_focus_entries", []) or []:
            if entry not in seen:
                entries.append(entry)
                seen.add(entry)
    return entries


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
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def validate_toolset(self, toolset_cls: type) -> None:
        _ActionValidator.instance().validate_class(toolset_cls)

    def run(self, request: _ActionRunRequest) -> RunResponseDocument:
        from tools.tool import RunError
        if request.action_name not in request.instance.actions:
            raise RunError(
                f"unknown action {request.action_name!r}",
                response={"ok": False, "action": request.action_name, "error": "unknown action"},
            )
        action_entry = request.instance.actions[str(request.action_name)]
        try:
            expanded = self._expander.expand(
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
        except Exception as exc:
            raise RunError(
                str(exc),
                response={"ok": False, "action": request.action_name, "error": str(exc)},
            ) from exc
        return self._build_response(
            request.request,
            request.toolset_path,
            request.action_name,
            request.arguments,
            request.instance,
            expanded,
        )

    def _build_response(
        self,
        request: dict[str, Any],
        toolset_path: Any,
        action_name: Any,
        arguments: dict[str, Any],
        instance: "Toolset",
        expanded: dict[str, Any],
    ) -> dict[str, Any]:
        from tools.tool import _ManifestYaml
        response: dict[str, Any] = {
            "ok": True,
            "toolset": str(toolset_path),
            "action": str(action_name),
            "result": expanded["result"],
            "instructions": expanded["instructions"],
            "arguments": _ManifestYaml.instance().serialize_value(arguments),
            "tools": expanded["tools"],
        }
        if request.get("include_resources", True):
            response["resources"] = _ManifestYaml.instance().serialize_value(instance.resources)
        return response


