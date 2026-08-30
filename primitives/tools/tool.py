"""_Tool and toolset primitives for discoverable capabilities.

Workflow for a @toolset class file:
1. Read the mandatory @toolset-manifest comment at the top of the file (identity only — do not remanifest).
2. Read the Agent reading this file line — slash/skill is the catalog; instructions load via CLI, not Python source.
3. Pipe a yaml fence to stdin; .\\tools.ps1 run - with tool: or action:. Do not write a request file.
4. Follow response.instructions before authoring behavior.

Parse headers with tools.toolset_header.read_toolset_header(path).
"""
from __future__ import annotations

import importlib.util
import inspect
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Mapping, get_args, get_origin

from tools.types import (
    JsonSchema,
    ManifestDocument,
    ResourceDocument,
    ResourceValues,
    RunRequestDocument,
    RunResponseDocument,
    SignatureEntry,
    ToolDocument,
    TypeAnnotation,
    YamlValue,
)

MANIFEST_MARKER = "@toolset-manifest"

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


class _classproperty:
    def __init__(self, fget: Callable[[type], Any]) -> None:
        self.fget = fget

    def __get__(self, instance: Any, owner: type) -> Any:
        return self.fget(owner)


class RunError(Exception):
    def __init__(self, message: str, *, response: RunResponseDocument | None = None) -> None:
        super().__init__(message)
        self._response = response or {"ok": False, "error": message}

    @property
    def response(self) -> RunResponseDocument:
        return self._response


class _SignatureReader:
    """Introspects callables for manifest signatures. Subclass and replace ``instance()`` to extend."""

    _instance: _SignatureReader | None = None

    @classmethod
    def instance(cls) -> _SignatureReader:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, reader: _SignatureReader | None) -> None:
        cls._instance = reader

    def member_instructions(self, func: Callable[..., Any]) -> str:
        from primitives.instructions import _expand_docstring

        doc = (func.__doc__ or "").strip()
        # No docstring: use the method name as the lookup label (same fallback _walk_body uses).
        label = doc if doc else func.__name__
        if label.isidentifier():
            return _expand_docstring(label, func)
        return label

    def simple_type(self, annotation: TypeAnnotation) -> str:
        if annotation is inspect.Parameter.empty:
            return "str"
        if isinstance(annotation, str):
            return self._simple_type_from_string(annotation)
        origin = get_origin(annotation)
        if origin is list:
            return self._list_simple_type(annotation)
        if origin is dict:
            return "dict"
        return self._builtin_simple_type(annotation, origin)

    def simple_return_type(self, func: Callable[..., Any]) -> str | None:
        sig = inspect.signature(func)
        if sig.return_annotation is inspect.Signature.empty:
            return None
        return self.simple_type(sig.return_annotation)

    def simple_parameters(self, func: Callable[..., Any]) -> dict[str, str]:
        sig = inspect.signature(func)
        parameters: dict[str, str] = {}
        for name, param in sig.parameters.items():
            if name in ("self", "cls"):
                continue
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            parameters[name] = self.simple_type(param.annotation)
        return parameters

    def annotation_schema(self, annotation: TypeAnnotation) -> JsonSchema:
        if annotation is inspect.Parameter.empty:
            return {"type": "string"}
        origin = get_origin(annotation)
        if origin is list:
            return self._list_annotation_schema(annotation)
        if origin is dict:
            return {"type": "object"}
        if origin is type(None) or annotation is type(None):
            return {"type": "null"}
        if origin is not None:
            return {"type": "string", "format": str(origin)}
        if isinstance(annotation, str):
            return {"type": "string", "format": annotation}
        return self._builtin_annotation_schema(annotation)

    def input_schema(self, func: Callable[..., Any]) -> JsonSchema:
        sig = inspect.signature(func)
        properties: dict[str, Any] = {}
        required: list[str] = []
        for name, param in sig.parameters.items():
            if name in ("self", "cls"):
                continue
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            properties[name] = self.annotation_schema(param.annotation)
            if param.default is inspect.Parameter.empty:
                required.append(name)
        if properties:
            return {"type": "object", "properties": properties, "required": required}
        return {"type": "object", "additionalProperties": False}

    def output_schema(self, func: Callable[..., Any]) -> JsonSchema | None:
        sig = inspect.signature(func)
        if sig.return_annotation is inspect.Signature.empty:
            return None
        if sig.return_annotation in (None, type(None)):
            return None
        return self.annotation_schema(sig.return_annotation)

    def _simple_type_from_string(self, annotation_text: str) -> str:
        origin_name, _, args_text = annotation_text.partition("[")
        if origin_name == "list":
            element_text = args_text.rstrip("]") if args_text else "str"
            return f"list[{self.simple_type(element_text)}]"
        return annotation_text

    def _list_simple_type(self, annotation: Any) -> str:
        args = get_args(annotation)
        element_type = self.simple_type(args[0]) if args else "str"
        return f"list[{element_type}]"

    def _builtin_simple_type(self, annotation: Any, origin: Any) -> str:
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

    def _list_annotation_schema(self, annotation: Any) -> dict[str, Any]:
        args = get_args(annotation)
        element_schema = self.annotation_schema(args[0]) if args else {"type": "string"}
        return {"type": "array", "items": element_schema}

    def _builtin_annotation_schema(self, annotation: Any) -> dict[str, Any]:
        if annotation is str:
            return {"type": "string"}
        if annotation is int:
            return {"type": "integer"}
        if annotation is float:
            return {"type": "number"}
        if annotation is bool:
            return {"type": "boolean"}
        return {"type": "string", "format": getattr(annotation, "__name__", str(annotation))}


