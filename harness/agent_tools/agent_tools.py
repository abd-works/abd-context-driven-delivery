"""Agent toolset — register, introspect, and validate one decorated AgentToolSet."""
from __future__ import annotations

import ast
import functools
import importlib.util
import inspect
import re
import sys
import textwrap
import types
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, ClassVar, Mapping, cast, get_args, get_origin, get_type_hints

from harness.name.name import Name
from harness.agent_tools.parameter_schema import ParameterSchema
from harness.agent_tools.tool_call import ToolCall
from harness.markdown.markdown import Markdown, MarkdownCollection
from harness.marks.mark import Mark, mark_kinds
from harness.agent_tools.recipe import ExpansionMode, ExpansionResult, RecipeExpansion, RecipePlaceholders, RecipeSource

ContextDocument = dict[str, Any]
ArgumentDocument = dict[str, Any]
TypeAnnotation = Any
# A `@tool_subject` loader or a class tool that takes this argument is handed the checkout of the project its call works
# on. No caller passes it, so it is not one of the tool's arguments.
CALLED_PROJECT = "project"


class CallNamesNoProject(Exception):
    """A tool that acts on a project's objects was called without naming the project, so it cannot tell which project's
    board, tickets, or files to load."""

    def __init__(self, tool: str) -> None:
        super().__init__(f"{tool} acts on a project's objects, but its call names no project")
        self.tool = tool


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


class ToolSetCollection:
    """Named child toolsets, iterated in entry order. The collection itself may have tools."""

    def __init__(self, entries: dict[str, Any] | None = None, parent: Any = None) -> None:
        self.entries: dict[str, Any] = dict(entries or {})
        self.parent = parent

    def __iter__(self):
        return iter(self.entries.values())

    def __len__(self) -> int:
        return len(self.entries)

    def __bool__(self) -> bool:
        return bool(self.entries)

    @property
    def name(self) -> str:
        return Name(type(self).__name__).snake

    @property
    def slug(self) -> str:
        return Name(self.name).kebab

    @property
    def registration_name(self) -> str:
        typ = type(self)
        return f"{typ.__module__}:{typ.__name__}"

    def attach(self, instance: Any, name: str | None = None) -> None:
        MarkdownCollection.attach(self, instance, name)

    @property
    def tools(self) -> dict[str, AgentTool]:
        """Tools declared on this collection, not on its entries."""
        members = ToolsetMembers(type(self))
        return {
            name: AgentTool(name=name, callable=members.callable_on(self, name, member), toolset=self)
            for name, member in members.marked
        }


class Collect:
    """Aggregate the same-named property across a collection's children: ``@collect`` on a collection's property
    answers its children's values joined as text, or bundled into the property's declared return type."""

    def __new__(cls, operation: Callable[..., Any]) -> property:
        return object.__new__(cls)._property(operation)

    def _property(self, operation: Callable[..., Any]) -> property:
        self._name = operation.__name__
        self._return_type = self._declared_return(operation)

        def getter(owner: Any) -> Any:
            return self.of(owner)

        getter.__doc__ = operation.__doc__
        getter.__name__ = self._name
        getter.__annotations__ = dict(getattr(operation, "__annotations__", {}))
        mark_kinds.copy_marks(operation, getter)
        return property(getter)

    def of(self, collection: Any) -> Any:
        """The collected value of this property on collection's children."""
        if self._return_type is str or self._return_type in (inspect.Signature.empty, None):
            return "\n\n".join(value for child in collection if (value := self._value(child)))
        return self._bundled(collection)

    def _value(self, child: Any) -> Any:
        value = getattr(child, self._name, None)
        return value() if callable(value) else value

    def _bundled(self, collection: Any) -> Any:
        entries = getattr(collection, "entries", None)
        if not isinstance(entries, dict):
            entries = {getattr(child, "name", str(index)): child for index, child in enumerate(collection)}
        bundled = {key: self._value(child) for key, child in entries.items()}
        if "parent" in inspect.signature(self._return_type).parameters:
            return self._return_type(bundled, parent=collection)
        return self._return_type(bundled)

    def _declared_return(self, operation: Callable[..., Any]) -> Any:
        try:
            hints = get_type_hints(operation, globalns=getattr(operation, "__globals__", None))
        except (NameError, TypeError, AttributeError):
            hints = dict(getattr(operation, "__annotations__", {}) or {})
        return hints.get("return", str)


collect = Collect


