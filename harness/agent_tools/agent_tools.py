"""Agent toolset — register, introspect, and validate one decorated AgentToolSet."""
from __future__ import annotations

import ast
import functools
import importlib.util
import inspect
import re
import sys
import types
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, ClassVar, Mapping, get_type_hints

from harness.annotations.class_folder import class_folder
from harness.annotations.name import Name
from harness.agent_tools.parameter_schema import ParameterSchema
from harness.agent_tools.tool_call import ToolCall
from harness.markdown.markdown import Markdown, MarkdownCollection, OperationProperty
from harness.annotations.annotation import Annotation, NamesAnnotation, annotation_kinds
from harness.agent_tools.recipe import ExpansionMode, ExpansionResult, RecipeExpansion, RecipePlaceholders, RecipeSource

ContextDocument = dict[str, Any]
ArgumentDocument = dict[str, Any]
SUB_AGENT_CALLER_PREAMBLE = """Hand work to a background sub-agent and continue without waiting.

Do not perform the delegated work in this conversation. Do not wait for the
sub-agent to finish.

Launch the Task tool with run_in_background true and subagent_type
generalPurpose. Pass the instructions below as the task prompt.

Tell the user you launched a non-blocking sub-agent and summarize what you delegated."""
# A `@tool_subject` loader or a class tool that takes one of these arguments is handed it from the call it serves: `project`
# the checkout of the project the call works on, `call` the call itself, with its chat and the sessions it opens. No
# caller passes them, so they are not among the tool's arguments.
CALLED_PROJECT = "project"
SERVED_CALL = "call"
FROM_THE_CALL = (CALLED_PROJECT, SERVED_CALL)


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

    @functools.cached_property
    def _own_name(self) -> Name:
        """The toolset's name, made once from its declared slug or its class."""
        return Name(self.domain_slug or type(self).__name__)

    @property
    def slug(self) -> str:
        return self._own_name.kebab

    @property
    def install_folder(self) -> Path:
        """The folder beside the toolset's class, which its installed files are named from."""
        return class_folder(type(self))

    @property
    def registration_name(self) -> str:
        """The ``module:Class`` reference configuration and the installer name this toolset by."""
        return str(ToolsetReference.of(type(self)))

    @property
    def description(self) -> str:
        return (self.__class__.__doc__ or "").strip()

    @property
    def overview(self) -> str:
        """What this toolset is for, which its ``instructions`` tool is described by when its docstring says nothing;
        none unless the toolset says."""
        return ""

    @property
    def session_context(self) -> str:
        """What an agent following one of this toolset's instructions needs to know about the session it works in,
        added after the instructions; none for a toolset that works in no session."""
        return ""

    pattern: ClassVar[str] = ""
    """The guideline in a project's ``.context/config.json`` that turns this toolset's hooks on, such as
    ``lern_domain_driven`` for a pattern; empty for a toolset whose hooks always run."""

    parameter_notes: ClassVar[dict[str, str]] = {}
    """What an agent reads about a parameter, by its name, after the description of every tool on this toolset that
    takes it; a guidance action explains its ``guidance`` parameter this way."""

    def schema_guide(self) -> str:
        """The schema this toolset's instructions tell an agent to conform its output to, which an installed skill of
        its instructions carries; none unless the toolset has one, as a practice does."""
        return ""

    @functools.cached_property
    def class_markdown(self) -> Markdown:
        """The markdown beside this toolset's class, which expands a tool's one-word description into its section."""
        return Markdown.from_label(self, "")


class ToolSetCollection(AgentToolSetOrigin):
    """Named child toolsets, iterated in entry order. The collection itself may have tools, and it is named and found
    the way a toolset is."""

    def __init__(self, entries: dict[str, Any] | None = None, parent: Any = None) -> None:
        self.entries: dict[str, Any] = dict(entries or {})
        self.parent = parent

    def __iter__(self):
        return iter(self.entries.values())

    def __len__(self) -> int:
        return len(self.entries)

    def __bool__(self) -> bool:
        return bool(self.entries)

    def attach(self, instance: Any, name: str | None = None) -> None:
        MarkdownCollection.attach(self, instance, name)

    @property
    def tools(self) -> dict[str, AgentTool]:
        """Tools declared on this collection, not on its entries, made once for this collection."""
        return self._declared_tools

    @functools.cached_property
    def _declared_tools(self) -> dict[str, AgentTool]:
        members = ToolsetMembers.of(type(self))
        return {
            name: AgentTool(name=name, callable=members.callable_on(self, name, member), toolset=self)
            for name, member in members.annotated
        }