class _ManifestYaml:
    """Serializes manifest documents to YAML. Subclass and replace ``instance()`` to extend."""

    _instance: _ManifestYaml | None = None

    @classmethod
    def instance(cls) -> _ManifestYaml:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, serializer: _ManifestYaml | None) -> None:
        cls._instance = serializer

    def serialize_value(self, raw_value: YamlValue) -> YamlValue:
        if isinstance(raw_value, Path):
            return str(raw_value)
        if isinstance(raw_value, dict):
            return {
                key: self.serialize_value(nested_value)
                for key, nested_value in raw_value.items()
            }
        if isinstance(raw_value, list):
            return [self.serialize_value(element) for element in raw_value]
        to_dict = getattr(raw_value, "to_dict", None)
        if callable(to_dict):
            return self.serialize_value(to_dict())
        return raw_value

    def dump_manifest(self, manifest_data: ManifestDocument) -> str:
        if yaml is None:
            raise RuntimeError("PyYAML required to render front matter")
        return yaml.safe_dump(
            self.serialize_value(manifest_data),
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        ).strip()

    def fenced(self, body: str, *, lang: str = "yaml") -> str:
        """Wrap YAML text in a markdown fence for agent-parseable CLI output."""
        return f"```{lang}\n{body.rstrip()}\n```"

    def dump_fenced(self, manifest_data: ManifestDocument, *, lang: str = "yaml") -> str:
        return self.fenced(self.dump_manifest(manifest_data), lang=lang)

    def unfence(self, text: str) -> str:
        lines = text.strip().splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines)

    def load_fenced(self, text: str) -> YamlValue:
        if yaml is None:
            raise RuntimeError("PyYAML required to parse YAML")
        return yaml.safe_load(self.unfence(text))

    def frontmatter(self, manifest_data: ManifestDocument) -> str:
        return f"---\n{self.dump_manifest(manifest_data)}\n---\n"


