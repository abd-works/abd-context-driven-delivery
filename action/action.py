# @toolset-manifest python -m tools manifest action.agent_with_actions:AgentWithActions
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.format python
# @toolset-manifest python -m tools manifest bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: bdd.bdd:Bdd
# invoke-check: action validate | toolset: bdd.bdd:Bdd
"""Action expansion — orchestration recipes that never execute, only instruct."""
from __future__ import annotations

import ast
import inspect
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

_DEFAULT_LOG_FILE = Path(__file__).parent / "log-action-requests.txt"


def _log_action_request(
    action_name: str,
    tool_steps: tuple[str, ...],
    log_file: Path = _DEFAULT_LOG_FILE,
) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    lines = [f"{ts} action: {action_name}"]
    for tool in tool_steps:
        lines.append(f"{ts} tool: {tool}")
    with log_file.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

from primitives.instruction_slot import (
    expand_docstring,
    inline,
    instruction_slot_names,
    is_framework_action,
)
from tools.tool import SignatureReader


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
        super().__init__(f"{location} — {message}")
        self.class_name = class_name
        self.action_name = action_name
        self.lineno = lineno


@dataclass(frozen=True)
class ActionBody:
    prose_parts: tuple[str, ...]
    tool_steps: tuple[str, ...]
    result_template: str


def action_slot_names(toolset_cls: type) -> frozenset[str]:
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
    No preamble strings — the chained action *is* the instruction.

    ``static_kwargs`` are fixed parameters the decorator supplies to the
    chained action (e.g. ``agent_dir`` for ``@sketch``). They are surfaced
    in the manifest chain entry so the AI knows what to pass.
    """

    name: str
    chained_action: "Callable[..., Any]"
    static_kwargs: dict = field(default_factory=dict)


def _action_wrapper_specs(action_func: Callable[..., Any]) -> tuple[_WrapperSpec, ...]:
    """Return wrapper specs registered on this action, in execution order (top-down)."""
    specs = getattr(action_func, "_action_wrapper_specs", None) or ()
    return tuple(specs)


def action_wrapper_names(action_func: Callable[..., Any]) -> tuple[str, ...]:
    """Return names of wrapping decorators contributed to this action, in execution order."""
    wrappers = getattr(action_func, "_action_wrappers", None) or ()
    return tuple(wrappers)


def require_action(func: Callable[..., Any], decorator_name: str) -> None:
    """Guard: ensure a chainable-action decorator's target is already ``@action``-marked.

    Chainable decorators (``@sketch``, ``@grill_with_context``, …) must be applied on top
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
    time, ``ActionExpander`` calls ``_parse_body_static(chained_action)`` and
    prepends the resulting prose to the base action's expanded body — no
    preamble strings, no builders, no slots. The chained action's own
    instructions *are* the wrapper's contribution.

    Prepends to ``_action_wrapper_specs`` and rebuilds ``_action_wrappers``
    from it. Prepending matches Python's inner-first decoration order so a
    top-declared decorator ends up first in the spec list — declaration order
    equals execution order.
    """
    spec = _WrapperSpec(name=name, chained_action=chained_action, static_kwargs=static_kwargs or {})
    specs = list(getattr(func, "_action_wrapper_specs", None) or [])
    specs.insert(0, spec)
    func._action_wrapper_specs = specs  # type: ignore[attr-defined]
    func._action_wrappers = [s.name for s in specs]  # type: ignore[attr-defined]


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
    """True when the body has no steps — only docstring, ``...``, ``pass``, and/or ``return``.

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


def _result_template_from(function_def: ast.FunctionDef, expander: "ActionExpander") -> str:
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

    When *after_class* is None, skip the instance's own definition (identity check —
    class-synthesis decorators like ``@generator`` may copy the same function onto
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


class ActionValidator:
    """Validates @action bodies reference only allowed members."""

    _instance: ActionValidator | None = None

    @classmethod
    def instance(cls) -> ActionValidator:
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
        base_line = action_func.__code__.co_firstlineno
        for node in ast.walk(body):
            if _cross_instance_call(node) is not None:
                continue
            member_name = _self_member_name(node)
            if member_name is None:
                continue
            if member_name not in allowed_names and member_name not in cross_providers:
                raise ActionValidationError(
                    f"self.{member_name} is not a @tool, @instruction, or @action",
                    class_name=class_name,
                    action_name=action_name,
                    lineno=base_line + node.lineno - 1,
                )

    def _allowed_names(self, toolset_cls: type) -> set[str]:
        return (
            self._tool_names(toolset_cls)
            | set(instruction_slot_names(toolset_cls))
            | set(action_slot_names(toolset_cls))
        )

    def _tool_names(self, toolset_cls: type) -> set[str]:
        names: set[str] = set()
        for name, member in inspect.getmembers(toolset_cls, predicate=inspect.isfunction):
            if getattr(member, "_is_tool", False):
                names.add(name)
        return names

    def _parse_source(self, action_func: Callable[..., Any]) -> ast.Module:
        source = textwrap.dedent(inspect.getsource(action_func))
        return ast.parse(source)

    def _self_tool_name(self, node: ast.Call) -> str | None:
        return _self_member_name(node)