class Collect:
    """Aggregate the same-named property across a collection's children: ``@collect`` on a collection's property
    answers its children's values joined as text, or bundled into the property's declared return type."""

    def __new__(cls, operation: Callable[..., Any]) -> property:
        return object.__new__(cls)._property(operation)

    def _property(self, operation: Callable[..., Any]) -> property:
        self._name = operation.__name__
        self._return_type = self._declared_return(operation)
        return OperationProperty(operation).reading(self.of)

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
    """The members of one toolset class and which of them its annotations make tools. A class's functions and properties are
    fixed once it is imported, and every hook dispatch asks this of every toolset, so the class holds its members
    (``ToolsetMembers.of``) and they are walked once."""

    _HELD_AS: ClassVar[str] = "_toolset_members"
    # The members every toolset has that are its tools and mode, never collections it holds.
    COLLECTION_SKIP: ClassVar[frozenset[str]] = frozenset({"tools", "operations", "instructions", "mode"})

    def __init__(self, owner: type) -> None:
        self._owner = owner

    @classmethod
    def of(cls, owner: type) -> ToolsetMembers:
        """The members owner holds, made and kept on owner itself the first time they are asked for. A subclass holds
        its own, because it may add or replace members."""
        held = owner.__dict__.get(cls._HELD_AS)
        if held is None or held._owner is not owner:
            held = cls(owner)
            try:
                setattr(owner, cls._HELD_AS, held)
            except TypeError:  # a built-in type keeps no attributes, so its members are walked for this read alone
                pass
        return held

    @functools.cached_property
    def every(self) -> list[tuple[str, Any]]:
        """Every function, class or static method, and property getter on the class, by name."""
        return self._walk()

    @functools.cached_property
    def annotated(self) -> list[tuple[str, Any]]:
        """The members that are tools: annotated ``@agent_tool`` or ``@agent_instructions``, or enlisted by a destination
        such as a hook."""
        return [(name, member) for name, member in self.every if self.is_tool(member)]

    @functools.cached_property
    def tool_names(self) -> set[str]:
        return {name for name, member in self.annotated if AgentToolAnnotation.annotates(member)}

    @functools.cached_property
    def instruction_names(self) -> frozenset[str]:
        return frozenset(name for name, member in self.annotated if AgentInstructionsAnnotation.annotates(member))

    @functools.cached_property
    def subject_loader(self) -> ToolSubjectLoader:
        """How the class finds the object a tool call acts on: its ``@tool_subject`` loader, read once."""
        return ToolSubjectLoader(self._owner)

    def is_tool(self, member: Any) -> bool:
        return AgentToolAnnotation.annotates(member) or AgentInstructionsAnnotation.annotates(member) or annotation_kinds.enlisting(member)

    def is_rules(self, member: Any) -> bool:
        return annotation_kinds.annotated_for(InstallDestination.RULE, member)

    @functools.cached_property
    def toolset_collection_names(self) -> list[str]:
        """The members annotated as toolset collections, such as a practice's fidelities, read once for the class."""
        return [name for name, member in self.every if name not in self.COLLECTION_SKIP and ToolSetCollectionAnnotation.annotates(member)]

    @functools.cached_property
    def collection_names(self) -> list[str]:
        """The members that can hold a collection of tools: those its annotations make tools or rules, and those whose
        return type is a toolset collection or a toolset; read once for the class, since its members' annotations are
        fixed once it is imported."""
        return [
            name
            for name, member in self.every
            if name not in self.COLLECTION_SKIP
            and (self.is_tool(member) or self.is_rules(member) or self._is_collection_type(self._return_type(member)))
        ]

    def collections_on(self, instance: Any) -> list[tuple[str, Any]]:
        """Each of those members that holds a collection of tools on instance, an instance of this class, by name."""
        held = ((name, getattr(instance, name, None)) for name in self.collection_names)
        return [(name, value) for name, value in held if value is not instance and self._is_tool_collection(value)]

    def _return_type(self, member: Any) -> Any:
        """The type member says it returns, its name resolved in the module that defines it, else the class's."""
        annotation = getattr(member, "__annotations__", {}).get("return")
        if not isinstance(annotation, str):
            return annotation
        resolved = getattr(member, "__globals__", {}).get(annotation)
        module = sys.modules.get(self._owner.__module__)
        if resolved is None and module is not None:
            resolved = getattr(module, annotation, None)
        return resolved

    def _is_collection_type(self, annotation: Any) -> bool:
        if not isinstance(annotation, type):
            return False
        return issubclass(annotation, ToolSetCollection) or self._is_toolset_class(annotation)

    def _is_tool_collection(self, value: Any) -> bool:
        if value is None:
            return False
        return isinstance(value, ToolSetCollection) or self._is_toolset_class(type(value))

    def _is_toolset_class(self, owner: type) -> bool:
        return ToolSetCollectionAnnotation.annotates(owner) or AgentToolSetAnnotation.annotates(owner)

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
            members.append((name, self._annotated_function(declared) if isinstance(declared, (staticmethod, classmethod)) else member))
        for base in self._owner.__mro__:
            for name, declared in base.__dict__.items():
                if name not in seen and isinstance(declared, (staticmethod, classmethod)):
                    seen.add(name)
                    members.append((name, self._annotated_function(declared)))
        for name, member in inspect.getmembers(self._owner, predicate=inspect.isdatadescriptor):
            getter = getattr(member, "fget", None)
            if getter is not None and name not in seen:
                members.append((name, getter))
        return members

    def _annotated_function(self, declared: staticmethod | classmethod) -> Any:
        """The function a static or class method wraps, carrying the annotations set on the wrapper."""
        function = declared.__func__
        for flag in annotation_kinds.copied_flags:
            if getattr(declared, flag, None) and not getattr(function, flag, None):
                setattr(function, flag, getattr(declared, flag))
        return function