class _ToolsetLoader:
    """Loads @toolset classes by module path. Subclass and replace ``instance()`` to extend."""

    _instance: _ToolsetLoader | None = None

    @classmethod
    def instance(cls) -> _ToolsetLoader:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, loader: _ToolsetLoader | None) -> None:
        cls._instance = loader

    def check_toolset(self, candidate: type) -> bool:
        return isinstance(candidate, type) and (
            getattr(candidate, "_is_toolset", False) or getattr(candidate, "_is_context", False)
        )

    def load(self, path: str) -> type:
        module_name, _, class_name = path.partition(":")
        if not class_name:
            raise ValueError(f"expected <module>:<Class>, got {path!r}")
        try:
            module = __import__(module_name, fromlist=[class_name])
        except ModuleNotFoundError:
            module = self._load_hyphenated(module_name)
        loaded = getattr(module, class_name)
        if not self.check_toolset(loaded):
            raise TypeError(f"{path} is not a @toolset class")
        return loaded

    def _load_hyphenated(self, module_name: str) -> ModuleType:
        """Fallback loader for modules whose directory uses hyphens instead of underscores.

        Translates each package segment's underscores to hyphens when the standard
        import fails, allowing e.g. ``some_domain.some_domain`` to resolve from
        ``<root>/some-domain/some_domain.py`` if the underscore directory is absent.
        """
        parts = module_name.split(".")
        repo = Path(__file__).resolve().parents[2]
        search_roots = [repo] + [
            repo / name for name in ("primitives", "utilities", "context_tools", "context_tools/actions")
        ]
        module_file = None
        for root in search_roots:
            search = root
            for part in parts[:-1]:
                hyphenated = part.replace("_", "-")
                candidate = search / hyphenated
                search = candidate if candidate.is_dir() else search / part
            candidate_file = search / f"{parts[-1]}.py"
            if candidate_file.exists():
                module_file = candidate_file
                break
        if module_file is None:
            raise ModuleNotFoundError(
                f"No module named {module_name!r} (also tried under {search_roots})"
            )
        spec = importlib.util.spec_from_file_location(module_name, module_file)
        if spec is None or spec.loader is None:
            raise ModuleNotFoundError(f"Cannot create spec for {module_file}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod


class _ToolsetRunner:
    """Invokes one tool from a YAML request dict. Subclass and replace ``instance()`` to extend."""

    _instance: _ToolsetRunner | None = None

    def __init__(self) -> None:
        self._loader = _ToolsetLoader.instance()
        self._yaml = _ManifestYaml.instance()

    @classmethod
    def instance(cls) -> _ToolsetRunner:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, runner: _ToolsetRunner | None) -> None:
        cls._instance = runner

    def run_request(self, request: RunRequestDocument) -> RunResponseDocument:
        from workspace import SessionLog

        parsed = self._parse_run_request(request)
        SessionLog.instance().set_session(parsed.session)
        toolset_cls = self._loader.load(str(parsed.toolset_path))
        instance = self._build_instance(toolset_cls, parsed.context)
        if parsed.action_name:
            return self._run_action(request, parsed, instance)
        return self._run_tool(request, parsed, instance)

    def _run_tool(
        self,
        request: dict[str, Any],
        parsed: "_RunRequest",
        instance: Toolset,
    ) -> dict[str, Any]:
        result = self._invoke_tool(instance, str(parsed.tool_name), parsed.arguments)
        return self._build_tool_response(request, parsed.toolset_path, parsed.tool_name, instance, result)

    def _run_action(
        self,
        request: dict[str, Any],
        parsed: "_RunRequest",
        instance: Toolset,
    ) -> dict[str, Any]:
        from tools.extensions import ToolsetExtensions

        return ToolsetExtensions.instance().run(
            "action",
            request,
            toolset_path=parsed.toolset_path,
            action_name=parsed.action_name,
            context=parsed.context,
            arguments=parsed.arguments,
            instance=instance,
        )

    def _parse_run_request(self, request: dict[str, Any]) -> "_RunRequest":
        if not isinstance(request, dict):
            raise RunError("request must be a YAML mapping", response={"ok": False, "error": "invalid request"})
        toolset_path = request.get("toolset")
        if not toolset_path:
            raise RunError("request missing toolset", response={"ok": False, "error": "request missing toolset"})
        tool_name = request.get("tool")
        action_name = request.get("action")
        if tool_name and action_name:
            raise RunError(
                "request must use tool or action, not both",
                response={"ok": False, "error": "tool and action are mutually exclusive"},
            )
        if not tool_name and not action_name:
            raise RunError(
                "request missing tool or action",
                response={"ok": False, "error": "request missing tool or action"},
            )
        context = self._mapping_field(request, "context", default={})
        arguments = self._mapping_field(request, "arguments", default={})
        session = request.get("session")
        log_control = request.get("log")
        return _RunRequest(
            toolset_path=toolset_path,
            tool_name=tool_name,
            action_name=action_name,
            context=context,
            arguments=arguments,
            session=str(session) if session is not None else None,
            log_control=str(log_control) if log_control is not None else None,
        )

    def _mapping_field(
        self, request: dict[str, Any], field_name: str, *, default: dict[str, Any]
    ) -> dict[str, Any]:
        field_value = request.get(field_name, default)
        if not isinstance(field_value, dict):
            raise RunError(
                f"{field_name} must be a mapping",
                response={"ok": False, "error": f"invalid {field_name}"},
            )
        return field_value

    def _build_instance(self, toolset_cls: type, context: dict[str, Any]) -> Toolset:
        reader = _SignatureReader.instance()
        schema = reader.input_schema(toolset_cls.__init__)
        missing = [name for name in schema.get("required", []) if name not in context]
        if missing:
            joined = ", ".join(missing)
            raise RunError(
                f"{toolset_cls.__name__} missing required context params: {joined} — use AskQuestion to get the value from the user",
                response={
                    "ok": False,
                    "error": "missing required context",
                    "missing": missing,
                    "detail": f"Use AskQuestion to collect: {joined}",
                },
            )
        try:
            return toolset_cls(**context)
        except TypeError as exc:
            raise RunError(
                f"invalid context for {toolset_cls.__name__}: {exc}",
                response={"ok": False, "error": "invalid context", "detail": str(exc)},
            ) from exc

    def _invoke_tool(self, instance: Toolset, tool_name: str, arguments: dict[str, Any]) -> Any:
        bound = self._resolve_runnable(instance, tool_name)
        if bound is None:
            raise RunError(
                f"unknown tool {tool_name!r}",
                response={"ok": False, "tool": tool_name, "error": "unknown tool"},
            )
        self._validate_arguments(bound, arguments)
        return getattr(instance, tool_name)(**arguments)

    def _resolve_runnable(self, instance: Toolset, tool_name: str) -> Any:
        """A @agent_tool, or a registered extension member that is not an @agent_instructions."""
        if tool_name in instance.tools:
            return instance.tools[tool_name]
        from tools.extensions import ToolsetExtensions

        members = ToolsetExtensions.instance().members("sub_agent", instance)
        if tool_name in members:
            return members[tool_name]
        return None

    def _validate_arguments(self, tool: _Tool, arguments: dict[str, Any]) -> None:
        reader = _SignatureReader.instance()
        schema = reader.input_schema(tool.callable)
        missing = [name for name in schema.get("required", []) if name not in arguments]
        if missing:
            joined = ", ".join(missing)
            raise RunError(
                f"{tool.name} missing required arguments: {joined} — use AskQuestion to get the value from the user",
                response={
                    "ok": False,
                    "tool": tool.name,
                    "error": "missing required arguments",
                    "missing": missing,
                    "detail": f"Use AskQuestion to collect: {joined}",
                },
            )

    def _build_tool_response(
        self,
        request: dict[str, Any],
        toolset_path: Any,
        tool_name: Any,
        instance: Toolset,
        result: Any,
    ) -> dict[str, Any]:
        response: dict[str, Any] = {
            "ok": True,
            "toolset": str(toolset_path),
            "tool": str(tool_name),
            "result": self._yaml.serialize_value(result),
        }
        if request.get("include_resources", True):
            response["resources"] = self._yaml.serialize_value(instance.resources)
        return response


