"""Recipe - reads an ``@agent_instructions`` recipe's source and expands it into the instructions an agent follows.

A recipe is the body of an ``@agent_instructions`` operation. *RecipeSource* reads what the body says without running
it: its function definition, whether it only defers to its parent, and the result line it returns. *RecipeExpansion*
runs the body once for one call's arguments and collects the prompt and the tools it names; it is made for that one
expansion, so two calls expanding the same operation never share what they collected. *RecipePlaceholders* fills the
``{{parameter}}`` and ``{{self.attribute}}`` placeholders of the collected text with one call's values."""

from __future__ import annotations

import ast
import builtins
import inspect
import re
import textwrap
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from harness.agent_tools.agent_tools import AgentInstructions

_PARAMETER_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")
_ATTRIBUTE_PLACEHOLDER = re.compile(r"\{\{self\.(\w+)\}\}")
_NOT_A_LOCAL = object()
# The names a recipe body reads that the expansion supplies, which a statement's own assignments never overwrite.
_RESERVED_NAMES = frozenset({"__builtins__", "self", "tools", "instructions"})


class RecipeLineFailed(Exception):
    """A line of an ``@agent_instructions`` recipe raised while the recipe was expanded into instructions.

    The message names the recipe, its file and line, and the line's source, so the broken line is found without
    re-running the expansion; the original error is kept as ``__cause__``."""

    def __init__(self, recipe: Callable[..., Any], line: ast.AST, cause: BaseException) -> None:
        self.recipe_name = recipe.__qualname__
        self.line_source = ast.unparse(line)
        self.path, self.lineno = self._file_line(recipe, line)
        super().__init__(
            f"{self.recipe_name} recipe line {self.path}:{self.lineno} `{self.line_source}` failed: "
            f"{type(cause).__name__}: {cause}"
        )

    def _file_line(self, recipe: Callable[..., Any], line: ast.AST) -> tuple[str, int]:
        """The recipe's file and the line's number in it; the recipe is parsed from its own source, so the parsed line
        number counts from the recipe's first line."""
        relative = getattr(line, "lineno", 1)
        try:
            first = inspect.getsourcelines(recipe)[1]
            path = inspect.getsourcefile(recipe) or "<unknown>"
        except (OSError, TypeError):
            return "<unknown>", relative
        return path, first + relative - 1


class RecipeCallsItself(Exception):
    """A recipe that expands, directly or through the recipes it names, back into itself, so its expansion never ends."""

    def __init__(self, toolset_class: str, recipe_name: str) -> None:
        super().__init__(f"{toolset_class}.{recipe_name}: recursive @agent_instructions call: {recipe_name}")
        self.toolset_class = toolset_class
        self.recipe_name = recipe_name


@dataclass(frozen=True)
class ExpansionMode:
    """How a toolset's recipes expand when another recipe names them: ``instructions`` expands them inline, ``tool``
    lists them as tools for the agent to call."""

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