class ToolsetReference:
    """A toolset named the way configuration and the installer name it: ``<module>:<Class>``. A module whose folder
    names use hyphens on disk, such as ``agent-bdd``, is found by its underscored name too, under each folder on the
    import path: the repository's toolsets put their checkout's import folders there, so this reference searches the
    same folders the installer and the servers load from."""

    def __init__(self, reference: str) -> None:
        self._module_name, _, self._class_name = reference.partition(":")
        if not self._class_name:
            raise ValueError(f"expected <module>:<Class>, got {reference!r}")
        self._reference = reference

    @classmethod
    def of(cls, toolset_class: type) -> ToolsetReference:
        """The reference that names toolset_class: its module's full name and its own."""
        return cls.in_module(toolset_class.__module__, toolset_class.__name__)

    @classmethod
    def in_module(cls, module: str, class_name: str) -> ToolsetReference:
        """The reference to the class class_name defined in module, named the one way references are written."""
        return cls(f"{module}:{class_name}")

    def __str__(self) -> str:
        return self._reference

    @property
    def module_name(self) -> str:
        """The full name of the module that defines the class, such as ``space.repo.repo``."""
        return self._module_name

    @property
    def toolset_class(self) -> type:
        """The ``@agent_toolset`` class the reference names. Raises TypeError for a class that is not one."""
        loaded = getattr(self._module, self._class_name)
        if not (isinstance(loaded, type) and AgentToolSetAnnotation.annotates(loaded)):
            raise TypeError(f"{self._reference} is not a @agent_toolset class")
        return loaded

    @property
    def _module(self) -> types.ModuleType:
        try:
            return importlib.import_module(self._module_name)
        except ModuleNotFoundError:
            return self._module_from_hyphenated_folders()

    def _module_from_hyphenated_folders(self) -> types.ModuleType:
        module_file = self.module_file()
        spec = importlib.util.spec_from_file_location(self._module_name, module_file)
        if spec is None or spec.loader is None:
            raise ModuleNotFoundError(f"Cannot create spec for {module_file}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[self._module_name] = module
        spec.loader.exec_module(module)
        return module

    def module_file(self) -> Path:
        """The source file of the referenced class's module, found on the import path without importing it."""
        roots = [Path(entry or ".") for entry in sys.path]
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
        self._members = ToolsetMembers.of(toolset_class)

    def validate(self) -> None:
        """Raises AgentToolValidationError naming the recipe and what is wrong with it."""
        allowed = self._members.tool_names | set(self._members.instruction_names)
        for name, member in self._members.every:
            if AgentInstructionsAnnotation.annotates(member):
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


class AgentToolSet(AgentToolSetOrigin):
    """Injected by @agent_toolset — the operations, instructions, and nested collections of one toolset as the tools it
    publishes."""

    _mode: str = "instructions"
    LOAD_FAILURES: ClassVar[tuple[type[BaseException], ...]] = (
        ImportError, SyntaxError, NameError, AttributeError, TypeError, ValueError, LookupError, OSError
    )
    """What making or reading a toolset raises when its code cannot be loaded, such as a module that does not import or
    a constructor that needs more than configuration gives it. A server that loads every toolset skips one that raises
    these, names it, and serves the rest."""

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
    def _made(cls, toolset: type, context: dict[str, Any]) -> Any:
        """A toolset with a ``@tool_subject`` loader is a domain class whose constructor needs a real object's
        collaborators. Listing its tools needs none of them, and each tool loads the object it acts on."""
        if ToolsetMembers.of(toolset).subject_loader.loader is not None:
            return toolset.__new__(toolset)
        return toolset(**context)

    # -- the tools this toolset publishes -------------------------------------------------------------------------

    @property
    def toolset_collections(self) -> list[Any]:
        """The toolset collections this toolset holds now, each a member annotated as one."""
        held = (getattr(self, name, None) for name in self._members.toolset_collection_names)
        return [value for value in held if value is not None and value is not self]

    def child_toolsets(self):
        for collection in self.toolset_collections:
            yield from collection

    # The tools are read-only properties over parts made once, so a section's settings never overwrite them.

    @property
    def operations(self) -> dict[str, AgentOperation]:
        """Each ``@agent_tool`` member of this toolset, made once for this toolset."""
        return self._operation_members

    @property
    def instructions(self) -> Mapping[str, AgentInstructions]:
        """Each ``@agent_instructions`` member of this toolset, made once for this toolset."""
        return self._instruction_members

    def instruction(self, name: str) -> AgentInstructions:
        """The ``@agent_instructions`` member called name. A recipe names its members by name in its source, and a
        practice's own ``instructions`` is its prose, so a recipe finds a member here."""
        return self._instruction_members[name]

    @property
    def tools(self) -> dict[str, AgentTool]:
        """Every tool this toolset publishes, made once for this toolset: its instructions, its operations, the members a
        destination enlists, and the tools of the collections it holds."""
        return self._published_tools

    @functools.cached_property
    def _operation_members(self) -> dict[str, AgentOperation]:
        return self._discover_operations()

    @functools.cached_property
    def _instruction_members(self) -> dict[str, AgentInstructions]:
        return self._discover_instruction_members()

    @functools.cached_property
    def _published_tools(self) -> dict[str, AgentTool]:
        merged: dict[str, AgentTool] = {}
        merged.update(self._instruction_members)
        merged.update(self.operations)  # @agent_tool wins same name — MCP must invoke, not only expand
        for name, tool in self._discover_enlisted_members().items():
            merged.setdefault(name, tool)
        merged.update(self._discover_collection_tools())
        return merged

    def tools_for(self, destination: str) -> list[AgentTool]:
        return [tool for tool in self.tools.values() if tool.install_to(destination)]

    @property
    def is_part_of_practice(self) -> bool:
        """Whether this toolset is one part of a practice, such as one of its fidelities: its files and commands sit in
        its practice's folder, named after its own slug, and its own instructions are published under that slug. A
        toolset is a whole of its own unless it says otherwise."""
        return False

    @property
    def is_served_on_mcp(self) -> bool:
        """Whether the cdd server publishes this toolset's tools: every toolset but a part of a practice made apart from
        any practice, whose tools are reached only through the practice that holds it."""
        return True

    def for_call(self, call: ToolCall) -> Any:
        """This toolset as call works on it. A toolset keeps no state of one call, so it serves every call itself; a
        toolset that does, such as a guidance action, answers one made for call."""
        return self

    def session_for(self, call: ToolCall) -> Any:
        """The session this toolset's tools log call in: the session whose session.json the call names in ``session``,
        as a board command names its ticket's, else the session the call's chat has open."""
        named = call.arguments.get("session")
        if isinstance(named, str) and named.strip().endswith("session.json"):
            try:
                return call.session_named(named.strip())
            except LookupError:
                pass
        return call.session

    @property
    def _members(self) -> ToolsetMembers:
        return ToolsetMembers.of(type(self))

    @property
    def operation_type(self) -> type[AgentOperation]:
        """The kind of tool each ``@agent_tool`` of this toolset is published as; a toolset whose tools log their calls
        another way, such as a guidance action, names its own."""
        return AgentOperation

    def _discover_operations(self) -> dict[str, AgentOperation]:
        return {
            name: self.operation_type(name=name, callable=self._operation_callable(name, member), toolset=self)
            for name, member in self._members.annotated if AgentToolAnnotation.annotates(member)
        }

    def _operation_callable(self, name: str, member: Any) -> Any:
        subject_loader = self._members.subject_loader
        load = subject_loader.loader
        if load is None or isinstance(inspect.getattr_static(type(self), name), classmethod):
            return subject_loader.given_the_call(self._members.callable_on(self, name, member))
        return subject_loader.on_subject(load, member)

    def _discover_instruction_members(self) -> dict[str, AgentInstructions]:
        members = self._members
        return {
            name: AgentInstructions(name=name, callable=members.callable_on(self, name, member), toolset=self)
            for name, member in members.annotated if AgentInstructionsAnnotation.annotates(member)
        }

    def _discover_enlisted_members(self) -> dict[str, AgentTool]:
        members = self._members
        return {
            name: AgentTool(name=name, callable=members.callable_on(self, name, member), toolset=self)
            for name, member in members.annotated if annotation_kinds.enlisting(member)
        }

    def _discover_collection_tools(self) -> dict[str, AgentTool]:
        found: dict[str, AgentTool] = {}
        for _key, collection in self._members.collections_on(self):
            found.update(self._rehost_collection_tools(collection, prefix=""))
        for key, collection in self._nested_tool_collections():
            found.update(self._rehost_collection_tools(collection, prefix=f"{key}."))
        return found

    def _nested_tool_collections(self) -> list[tuple[str, Any]]:
        return [
            (key, bag)
            for collection in self.toolset_collections
            for key, child in getattr(collection, "entries", {}).items()
            for _name, bag in ToolsetMembers.of(type(child)).collections_on(child)
        ]

    def _rehost_collection_tools(self, collection: Any, prefix: str) -> dict[str, AgentTool]:
        found: dict[str, AgentTool] = {}
        for name, tool in (getattr(collection, "tools", None) or {}).items():
            if prefix and PublishedWhereHeld.annotates(tool.callable):
                continue
            found[f"{prefix}{name}"] = AgentTool(
                name=name,
                callable=getattr(tool, "callable", None) or getattr(collection, name),
                toolset=self,
            )
        return found


class ToolSubjectLoader:
    """How a domain class annotated ``@agent_toolset`` finds the object a tool call acts on: its ``@tool_subject``
    classmethod. Each instance operation's tool takes the loader's arguments before its own, and a loader or class
    operation that takes ``project`` is handed the checkout its call names."""

    def __init__(self, toolset_class: type) -> None:
        self._toolset_class = toolset_class

    @functools.cached_property
    def loader(self) -> Callable[..., Any] | None:
        """The classmethod annotated ``@tool_subject`` on the class, bound to it, found once; none when it has none."""
        for name in dir(self._toolset_class):
            member = inspect.getattr_static(self._toolset_class, name, None)
            if isinstance(member, classmethod) and ToolSubject.annotates(member.__func__):
                return self.given_the_call(getattr(self._toolset_class, name))
        return None

    def on_subject(self, load: Callable[..., Any], operation: Callable[..., Any]) -> Callable[..., Any]:
        """A tool over ``operation`` that first loads the object the call names: it takes the loader's
        arguments and the operation's own, so every reader of its signature sees what a caller passes. The loader is
        handed what it takes from the call, and an operation that takes ``call`` is handed the call too, so a line it
        logs points at the call's chat."""
        operation_takes_call = SERVED_CALL in inspect.signature(operation).parameters
        own = [param for param in inspect.signature(operation).parameters.values() if param.name not in ("self", SERVED_CALL)]
        named_objects = self._named_objects(operation, own)
        taken = tuple(dict.fromkeys([
            *TakesFromCall.names_on(load), *(name for other in named_objects.values() for name in TakesFromCall.names_on(other)),
            *([SERVED_CALL] if operation_takes_call else []),
        ]))
        on_subject = self._loading(load, operation, named_objects, taken)
        self._publish(on_subject, load, operation, own, named_objects)
        if taken:
            TakesFromCall(*taken).annotate(on_subject)
        return OnSubject(on_subject)

    def _loading(
        self, load: Callable[..., Any], operation: Callable[..., Any], named_objects: dict[str, Callable[..., Any]], taken: tuple[str, ...]
    ) -> Callable[..., Any]:
        """The tool's body: load each object the call names, then the subject, then run the operation on it."""
        operation_takes_call = SERVED_CALL in taken
        identity_names = [*inspect.signature(load).parameters, *TakesFromCall.names_on(load)]

        @functools.wraps(operation)
        def on_subject(**arguments: Any) -> Any:
            call = arguments.get(SERVED_CALL)
            from_call = {name: arguments[name] for name in taken if name in arguments and name != SERVED_CALL}
            for name, load_other in named_objects.items():
                if name in arguments:
                    arguments[name] = self._object_named(load_other, arguments[name], from_call)
            found = load(**{name: arguments.pop(name) for name in identity_names if name in arguments})
            for name in taken:
                arguments.pop(name, None)
            return operation(found, **arguments, **({SERVED_CALL: call} if operation_takes_call else {}))

        return on_subject

    def _publish(
        self, on_subject: Callable[..., Any], load: Callable[..., Any], operation: Callable[..., Any],
        own: list[inspect.Parameter], named_objects: dict[str, Callable[..., Any]],
    ) -> None:
        """Give the tool the signature a caller reads: the loader's arguments, then the operation's own, with each
        object argument taken by name."""
        identity = list(inspect.signature(load).parameters.values())
        published = [self._by_name(param) if param.name in named_objects else param for param in own]
        on_subject.__signature__ = inspect.Signature(identity + published, return_annotation=inspect.signature(operation).return_annotation)
        on_subject.__annotations__ = {
            name: (str if name in named_objects else hint)
            for name, hint in {**load.__annotations__, **operation.__annotations__}.items() if name != SERVED_CALL
        }

    def _named_objects(self, operation: Callable[..., Any], own: list[inspect.Parameter]) -> dict[str, Callable[..., Any]]:
        """The operation's arguments that are themselves objects a tool can load, such as another ``Ticket``, each with
        its class's loader: a tool call names such an object, as it names the tool's own subject, and the tool loads it."""
        try:
            hints = get_type_hints(operation)
        except (NameError, TypeError):  # a hint naming a class this module cannot see loads nothing
            return {}
        found = {}
        for param in own:
            owner = self._object_class_in(hints.get(param.name))
            loader = ToolsetMembers.of(owner).subject_loader.loader if owner is not None else None
            if loader is not None:
                found[param.name] = loader
        return found

    def _object_named(self, load_other: Callable[..., Any], named: Any, from_call: dict[str, Any]) -> Any:
        """The object a call names by its identity, loaded as its own tools load it; none when the call names none, and
        an object a caller already holds as it is."""
        if not isinstance(named, str):
            return named
        if not named:
            return None
        identity = next(iter(inspect.signature(load_other).parameters))
        wanted = TakesFromCall.names_on(load_other)
        return load_other(**{identity: named, **{name: value for name, value in from_call.items() if name in wanted}})

    def _object_class_in(self, hint: Any) -> type | None:
        """The class a hint names, a ``Ticket`` or a ``Ticket | None``; none for any other hint."""
        if isinstance(hint, type):
            return hint if hint.__module__ != "builtins" else None
        named = [member for member in getattr(hint, "__args__", ()) if isinstance(member, type) and member is not type(None)]
        return named[0] if len(named) == 1 and type(None) in getattr(hint, "__args__", ()) else None

    def _by_name(self, param: inspect.Parameter) -> inspect.Parameter:
        """An object argument as a tool publishes it: its name, empty for none when the operation allows none."""
        default = "" if param.default is None else param.default
        return param.replace(annotation=str, default=default)

    def given_the_call(self, operation: Any) -> Any:
        """A class operation that takes the call's project or the call itself, with those left out of its signature, so
        no caller passes them and its tool hands them over from the call it serves. Any other operation as it is."""
        taken = tuple(name for name in FROM_THE_CALL if inspect.ismethod(operation) and name in inspect.signature(operation).parameters)
        if not taken:
            return operation
        function = operation.__func__
        signature = inspect.signature(function)

        @functools.wraps(function)
        def on_the_call(owner: Any, *arguments: Any, **named: Any) -> Any:
            return function(owner, *arguments, **named)

        on_the_call.__signature__ = signature.replace(parameters=[parameter for parameter in signature.parameters.values() if parameter.name not in taken])
        on_the_call.__annotations__ = {name: hint for name, hint in function.__annotations__.items() if name not in taken}
        return types.MethodType(TakesFromCall(*taken).annotate(on_the_call), operation.__self__)


class InstallDestination:
    """The channels a member is published to, in the order a tool lists them. Each channel's annotation is a *Destination*
    its publisher defines (harness/installation, harness/mcp, harness/hooks), so this module names the channels and
    never imports the publishers."""

    MCP = "mcp"
    HOOK = "hook"
    SKILL = "skill"
    COMMAND = "command"
    RULE = "rules"
    LISTED = (MCP, SKILL, COMMAND, RULE, HOOK)


class AgentToolDestination:
    """Which install destinations this tool is annotated for."""

    callable: Callable[..., Any]

    @property
    def install_to_mcp(self) -> bool:
        return self.install_to(InstallDestination.MCP)

    @property
    def install_to_hook(self) -> bool:
        return self.install_to(InstallDestination.HOOK)

    @property
    def hook_event(self) -> str:
        """The IDE event this tool's ``@Hook`` annotation names, or empty when the tool is not a hook."""
        return annotation_kinds.name_given_for(InstallDestination.HOOK, self.callable)

    @property
    def install_to_skill(self) -> bool:
        return self.install_to(InstallDestination.SKILL)

    def install_to(self, destination: str) -> bool:
        return annotation_kinds.publishes(destination, self.callable)

    @property
    def destinations(self) -> list[str]:
        return [destination for destination in InstallDestination.LISTED if self.install_to(destination)]


@dataclass
class AgentTool(AgentToolDestination):
    name: str
    callable: Callable[..., Any]
    toolset: AgentToolSet
    _body: str | None = field(default=None, repr=False)

    # The line a skill or command ends with to tell the agent which MCP tool runs it. A tool writes it, and the
    # installer reads the tool names back from installed files, so both go through here.
    INVOKE_PREFIX: ClassVar[str] = "Use MCP tool:"
    _INVOKED_NAME: ClassVar[re.Pattern[str]] = re.compile(r"Use MCP tool:\s*`([A-Za-z0-9_.-]+)")

    @classmethod
    def invoked_names(cls, text: str) -> list[str]:
        """The MCP tool each ``Use MCP tool:`` line in text names."""
        return cls._INVOKED_NAME.findall(text)

    @classmethod
    def is_invoke_line(cls, line: str) -> bool:
        """Whether line is a ``Use MCP tool:`` line."""
        return line.strip().casefold().startswith(cls.INVOKE_PREFIX.casefold())

    @property
    def slug(self) -> str:
        return self.toolset.slug

    @property
    def registration_name(self) -> str:
        return self.toolset.registration_name

    @property
    def deploy_name(self) -> str:
        return (
            annotation_kinds.name_given_for(InstallDestination.COMMAND, self.callable)
            or annotation_kinds.name_given_for(InstallDestination.SKILL, self.callable)
            or self.name
        )

    @property
    def mcp_name(self) -> str:
        """The name MCP publishes this tool under and the session log records it by: ``{toolset slug}.{name}``. A
        practice's own instructions are published under the practice's slug alone."""
        if self.toolset.is_part_of_practice and self.name == "instructions":
            return self.slug
        return f"{self.slug}.{self.name}"

    def is_called(self, called: str) -> bool:
        """Whether called, the name a client sent, names this tool: its MCP name as published (``generate.generate``),
        or as an IDE spells it, with any ``mcp__{server}__`` prefix Claude Code adds, in any case, and with dots and
        hyphens written as underscores (``generate_generate``, ``fidelity_progress_files``). The server resolves a call
        and a rules hook recognises its own action's tool by this one rule, so the two never disagree on a name."""
        return bool(called) and self.spelled(called) == self.spelled(self.mcp_name)

    @classmethod
    def spelled(cls, name: str) -> str:
        """name as every client spelling of it compares: without an ``mcp__{server}__`` prefix, case folded, with dots and
        hyphens as underscores."""
        return name.rsplit("__", 1)[-1].casefold().replace(".", "_").replace("-", "_")

    def invoke_line(self) -> str:
        """The ``Use MCP tool:`` line a skill or command ends with, naming the tool and the parameters it takes."""
        try:
            signature = inspect.signature(self.callable)
            params = inspect.Signature([p for n, p in signature.parameters.items() if n not in {"self", "cls"}])
            suffix = str(params)
        except (TypeError, ValueError):
            suffix = "()"
        return f"{self.INVOKE_PREFIX} `{self.mcp_name}{suffix}`"

    @functools.cached_property
    def parameter_schema(self) -> ParameterSchema:
        """The parameters a caller passes to this tool's callable, read once from its type hints."""
        return ParameterSchema(self.callable)

    @property
    def input_schema(self) -> dict[str, Any]:
        """The JSON Schema of the arguments a caller passes, read from the callable's type hints."""
        return self.parameter_schema.json_schema

    def invoke(self, arguments: dict[str, Any] | None = None, *, project: Path | str | None = None) -> Any:
        """Run the tool with arguments as a caller sent them, on the checkout of project, the project the calling chat
        works on."""
        return self.answer(ToolCall(arguments, project))

    def answer(self, call: ToolCall) -> Any:
        """Answer call on its toolset made for it: log the call in the session it works in, then call the tool with each
        argument in the type its parameter declares."""
        with call.being_answered():
            tool = self.on(self.toolset.for_call(call))
            tool.log_session_invocation(call)
            return tool.callable(**self.parameter_schema.coerced(call.arguments), **tool._from_the_call(call))

    def on(self, toolset: Any) -> AgentTool:
        """This tool on toolset, a toolset of the same class made for one call; the tool as it is when toolset is its
        own."""
        if toolset is self.toolset:
            return self
        bound = getattr(self.callable, "__self__", None) is self.toolset
        return replace(self, callable=types.MethodType(self.callable.__func__, toolset) if bound else self.callable, toolset=toolset)

    def _from_the_call(self, call: ToolCall) -> dict[str, Any]:
        """The arguments a callable that takes them is handed from call: the checkout call names as ``project``, and
        call itself as ``call``."""
        taken = TakesFromCall.names_on(self.callable)
        if CALLED_PROJECT in taken and call.project is None:
            raise CallNamesNoProject(self.mcp_name)
        return {name: call.project if name == CALLED_PROJECT else call for name in taken}

    def should_log_session_invocation(self, arguments: dict[str, Any] | None) -> bool:
        if arguments and arguments.get("ping") is True:
            return False
        if NoSessionLog.annotates(self.callable):
            return False
        if AgentToolAnnotation.annotates(self.callable):
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
        session.log.by(call.chat).tool(self.mcp_name, call.named_paths)

    @property
    def kind(self) -> str:
        if AgentToolAnnotation.annotates(self.callable):
            return "tool"
        if AgentInstructionsAnnotation.annotates(self.callable):
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
        for parameter, note in self.toolset.parameter_notes.items():
            if parameter in parameters and note not in text:
                text = f"{text}\n\n{note}" if text else note
        return text

    def _with_sub_agent_preamble(self, text: str) -> str:
        return SubAgentAnnotation.with_hand_off(text) if SubAgentAnnotation.annotates(self.callable) else text

    @functools.cached_property
    def description(self) -> str:
        """What the tool does, expanded from its docstring once: MCP lists it on every request for the tool list."""
        expanded = self.toolset.class_markdown.expand_docstring(self.docstring)
        if expanded:
            return expanded
        if self.name == "instructions" and (self.toolset.overview or "").strip():
            return self.toolset.overview.strip()
        return self.docstring or self.callable.__name__


@dataclass
class AgentOperation(AgentTool):
    @property
    def kind(self) -> str:
        return "tool"


@dataclass
class AgentInstructions(AgentTool):
    """An ``@agent_instructions`` operation: its recipe body, expanded for a call, is the instructions an agent
    follows. Each expansion runs in a *RecipeExpansion* of its own."""

    @property
    def kind(self) -> str:
        if AgentToolAnnotation.annotates(self.callable):
            return "tool"
        return "instructions"

    @classmethod
    def for_callable(cls, callable: Callable[..., Any], toolset: AgentToolSet) -> AgentInstructions:
        """The instructions member of toolset that callable, one of its ``@agent_instructions`` operations, is."""
        if isinstance(callable, property):
            callable = callable.fget
        return toolset.instruction(callable.__name__)

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
        if tool.name == "instructions":
            return tool.toolset.instructions
        return tool._expanded_reply(call.arguments)

    def _expanded_reply(self, arguments: dict[str, Any]) -> str:
        toolset = self.toolset
        expanded = self.expand(arguments)
        body = (expanded.instructions or "").strip()
        doc = (inspect.getdoc(self.callable) or "").strip()
        if doc and doc not in body:
            body = f"{doc}\n\n{body}".strip() if body else doc
        reply = body or self.description or doc
        # An action that works in a session says which one, so the agent knows its folders without looking for them.
        session = toolset.session_context
        return f"{reply}\n\n{session}" if session else reply

    @functools.cached_property
    def recipe_source(self) -> RecipeSource:
        """What this operation's recipe says, read once from the callable it holds."""
        return RecipeSource(self.callable)

    def expand(self, arguments: dict[str, Any]) -> ExpansionResult:
        """The recipe expanded for one call's arguments: its instructions, the tools it names, and its result line, what
        the recipe returned for those arguments, with every placeholder filled."""
        expansion = RecipeExpansion(self, arguments).run()
        values = self.parameter_schema.with_defaults(arguments)
        placeholders = RecipePlaceholders(values, set(self.parameter_schema.names), self.toolset)
        lines = (placeholders.filled(part) for part in expansion.prompt)
        instructions = "\n\n".join(line for line in lines if line.strip())
        return ExpansionResult(
            instructions=self._with_sub_agent_preamble(instructions),
            tools=expansion.tools,
            result=placeholders.filled(expansion.result or f"Instructions for {self.callable.__name__}"),
        )

    def members_of(self, target: Any) -> ToolsetMembers:
        """The members of target, a toolset this recipe names, that are its tools."""
        return ToolsetMembers.of(type(target))

    def member_of(self, target: AgentToolSet, member: str) -> AgentInstructions:
        """The instructions operation member on target, a toolset this recipe names."""
        return target.instruction(member)

    def provider_of(self, owner: Any, provider_name: str) -> Any:
        """The object owner's provider gives: a toolset it holds as it is, or what a provider operation answers."""
        provided = getattr(owner, provider_name)
        if AgentToolSetAnnotation.annotates(type(provided)):
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
            if callable(recipe) and AgentInstructionsAnnotation.annotates(recipe):
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


class AgentToolAnnotation(Annotation):
    """Annotate a method as a tool; description comes from the method docstring."""

    flag = "_is_agent_tool"
    typed_name = "agent_tool"

    @classmethod
    def installs_member(cls) -> bool:
        return True


class AgentInstructionsAnnotation(Annotation):
    """Annotate a method as @agent_instructions; unwrapped body code runs during expand."""

    flag = "_is_agent_instructions"
    typed_name = "agent_instructions"

    @classmethod
    def installs_member(cls) -> bool:
        return True


class _ClassJoiningAnnotation(Annotation):
    """A class annotation that gives the class it annotates a framework base by making, in its place, a class of the same name
    that derives from both: ``@agent_toolset`` gives AgentToolSet, ``@toolset_collection`` ToolSetCollection. Authors
    annotate the class rather than subclass the base, so a class reads as its own domain first."""

    annotation_name = ""

    def __new__(cls, target: Any = None):
        annotation = object.__new__(cls)
        return annotation.annotate(target) if target is not None else annotation

    def __call__(self, target: Any) -> Any:
        return self.annotate(target)

    def _joined(self, target: type, base: type) -> type:
        """target joined with base, or target itself when it already carries this annotation. Raises TypeError for a class
        that subclasses base directly."""
        if self.flag in target.__dict__ or self.annotates(target):
            return target
        if issubclass(target, base):
            raise TypeError(f"{target.__name__} must use @{self.annotation_name} — do not subclass {base.__name__} directly")
        own = {name: value for name, value in vars(target).items() if name not in ("__dict__", "__weakref__")}
        joined = type(target.__name__, (target, base), own)
        joined.__doc__ = target.__doc__
        joined.__module__ = target.__module__
        joined.__qualname__ = target.__qualname__
        setattr(joined, self.flag, True)
        return joined


class AgentToolSetAnnotation(_ClassJoiningAnnotation):
    """Annotate a class as an agent toolset — @agent_tool and @agent_instructions."""

    flag = "_is_agent_toolset"
    annotation_name = "agent_toolset"
    copied = False

    def __new__(cls, target: type | None = None):
        return super().__new__(cls, target if isinstance(target, type) else None)

    def annotate(self, toolset_class: type) -> type:
        if self.flag in toolset_class.__dict__:
            return toolset_class
        joined = self._joined(toolset_class, AgentToolSet)
        ToolsetValidator(joined).validate()
        return joined


class ToolSetCollectionAnnotation(_ClassJoiningAnnotation):
    """Annotate a class as a ToolSetCollection, or a property as one of this toolset's collections."""

    flag = "_is_toolset_collection"
    annotation_name = "toolset_collection"

    def annotate(self, target: Any) -> Any:
        if inspect.isclass(target):
            return self._joined(target, ToolSetCollection)
        setattr(getattr(target, "fget", target), self.flag, True)
        return target


class PublishedWhereHeld(Annotation):
    """A collection's tool that only the toolset holding the collection itself publishes: a toolset that reaches the
    collection through one of its child toolsets, as a practice reaches each fidelity's rules, does not publish it as
    its own. A practice's rule injection serves its shared rules this way, and each fidelity's rules are not injected
    a second time through the practice."""

    flag = "_published_where_held"
    copied = False


class SubAgentAnnotation(Annotation):
    """Annotate an @agent_tool or @agent_instructions member for non-blocking sub-agent launch: its description starts with
    the hand-off to a background sub-agent. The ``sub-agent.sub_agent`` operation itself is the SubAgent toolset in
    tools/sub_agent."""

    flag = "_sub_agent"

    @classmethod
    def with_hand_off(cls, text: str) -> str:
        """text with the hand-off to a background sub-agent in front of it."""
        preamble = SUB_AGENT_CALLER_PREAMBLE.strip()
        body = (text or "").strip()
        return f"{preamble}\n\n{body}" if body else preamble


class NoSessionLog(Annotation):
    """Keep an operation's calls out of the session log. Use it on reads an agent or a mod repeats often, such as the
    session board, so the log keeps the work that was done rather than every look at it."""

    flag = "_no_session_log"
    copied = False


class ToolSubject(Annotation):
    """Annotate the classmethod that finds the object a tool call acts on, so ``@agent_tool`` can sit on a domain class
    whose constructor takes collaborators. Each instance operation's tool takes this loader's arguments before its
    own: ``load(ticket)`` and ``move_next(self)`` make the tool ``ticket.move_next(ticket)``. A loader that takes
    ``project`` is handed the checkout of the project its call works on, so ``load(ticket, *, project)`` loads the
    ticket from that project's board and the tool still takes only ``ticket``."""

    flag = "_is_tool_subject"
    copied = False


class OnSubject(Annotation):
    """Set on the tool made from an instance operation of a ``@tool_subject`` class: it loads its object from its
    leading arguments before it runs the operation."""

    flag = "_runs_on_subject"
    copied = False


class TakesFromCall(NamesAnnotation):
    """Set on a tool's callable that takes the project its call works on, or the call itself, which its signature
    leaves out because no caller passes them: the tool hands them over from the ``ToolCall`` it serves. A loader that
    takes the call opens the session the call names, and an operation that takes it points what it logs at the chat the
    call came from."""

    flag = "_takes_from_call"


noSessionLog = NoSessionLog
subAgent = SubAgentAnnotation()
published_where_held = PublishedWhereHeld
tool_subject = ToolSubject


agent_tool = AgentToolAnnotation
agent_toolset = AgentToolSetAnnotation
agent_instructions = AgentInstructionsAnnotation
toolset_collection = ToolSetCollectionAnnotation
