"""The parameters of one tool's callable, read from its Python type hints: the JSON Schema MCP publishes for it, and
the arguments a call sends turned back into the Python types the callable declares."""
from __future__ import annotations

import functools
import inspect
import types as py_types
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, NotRequired, Required, Union, get_args, get_origin, get_type_hints, is_typeddict

_UNION_ORIGINS = {Union, py_types.UnionType}
_ARRAY_ORIGINS = {list, tuple, Sequence}
_OBJECT_ORIGINS = {dict, Mapping}
_SCALAR_SCHEMAS: dict[object, dict[str, Any]] = {
    str: {"type": "string"},
    int: {"type": "integer"},
    float: {"type": "number"},
    bool: {"type": "boolean"},
    type(None): {"type": "null"},
    Path: {"type": "string", "description": "Filesystem path"},
    bytes: {"type": "string"},
}


class ParameterSchema:
    """The parameters a caller passes to one callable, as their type hints declare them. Every reader of a tool's
    parameter types goes through here, so the schema MCP publishes and the arguments it hands on always agree."""

    def __init__(self, callable: Callable[..., object]) -> None:
        self._callable = callable

    @functools.cached_property
    def json_schema(self) -> dict[str, Any]:
        """The JSON Schema of the parameters a caller passes, read once; ``self`` and ``cls`` are not among them."""
        hints = self._hints()
        properties: dict[str, Any] = {}
        required: list[str] = []
        for name, param in self._parameters().items():
            properties[name] = self._parameter_schema(hints, name, param)
            if param.default is inspect.Parameter.empty:
                required.append(name)
        result: dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            result["required"] = required
        return result

    @functools.cached_property
    def names(self) -> tuple[str, ...]:
        """The name of each parameter a caller passes, in the order the callable declares them."""
        return tuple(self._parameters())

    def coerced(self, arguments: Mapping[str, object]) -> dict[str, object]:
        """arguments with each text sent for a ``Path`` parameter made a ``Path``, because JSON carries paths as text."""
        hints = self._hints()
        coerced = dict(arguments)
        for name, param in self._parameters().items():
            value = coerced.get(name)
            if isinstance(value, str) and self._uses_path(hints.get(name, param.annotation)):
                coerced[name] = Path(value)
        return coerced

    def _parameters(self) -> dict[str, inspect.Parameter]:
        try:
            signature = inspect.signature(self._callable)
        except (TypeError, ValueError):
            return {}
        return {name: param for name, param in signature.parameters.items() if self._is_passed(name, param)}

    def _is_passed(self, name: str, param: inspect.Parameter) -> bool:
        if name in {"self", "cls"}:
            return False
        return param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)

    def _uses_path(self, annotation: object) -> bool:
        if annotation is Path:
            return True
        if get_origin(annotation) in _UNION_ORIGINS:
            return any(self._uses_path(arg) for arg in get_args(annotation))
        return False

    def _hints(self) -> dict[str, Any]:
        function = getattr(self._callable, "__func__", self._callable)
        try:
            return get_type_hints(function)
        except (NameError, TypeError, AttributeError):
            return self._hints_one_by_one(function)

    def _hints_one_by_one(self, function: Callable[..., object]) -> dict[str, Any]:
        """Each annotation read on its own, so one naming a class imported only for type checking, as a return type
        often does to break a circular import, leaves the parameters' types readable. One that cannot be read is left
        out."""
        hints: dict[str, Any] = {}
        module_names = getattr(function, "__globals__", {})
        for name, annotation in getattr(function, "__annotations__", {}).items():
            try:
                hints[name] = eval(annotation, module_names) if isinstance(annotation, str) else annotation
            except NameError:
                continue
        return hints

    def _parameter_schema(self, hints: dict[str, Any], name: str, param: inspect.Parameter) -> dict[str, Any]:
        annotation = hints.get(name, param.annotation)
        if annotation is inspect.Parameter.empty:
            return {"type": "string"}
        return self._annotation_schema(annotation)

    def _annotation_schema(self, annotation: object) -> dict[str, Any]:
        annotation = self._unwrap_required(annotation)
        if annotation is Any:
            return {}
        if is_typeddict(annotation):
            return self._typed_dict_schema(annotation)
        origin = get_origin(annotation)
        if origin in _UNION_ORIGINS:
            return self._union_schema(annotation)
        if annotation is list or origin in _ARRAY_ORIGINS:
            return self._array_schema(annotation)
        if annotation is dict or origin in _OBJECT_ORIGINS:
            return self._object_schema(annotation)
        return self._scalar_schema(annotation)

    def _unwrap_required(self, annotation: object) -> object:
        if get_origin(annotation) in {NotRequired, Required}:
            args = get_args(annotation)
            if args:
                return args[0]
        return annotation

    def _typed_dict_schema(self, annotation: object) -> dict[str, Any]:
        hints = get_type_hints(annotation, include_extras=True)
        properties: dict[str, Any] = {}
        required: list[str] = []
        for name, hint in hints.items():
            if get_origin(hint) is NotRequired:
                hint = get_args(hint)[0]
            else:
                required.append(name)
            properties[name] = self._annotation_schema(hint)
        schema: dict[str, Any] = {"type": "object", "properties": properties, "additionalProperties": False}
        if required:
            schema["required"] = required
        return schema

    def _union_schema(self, annotation: object) -> dict[str, Any]:
        variants = [self._annotation_schema(arg) for arg in get_args(annotation)]
        if len(variants) == 1:
            return variants[0]
        return {"anyOf": variants}

    def _array_schema(self, annotation: object) -> dict[str, Any]:
        args = get_args(annotation)
        item_schema = self._annotation_schema(args[0]) if args else {"type": "string"}
        return {"type": "array", "items": item_schema}

    def _object_schema(self, annotation: object) -> dict[str, Any]:
        args = get_args(annotation)
        schema: dict[str, Any] = {"type": "object"}
        if len(args) >= 2:
            schema["additionalProperties"] = self._annotation_schema(args[1])
        return schema

    def _scalar_schema(self, annotation: object) -> dict[str, Any]:
        """A class the schema has no word for is an object; anything else it cannot name is sent as text."""
        if annotation in _SCALAR_SCHEMAS:
            return dict(_SCALAR_SCHEMAS[annotation])
        if inspect.isclass(annotation):
            return {"type": "object"}
        return {"type": "string"}