def _resolve_chain_placeholders(part: str, next_name: str, prev_name: str) -> str:
    """Substitute {next} and {prev} in wrapper prose for the resolved stage names."""
    if not part:
        return part
    result = part.replace("{next}", next_name)
    if prev_name:
        result = result.replace("{prev}", prev_name)
    return result


def _chain_navigation(next_name: str, prev_name: str) -> list[str]:
    """Return framework-injected navigation hints for a wrapper in a chain.

    These are emitted automatically — individual actions must not repeat them.
    When run standalone (no chain), this returns an empty list.
    """
    hints: list[str] = []
    hints.append(f"When done, proceed to {next_name}.")
    if prev_name:
        hints.append(f"If the user wants to revise assumptions, return to {prev_name}.")
    return hints


class ActionExpander:
    """Expands @action bodies into instructions for a calling agent."""

    _instance: ActionExpander | None = None

    def __init__(self) -> None:
        self._reader = SignatureReader.instance()
        self._validator = ActionValidator.instance()

    @classmethod
    def instance(cls) -> ActionExpander:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def parse_body(
        self,
        action_func: Callable[..., Any],
        instance: Any | None = None,
    ) -> ActionBody:
        if instance is not None:
            return self._parse_body_resolved(action_func, instance)
        return self._parse_body_static(action_func)

    def _parse_body_static(self, action_func: Callable[..., Any]) -> ActionBody:
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
        return ActionBody(
            prose_parts=tuple(prose),
            tool_steps=tuple(steps),
            result_template=result_template,
        )

    def _parse_body_resolved(self, action_func: Callable[..., Any], instance: Any) -> ActionBody:
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
        specs = list(_action_wrapper_specs(action_func))
        for index, spec in enumerate(specs):
            next_name = specs[index + 1].name if index + 1 < len(specs) else action_func.__name__
            prev_name = specs[index - 1].name if index > 0 else ""
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
        return ActionBody(
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
        same focus — do not dump the folder here. Legacy flat {group}/{filter}.md
        files are still appended when present.
        """
        focus_entries: list[tuple[str, str]] = getattr(action_func, "_focus_entries", [])
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
        action_slots = action_slot_names(toolset_cls)
        tool_names = self._validator._tool_names(toolset_cls)

        prose: list[str] = []
        tool_steps: list[str] = []
        seen_prose: set[str] = set()

        docstring = ast.get_docstring(function_def)
        action_func = getattr(toolset_cls, current_action)
        if docstring and docstring.strip():
            doc_text = docstring.strip()
        elif getattr(toolset_cls, "_is_generator", False) and is_framework_action(current_action):
            doc_text = f"base-generator/{current_action}"
        else:
            doc_text = ""
        if doc_text:
            expanded = expand_docstring(doc_text, action_func, instance=instance)
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
            cross = _cross_instance_call(expr_node)
            if cross:
                provider_method, member = cross
                target_instance = getattr(instance, provider_method)()
                target_cls = type(target_instance)
                target_actions = action_slot_names(target_cls)
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
                    text = inline(instance, member)
                    if text and text not in seen_prose:
                        prose.append(text)
                        seen_prose.add(text)
                elif member in tool_names:
                    tool_steps.append(member)
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

    def expand(
        self,
        *,
        action_func: Callable[..., Any],
        toolset_path: str,
        context: dict[str, Any],
        arguments: dict[str, Any],
        tool_callables: dict[str, Callable[..., Any]],
        instance: Any | None = None,
        log_file: Path | None = None,
    ) -> dict[str, Any]:
        body = self.parse_body(action_func, instance)
        _log_action_request(action_func.__name__, body.tool_steps, log_file or self._log_file_for(instance))
        parameter_names = set(self._reader.simple_parameters(action_func))
        result = self._substitute(body.result_template, arguments, parameter_names)
        instructions = self._build_instructions(
            body=body,
            toolset_path=toolset_path,
            context=context,
            arguments=arguments,
            parameter_names=parameter_names,
            tool_callables=tool_callables,
        )
        return {
            "result": result,
            "instructions": instructions,
            "tools": list(dict.fromkeys(body.tool_steps)),
        }

    def _log_file_for(self, instance: Any | None) -> Path:
        if instance is None:
            return _DEFAULT_LOG_FILE
        return Path(inspect.getfile(type(instance))).parent / "log-action-requests.txt"

    def _build_instructions(
        self,
        *,
        body: ActionBody,
        toolset_path: str,
        context: dict[str, Any],
        arguments: dict[str, Any],
        parameter_names: set[str],
        tool_callables: dict[str, Callable[..., Any]],
    ) -> str:
        lines: list[str] = []
        for part in body.prose_parts:
            lines.append(self._substitute(part, arguments, parameter_names))
            lines.append("")
        lines.append(
            "Every tool call uses this shape — set `tool` and `arguments`, pipe to CLI:"
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
        self, template: str, arguments: dict[str, Any], parameter_names: set[str]
    ) -> str:
        rendered = template
        for name in parameter_names:
            placeholder = "{" + name + "}"
            if placeholder not in rendered:
                continue
            if name not in arguments:
                raise ValueError(f"missing argument {name!r} for placeholder {placeholder}")
            rendered = rendered.replace(placeholder, str(arguments[name]))
        return rendered

    def _expression_text(self, node: ast.expr | None, _parameters: set[str]) -> str:
        if node is None:
            return ""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value.strip()
        if isinstance(node, ast.JoinedStr):
            return self._joined_string(node)
        if isinstance(node, ast.Name):
            return "{" + node.id + "}"
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
    """One orchestration recipe on a toolset — expanded into instructions, never executed."""

    name: str
    callable: Callable[..., Any]

    @property
    def instructions(self) -> str:
        return SignatureReader.instance().member_instructions(self.callable)

    @property
    def signature_entry(self) -> dict[str, Any]:
        reader = SignatureReader.instance()
        body = ActionExpander.instance().parse_body(self.callable)
        entry: dict[str, Any] = {
            "kind": "action",
            "tools": list(dict.fromkeys(body.tool_steps)),
        }
        specs = list(_action_wrapper_specs(self.callable))
        if specs:
            chain: list = []
            for spec in specs:
                if spec.static_kwargs:
                    chain.append({"name": spec.name, **spec.static_kwargs})
                else:
                    chain.append(spec.name)
            entry["chain"] = chain
        focus_entries: list[tuple[str, str]] = getattr(self.callable, "_focus_entries", [])
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

    def add_to_signature(self, signature: dict[str, Any]) -> None:
        signature[self.name] = self.signature_entry


def discover_actions(instance: "Toolset") -> "dict[str, Action]":
    discovered: dict[str, Action] = {}
    for name, member in inspect.getmembers(instance.__class__, predicate=inspect.isfunction):
        if getattr(member, "_is_action", False):
            discovered[name] = Action(name=name, callable=getattr(instance, name))
    return discovered


def has_actions(instance: "Toolset") -> bool:
    return bool(discover_actions(instance))


class ActionRunner:
    """Invokes one action from a parsed run request."""

    _instance: ActionRunner | None = None

    def __init__(self) -> None:
        from tools.tool import ManifestYaml
        self._expander = ActionExpander.instance()
        self._yaml = ManifestYaml.instance()

    @classmethod
    def instance(cls) -> ActionRunner:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def validate_toolset(self, toolset_cls: type) -> None:
        ActionValidator.instance().validate_class(toolset_cls)

    def run(
        self,
        request: dict[str, Any],
        *,
        toolset_path: Any,
        action_name: Any,
        context: dict[str, Any],
        arguments: dict[str, Any],
        instance: "Toolset",
    ) -> dict[str, Any]:
        from tools.tool import RunError
        if action_name not in instance.actions:
            raise RunError(
                f"unknown action {action_name!r}",
                response={"ok": False, "action": action_name, "error": "unknown action"},
            )
        action_entry = instance.actions[str(action_name)]
        try:
            expanded = self._expander.expand(
                action_func=action_entry.callable,
                toolset_path=str(toolset_path),
                context=context,
                arguments=arguments,
                tool_callables={name: tool.callable for name, tool in instance.tools.items()},
                instance=instance,
            )
        except Exception as exc:
            raise RunError(
                str(exc),
                response={"ok": False, "action": action_name, "error": str(exc)},
            ) from exc
        return self._build_response(
            request, toolset_path, action_name, arguments, instance, expanded
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
        from tools.tool import ManifestYaml
        response: dict[str, Any] = {
            "ok": True,
            "toolset": str(toolset_path),
            "action": str(action_name),
            "result": expanded["result"],
            "instructions": expanded["instructions"],
            "arguments": ManifestYaml.instance().serialize_value(arguments),
            "tools": expanded["tools"],
        }
        if request.get("include_resources", True):
            response["resources"] = ManifestYaml.instance().serialize_value(instance.resources)
        return response