class ToolsetMembers:
    """The members of one toolset class and which of them its marks make tools. A class's functions and properties are
    fixed once it is imported, and every hook dispatch asks this of every toolset, so each class is walked once."""

    _walked: ClassVar[dict[type, list[tuple[str, Any]]]] = {}

    def __init__(self, owner: type) -> None:
        self._owner = owner

    @property
    def every(self) -> list[tuple[str, Any]]:
        """Every function, class or static method, and property getter on the class, by name."""
        walked = ToolsetMembers._walked.get(self._owner)
        if walked is None:
            walked = ToolsetMembers._walked[self._owner] = self._walk()
        return walked

    @property
    def marked(self) -> list[tuple[str, Any]]:
        """The members that are tools: marked ``@agent_tool`` or ``@agent_instructions``, or enlisted by a destination
        such as a hook."""
        return [(name, member) for name, member in self.every if self.is_tool(member)]

    @property
    def tool_names(self) -> set[str]:
        return {name for name, member in self.marked if AgentToolMark.marks(member)}

    @property
    def instruction_names(self) -> frozenset[str]:
        return frozenset(name for name, member in self.marked if AgentInstructionsMark.marks(member))

    def is_tool(self, member: Any) -> bool:
        return AgentToolMark.marks(member) or AgentInstructionsMark.marks(member) or mark_kinds.enlisting(member)

    def is_rules(self, member: Any) -> bool:
        return mark_kinds.marked_for(InstallDestination.RULE, member)

    def declared(self, name: str) -> Any:
        """The attribute name as the nearest class in the class order defines it, before Python resolves it."""
        return next((base.__dict__[name] for base in self._owner.__mro__ if name in base.__dict__), None)

    def callable_on(self, instance: Any, name: str, member: Any) -> Any:
        """The member as instance calls it: a static or class method on the class, an operation bound to instance."""
        declared = self.declared(name)
        if isinstance(declared, staticmethod):
            return declared.__func__
        if isinstance(declared, classmethod):
            return declared.__get__(None, self._owner)
        if inspect.isfunction(member) and getattr(self._owner, name, None) is member:
            return getattr(instance, name)
        return member

    def _walk(self) -> list[tuple[str, Any]]:
        seen: set[str] = set()
        members: list[tuple[str, Any]] = []
        for name, member in inspect.getmembers(self._owner, predicate=inspect.isfunction):
            declared = self.declared(name)
            seen.add(name)
            members.append((name, self._marked_function(declared) if isinstance(declared, (staticmethod, classmethod)) else member))
        for base in self._owner.__mro__:
            for name, declared in base.__dict__.items():
                if name not in seen and isinstance(declared, (staticmethod, classmethod)):
                    seen.add(name)
                    members.append((name, self._marked_function(declared)))
        for name, member in inspect.getmembers(self._owner, predicate=inspect.isdatadescriptor):
            getter = getattr(member, "fget", None)
            if getter is not None and name not in seen:
                members.append((name, getter))
        return members

    def _marked_function(self, declared: staticmethod | classmethod) -> Any:
        """The function a static or class method wraps, carrying the marks set on the wrapper."""
        function = declared.__func__
        for flag in mark_kinds.copied_flags:
            if getattr(declared, flag, None) and not getattr(function, flag, None):
                setattr(function, flag, getattr(declared, flag))
        return function


