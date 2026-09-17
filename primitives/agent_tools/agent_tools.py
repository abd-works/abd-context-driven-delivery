"""Agent toolset — register, introspect, and validate one decorated AgentToolSet."""
from __future__ import annotations

import ast
import inspect
import re
import textwrap
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, cast, get_args, get_origin

ContextDocument = dict[str, Any]
ArgumentDocument = dict[str, Any]
TypeAnnotation = Any


class AgentToolValidationError(Exception):
    def __init__(
        self,
        message: str,
        *,
        class_name: str = "",
        action_name: str = "",
        lineno: int | None = None,
    ) -> None:
        detail = message
        if class_name or action_name:
            where = f"{class_name}.{action_name}" if class_name and action_name else class_name or action_name
            detail = f"{where}: {message}"
        if lineno is not None:
            detail = f"{detail} (line {lineno})"
        super().__init__(detail)
        self.class_name = class_name
        self.action_name = action_name
        self.lineno = lineno

@dataclass(frozen=True)
class ExpansionMode:
    value: str

    def __post_init__(self) -> None:
        if self.value not in ("instructions", "tool"):
            raise ValueError(f"mode must be 'instructions' or 'tool', got {self.value!r}")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ExpansionMode):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return NotImplemented

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ExpansionResult:
    instructions: str
    tools: list[str]
    result: str


_PARAM_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")
_SELF_PLACEHOLDER = re.compile(r"\{\{self\.(\w+)\}\}")
_EXEC_LOCAL_MISSING = object()


class ToolSetCollection:
    """Named child toolsets, iterated in entry order."""

    def __init__(self, entries: dict[str, Any] | None = None) -> None:
        self.entries: dict[str, Any] = dict(entries or {})

    def __iter__(self):
        return iter(self.entries.values())

    def __len__(self) -> int:
        return len(self.entries)

    def __bool__(self) -> bool:
        return bool(self.entries)