class RecipePlaceholders:
    """One call's values for a recipe's placeholders: ``{{name}}`` takes the argument of a parameter the recipe
    declares, and ``{{self.attribute}}`` takes the attribute of the toolset the call runs on."""

    def __init__(self, arguments: dict[str, Any], parameter_names: set[str], toolset: Any = None) -> None:
        self._arguments = arguments
        self._parameter_names = parameter_names
        self._toolset = toolset

    def filled(self, template: str) -> str:
        """template with every placeholder replaced; a ``{{name}}`` that is not a parameter stays as it is.
        Raises ValueError for a parameter the call has no argument for, or an attribute the toolset lacks."""
        return _PARAMETER_PLACEHOLDER.sub(self._argument, _ATTRIBUTE_PLACEHOLDER.sub(self._attribute, template))

    def _attribute(self, match: re.Match[str]) -> str:
        attribute = match.group(1)
        if self._toolset is None or not hasattr(self._toolset, attribute):
            raise ValueError(f"missing instance attribute {attribute!r}")
        return str(getattr(self._toolset, attribute))

    def _argument(self, match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in self._parameter_names:
            return match.group(0)
        if name not in self._arguments:
            raise ValueError(f"missing argument {name!r}")
        return str(self._arguments[name])


class RecipeSource:
    """What a recipe's source says, read without running it."""

    def __init__(self, recipe: Callable[..., Any]) -> None:
        self._recipe = recipe

    @property
    def module(self) -> ast.Module:
        return ast.parse(textwrap.dedent(inspect.getsource(self._recipe)))

    @property
    def function_def(self) -> ast.FunctionDef:
        function_def = self.module.body[0]
        if not isinstance(function_def, ast.FunctionDef):
            raise RecipeNotAFunction(self._recipe)
        return function_def

    @property
    def only_defers_to_parent(self) -> bool:
        """True when the body holds nothing but a docstring, ``...``, ``pass``, or an empty return, so the recipe is
        its parent class's recipe."""
        statements = [statement for statement in self.function_def.body if not isinstance(statement, ast.Pass)]
        if statements and self.is_docstring(statements[0]):
            statements = statements[1:]
        returns = [statement for statement in statements if isinstance(statement, ast.Return)]
        others = [statement for statement in statements if not isinstance(statement, ast.Return)]
        if not all(isinstance(statement, ast.Expr) and self.is_ellipsis(statement.value) for statement in others):
            return False
        return bool(others) or all(self._is_empty_return(statement) for statement in returns)

    @property
    def result_template(self) -> str:
        """The text the recipe's first ``return`` gives, with its names written as placeholders; empty when it has
        none."""
        returned = next((statement for statement in self.function_def.body if isinstance(statement, ast.Return)), None)
        return self.text_of(returned.value) if returned is not None else ""

    def text_of(self, node: ast.expr | None) -> str:
        """An expression as recipe text: a string as it is, ``self.x`` as ``{{self.x}}``, a name as ``{{name}}``."""
        if node is None:
            return ""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value.strip()
        if isinstance(node, ast.JoinedStr):
            return "".join(self._part_text(part) for part in node.values)
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
            return "{{self." + node.attr + "}}"
        if isinstance(node, ast.Name):
            return "{{" + node.id + "}}"
        return ast.unparse(node)

    def member_on_self(self, node: ast.AST) -> str | None:
        """The member a ``self.member`` or ``self.member(...)`` expression names; none for any other expression."""
        target = node.func if isinstance(node, ast.Call) else node
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
            return target.attr
        return None

    def provider_member(self, node: ast.AST, roots: frozenset[str] = frozenset({"self"})) -> tuple[str, str] | None:
        """The provider and member ``<root>.<provider>().<member>()``, ``<root>.<provider>.<member>()``, or the same
        chains without the last call name, for a root in roots; none for any other expression."""
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            member, provider = node.func.attr, node.func.value
        elif isinstance(node, ast.Attribute):
            member, provider = node.attr, node.value
        else:
            return None
        provider = provider.func if isinstance(provider, ast.Call) else provider
        if not (isinstance(provider, ast.Attribute) and isinstance(provider.value, ast.Name)):
            return None
        return (provider.attr, member) if provider.value.id in roots else None

    def loop_providers(self) -> set[str]:
        """The members a ``for item in self.member():`` loop in the body iterates."""
        return {
            member for node in ast.walk(self.module) if isinstance(node, ast.For)
            and (member := self.member_on_self(node.iter)) is not None
        }

    def _part_text(self, part: ast.expr) -> str:
        if isinstance(part, ast.Constant) and isinstance(part.value, str):
            return part.value
        return self.text_of(part.value) if isinstance(part, ast.FormattedValue) else ""

    def is_docstring(self, statement: ast.stmt) -> bool:
        return isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str)

    def is_ellipsis(self, node: ast.AST) -> bool:
        return isinstance(node, ast.Constant) and node.value is Ellipsis

    def _is_empty_return(self, statement: ast.Return) -> bool:
        return statement.value is None or (isinstance(statement.value, ast.Constant) and statement.value.value in ("", None))


class RecipeNotAFunction(Exception):
    """A recipe whose source does not parse to a function definition, such as a lambda."""

    def __init__(self, recipe: Callable[..., Any]) -> None:
        super().__init__(f"{recipe.__qualname__}: action body is not a function")