class ToolsetReference:
    """A toolset named the way configuration and the installer name it: ``<module>:<Class>``. A module whose folder
    names use hyphens on disk, such as ``agent-bdd``, is found by its underscored name too."""

    _SEARCH_FOLDERS = ("harness", "tools", "cdd_guidance/practices", "cdd_guidance/actions", "cdd_guidance/builders")

    def __init__(self, reference: str) -> None:
        self._module_name, _, self._class_name = reference.partition(":")
        if not self._class_name:
            raise ValueError(f"expected <module>:<Class>, got {reference!r}")
        self._reference = reference

    @property
    def toolset_class(self) -> type:
        """The ``@agent_toolset`` class the reference names. Raises TypeError for a class that is not one."""
        loaded = getattr(self._module, self._class_name)
        if not (isinstance(loaded, type) and AgentToolSetMark.marks(loaded)):
            raise TypeError(f"{self._reference} is not a @agent_toolset class")
        return loaded

    @property
    def _module(self) -> types.ModuleType:
        try:
            return importlib.import_module(self._module_name)
        except ModuleNotFoundError:
            return self._module_from_hyphenated_folders()

    def _module_from_hyphenated_folders(self) -> types.ModuleType:
        module_file = self._module_file()
        spec = importlib.util.spec_from_file_location(self._module_name, module_file)
        if spec is None or spec.loader is None:
            raise ModuleNotFoundError(f"Cannot create spec for {module_file}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[self._module_name] = module
        spec.loader.exec_module(module)
        return module

    def _module_file(self) -> Path:
        repository = Path(__file__).resolve().parents[2]
        roots = [repository, *(repository / folder for folder in self._SEARCH_FOLDERS)]
        for root in roots:
            located = self._file_under(root, self._module_name.split("."))
            if located is not None:
                return located
        raise ModuleNotFoundError(f"No module named {self._module_name!r} (also tried under {roots})")

    def _file_under(self, root: Path, parts: list[str]) -> Path | None:
        folder = root
        for part in parts[:-1]:
            folder = next((folder / name for name in (part.replace("_", "-"), part) if (folder / name).is_dir()), None)
            if folder is None:
                return None
        candidate = folder / f"{parts[-1]}.py"
        return candidate if candidate.exists() else None


class ToolsetValidator:
    """Checks one ``@agent_toolset`` class as it is defined: every ``@agent_instructions`` recipe takes the receiver
    its kind of operation takes, and every ``tools(...)`` or ``instructions(...)`` line names a member the toolset
    has, a loop's item, or a provider the recipe reads. A broken recipe fails where the class is defined rather than
    when an agent first calls it."""

    def __init__(self, toolset_class: type) -> None:
        self._toolset_class = toolset_class
        self._members = ToolsetMembers(toolset_class)

    def validate(self) -> None:
        """Raises AgentToolValidationError naming the recipe and what is wrong with it."""
        allowed = self._members.tool_names | set(self._members.instruction_names)
        for name, member in self._members.every:
            if AgentInstructionsMark.marks(member):
                self._validate_recipe(member, self._receiver(name), allowed)

    def _receiver(self, name: str) -> str | None:
        declared = self._members.declared(name)
        if isinstance(declared, staticmethod):
            return None
        return "cls" if isinstance(declared, classmethod) else "self"

    def _validate_recipe(self, recipe: Callable[..., Any], receiver: str | None, allowed: set[str]) -> None:
        if receiver is not None:
            self._validate_receiver(recipe, receiver)
        source = RecipeSource(recipe)
        providers = {cross[0] for node in ast.walk(source.module) if (cross := source.provider_member(node)) is not None}
        _RecipeLinesValidator(
            source=source,
            allowed_names=allowed,
            all_providers=providers | source.loop_providers(),
            class_name=self._toolset_class.__name__,
            action_name=recipe.__name__,
        ).visit(source.module)

    def _validate_receiver(self, recipe: Callable[..., Any], receiver: str) -> None:
        parameters = list(inspect.signature(recipe).parameters.values())
        where = {"class_name": self._toolset_class.__name__, "action_name": recipe.__name__}
        if not parameters or parameters[0].name != receiver:
            raise AgentToolValidationError(f"first parameter must be named '{receiver}'", **where)
        if parameters[0].default is not inspect.Parameter.empty:
            raise AgentToolValidationError(f"{receiver} parameter must not have a default", **where)


class _RecipeLinesValidator(ast.NodeVisitor):
    """Validate ``tools(...)`` and ``instructions(...)`` in one ``@agent_instructions`` body: raises
    ``AgentToolValidationError`` when a line names a member that is not an allowed ``@agent_tool``,
    ``@agent_instructions`` peer, loop item, or provider the recipe reads."""

    def __init__(
        self,
        *,
        source: RecipeSource,
        allowed_names: set[str],
        all_providers: set[str],
        class_name: str,
        action_name: str,
    ) -> None:
        self._source = source
        self._allowed_names = allowed_names
        self._all_providers = all_providers
        self._class_name = class_name
        self._action_name = action_name
        self._loop_vars: list[str] = []

    def visit_For(self, node: ast.For) -> None:
        if not isinstance(node.target, ast.Name):
            self.generic_visit(node)
            return
        self._loop_vars.append(node.target.id)
        self.generic_visit(node)
        self._loop_vars.pop()

    def visit_Call(self, node: ast.Call) -> None:
        wrapper = node.func.id if isinstance(node.func, ast.Name) and node.func.id in ("tools", "instructions") else None
        if wrapper is not None and self._validate_wrapper_arg(wrapper, node.args[0] if node.args else None):
            return
        self.generic_visit(node)

    def _validate_wrapper_arg(self, wrapper: str, arg: ast.AST | None) -> bool:
        if arg is None:
            if wrapper == "tools":
                self._fail(f"{wrapper}(...) requires one argument")
            return False
        if self._names_provider_or_loop_item(arg):
            return True
        member = self._source.member_on_self(arg)
        if member is not None:
            self._check_member(member)
            return True
        if wrapper == "tools":
            self._fail(f"{wrapper}(...) argument is not a recognized tool step")
        return False

    def _names_provider_or_loop_item(self, arg: ast.AST) -> bool:
        if self._source.provider_member(arg) is not None:
            return True
        if self._loop_vars and self._source.provider_member(arg, frozenset(self._loop_vars)) is not None:
            return True
        target = arg.func if isinstance(arg, ast.Call) else arg
        return isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id in self._loop_vars

    def _check_member(self, member_name: str) -> None:
        if member_name not in self._allowed_names and member_name not in self._all_providers:
            self._fail(f"{member_name!r} is not an allowed tool step")

    def _fail(self, message: str) -> None:
        raise AgentToolValidationError(message, class_name=self._class_name, action_name=self._action_name)


class AgentToolSetOrigin:
    """Where a toolset lives and what it is called."""

    domain_slug: str | None = None

    @property
    def name(self) -> str:
        stored = getattr(self, "_name", None)
        if isinstance(stored, str) and stored:
            return stored
        return Name(type(self).__name__).snake

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def slug(self) -> str:
        return Name(self.domain_slug or type(self).__name__).kebab

    @property
    def install_folder(self) -> Path:
        try:
            return Path(inspect.getfile(type(self))).resolve().parent
        except (TypeError, OSError):
            return Path(self.slug)

    @property
    def registration_name(self) -> str:
        typ = type(self)
        return f"{typ.__module__}:{typ.__name__}"

    @property
    def description(self) -> str:
        return (self.__class__.__doc__ or "").strip()


class AgentToolSet(AgentToolSetOrigin):
    """Injected by @agent_toolset — the operations, instructions, and nested collections of one toolset as the tools it
    publishes."""

    _mode: str = "instructions"
    HOSTED_ONLY_CLASS_NAMES: ClassVar[frozenset[str]] = frozenset(
        {
            "RulesCollection",
            "MarkdownCollection",
            "GuidanceCollection",
            "PracticeGuidance",
            "FidelityGuidance",
        }
    )
    """Classes whose tools run only through the practice or toolset that holds them. Install and the hook server skip
    them by class name, because the installer reads class names from source without importing it."""
    parameter_notes: ClassVar[dict[str, str]] = {}
    """What an agent reads about a parameter, by its name, after the description of every tool on this toolset that
    takes it; a guidance action explains its ``guidance`` parameter this way."""
    _COLLECTION_SKIP = frozenset({"tools", "operations", "instructions", "mode"})

    @property
    def mode(self) -> ExpansionMode:
        """Execution mode for @agent_instructions calls into this instance.
        instructions = expand inline; tool = list action in tools, defer its body."""
        return ExpansionMode(self._mode)

    @mode.setter
    def mode(self, new_mode: str | ExpansionMode) -> None:
        self._mode = ExpansionMode(str(new_mode)).value

    @classmethod
    def instantiate(cls, toolset: Any = None) -> Any:
        """A toolset made from what configuration names: a ``<module>:<Class>`` reference, ``{"toolset": reference,
        "context": {...}}`` with the constructor's arguments, a toolset class, or a toolset already made."""
        if toolset is None:
            return cls()
        if isinstance(toolset, dict) and "toolset" in toolset:
            context = dict(toolset.get("context") or {})
            for key, value in toolset.items():
                if key not in {"toolset", "context"}:
                    context.setdefault(key, value)
            return cls._made(ToolsetReference(str(toolset["toolset"])).toolset_class, context)
        if isinstance(toolset, dict):
            return cls(**toolset)
        if isinstance(toolset, str):
            return cls._made(ToolsetReference(toolset).toolset_class, {})
        if isinstance(toolset, type):
            return cls._made(toolset, {})
        return toolset

    @classmethod
    def from_items(cls, items: list[Any], *, context: dict[str, object] | None = None) -> list[Any]:
        """One toolset for each item ``instantiate`` takes, the first of each class only; a reference string is made
        with context."""
        made: dict[type, Any] = {}
        for item in items:
            toolset = cls.instantiate({"toolset": item, "context": dict(context)} if isinstance(item, str) and context is not None else item)
            made.setdefault(type(toolset), toolset)
        return list(made.values())

    @classmethod
    def instantiate_all(cls, items: list) -> list:
        return [cls.instantiate(item) for item in items]

    @classmethod
    def _made(cls, toolset: type, context: dict[str, Any]) -> Any:
        """A toolset with a ``@tool_subject`` loader is a domain class whose constructor needs a real object's
        collaborators. Listing its tools needs none of them, and each tool loads the object it acts on."""
        if ToolSubjectLoader(toolset).loader is not None:
            return toolset.__new__(toolset)
        return toolset(**context)

    # -- the tools this toolset publishes -------------------------------------------------------------------------

    @property
    def toolset_collections(self) -> list[Any]:
        found: list[Any] = []
        for name, member in self._members.every:
            if name in self._COLLECTION_SKIP or not ToolSetCollectionMark.marks(member):
                continue
            value = getattr(self, name, None)
            if value is not None and value is not self:
                found.append(value)
        return found

    def child_toolsets(self):
        for collection in self.toolset_collections:
            yield from collection

    @property
    def operations(self) -> dict[str, AgentOperation]:
        return self._discover_operations()

    @property
    def instructions(self) -> Mapping[str, AgentInstructions]:
        return self._discover_instruction_members()

    @property
    def tools(self) -> dict[str, AgentTool]:
        merged: dict[str, AgentTool] = {}
        merged.update(self._discover_instruction_members())
        merged.update(self.operations)  # @agent_tool wins same name — MCP must invoke, not only expand
        for name, tool in self._discover_enlisted_members().items():
            merged.setdefault(name, tool)
        merged.update(self._discover_collection_tools())
        return merged

    def tools_for(self, destination: str) -> list[AgentTool]:
        return [tool for tool in self.tools.values() if tool.install_to(destination)]

    def for_call(self, call: ToolCall) -> Any:
        """This toolset as call works on it. A toolset keeps no state of one call, so it serves every call itself; a
        toolset that does, such as a guidance action, answers one made for call."""
        return self

    def session_for(self, call: ToolCall) -> Any:
        """The session this toolset's tools log call in: the session open in the call's project."""
        return call.session

    @property
    def _members(self) -> ToolsetMembers:
        return ToolsetMembers(type(self))

    def _discover_operations(self) -> dict[str, AgentOperation]:
        return {
            name: AgentOperation(name=name, callable=self._operation_callable(name, member), toolset=self)
            for name, member in self._members.marked if AgentToolMark.marks(member)
        }

    def _operation_callable(self, name: str, member: Any) -> Any:
        load = ToolSubjectLoader(type(self)).loader
        if load is None or isinstance(inspect.getattr_static(type(self), name), classmethod):
            return ToolSubjectLoader(type(self)).given_the_called_project(self._members.callable_on(self, name, member))
        return ToolSubjectLoader(type(self)).on_subject(load, member)

    def _discover_instruction_members(self) -> dict[str, AgentInstructions]:
        members = self._members
        return {
            name: AgentInstructions(name=name, callable=members.callable_on(self, name, member), toolset=self)
            for name, member in members.marked if AgentInstructionsMark.marks(member)
        }

    def _discover_enlisted_members(self) -> dict[str, AgentTool]:
        members = self._members
        return {
            name: AgentTool(name=name, callable=members.callable_on(self, name, member), toolset=self)
            for name, member in members.marked if mark_kinds.enlisting(member)
        }

    def _discover_collection_tools(self) -> dict[str, AgentTool]:
        found: dict[str, AgentTool] = {}
        for _key, collection in self._collections_on(self):
            found.update(self._rehost_collection_tools(collection, prefix=""))
        for key, collection in self._nested_tool_collections():
            found.update(self._rehost_collection_tools(collection, prefix=f"{key}."))
        return found

    def _nested_tool_collections(self) -> list[tuple[str, Any]]:
        return [
            (key, bag)
            for collection in self.toolset_collections
            for key, child in getattr(collection, "entries", {}).items()
            for _name, bag in self._collections_on(child)
        ]

    def _rehost_collection_tools(self, collection: Any, prefix: str) -> dict[str, AgentTool]:
        found: dict[str, AgentTool] = {}
        for name, tool in (getattr(collection, "tools", None) or {}).items():
            if prefix and name == "inject_rules":
                continue
            found[f"{prefix}{name}"] = AgentTool(
                name=name,
                callable=getattr(tool, "callable", None) or getattr(collection, name),
                toolset=self,
            )
        return found

    def _collections_on(self, instance: Any) -> list[tuple[str, Any]]:
        if instance is None:
            return []
        members = ToolsetMembers(type(instance))
        found: list[tuple[str, Any]] = []
        for name, member in members.every:
            if name in self._COLLECTION_SKIP:
                continue
            marked = members.is_tool(member) or members.is_rules(member)
            if not marked and not self._is_collection_type(self._return_type(member, type(instance))):
                continue
            value = getattr(instance, name, None)
            if value is not instance and self._is_tool_collection(value):
                found.append((name, value))
        return found

    def _return_type(self, member: Any, owner: type) -> Any:
        annotation = getattr(member, "__annotations__", {}).get("return")
        if not isinstance(annotation, str):
            return annotation
        resolved = getattr(member, "__globals__", {}).get(annotation)
        module = sys.modules.get(owner.__module__)
        if resolved is None and module is not None:
            resolved = getattr(module, annotation, None)
        return resolved

    def _is_collection_type(self, annotation: Any) -> bool:
        if not isinstance(annotation, type):
            return False
        return issubclass(annotation, ToolSetCollection) or ToolSetCollectionMark.marks(annotation) or AgentToolSetMark.marks(annotation)

    def _is_tool_collection(self, value: Any) -> bool:
        if value is None:
            return False
        return isinstance(value, ToolSetCollection) or ToolSetCollectionMark.marks(type(value)) or AgentToolSetMark.marks(type(value))


class ToolSubjectLoader:
    """How a domain class marked ``@agent_toolset`` finds the object a tool call acts on: its ``@tool_subject``
    classmethod. Each instance operation's tool takes the loader's arguments before its own, and a loader or class
    operation that takes ``project`` is handed the checkout its call names."""

    def __init__(self, toolset_class: type) -> None:
        self._toolset_class = toolset_class

    @property
    def loader(self) -> Callable[..., Any] | None:
        """The classmethod marked ``@tool_subject`` on the class, bound to it; none when it has none."""
        for name in dir(self._toolset_class):
            member = inspect.getattr_static(self._toolset_class, name, None)
            if isinstance(member, classmethod) and ToolSubject.marks(member.__func__):
                return self.given_the_called_project(getattr(self._toolset_class, name))
        return None

    def on_subject(self, load: Callable[..., Any], operation: Callable[..., Any]) -> Callable[..., Any]:
        """A tool over ``operation`` that first loads the object the call names: it takes the loader's
        arguments and the operation's own, so every reader of its signature sees what a caller passes."""
        identity = list(inspect.signature(load).parameters.values())
        own = [param for param in inspect.signature(operation).parameters.values() if param.name != "self"]
        identity_names = [*(param.name for param in identity), *([CALLED_PROJECT] if TakesCalledProject.marks(load) else [])]

        @functools.wraps(operation)
        def on_subject(**arguments: Any) -> Any:
            found = load(**{name: arguments.pop(name) for name in identity_names if name in arguments})
            return operation(found, **arguments)

        on_subject.__signature__ = inspect.Signature(identity + own, return_annotation=inspect.signature(operation).return_annotation)
        on_subject.__annotations__ = {**load.__annotations__, **operation.__annotations__}
        if TakesCalledProject.marks(load):
            TakesCalledProject(on_subject)
        return OnSubject(on_subject)

    def given_the_called_project(self, operation: Any) -> Any:
        """A class operation that takes the call's project, with the project left out of its signature, so no caller
        passes it and its tool hands it the project its call names. Any other operation as it is."""
        if not inspect.ismethod(operation) or CALLED_PROJECT not in inspect.signature(operation).parameters:
            return operation
        function = operation.__func__
        signature = inspect.signature(function)

        @functools.wraps(function)
        def on_called_project(owner: Any, *arguments: Any, **named: Any) -> Any:
            return function(owner, *arguments, **named)

        on_called_project.__signature__ = signature.replace(parameters=[parameter for parameter in signature.parameters.values() if parameter.name != CALLED_PROJECT])
        on_called_project.__annotations__ = {name: hint for name, hint in function.__annotations__.items() if name != CALLED_PROJECT}
        return types.MethodType(TakesCalledProject(on_called_project), operation.__self__)


class InstallDestination:
    """The channels a member is published to, in the order a tool lists them. Each channel's mark is a *Destination*
    its publisher defines (harness/installation, harness/mcp, harness/hooks), so this module names the channels and
    never imports the publishers."""

    MCP = "mcp"
    HOOK = "hook"
    SKILL = "skill"
    COMMAND = "command"
    RULE = "rules"
    LISTED = (MCP, SKILL, COMMAND, RULE, HOOK)


class AgentToolDestination:
    """Which install destinations this tool is marked for."""

    callable: Callable[..., Any]

    @property
    def install_to_mcp(self) -> bool:
        return self.install_to(InstallDestination.MCP)

    @property
    def install_to_hook(self) -> bool:
        return self.install_to(InstallDestination.HOOK)

    @property
    def hook_event(self) -> str:
        """The IDE event this tool's ``@Hook`` mark names, or empty when the tool is not a hook."""
        return mark_kinds.name_given_for(InstallDestination.HOOK, self.callable)

    @property
    def install_to_skill(self) -> bool:
        return self.install_to(InstallDestination.SKILL)

    def install_to(self, destination: str) -> bool:
        return mark_kinds.publishes(destination, self.callable)

    @property
    def destinations(self) -> list[str]:
        return [destination for destination in InstallDestination.LISTED if self.install_to(destination)]


@dataclass
class AgentTool(AgentToolDestination):
    name: str
    callable: Callable[..., Any]
    toolset: AgentToolSet
    _body: str | None = field(default=None, repr=False)

    @property
    def slug(self) -> str:
        return self.toolset.slug

    @property
    def registration_name(self) -> str:
        return self.toolset.registration_name

    @property
    def deploy_name(self) -> str:
        return (
            mark_kinds.name_given_for(InstallDestination.COMMAND, self.callable)
            or mark_kinds.name_given_for(InstallDestination.SKILL, self.callable)
            or self.name
        )

    @property
    def mcp_name(self) -> str:
        """The name MCP publishes this tool under and the session log records it by: ``{toolset slug}.{name}``. A
        practice's own instructions are published under the practice's slug alone."""
        if getattr(self.toolset, "practice_guidance", None) is not None and self.name == "instructions":
            return self.slug
        return f"{self.slug}.{self.name}"

    def invoke_line(self) -> str:
        """The ``Use MCP tool:`` line a skill or command ends with, naming the tool and the parameters it takes."""
        try:
            signature = inspect.signature(self.callable)
            params = inspect.Signature([p for n, p in signature.parameters.items() if n not in {"self", "cls"}])
            suffix = str(params)
        except (TypeError, ValueError):
            suffix = "()"
        return f"Use MCP tool: `{self.mcp_name}{suffix}`"

    @property
    def input_schema(self) -> dict[str, Any]:
        """The JSON Schema of the arguments a caller passes, read from the callable's type hints."""
        return ParameterSchema(self.callable).json_schema

    def invoke(self, arguments: dict[str, Any] | None = None, *, project: Path | str | None = None) -> Any:
        """Run the tool with arguments as a caller sent them, on the checkout of project, the project the calling chat
        works on."""
        return self.answer(ToolCall(arguments, project))

    def answer(self, call: ToolCall) -> Any:
        """Answer call on its toolset made for it: log the call in the session it works in, then call the tool with each
        argument in the type its parameter declares."""
        tool = self.on(self.toolset.for_call(call))
        tool.log_session_invocation(call)
        return tool.callable(**ParameterSchema(tool.callable).coerced(call.arguments), **tool._called_project(call))

    def on(self, toolset: Any) -> AgentTool:
        """This tool on toolset, a toolset of the same class made for one call; the tool as it is when toolset is its
        own."""
        if toolset is self.toolset:
            return self
        bound = getattr(self.callable, "__self__", None) is self.toolset
        return replace(self, callable=types.MethodType(self.callable.__func__, toolset) if bound else self.callable, toolset=toolset)

    def _called_project(self, call: ToolCall) -> dict[str, Path]:
        """The project argument a callable that takes it is handed: the checkout call names."""
        if not TakesCalledProject.marks(self.callable):
            return {}
        if call.project is None:
            raise CallNamesNoProject(self.mcp_name)
        return {CALLED_PROJECT: call.project}

    def should_log_session_invocation(self, arguments: dict[str, Any] | None) -> bool:
        if arguments and arguments.get("ping") is True:
            return False
        if NoSessionLog.marks(self.callable):
            return False
        if AgentToolMark.marks(self.callable):
            return True
        return self.install_to_mcp

    def log_session_invocation(self, call: ToolCall) -> None:
        """Log call in the session its toolset works in for it: a guidance action's own session, which a board command
        names, or else the session open in the call's project. A call that works in no session logs nothing."""
        if not self.should_log_session_invocation(call.arguments):
            return
        session = self.toolset.session_for(call)
        if session is None:
            return
        logged_args = {
            key: value
            for key, value in call.arguments.items()
            if isinstance(value, (str, int, float, bool, list))
        }
        session.log.tool(self.mcp_name, logged_args)

    @property
    def kind(self) -> str:
        if AgentToolMark.marks(self.callable):
            return "tool"
        if AgentInstructionsMark.marks(self.callable):
            return "instructions"
        return "none"

    @property
    def docstring(self) -> str:
        if self._body is not None:
            body = self._body
        else:
            body = (inspect.getdoc(self.callable) or "").strip()
        return self._with_parameter_notes(self._with_sub_agent_preamble(body))

    def _with_parameter_notes(self, text: str) -> str:
        """text followed by the note its toolset gives each parameter this tool takes, once each."""
        try:
            parameters = inspect.signature(self.callable).parameters
        except (TypeError, ValueError):
            return text
        notes = getattr(self.toolset, "parameter_notes", {})
        for parameter, note in notes.items():
            if parameter in parameters and note not in text:
                text = f"{text}\n\n{note}" if text else note
        return text

    def _with_sub_agent_preamble(self, text: str) -> str:
        from harness.agent_tools.sub_agent.mark import (
            marked_as_sub_agent,
            prepend_sub_agent_instructions,
        )

        if marked_as_sub_agent(self.callable):
            return prepend_sub_agent_instructions(text)
        return text

    @functools.cached_property
    def description(self) -> str:
        """What the tool does, expanded from its docstring once: MCP lists it on every request for the tool list."""
        expanded = Markdown.from_label(self.toolset, "").expand_docstring(self.docstring)
        if expanded:
            return expanded
        if self.name == "instructions":
            overview = getattr(self.toolset, "overview", None)
            if callable(overview):
                overview = overview()
            if isinstance(overview, str) and overview.strip():
                return overview.strip()
        return self.docstring or self.callable.__name__

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


@dataclass
class GuidanceAgentOperation(AgentOperation):
    """An ``@agent_tool`` on a guidance action: its call is logged as the action, such as ``render``, rather than as a
    ``tool …`` line."""

    def log_session_invocation(self, call: ToolCall) -> None:
        """Log the call as its action, in the session the action made for it works in."""
        if not self.should_log_session_invocation(call.arguments):
            return
        self.toolset._log_running_action(self.name)


@dataclass
class AgentInstructions(AgentTool):
    """An ``@agent_instructions`` operation: its recipe body, expanded for a call, is the instructions an agent
    follows. Each expansion runs in a *RecipeExpansion* of its own."""

    @property
    def kind(self) -> str:
        if AgentToolMark.marks(self.callable):
            return "tool"
        return "instructions"

    @classmethod
    def for_callable(
        cls,
        callable: Callable[..., Any],
        instance: AgentToolSet | None = None,
    ) -> AgentInstructions:
        if instance is not None:
            if isinstance(callable, property):
                callable = callable.fget
            return instance._discover_instruction_members()[callable.__name__]
        return cls(
            name=callable.__name__,
            callable=callable,
            toolset=AgentToolSet(),
        )

    @property
    def prompt(self) -> tuple[str, ...]:
        """The recipe's prompt lines, expanded with each parameter's default."""
        return RecipeExpansion(self).run().prompt

    @property
    def tools(self) -> list[str]:
        """The tools the recipe names, expanded with each parameter's default."""
        return RecipeExpansion(self).run().tools

    def answer(self, call: ToolCall) -> str:
        """The instructions an agent follows for call, expanded with its arguments by the toolset made for it."""
        tool = self.on(self.toolset.for_call(call))
        tool.log_session_invocation(call)
        if tool.name == "instructions" and hasattr(tool.toolset, "instructions"):
            return tool.toolset.instructions
        return tool._expanded_reply(call.arguments)

    def _expanded_reply(self, arguments: dict[str, Any]) -> str:
        toolset = self.toolset
        expanded = AgentInstructions.for_callable(self.callable, toolset).expand(arguments)
        body = (expanded.instructions or "").strip()
        doc = (inspect.getdoc(self.callable) or "").strip()
        if doc and doc not in body:
            body = f"{doc}\n\n{body}".strip() if body else doc
        reply = body or self.description or doc
        # An action that works in a session says which one, so the agent knows its folders without looking for them.
        session = getattr(toolset, "session_context", "")
        return f"{reply}\n\n{session}" if session else reply

    @property
    def result_template(self) -> str:
        source = RecipeSource(self.callable)
        result_template = source.result_template
        if not result_template and source.only_defers_to_parent:
            parent = self.parent_recipe()
            result_template = RecipeSource(parent[0].callable).result_template if parent is not None else ""
        return result_template or f"Instructions for {self.callable.__name__}"

    def expand(self, arguments: dict[str, Any]) -> ExpansionResult:
        """The recipe expanded for one call's arguments: its instructions, the tools it names, and its result line,
        with every placeholder filled."""
        expansion = RecipeExpansion(self, arguments).run()
        placeholders = RecipePlaceholders(arguments, set(self.parameters), self.toolset)
        lines = (placeholders.filled(part) for part in expansion.prompt)
        instructions = "\n\n".join(line for line in lines if line.strip())
        return ExpansionResult(
            instructions=self._with_sub_agent_preamble(instructions),
            tools=expansion.tools,
            result=placeholders.filled(self.result_template),
        )

    def members_of(self, target: Any) -> ToolsetMembers:
        """The members of target, a toolset this recipe names, that are its tools."""
        return ToolsetMembers(type(target))

    def member_of(self, target: Any, member: str) -> AgentInstructions:
        """The instructions operation member on target, a toolset this recipe names."""
        return AgentToolSet._discover_instruction_members(target)[member]

    def provider_of(self, owner: Any, provider_name: str) -> Any:
        """The object owner's provider gives: a toolset it holds as it is, or what a provider operation answers."""
        provided = getattr(owner, provider_name)
        if AgentToolSetMark.marks(type(provided)):
            return provided
        return provided() if callable(provided) else provided

    def parent_recipe(self, after_class: type | None = None) -> tuple[AgentInstructions, type] | None:
        """The recipe of the same name on the nearest class above after_class (above the toolset's own class when none)
        in the toolset's class order, with that class; none when no class above defines one."""
        own_class = type(self.toolset)
        method_name = self.callable.__name__
        own_recipe = own_class.__dict__.get(method_name)
        if own_recipe is None:
            return None
        classes = own_class.__mro__
        if after_class is not None and after_class not in classes:
            return None
        above = classes[classes.index(after_class) + 1:] if after_class is not None else classes
        for owner in above:
            recipe = owner.__dict__.get(method_name)
            if recipe is None or (after_class is None and recipe is own_recipe):
                continue
            if callable(recipe) and AgentInstructionsMark.marks(recipe):
                return AgentInstructions(name=method_name, callable=recipe, toolset=self.toolset), owner
        return None


def _callable_needs_arguments(call: Callable[..., Any]) -> bool:
    try:
        signature = inspect.signature(call)
    except (TypeError, ValueError):
        return False
    for parameter in signature.parameters.values():
        if parameter.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue
        if parameter.default is inspect.Parameter.empty:
            return True
    return False


def tools(*calls: Callable[..., Any]) -> list[Any]:
    rendered: list[Any] = []
    for call in calls:
        if callable(call) and not _callable_needs_arguments(call):
            rendered.append(call())
        else:
            rendered.append(call)
    return rendered


def instructions(*calls: Callable[..., Any]) -> str:
    parts: list[str] = []
    for call in calls:
        if isinstance(call, str):
            parts.append(call.strip())
        elif callable(call):
            doc = inspect.getdoc(call) or ""
            parts.append(doc.strip())
    return "\n\n".join(part for part in parts if part)


class AgentToolMark(Mark):
    """Mark a method as a tool; description comes from the method docstring."""

    flag = "_is_agent_tool"


class AgentInstructionsMark(Mark):
    """Mark a method as @agent_instructions; unwrapped body code runs during expand."""

    flag = "_is_agent_instructions"


class AgentToolSetMark(Mark):
    """Mark a class as an agent toolset — @agent_tool and @agent_instructions."""

    flag = "_is_agent_toolset"
    copied = False

    def __new__(cls, target: type | None = None):
        mark = object.__new__(cls)
        if isinstance(target, type):
            return mark.annotate(target)
        return mark

    def __call__(self, target: type) -> type:
        return self.annotate(target)

    def annotate(self, toolset_cls: type) -> type:
        if self.flag in toolset_cls.__dict__:
            return toolset_cls
        if self.marks(toolset_cls):
            ToolsetValidator(toolset_cls).validate()
            return toolset_cls
        if issubclass(toolset_cls, AgentToolSet):
            raise TypeError(
                f"{toolset_cls.__name__} must use @agent_toolset — do not subclass AgentToolSet directly"
            )
        merged = type(
            toolset_cls.__name__,
            (toolset_cls, AgentToolSet),
            {
                attribute_name: attribute_value
                for attribute_name, attribute_value in vars(toolset_cls).items()
                if attribute_name not in ("__dict__", "__weakref__")
            },
        )
        merged.__doc__ = toolset_cls.__doc__
        merged.__module__ = toolset_cls.__module__
        merged.__qualname__ = toolset_cls.__qualname__
        setattr(merged, self.flag, True)
        ToolsetValidator(merged).validate()
        return merged


class ToolSetCollectionMark(Mark):
    """Mark a class as a ToolSetCollection, or a property as one of this toolset's collections."""

    flag = "_is_toolset_collection"

    def __new__(cls, target: Any = None):
        mark = object.__new__(cls)
        if target is not None:
            return mark.annotate(target)
        return mark

    def __call__(self, target: Any) -> Any:
        return self.annotate(target)

    def annotate(self, target: Any) -> Any:
        if not inspect.isclass(target):
            fn = getattr(target, "fget", target)
            setattr(fn, self.flag, True)
            return target
        if self.flag in target.__dict__:
            return target
        if self.marks(target):
            return target
        if issubclass(target, ToolSetCollection):
            raise TypeError(
                f"{target.__name__} must use @toolset_collection — do not subclass ToolSetCollection directly"
            )
        merged = type(
            target.__name__,
            (target, ToolSetCollection),
            {
                attribute_name: attribute_value
                for attribute_name, attribute_value in vars(target).items()
                if attribute_name not in ("__dict__", "__weakref__")
            },
        )
        merged.__doc__ = target.__doc__
        merged.__module__ = target.__module__
        merged.__qualname__ = target.__qualname__
        setattr(merged, self.flag, True)
        return merged


class NoSessionLog(Mark):
    """Keep an operation's calls out of the session log. Use it on reads an agent or a mod repeats often, such as the
    session board, so the log keeps the work that was done rather than every look at it."""

    flag = "_no_session_log"
    copied = False


class ToolSubject(Mark):
    """Mark the classmethod that finds the object a tool call acts on, so ``@agent_tool`` can sit on a domain class
    whose constructor takes collaborators. Each instance operation's tool takes this loader's arguments before its
    own: ``load(ticket)`` and ``move_next(self)`` make the tool ``ticket.move_next(ticket)``. A loader that takes
    ``project`` is handed the checkout of the project its call works on, so ``load(ticket, *, project)`` loads the
    ticket from that project's board and the tool still takes only ``ticket``."""

    flag = "_is_tool_subject"
    copied = False


class OnSubject(Mark):
    """Set on the tool made from an instance operation of a ``@tool_subject`` class: it loads its object from its
    leading arguments before it runs the operation."""

    flag = "_runs_on_subject"
    copied = False


class TakesCalledProject(Mark):
    """Set on a tool's callable that takes the project its call works on, which its signature leaves out because no
    caller passes it: the tool hands it the project its ``ToolCall`` names."""

    flag = "_takes_called_project"
    copied = False


noSessionLog = NoSessionLog
tool_subject = ToolSubject


agent_tool = AgentToolMark
agent_toolset = AgentToolSetMark
agent_instructions = AgentInstructionsMark
toolset_collection = ToolSetCollectionMark