class AgentToolSet:
    """Injected by @agent_toolset — operations and @agent_instructions on one toolset."""

    _mode: str = "instructions"
    domain_slug: str | None = None

    def __init__(self) -> None:
        self.nested_toolsets = ToolSetCollection()

    @property
    def name(self) -> str:
        return AgentToolSet._slugify_class_name(type(self).__name__)

    @property
    def description(self) -> str:
        return (self.__class__.__doc__ or "").strip()

    @property
    def operations(self) -> dict[str, AgentOperation]:
        return self._discover_operations()

    @property
    def instructions(self) -> Mapping[str, AgentInstructions]:
        return self._discover_instruction_members()

    @property
    def tools(self) -> dict[str, AgentTool]:
        merged: dict[str, AgentTool] = {}
        merged.update(self.operations)
        merged.update(self._discover_instruction_members())
        for name, tool in self._discover_hook_members().items():
            merged.setdefault(name, tool)
        return merged

    @property
    def mode(self) -> ExpansionMode:
        """Execution mode for @agent_instructions calls into this instance.
        instructions = expand inline; tool = list action in tools, defer its body."""
        return ExpansionMode(self._mode)

    @mode.setter
    def mode(self, new_mode: str | ExpansionMode) -> None:
        value = new_mode.value if isinstance(new_mode, ExpansionMode) else new_mode
        if value not in ("instructions", "tool"):
            raise ValueError(f"mode must be 'instructions' or 'tool', got {value!r}")
        self._mode = value

    def _discover_operations(self) -> dict[str, AgentOperation]:
        discovered: dict[str, AgentOperation] = {}
        for name, member in inspect.getmembers(self.__class__, predicate=inspect.isfunction):
            if getattr(member, "_is_agent_tool", False):
                discovered[name] = AgentOperation(
                    name=name,
                    callable=getattr(self, name),
                    toolset=self,
                )
        return discovered

    def _discover_instruction_members(self) -> dict[str, AgentInstructions]:
        discovered: dict[str, AgentInstructions] = {}
        for name, member in inspect.getmembers(type(self), predicate=inspect.isfunction):
            if getattr(member, "_is_agent_instructions", False):
                discovered[name] = AgentInstructions(
                    name=name,
                    callable=getattr(self, name),
                    toolset=self,
                )
        return discovered

    def _discover_hook_members(self) -> dict[str, AgentTool]:
        discovered: dict[str, AgentTool] = {}
        for name, member in inspect.getmembers(type(self), predicate=inspect.isfunction):
            if getattr(member, "_hook", False):
                discovered[name] = AgentTool(
                    name=name,
                    callable=getattr(self, name),
                    toolset=self,
                )
        return discovered

    @classmethod
    def _slugify_class_name(cls, name: str) -> str:
        """PascalCase -> snake_case so toolset_name matches package/folder names."""
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    @classmethod
    def _marked_tool_names(cls, toolset_cls: type) -> set[str]:
        names: set[str] = set()
        for name, member in inspect.getmembers(toolset_cls, predicate=inspect.isfunction):
            if getattr(member, "_is_agent_tool", False):
                names.add(name)
        return names

    @classmethod
    def _instruction_names(cls, toolset_cls: type) -> frozenset[str]:
        names: set[str] = set()
        for name, member in inspect.getmembers(toolset_cls, predicate=inspect.isfunction):
            if getattr(member, "_is_agent_instructions", False):
                names.add(name)
        return frozenset(names)


    class _InstructionBodyValidator(ast.NodeVisitor):
        """Validate ``tools(...)`` and ``instructions(...)`` in one ``@agent_instructions`` body.

        Invoked from ``_validate_action`` when an ``@agent_toolset`` class is registered.
        Walks the action AST and raises ``AgentToolValidationError`` when a wrapper
        names a member that is not an allowed ``@agent_tool``, ``@agent_instructions``
        peer, loop-bound companion, or recognized cross-toolset provider. The visit
        performs the check — not a passive tree walk for something else to interpret.
        """

        def __init__(
            self,
            *,
            allowed_names: set[str],
            all_providers: set[str],
            class_name: str,
            action_name: str,
        ) -> None:
            self._allowed_names = allowed_names
            self._all_providers = all_providers
            self._class_name = class_name
            self._action_name = action_name
            self._loop_vars: list[str] = []

        def visit_For(self, node: ast.For) -> None:
            if isinstance(node.target, ast.Name):
                self._loop_vars.append(node.target.id)
                self.generic_visit(node)
                self._loop_vars.pop()
                return
            self.generic_visit(node)

        def _validate_wrapper_arg(self, wrapper: str, arg: ast.AST | None) -> bool:
            if arg is None:
                if wrapper == "tools":
                    raise AgentToolValidationError(
                        f"{wrapper}(...) requires one argument",
                        class_name=self._class_name,
                        action_name=self._action_name,
                    )
                return False
            if AgentToolSet._provider_cross_call(arg) is not None:
                return True
            if self._loop_vars and AgentToolSet._provider_cross_call(
                arg, frozenset(self._loop_vars)
            ) is not None:
                return True
            if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute):
                if isinstance(arg.func.value, ast.Name) and arg.func.value.id in self._loop_vars:
                    return True
            member = AgentInstructions._self_member_name(arg)
            if member is not None:
                self._check_member(member)
                return True
            if wrapper == "tools":
                raise AgentToolValidationError(
                    f"{wrapper}(...) argument is not a recognized tool step",
                    class_name=self._class_name,
                    action_name=self._action_name,
                )
            return False

        def _check_member(self, member_name: str) -> None:
            if member_name in self._allowed_names or member_name in self._all_providers:
                return
            raise AgentToolValidationError(
                f"{member_name!r} is not an allowed tool step",
                class_name=self._class_name,
                action_name=self._action_name,
            )

        def visit_Call(self, node: ast.Call) -> None:
            if isinstance(node.func, ast.Name) and node.func.id == "tools":
                if self._validate_wrapper_arg("tools", node.args[0] if node.args else None):
                    return
            if isinstance(node.func, ast.Name) and node.func.id == "instructions":
                if self._validate_wrapper_arg(
                    "instructions", node.args[0] if node.args else None
                ):
                    return
            self.generic_visit(node)

    @classmethod
    def _validate_self_param(
        cls,
        class_name: str,
        action_name: str,
        action_func: Callable[..., Any],
    ) -> None:
        params = list(inspect.signature(action_func).parameters.values())
        if not params or params[0].name != "self":
            raise AgentToolValidationError(
                "first parameter must be named 'self'",
                class_name=class_name,
                action_name=action_name,
            )
        if params[0].default is not inspect.Parameter.empty:
            raise AgentToolValidationError(
                "self parameter must not have a default",
                class_name=class_name,
                action_name=action_name,
            )

    @classmethod
    def _validate_action(
        cls,
        class_name: str,
        action_name: str,
        action_func: Callable[..., Any],
        allowed_names: set[str],
    ) -> None:
        cls._validate_self_param(class_name, action_name, action_func)
        body_ast = AgentInstructions.for_callable(action_func)._parse_source(action_func)
        all_providers = cls._cross_instance_providers(body_ast) | cls._for_each_providers(body_ast)
        cls._InstructionBodyValidator(
            allowed_names=allowed_names,
            all_providers=all_providers,
            class_name=class_name,
            action_name=action_name,
        ).visit(body_ast)

    @classmethod
    def _validate_toolset_class(cls, toolset_cls: type) -> None:
        allowed = cls._marked_tool_names(toolset_cls) | set(cls._instruction_names(toolset_cls))
        for name, member in inspect.getmembers(toolset_cls, predicate=inspect.isfunction):
            if not getattr(member, "_is_agent_instructions", False):
                continue
            cls._validate_action(toolset_cls.__name__, name, member, allowed)

    @classmethod
    def _validate_toolset(cls, toolset_cls: type) -> None:
        cls._validate_toolset_class(toolset_cls)

    @classmethod
    def _provider_cross_call(
        cls,
        node: ast.AST,
        roots: frozenset[str] = frozenset({"self"}),
    ) -> tuple[str, str] | None:
        """Match ``<root>.<provider>().<member>()`` or ``<root>.<provider>.<member>()``."""
        if not isinstance(node, ast.Call):
            return None
        if not isinstance(node.func, ast.Attribute):
            return None
        member = node.func.attr
        provider_node = node.func.value
        provider_attr = provider_node.func if isinstance(provider_node, ast.Call) else provider_node
        if not isinstance(provider_attr, ast.Attribute):
            return None
        if not isinstance(provider_attr.value, ast.Name) or provider_attr.value.id not in roots:
            return None
        return provider_attr.attr, member

    @classmethod
    def _cross_instance_call(cls, node: ast.AST) -> tuple[str, str] | None:
        return cls._provider_cross_call(node, frozenset({"self"}))

    @classmethod
    def _cross_instance_providers(cls, body: ast.Module) -> set[str]:
        providers: set[str] = set()
        for node in ast.walk(body):
            cross = cls._cross_instance_call(node)
            if cross is not None:
                providers.add(cross[0])
        return providers

    @classmethod
    def _for_each_providers(cls, body: ast.Module) -> set[str]:
        providers: set[str] = set()
        for node in ast.walk(body):
            if not isinstance(node, ast.For):
                continue
            iter_member = AgentInstructions._self_member_name(node.iter)
            if iter_member is not None:
                providers.add(iter_member)
        return providers

    @classmethod
    def instantiate(cls, context: dict[str, Any] | None = None) -> AgentToolSet:
        return cls(**(context or {}))

    def validate(self) -> None:
        AgentToolSet._validate_toolset_class(type(self))