@dataclass(frozen=True)
class _LoopItem:
    """One pass of a ``for`` loop in a recipe: the loop variable's name and the item it holds on this pass, so
    ``tools(item.member)`` and ``instructions(item.member)`` expand that item's member."""

    name: str
    item: Any


class RecipeExpansion:
    """One expansion of one recipe: it runs the body for one call's arguments and collects the prompt lines and the tool
    names the body gives. A recipe it names expands in an expansion of its own, which shares the recipes already being
    expanded so a recipe that names itself fails rather than recursing forever."""

    def __init__(
        self,
        instructions: AgentInstructions,
        arguments: dict[str, Any] | None = None,
        *,
        expanding: frozenset[tuple[str, str]] = frozenset(),
        defining_class: type | None = None,
    ) -> None:
        self._instructions = instructions
        self._toolset = instructions.toolset
        self._recipe = instructions.callable
        self._source = RecipeSource(self._recipe)
        self._defining_class = defining_class
        self._expanding = self._expanding_with_this(expanding)
        self._mode = self._declared_mode(self._toolset)
        self._prompt: list[str] = []
        self._tools: list[str] = []
        self._loop_item_modes: dict[int, str] = {}
        self._locals = {**self._parameter_defaults(), **(arguments or {})}

    @property
    def prompt(self) -> tuple[str, ...]:
        return tuple(self._prompt)

    @property
    def tools(self) -> list[str]:
        return list(dict.fromkeys(self._tools))

    def run(self) -> RecipeExpansion:
        """Walk the body, or the parent's recipe when the body only defers to it; answers this expansion."""
        if self._source.only_defers_to_parent:
            self._expand_parent()
            return self
        statements = self._source.function_def.body
        if statements and self._source.is_docstring(statements[0]):
            self._add_prompt(statements[0].value.value.strip())
            statements = statements[1:]
        for statement in statements:
            self._walk_body_statement(statement)
        return self

    def _expanding_with_this(self, expanding: frozenset[tuple[str, str]]) -> frozenset[tuple[str, str]]:
        owner = self._defining_class if self._defining_class is not None else type(self._toolset)
        key = (owner.__qualname__, self._recipe.__name__)
        if key in expanding:
            raise RecipeCallsItself(type(self._toolset).__name__, self._recipe.__name__)
        return expanding | {key}

    def _parameter_defaults(self) -> dict[str, Any]:
        try:
            parameters = inspect.signature(self._recipe).parameters.values()
        except (TypeError, ValueError):
            return {}
        skipped = (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        return {
            parameter.name: None if parameter.default is inspect.Parameter.empty else parameter.default
            for parameter in parameters if parameter.name not in {"self", "cls"} and parameter.kind not in skipped
        }

    def _walk_body_statement(self, statement: ast.stmt) -> None:
        if isinstance(statement, ast.Return):
            self._add_returned(statement)
            return
        if isinstance(statement, ast.Expr) and self._source.is_ellipsis(statement.value):
            return
        self._walk(statement)

    def _add_returned(self, statement: ast.Return) -> None:
        if statement.value is None:
            return
        value = self._evaluated(statement.value)
        if isinstance(value, str) and value.strip():
            self._add_prompt(value.strip())

    def _add_prompt(self, text: str) -> None:
        if text and text not in self._prompt:
            self._prompt.append(text)

    def _merge(self, other: RecipeExpansion) -> None:
        self._tools.extend(other._tools)
        for part in other._prompt:
            self._add_prompt(part)

    def _expand_nested(self, nested: AgentInstructions, defining_class: type | None = None) -> None:
        self._merge(RecipeExpansion(nested, expanding=self._expanding, defining_class=defining_class).run())

    def _expand_parent(self) -> None:
        parent = self._instructions.parent_recipe(self._defining_class)
        if parent is not None:
            self._expand_nested(*parent)

    def _mode_of(self, target: Any) -> str:
        if target is self._toolset:
            return self._mode
        return self._loop_item_modes.get(id(target)) or self._declared_mode(target)

    def _declared_mode(self, target: Any) -> str:
        """The mode target's recipes expand in; ``instructions`` for an object that names none."""
        return str(getattr(target, "mode", "instructions"))

    def _expand_member(self, member: str, target: Any) -> None:
        if self._mode_of(target) == "tool":
            self._tools.append(member)
            return
        self._expand_nested(self._instructions.member_of(target, member))

    def _expand_target_member(self, member: str, target: Any) -> None:
        if target is None:
            self._tools.append(member)
            return
        members = self._instructions.members_of(target)
        if member in members.instruction_names:
            self._expand_member(member, target)
            return
        if member in members.tool_names:
            self._tools.append(member)

    def _provider(self, owner: Any, provider_name: str, line: ast.AST) -> Any:
        """The object owner's provider gives, as the recipe line names it; a provider that raises fails the line."""
        try:
            return self._instructions.provider_of(owner, provider_name)
        except Exception as exc:  # noqa: BLE001 - re-raised as the recipe line that failed, with the cause kept
            raise RecipeLineFailed(self._recipe, line, exc) from exc

    # -- tools(...) and instructions(...) -------------------------------------------------------------------------

    def _expand_cross_arg(self, arg: ast.AST, loop: _LoopItem | None = None) -> bool:
        cross = self._source.provider_member(arg, frozenset({loop.name}) if loop else frozenset({"self"}))
        if cross is None:
            return False
        owner = loop.item if loop else self._toolset
        provider_name, member = cross
        if owner is not None:
            self._expand_target_member(member, self._provider(owner, provider_name, arg))
        return True

    def _attribute_chain(self, node: ast.AST) -> list[str]:
        names: list[str] = []
        while isinstance(node, ast.Attribute):
            names.append(node.attr)
            node = node.value
        return [node.id, *reversed(names)] if isinstance(node, ast.Name) else []

    def _loop_item_instructions(self, arg: ast.AST, loop: _LoopItem) -> bool:
        names = self._attribute_chain(arg)
        if loop.item is None or not names or names[0] != loop.name:
            return False
        target: Any = loop.item
        for name in names[1:-1]:
            target = getattr(target, name, None)
            if target is None:
                return False
        self._expand_target_member(names[-1], target)
        return True

    def _expand_instructions_cross(self, arg: ast.AST) -> bool:
        cross = self._source.provider_member(arg)
        if cross is None:
            return False
        provider_name, member = cross
        self._expand_member(member, self._provider(self._toolset, provider_name, arg))
        return True

    def _loop_member(self, arg: ast.AST, loop: _LoopItem | None) -> str | None:
        """The member ``item.member`` or ``item.member()`` names on the loop's item; none for any other expression."""
        target = arg.func if isinstance(arg, ast.Call) else arg
        if loop is None or not isinstance(target, ast.Attribute):
            return None
        return target.attr if isinstance(target.value, ast.Name) and target.value.id == loop.name else None

    def _wrapped_member_name(self, node: ast.AST | None) -> str | None:
        if node is None:
            return None
        on_self = self._source.member_on_self(node)
        if on_self is not None:
            return on_self
        target = node.func if isinstance(node, ast.Call) else node
        return target.attr if isinstance(target, ast.Attribute) else None

    def _expand_tools_arg(self, arg: ast.AST | None, loop: _LoopItem | None = None) -> bool:
        if arg is None:
            return False
        if self._expand_cross_arg(arg, loop):
            return True
        loop_member = self._loop_member(arg, loop) if isinstance(arg, ast.Call) else None
        if loop_member is not None:
            self._expand_target_member(loop_member, loop.item)
            return True
        on_self = self._source.member_on_self(arg) if loop is None else None
        if on_self:
            self._expand_target_member(on_self, self._toolset)
            return True
        member = self._wrapped_member_name(arg)
        if member:
            self._tools.append(member)
        return bool(member)

    def _expand_instructions_arg(self, arg: ast.AST | None) -> bool:
        if arg is None:
            return False
        if isinstance(arg, ast.JoinedStr) or (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
            self._add_prompt(self._source.text_of(arg))
            return True
        if self._expand_instructions_cross(arg):
            return True
        member = self._wrapped_member_name(arg)
        if member and member in self._instructions.members_of(self._toolset).instruction_names:
            self._expand_member(member, self._toolset)
            return True
        value = self._evaluated(arg)
        if isinstance(value, str) and value.strip():
            self._add_prompt(value.strip())
            return True
        return False

    def _expand_loop_wrapper(self, statement: ast.stmt, loop: _LoopItem) -> bool:
        """A ``tools(...)`` or ``instructions(...)`` line inside a loop over a provider's items."""
        call = statement.value if isinstance(statement, ast.Expr) else None
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.args):
            return False
        if call.func.id == "tools":
            return self._expand_tools_arg(call.args[0], loop)
        if call.func.id != "instructions":
            return False
        arg = call.args[0]
        loop_member = self._loop_member(arg, loop)
        if loop_member is not None:
            self._expand_target_member(loop_member, loop.item)
            return True
        return self._loop_item_instructions(arg, loop) or self._expand_cross_arg(arg, loop)

    # -- running the body's statements ----------------------------------------------------------------------------

    def _environment(self) -> dict[str, Any]:
        # The recipe's module comes after the stand-ins, so the module's own ``tools`` and ``instructions`` run inside
        # an expression such as ``text = instructions(...)``; only a line the expansion reads itself uses neither.
        environment: dict[str, Any] = {
            "__builtins__": builtins,
            "self": self._toolset,
            "tools": self._unhandled_tools,
            "instructions": self._unhandled_instructions,
        }
        module = inspect.getmodule(self._recipe)
        if module is not None:
            environment.update(vars(module))
        environment.update(self._locals)
        return environment

    def _unhandled_tools(self, *_arguments: Any, **_named: Any) -> None:
        raise RuntimeError("tools(...) was not handled by the @agent_instructions expander")

    def _unhandled_instructions(self, *_arguments: Any, **_named: Any) -> None:
        raise RuntimeError("instructions(...) was not handled by the @agent_instructions expander")

    def _keep_locals(self, environment: dict[str, Any]) -> None:
        self._locals.update(
            (name, value) for name, value in environment.items() if name not in _RESERVED_NAMES and not name.startswith("__")
        )

    def _evaluated(self, node: ast.expr) -> Any:
        environment = self._environment()
        code = compile(ast.Expression(node), "<agent_instructions>", "eval")
        value = self._ran(lambda: eval(code, environment, environment), node)
        self._keep_locals(environment)
        return value

    def _execute(self, statement: ast.stmt) -> None:
        environment = self._environment()
        code = compile(ast.Module(body=[statement], type_ignores=[]), "<agent_instructions>", "exec")
        self._ran(lambda: exec(code, environment, environment), statement)
        self._keep_locals(environment)

    def _ran(self, line: Callable[[], Any], node: ast.AST) -> Any:
        try:
            return line()
        except RecipeLineFailed:
            raise
        except Exception as exc:  # noqa: BLE001 - re-raised as the recipe line that failed, with the cause kept
            raise RecipeLineFailed(self._recipe, node, exc) from exc

    def _add_evaluated(self, node: ast.expr) -> None:
        value = self._evaluated(node)
        texts = value if isinstance(value, (list, tuple)) else [value]
        for text in texts:
            if isinstance(text, str) and text.strip():
                self._add_prompt(text.strip())

    def _walk(self, statement: ast.stmt) -> None:
        mode = self._assigned_mode(statement, "self")
        if mode is not None:
            self._mode = mode
        elif isinstance(statement, ast.If):
            for branch_statement in statement.body if self._evaluated(statement.test) else statement.orelse:
                self._walk(branch_statement)
        elif isinstance(statement, ast.Try):
            for body_statement in statement.body:
                self._walk(body_statement)
        elif isinstance(statement, ast.For):
            self._walk_loop(statement)
        elif isinstance(statement, ast.Expr):
            self._walk_expression(statement.value)
        elif not isinstance(statement, ast.Pass):
            self._execute(statement)

    def _assigned_mode(self, statement: ast.stmt, receiver: str) -> str | None:
        """The mode a ``receiver.mode = "tool"`` line sets; none for any other line."""
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            return None
        target = statement.targets[0]
        if not (isinstance(target, ast.Attribute) and target.attr == "mode" and isinstance(target.value, ast.Name)):
            return None
        value = statement.value
        if target.value.id != receiver or not (isinstance(value, ast.Constant) and isinstance(value.value, str)):
            return None
        return value.value

    def _walk_expression(self, value: ast.expr) -> None:
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            self._add_prompt(value.value.strip())
            return
        if self._calls_super(value):
            self._expand_parent()
            return
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
            arg = value.args[0] if value.args else None
            if value.func.id == "tools" and self._expand_tools_arg(arg):
                return
            if value.func.id == "instructions" and self._expand_instructions_arg(arg):
                return
        if isinstance(value, ast.Call):
            self._walk_member_call(value)
            return
        self._add_evaluated(value)

    def _calls_super(self, node: ast.AST) -> bool:
        """True for ``super().member(...)``."""
        receiver = node.func.value if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) else None
        return isinstance(receiver, ast.Call) and isinstance(receiver.func, ast.Name) and receiver.func.id == "super"

    def _walk_member_call(self, value: ast.Call) -> None:
        member = self._wrapped_member_name(value)
        if not member:
            self._add_evaluated(value)
            return
        target = self._toolset
        provider = self._source.member_on_self(value.func.value) if isinstance(value.func, ast.Attribute) and isinstance(value.func.value, ast.Call) else None
        if provider:
            target = self._provider(self._toolset, provider, value)
        members = self._instructions.members_of(target) if target is not None else None
        if members is None or member in members.instruction_names:
            self._expand_target_member(member, target)
            return
        if member in members.tool_names:
            self._expand_target_member(member, target)
        self._add_evaluated(value)

    def _walk_loop(self, statement: ast.For) -> None:
        if not isinstance(statement.target, ast.Name):
            self._execute(statement)
            return
        if isinstance(statement.iter, ast.Call) and self._source.member_on_self(statement.iter) is not None:
            self._walk_provider_loop(statement)
            return
        name = statement.target.id
        items = self._evaluated(statement.iter)
        previous = self._locals.get(name, _NOT_A_LOCAL)
        for item in items if isinstance(items, (list, tuple)) else list(items or []):
            self._locals[name] = item
            self._walk_loop_body(statement.body, _LoopItem(name, item))
        if previous is _NOT_A_LOCAL:
            self._locals.pop(name, None)
        else:
            self._locals[name] = previous
        for else_statement in statement.orelse:
            self._walk(else_statement)

    def _walk_provider_loop(self, statement: ast.For) -> None:
        """A ``for item in self.member():`` loop. A provider that gives no items is walked once without one, so the
        loop's body still lists the tools it names."""
        items = self._evaluated(statement.iter)
        for item in (items if isinstance(items, (list, tuple)) else []) or [None]:
            self._walk_loop_body(statement.body, _LoopItem(statement.target.id, item))

    def _walk_loop_body(self, body: list[ast.stmt], loop: _LoopItem) -> None:
        for statement in body:
            if self._reads_missing_loop_item(statement, loop):
                continue
            if loop.item is not None and self._walk_loop_item_statement(statement, loop):
                continue
            self._walk(statement)

    def _walk_loop_item_statement(self, statement: ast.stmt, loop: _LoopItem) -> bool:
        mode = self._assigned_mode(statement, loop.name)
        if mode is not None:
            self._loop_item_modes[id(loop.item)] = mode
            return True
        return self._expand_loop_wrapper(statement, loop)

    def _reads_missing_loop_item(self, statement: ast.stmt, loop: _LoopItem) -> bool:
        """An ``instructions(item...)`` line on the pass a loop makes without an item, which it makes only to list
        the tools its body names: there is no item to read instructions from, so the line adds nothing."""
        call = statement.value if loop.item is None and isinstance(statement, ast.Expr) else None
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "instructions"):
            return False
        return bool(call.args) and self._roots_at(call.args[0], loop.name)

    def _roots_at(self, node: ast.AST, name: str) -> bool:
        """True when an attribute or call chain such as ``item.rules.markdown_block`` starts at the name."""
        while isinstance(node, (ast.Attribute, ast.Call)):
            node = node.func if isinstance(node, ast.Call) else node.value
        return isinstance(node, ast.Name) and node.id == name