@dataclass(frozen=True)
class _RunRequest:
    toolset_path: Any
    tool_name: Any
    action_name: Any
    context: dict[str, Any]
    arguments: dict[str, Any]
    session: str | None = None
    log_control: str | None = None


def _slugify_class_name(name: str) -> str:
    """PascalCase -> snake_case so toolset_name matches package/folder names."""
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class Toolset:
    """Injected by @toolset - use the decorator, not direct subclassing."""

    def __init__(self) -> None:
        pass

    @property
    def toolset_name(self) -> str:
        return _slugify_class_name(type(self).__name__)

    @property
    def domain_slug(self) -> str:
        return self.toolset_name

    @property
    def instructions(self) -> str:
        return (self.__class__.__doc__ or "").strip()

    @property
    def tools(self) -> dict[str, _Tool]:
        return _discover_tools(self)

    @property
    def actions(self) -> Mapping[str, Any]:
        """Action members when the actions package has registered; otherwise empty."""
        from tools.extensions import ToolsetExtensions

        return ToolsetExtensions.instance().members("actions", self)

    @property
    def resource_entries(self) -> dict[str, _Resource]:
        return _discover_resources(self)

    @property
    def resources(self) -> ResourceValues:
        return {name: getattr(self, name) for name in self.resource_entries}

    @property
    def signature(self) -> ManifestDocument:
        from tools.manifest import _ManifestBuilder

        return _ManifestBuilder(self).build()

    @property
    def capabilities(self) -> list[str]:
        from tools.extensions import ToolsetExtensions

        return ["tool", *ToolsetExtensions.instance().extra_capabilities(self)]

    @property
    def front_matter(self) -> str:
        cls = type(self)
        return _ManifestYaml.instance().frontmatter(
            {
                "type": cls.toolset_slug,
                "capabilities": self.capabilities,
                "signature": self.signature,
            }
        )

    @_classproperty
    def toolset_slug(cls) -> str:
        return cls.__name__.lower()

    @_classproperty
    def manifest_path(cls) -> str:
        return f"{cls.__module__}:{cls.__name__}"

    @_classproperty
    def manifest_command(cls) -> str:
        return f"python -m tools manifest {cls.manifest_path}"

    @_classproperty
    def run_command(cls) -> str:
        return ".\\tools.ps1 run -"

    @_classproperty
    def manifest(cls) -> Toolset:
        """Toolset without context - read front matter and MCP shape without running tools."""
        if not _ToolsetLoader.instance().check_toolset(cls):
            raise TypeError(f"{cls.__name__} is not a @toolset class")
        instance = object.__new__(cls)
        Toolset.__init__(instance)
        return instance