class InstallDestination:
    MCP = "mcp"
    HOOK = "hook"
    SKILL = "skill"
    COMMAND = "command"
    RULE = "rules"


@dataclass
class AgentTool:
    name: str
    callable: Callable[..., Any]
    toolset: AgentToolSet

    @classmethod
    def from_callable(cls, func: Callable[..., Any]) -> AgentTool:
        return cls(name=func.__name__, callable=func, toolset=AgentToolSet())

    @property
    def install_to_mcp(self) -> bool:
        return bool(getattr(self.callable, "_mcp", False))

    @property
    def install_to_hook(self) -> bool:
        return bool(getattr(self.callable, "_hook", False))

    @property
    def install_to_skill(self) -> bool:
        return bool(getattr(self.callable, "_skill", False))

    @property
    def install_to_command(self) -> bool:
        return bool(getattr(self.callable, "_command", False))

    @property
    def install_to_rule(self) -> bool:
        return bool(getattr(self.callable, "_rules", False))

    def install_to(self, destination: str) -> bool:
        if destination == InstallDestination.MCP:
            return self.install_to_mcp
        if destination == InstallDestination.HOOK:
            return self.install_to_hook
        if destination == InstallDestination.SKILL:
            return self.install_to_skill
        if destination == InstallDestination.COMMAND:
            return self.install_to_command
        if destination == InstallDestination.RULE:
            return self.install_to_rule
        return False

    @property
    def destinations(self) -> list[str]:
        destinations: list[str] = []
        if self.install_to_mcp:
            destinations.append(InstallDestination.MCP)
        if self.install_to_skill:
            destinations.append(InstallDestination.SKILL)
        if self.install_to_command:
            destinations.append(InstallDestination.COMMAND)
        if self.install_to_rule:
            destinations.append(InstallDestination.RULE)
        if self.install_to_hook:
            destinations.append(InstallDestination.HOOK)
        return destinations

    @property
    def deploy_name(self) -> str:
        return (
            getattr(self.callable, "_command_name", None)
            or getattr(self.callable, "_skill_name", None)
            or self.name
        )

    @property
    def kind(self) -> str:
        if getattr(self.callable, "_is_agent_tool", False):
            return "tool"
        if getattr(self.callable, "_is_agent_instructions", False):
            return "instructions"
        return "none"

    @property
    def description(self) -> str:
        doc = (self.callable.__doc__ or "").strip()
        return doc if doc else self.callable.__name__

    @property
    def parameters(self) -> dict[str, str]:
        sig = inspect.signature(self.callable)
        parameters: dict[str, str] = {}
        for name, param in sig.parameters.items():
            if name in ("self", "cls"):
                continue
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            parameters[name] = self._format_type(param.annotation)
        return parameters

    @property
    def response(self) -> str | None:
        sig = inspect.signature(self.callable)
        if sig.return_annotation is inspect.Signature.empty:
            return None
        return self._format_type(sig.return_annotation)

    def _format_type(self, annotation: TypeAnnotation) -> str:
        if annotation is inspect.Parameter.empty:
            return "str"
        if isinstance(annotation, str):
            return self._format_type_from_string(annotation)
        origin = get_origin(annotation)
        if origin is list:
            return self._format_list_type(annotation)
        if origin is dict:
            return "dict"
        return self._format_builtin_type(annotation, origin)

    def _format_type_from_string(self, annotation_text: str) -> str:
        origin_name, _, args_text = annotation_text.partition("[")
        if origin_name == "list":
            element_text = args_text.rstrip("]") if args_text else "str"
            return f"list[{self._format_type(element_text)}]"
        return annotation_text

    def _format_list_type(self, annotation: Any) -> str:
        args = get_args(annotation)
        element_type = self._format_type(args[0]) if args else "str"
        return f"list[{element_type}]"

    def _format_builtin_type(self, annotation: Any, origin: Any) -> str:
        if annotation is str:
            return "str"
        if annotation is int:
            return "int"
        if annotation is float:
            return "float"
        if annotation is bool:
            return "bool"
        if annotation in (None, type(None)):
            return "None"
        if origin is not None:
            return getattr(annotation, "__name__", str(origin))
        return getattr(annotation, "__name__", str(annotation))

@dataclass
class AgentOperation(AgentTool):
    @property
    def kind(self) -> str:
        return "tool"

    def invoke(self, arguments: dict[str, Any]) -> Any:
        return self.callable(**arguments)

@dataclass
class AgentInstructions(AgentTool):
    _prompt: list[str] = field(default_factory=list, init=False, repr=False)
    _tools: list[str] = field(default_factory=list, init=False, repr=False)
    _seen_prompt: set[str] = field(default_factory=set, init=False, repr=False)
    _visited: frozenset[tuple[str, str]] = field(default_factory=frozenset, init=False, repr=False)
    _defining_class: type | None = field(default=None, init=False, repr=False)
    _mode: str = field(default='instructions', init=False, repr=False)
    _loop_item_modes: dict[int, str] = field(default_factory=dict, init=False, repr=False)
    _execution_locals: dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    @property
    def kind(self) -> str:
        return "instructions"

    @classmethod
    def for_callable(
        cls,
        callable: Callable[..., Any],
        instance: AgentToolSet | None = None,
    ) -> AgentInstructions:
        if instance is not None:
            return instance.instructions[callable.__name__]
        return cls(
            name=callable.__name__,
            callable=callable,
            toolset=AgentToolSet(),
        )

    @property
    def prompt(self) -> tuple[str, ...]:
        self._scan()
        return tuple(self._prompt)

    @property
    def tools(self) -> list[str]:
        self._scan()
        return list(dict.fromkeys(self._tools))

    @property
    def result_template(self) -> str:
        function_def = self._require_function_def(self.callable)
        result_template = self._result_template_from(function_def)
        if not result_template and self._is_empty_action_body(function_def):
            result_template = self._resolve_parent_result_template(self.callable, self.toolset)
        if not result_template:
            result_template = f"Instructions for {self.callable.__name__}"
        return result_template

    @classmethod
    def substitute_template(
        cls,
        template: str,
        arguments: dict[str, Any],
        parameter_names: set[str],
        *,
        instance: Any | None = None,
    ) -> str:
        return cls.for_callable(lambda self: None)._substitute(
            template, arguments, parameter_names, instance=instance,
        )

    def expand(self, context: dict[str, Any], arguments: dict[str, Any]) -> ExpansionResult:
        del context
        self._scan()
        parameter_names = set(self.parameters)
        result = self._substitute(
            self.result_template, arguments, parameter_names, instance=self.toolset,
        )
        instructions = self._join_prompt(tuple(self._prompt), arguments)
        return ExpansionResult(
            instructions=instructions,
            tools=list(dict.fromkeys(self._tools)),
            result=result,
        )

    def _scan(
        self,
        *,
        visited: frozenset[tuple[str, str]] | None = None,
        defining_class: type | None = None,
        reset: bool = True,
    ) -> None:
        if reset:
            self._prompt = []
            self._tools = []
            self._seen_prompt = set()
            self._loop_item_modes = {}
            self._execution_locals = {}
        self._defining_class = defining_class
        self._mode = self._read_mode(self.toolset)
        self._visited = self._check_and_advance_visited(
            self.toolset, self.callable.__name__, defining_class, visited or frozenset(),
        )
        function_def = self._require_function_def(self.callable)
        if self._is_empty_action_body(function_def):
            self._walk_super()
        else:
            self._walk_statements(function_def)

    def _merge_from(self, other: AgentInstructions) -> None:
        self._tools.extend(other._tools)
        for part in other._prompt:
            self._add_prompt(part)

    def _add_prompt(self, text: str) -> None:
        if text and text not in self._seen_prompt:
            self._prompt.append(text)
            self._seen_prompt.add(text)

    def _effective_mode(self, target: Any) -> str:
        if target is self.toolset:
            return self._mode
        loop_mode = self._loop_item_modes.get(id(target))
        if loop_mode is not None:
            return loop_mode
        mode = getattr(target, "mode", "instructions")
        return mode.value if isinstance(mode, ExpansionMode) else str(mode)

    def _parse_source(self, action_func: Callable[..., Any]) -> ast.Module:
        source = textwrap.dedent(inspect.getsource(action_func))
        return ast.parse(source)

    def _require_function_def(self, action_func: Callable[..., Any]) -> ast.FunctionDef:
        module = self._parse_source(action_func)
        function_def = module.body[0]
        if not isinstance(function_def, ast.FunctionDef):
            raise AgentToolValidationError(
                "action body is not a function",
                class_name=action_func.__qualname__,
                action_name=action_func.__name__,
            )
        return function_def

    @staticmethod
    def _self_member_name(node: ast.AST) -> str | None:
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "self":
                return func.attr
            return None
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
            return node.attr
        return None

    def _visit_key(self, instance: Any, action_name: str, defining_class: type | None = None) -> tuple[str, str]:
        cls = defining_class if defining_class is not None else type(instance)
        return cls.__qualname__, action_name

    def _check_and_advance_visited(
        self,
        instance: Any,
        current_action: str,
        defining_class: type | None,
        visited: frozenset[tuple[str, str]],
    ) -> frozenset[tuple[str, str]]:
        visit_key = self._visit_key(instance, current_action, defining_class)
        if visit_key in visited:
            raise AgentToolValidationError(
                f"recursive @agent_instructions call: {current_action}",
                class_name=type(instance).__name__,
                action_name=current_action,
            )
        return visited | {visit_key}

    def _find_parent_action(
        self,
        own_class: type,
        method_name: str,
        after_class: type | None,
        own_func: Callable[..., Any],
    ) -> tuple[Callable[..., Any], type] | None:
        past_anchor = after_class is None
        for klass in own_class.__mro__:
            if not past_anchor:
                past_anchor = klass is after_class
                continue
            if method_name not in klass.__dict__:
                continue
            func = klass.__dict__[method_name]
            if after_class is None and func is own_func:
                continue
            if callable(func) and getattr(func, "_is_agent_instructions", False):
                return func, klass
        return None

    def _resolve_super_func(
        self,
        instance: Any,
        method_name: str,
        *,
        after_class: type | None = None,
    ) -> tuple[Callable[..., Any], type] | None:
        own_class = type(instance)
        own_func = own_class.__dict__.get(method_name)
        if own_func is None:
            return None
        return self._find_parent_action(own_class, method_name, after_class, own_func)

    @staticmethod
    def _is_leading_docstring(statement: ast.stmt, already_skipped: bool) -> bool:
        return (
            not already_skipped
            and isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        )

    @staticmethod
    def _is_ellipsis_expr(node: ast.AST) -> bool:
        return isinstance(node, ast.Constant) and node.value is Ellipsis

    def _is_empty_action_body(self, function_def: ast.FunctionDef) -> bool:
        skipped_docstring = False
        for statement in function_def.body:
            if isinstance(statement, (ast.Pass, ast.Return)):
                continue
            if isinstance(statement, ast.Expr):
                expr_value = statement.value
                if self._is_leading_docstring(statement, skipped_docstring):
                    skipped_docstring = True
                    continue
                if self._is_ellipsis_expr(expr_value):
                    continue
                return False
            return False
        return True

    def _result_template_from(self, function_def: ast.FunctionDef) -> str:
        for statement in function_def.body:
            if isinstance(statement, ast.Return):
                return self._expression_text(statement.value)
        return ""

    def _expression_text(self, node: ast.expr | None) -> str:
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
                parts.append(self._expression_text(str_value.value))
        return "".join(parts)

    def _super_call_name(self, node: ast.AST) -> str | None:
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

    def _wrapped_member_name(self, node: ast.AST | None) -> str | None:
        if node is None:
            return None
        self_name = self._self_member_name(node)
        if self_name is not None:
            return self_name
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            return node.func.attr
        if isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _resolve_provider(self, instance: Any, provider_name: str) -> Any:
        raw = getattr(instance, provider_name)
        if getattr(type(raw), "_is_agent_toolset", False):
            return raw
        return raw() if callable(raw) else raw

    def _expand_member(
        self,
        member: str,
        target_instance: Any,
    ) -> None:
        if self._effective_mode(target_instance) == "tool":
            self._tools.append(member)
            return
        nested = target_instance.instructions[member]
        nested._scan(visited=self._visited)
        self._merge_from(nested)

    def _expand_target_member(self, member: str, target: Any) -> None:
        if target is None:
            self._tools.append(member)
            return
        target_cls = type(target)
        if member in AgentToolSet._instruction_names(target_cls):
            self._expand_member(member, target)
            return
        if member in AgentToolSet._marked_tool_names(target_cls):
            self._tools.append(member)

    def _walk_super(self) -> None:
        resolved = self._resolve_super_func(
            self.toolset, self.callable.__name__, after_class=self._defining_class,
        )
        if resolved is None:
            return
        parent_func, parent_cls = resolved
        parent = AgentInstructions(
            name=parent_func.__name__,
            callable=parent_func,
            toolset=self.toolset,
        )
        parent._scan(visited=self._visited, defining_class=parent_cls)
        self._merge_from(parent)

    def _mode_assign_value(self, statement: ast.stmt) -> str | None:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            return None
        target = statement.targets[0]
        if not isinstance(target, ast.Attribute) or target.attr != "mode":
            return None
        is_self = isinstance(target.value, ast.Name) and target.value.id == "self"
        if not is_self:
            return None
        if isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str):
            return statement.value.value
        return None

    def _loop_var_mode_assign(self, statement: ast.stmt, var_name: str) -> str | None:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            return None
        target = statement.targets[0]
        if not (
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == var_name
            and target.attr == "mode"
        ):
            return None
        if isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str):
            return statement.value.value
        return None

    def _dispatch_tools_arg(
        self,
        arg: ast.AST | None,
        *,
        loop_var: str | None = None,
        loop_item: Any = None,
    ) -> bool:
        if arg is None:
            return False
        roots = frozenset({loop_var}) if loop_var else frozenset({"self"})
        cross = (
            AgentToolSet._provider_cross_call(arg, roots)
            if isinstance(arg, ast.Call)
            else None
        )
        if cross is not None:
            provider_name, member = cross
            owner = loop_item if loop_var else self.toolset
            try:
                target = self._resolve_provider(owner, provider_name)
            except Exception as exc:  # noqa: BLE001
                self._add_prompt(f"Could not resolve `{provider_name}`: {exc}")
                self._tools.append(member)
                return True
            self._expand_target_member(member, target)
            return True
        if loop_var and isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute):
            if isinstance(arg.func.value, ast.Name) and arg.func.value.id == loop_var:
                self._expand_target_member(arg.func.attr, loop_item)
                return True
        if loop_var is None:
            member_name = self._self_member_name(arg)
            if member_name:
                self._expand_target_member(member_name, self.toolset)
                return True
        member = self._wrapped_member_name(arg)
        if member:
            self._tools.append(member)
            return True
        return False

    def _walk_for_each_wrapped(
        self,
        body_stmt: ast.stmt,
        var_name: str,
        target_item: Any,
    ) -> bool:
        if not isinstance(body_stmt, ast.Expr) or not isinstance(body_stmt.value, ast.Call):
            return False
        call = body_stmt.value
        if not isinstance(call.func, ast.Name) or call.func.id not in ("tools", "instructions"):
            return False
        arg = call.args[0] if call.args else None
        if arg is None:
            return False
        if call.func.id == "tools":
            return self._dispatch_tools_arg(arg, loop_var=var_name, loop_item=target_item)
        if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute):
            if isinstance(arg.func.value, ast.Name) and arg.func.value.id == var_name:
                self._expand_target_member(arg.func.attr, target_item)
                return True
        cross = AgentToolSet._provider_cross_call(arg, frozenset({var_name}))
        if cross is not None:
            provider_name, member = cross
            try:
                target = self._resolve_provider(target_item, provider_name)
            except Exception as exc:  # noqa: BLE001
                self._add_prompt(f"Could not resolve `{provider_name}`: {exc}")
                self._tools.append(member)
                return True
            self._expand_target_member(member, target)
            return True
        return False

    def _is_companion_for(self, stmt: ast.For) -> bool:
        if not isinstance(stmt.target, ast.Name):
            return False
        if not isinstance(stmt.iter, ast.Call):
            return False
        return self._self_member_name(stmt.iter) is not None

    @staticmethod
    def _expander_stub_tools(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("tools(...) was not handled by the @agent_instructions expander")

    @staticmethod
    def _expander_stub_instructions(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("instructions(...) was not handled by the @agent_instructions expander")

    def _execution_env(self) -> dict[str, Any]:
        import builtins

        env: dict[str, Any] = {
            "__builtins__": builtins,
            "self": self.toolset,
            "tools": AgentInstructions._expander_stub_tools,
            "instructions": AgentInstructions._expander_stub_instructions,
        }
        env.update(self._execution_locals)
        return env

    def _sync_execution_locals(self, env: dict[str, Any]) -> None:
        reserved = {"__builtins__", "self", "tools", "instructions"}
        for name, value in env.items():
            if name in reserved or name.startswith("__"):
                continue
            self._execution_locals[name] = value

    def _eval_expr(self, node: ast.expr) -> Any:
        env = self._execution_env()
        value = eval(compile(ast.Expression(node), "<agent_instructions>", "eval"), env, env)
        self._sync_execution_locals(env)
        return value

    def _execute_statement(self, statement: ast.stmt) -> None:
        env = self._execution_env()
        exec(
            compile(ast.Module(body=[statement], type_ignores=[]), "<agent_instructions>", "exec"),
            env,
            env,
        )
        self._sync_execution_locals(env)

    def _run_expr(self, node: ast.expr) -> None:
        try:
            value = self._eval_expr(node)
        except Exception:  # noqa: BLE001
            return
        if isinstance(value, str) and value.strip():
            self._add_prompt(value.strip())

    def _dispatch_for_body(
        self,
        body: list[ast.stmt],
        *,
        loop_var: str | None = None,
        loop_item: Any | None = None,
    ) -> None:
        for body_stmt in body:
            if loop_var is not None and loop_item is not None:
                mode_value = self._loop_var_mode_assign(body_stmt, loop_var)
                if mode_value is not None:
                    self._loop_item_modes[id(loop_item)] = mode_value
                    continue
                if self._walk_for_each_wrapped(body_stmt, loop_var, loop_item):
                    continue
            self._dispatch_statement(body_stmt)

    def _walk_generic_for(self, stmt: ast.For) -> None:
        if not isinstance(stmt.target, ast.Name):
            self._execute_statement(stmt)
            return
        var_name = stmt.target.id
        try:
            items = self._eval_expr(stmt.iter)
        except Exception:  # noqa: BLE001
            items = []
        if not isinstance(items, (list, tuple)):
            items = list(items) if items is not None else []
        previous = self._execution_locals.get(var_name, _EXEC_LOCAL_MISSING)
        for item in items:
            self._execution_locals[var_name] = item
            self._dispatch_for_body(stmt.body, loop_var=var_name, loop_item=item)
        if previous is _EXEC_LOCAL_MISSING:
            self._execution_locals.pop(var_name, None)
        else:
            self._execution_locals[var_name] = previous
        for body_stmt in stmt.orelse:
            self._dispatch_statement(body_stmt)

    def _dispatch_instructions_arg(self, arg: ast.AST | None) -> bool:
        if arg is None:
            return False
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            self._add_prompt(arg.value.strip())
            return True
        if isinstance(arg, ast.JoinedStr):
            self._add_prompt(self._joined_string(arg))
            return True
        cross = (
            AgentToolSet._provider_cross_call(arg, frozenset({"self"}))
            if isinstance(arg, ast.Call)
            else None
        )
        if cross is not None:
            provider_name, member = cross
            try:
                target = self._resolve_provider(self.toolset, provider_name)
            except Exception as exc:  # noqa: BLE001
                self._add_prompt(f"Could not resolve `{provider_name}`: {exc}")
                self._tools.append(member)
                return True
            self._expand_member(member, target)
            return True
        member = self._wrapped_member_name(arg)
        if member and member in AgentToolSet._instruction_names(type(self.toolset)):
            self._expand_member(member, self.toolset)
            return True
        return False

    def _dispatch_expr_statement(self, statement: ast.Expr) -> None:
        value = statement.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            self._add_prompt(value.value.strip())
            return
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
            arg = value.args[0] if value.args else None
            if value.func.id == "tools":
                if self._dispatch_tools_arg(arg):
                    return
            if value.func.id == "instructions":
                if self._dispatch_instructions_arg(arg):
                    return
        if self._super_call_name(value) is not None:
            self._walk_super()
            return
        self._run_expr(value)

    def _dispatch_statement(self, statement: ast.stmt) -> None:
        mode_value = self._mode_assign_value(statement)
        if mode_value is not None:
            self._mode = mode_value
            return
        if isinstance(statement, ast.If):
            try:
                take_body = bool(self._eval_expr(statement.test))
            except Exception:  # noqa: BLE001
                take_body = False
            branch = statement.body if take_body else statement.orelse
            for body_stmt in branch:
                self._dispatch_statement(body_stmt)
            return
        if isinstance(statement, ast.Try):
            for body_stmt in statement.body:
                self._dispatch_statement(body_stmt)
            return
        if isinstance(statement, ast.For):
            if self._is_companion_for(statement):
                self._walk_for_each_statement(statement)
            else:
                self._walk_generic_for(statement)
            return
        if isinstance(statement, ast.With):
            self._execute_statement(statement)
            return
        if isinstance(statement, ast.Expr):
            self._dispatch_expr_statement(statement)
            return
        if isinstance(statement, ast.Pass):
            return
        self._execute_statement(statement)

    def _walk_for_each_statement(self, stmt: ast.For) -> None:
        iter_node, loop_var = stmt.iter, stmt.target
        if not (isinstance(loop_var, ast.Name) and isinstance(iter_node, ast.Call)):
            return
        iter_member = self._self_member_name(iter_node)
        if iter_member is None:
            return
        try:
            items = getattr(self.toolset, iter_member)()
        except Exception:  # noqa: BLE001
            items = []
        if not isinstance(items, (list, tuple)):
            items = []
        if not items:
            items = [None]
        for target_item in items:
            self._dispatch_for_body(stmt.body, loop_var=loop_var.id, loop_item=target_item)

    def _walk_statements(self, function_def: ast.FunctionDef) -> None:
        skipped_docstring = False
        for statement in function_def.body:
            if isinstance(statement, ast.Return):
                continue
            if isinstance(statement, ast.Expr) and self._is_ellipsis_expr(statement.value):
                continue
            if self._is_leading_docstring(statement, skipped_docstring):
                skipped_docstring = True
                continue
            self._dispatch_statement(statement)

    def _read_mode(self, target: Any) -> str:
        mode = getattr(target, "mode", "instructions")
        return mode.value if isinstance(mode, ExpansionMode) else str(mode)

    def _resolve_parent_result_template(self, action_func: Callable[..., Any], instance: Any) -> str:
        resolved = self._resolve_super_func(instance, action_func.__name__)
        if resolved is None:
            return ""
        parent_func, _ = resolved
        parent = AgentInstructions(
            name=parent_func.__name__,
            callable=parent_func,
            toolset=instance,
        )
        parent_fdef = parent._require_function_def(parent_func)
        if parent_fdef is None:
            return ""
        return parent._result_template_from(parent_fdef)

    def _join_prompt(self, prompt_parts: tuple[str, ...], arguments: dict[str, Any]) -> str:
        parameter_names = set(self.parameters)
        lines = [
            self._substitute(part, arguments, parameter_names, instance=self.toolset)
            for part in prompt_parts
        ]
        return "\n\n".join(line for line in lines if line.strip())

    def _substitute(
        self,
        template: str,
        arguments: dict[str, Any],
        parameter_names: set[str],
        *,
        instance: Any | None = None,
    ) -> str:
        def replace_self(match: re.Match[str]) -> str:
            attr = match.group(1)
            if instance is None or not hasattr(instance, attr):
                raise ValueError(f"missing instance attribute {attr!r}")
            return str(getattr(instance, attr))

        def replace_param(match: re.Match[str]) -> str:
            name = match.group(1)
            if name not in parameter_names:
                return match.group(0)
            if name not in arguments:
                raise ValueError(f"missing argument {name!r}")
            return str(arguments[name])

        rendered = _SELF_PLACEHOLDER.sub(replace_self, template)
        return _PARAM_PLACEHOLDER.sub(replace_param, rendered)



def agent_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a method as a tool; description comes from the method docstring."""
    func._is_agent_tool = True
    return func

def agent_toolset(cls: type) -> type:
    """Mark a class as an agent toolset — @agent_tool and @agent_instructions."""
    if "_is_agent_toolset" in cls.__dict__:
        return cls
    if getattr(cls, "_is_agent_toolset", False):
        AgentToolSet._validate_toolset(cls)
        return cls
    if issubclass(cls, AgentToolSet):
        raise TypeError(
            f"{cls.__name__} must use @agent_toolset — do not subclass AgentToolSet directly"
        )
    merged = type(
        cls.__name__,
        (cls, AgentToolSet),
        {
            attribute_name: attribute_value
            for attribute_name, attribute_value in vars(cls).items()
            if attribute_name not in ("__dict__", "__weakref__")
        },
    )
    merged.__doc__ = cls.__doc__
    merged.__module__ = cls.__module__
    merged.__qualname__ = cls.__qualname__
    merged._is_agent_toolset = True  # type: ignore[attr-defined]
    AgentToolSet._validate_toolset(merged)
    return merged


def tools(*calls: Callable[..., Any]) -> list[Any]:
    return [call() if callable(call) else call for call in calls]


def instructions(*calls: Callable[..., Any]) -> str:
    parts: list[str] = []
    for call in calls:
        if isinstance(call, str):
            parts.append(call.strip())
        elif callable(call):
            doc = inspect.getdoc(call) or ""
            parts.append(doc.strip())
    return "\n\n".join(part for part in parts if part)


def agent_instructions(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a method as @agent_instructions; unwrapped body code runs during expand."""
    func._is_agent_instructions = True
    return func