@dataclass(frozen=True)
class _Tool:
    """One invokable action on a toolset."""

    name: str
    callable: Callable[..., Any]

    @property
    def instructions(self) -> str:
        return _SignatureReader.instance().member_instructions(self.callable)

    @property
    def manifest(self) -> ToolDocument:
        """MCP _Tool - name, description, inputSchema, optional outputSchema."""
        reader = _SignatureReader.instance()
        entry: ToolDocument = {
            "name": self.name,
            "description": self.instructions,
            "inputSchema": reader.input_schema(self.callable),
        }
        output = reader.output_schema(self.callable)
        if output is not None:
            entry["outputSchema"] = output
        return entry

    @property
    def signature_entry(self) -> SignatureEntry:
        reader = _SignatureReader.instance()
        entry: SignatureEntry = {"kind": "tool"}
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


@dataclass(frozen=True)
class _Resource:
    """One read-only observable on a toolset."""

    name: str
    getter: Callable[..., Any]
    toolset_name: str

    @property
    def instructions(self) -> str:
        return _SignatureReader.instance().member_instructions(self.getter)

    @property
    def manifest(self) -> ResourceDocument:
        """MCP _Resource - uri, name, description, mimeType."""
        return {
            "uri": f"resource://{self.toolset_name}/{self.name}",
            "name": self.name,
            "description": self.instructions,
            "mimeType": "application/json",
        }

    @property
    def signature_entry(self) -> SignatureEntry:
        reader = _SignatureReader.instance()
        return {
            "kind": "resource",
            "type": reader.simple_return_type(self.getter) or "str",
        }

    def add_to_signature(self, signature: ManifestDocument) -> None:
        signature[self.name] = self.signature_entry


def agent_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a method as a tool; instructions come from the method docstring."""
    func._is_agent_tool = True
    return func


def resource(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a property getter as a read-only resource; instructions come from the getter docstring."""
    func._is_resource = True
    return func


def _discover_tools(instance: Toolset) -> dict[str, _Tool]:
    discovered: dict[str, _Tool] = {}
    for name, member in inspect.getmembers(instance.__class__, predicate=inspect.isfunction):
        if getattr(member, "_is_agent_tool", False):
            discovered[name] = _Tool(name=name, callable=getattr(instance, name))
    return discovered


def _discover_resources(instance: Toolset) -> dict[str, _Resource]:
    discovered: dict[str, _Resource] = {}
    toolset_name = instance.__class__.__name__
    for cls in instance.__class__.__mro__:
        for name, member in cls.__dict__.items():
            if name in discovered:
                continue
            if not isinstance(member, property) or member.fget is None:
                continue
            if getattr(member.fget, "_is_resource", False):
                discovered[name] = _Resource(
                    name=name,
                    getter=member.fget,
                    toolset_name=toolset_name,
                )
    return discovered

def toolset(cls: type) -> type:
    """Mark a class as a toolset and inject toolset behavior."""
    if "_is_toolset" in cls.__dict__:
        return cls
    if getattr(cls, "_is_toolset", False):
        from workspace import inherit_annotations_from_bases
        from tools.extensions import ToolsetExtensions

        inherit_annotations_from_bases(cls)
        ToolsetExtensions.instance().validate_toolset(cls)
        return cls
    if issubclass(cls, Toolset):
        raise TypeError(f"{cls.__name__} must use @toolset - do not subclass Toolset")
    merged = type(
        cls.__name__,
        (cls, Toolset),
        {
            attribute_name: attribute_value
            for attribute_name, attribute_value in vars(cls).items()
            if attribute_name not in ("__dict__", "__weakref__")
        },
    )
    merged.__doc__ = cls.__doc__
    merged.__module__ = cls.__module__
    merged.__qualname__ = cls.__qualname__
    merged._is_toolset = True  # type: ignore[attr-defined]
    from workspace import inherit_annotations_from_bases
    from tools.extensions import ToolsetExtensions

    inherit_annotations_from_bases(merged)
    ToolsetExtensions.instance().validate_toolset(merged)
    return merged
