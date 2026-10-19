"""TypeScript code channel for the CleanEngineering model - model fidelity.

Renders typed class stubs with property declarations and stub method bodies.
Parses class names from TypeScript source.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional

_repo = Path(__file__).resolve().parents[3]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from practices.clean_engineering.model.property import invariant_lines, property_notes
from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    OoadNode,
    companion_interface_name,
    is_interface_name,
)
from practices.clean_engineering.model.c_family_parse import CFamilyParse
from practices.clean_engineering.model.operation import Operation, Parameter
from practices.clean_engineering.model.property import Property
from practices.clean_engineering.model.update_report import ChildCollectionPair, UpdateReport

_TYPE_MAP = {
    "str": "string",
    "int": "number",
    "float": "number",
    "bool": "boolean",
    "None": "void",
    "list": "Array<any>",
    "dict": "Record<string, any>",
    "object": "any",
}


def _ts_type(py_type: str) -> str:
    return _TYPE_MAP.get(py_type.strip(), py_type.strip())


def _camel_identifier(name: str) -> str:
    parts = re.split(r"_+", name)
    return parts[0] + "".join(part.title() for part in parts[1:])


_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_PROSE = re.compile(
    r"\b(the|and|is|are|a|an|of|to|for|that|this|with|from|into|each|same|only|like)\b",
    re.I,
)


def _render_callee(callee: str) -> str:
    text = callee.strip()
    if not text:
        return ""
    tokens = text.split()
    if _PROSE.search(text) and len(tokens) >= 3:
        return ""
    head = tokens[0]
    args = ", ".join(tokens[1:])
    call = f"({args})"
    if head.startswith("super."):
        rest = head[6:]
        if rest and rest[0].isupper():
            return f"    super{call};"
        return f"    super.{rest}{call};"
    if head == "super":
        return f"    super{call};"
    if "." in head:
        return f"    {head}{call};"
    if head[0].isupper() and _IDENT.match(head):
        target = _camel_identifier(tokens[1]) if len(tokens) > 1 else _camel_identifier(head)
        return f"    this.{target} = new {head}{call};"
    return f"    {head}{call};"


class TypeScriptProperty(Property):
    def ts_type(self) -> str:
        return _ts_type(self.type_hint) if self.type_hint else "any"

    def constructor_parameter(self) -> str:
        return f"{_camel_identifier(self.name)}: {self.ts_type()}"

    def render(self) -> str:
        lines = []
        if self.stereotype:
            lines.append(f"  // << {self.stereotype} >>")
        lines.extend(f"  // {note}" for note in property_notes(self))
        lines.append(f"  {_camel_identifier(self.name)}: {self.ts_type()};")
        return "\n".join(lines)


class TypeScriptOperation(Operation):
    def render(self, *, signature_only: bool = False) -> str:
        if self.name.startswith("_") and signature_only:
            return ""
        params = ", ".join(parameter.save() for parameter in self.parameters)
        ret = _ts_type(self.return_type) if self.return_type else "void"
        camel = _camel_identifier(self.name)
        if signature_only:
            return f"  {camel}({params}): {ret};"
        access = "private " if self.name.startswith("_") else ""
        lines = [f"  {access}{camel}({params}): {ret} {{"]
        for note in invariant_lines(self):
            lines.append(f"    // {note}")
        for callee in self.callees:
            rendered = _render_callee(callee)
            if rendered:
                lines.append(rendered)
        lines.append("  }")
        return "\n".join(lines)


class TypeScriptOoadClass(OoadClass):
    def load_property_field(self, source: Property) -> TypeScriptProperty:
        loaded = TypeScriptProperty(name=source.name)
        loaded.update_self(source)
        return loaded

    def load_operation_field(self, source: Operation) -> TypeScriptOperation:
        loaded = TypeScriptOperation(name=source.name)
        loaded.update_self(source)
        return loaded

    def child_collections(self, source: OoadNode) -> List[ChildCollectionPair]:
        assert isinstance(source, OoadClass)
        return [
            ChildCollectionPair(self.properties, source.properties, self.load_property_field),
            ChildCollectionPair(self.operations, source.operations, self.load_operation_field),
        ]

    def update_self(self, source: OoadNode) -> None:
        assert isinstance(source, OoadClass)
        self.intent = source.intent
        self.collaborators = list(source.collaborators)
        self.line = source.line

    def render(self, known_names: Optional[List[str]] = None) -> str:
        names = known_names or []
        lines: List[str] = []
        if self.intent:
            lines.append("/**")
            for note in self.intent.splitlines():
                if note.strip():
                    lines.append(f" * {note.strip()}")
            lines.append(" */")
        if is_interface_name(self.name):
            lines.append(f"interface {self.name} {{")
            for property_row in self.properties:
                lines.append(property_row.render())
            for operation in self.operations:
                rendered = operation.render(signature_only=True) if hasattr(operation, "render") else ""
                if rendered:
                    lines.append(rendered)
            lines.append("}")
            return "\n".join(lines)
        iface = companion_interface_name(self.name, names)
        bases = list(self.collaborators)
        if iface:
            lines.append(f"abstract class {self.name} implements {iface} {{")
        elif bases:
            lines.append(f"class {self.name} extends {bases[0]} {{")
        else:
            lines.append(f"class {self.name} {{")
        for property_row in self.properties:
            rendered = property_row.render() if hasattr(property_row, "render") else f"  {property_row.name};"
            lines.append(rendered)
        constructors = [
            operation for operation in self.operations
            if operation.name in {self.name, "constructor"}
        ]
        methods = [
            operation for operation in self.operations
            if operation.name not in {self.name, "constructor"}
        ]
        constructor_params = self._constructor_parameters(constructors)
        if constructor_params or constructors:
            lines.append("")
            params = ", ".join(
                f"{_camel_identifier(parameter.name)}: any"
                for parameter in constructor_params
            )
            lines.append(f"  constructor({params}) {{")
            for operation in constructors:
                for note in invariant_lines(operation):
                    lines.append(f"    // {note}")
                for callee in operation.callees:
                    rendered = _render_callee(callee)
                    if rendered:
                        lines.append(rendered)
            for parameter in constructor_params:
                camel = _camel_identifier(parameter.name)
                lines.append(f"    this.{camel} = {camel};")
            lines.append("  }")
            lines.append("")
        for operation in methods:
            lines.append(operation.render() if hasattr(operation, "render") else operation.name)
        lines.append("}")
        return "\n".join(lines)

    def _constructor_parameters(self, constructors: List[Operation]) -> list:
        if constructors and constructors[0].parameters:
            return list(constructors[0].parameters)
        if constructors:
            return []
        return [
            Parameter(name=property_row.name, sequential_order=index)
            for index, property_row in enumerate(self.properties, start=1)
        ]


class TypeScriptModule(Module):
    def load_class(self, source: OoadClass) -> TypeScriptOoadClass:
        loaded = TypeScriptOoadClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    def render(self, known_names: Optional[List[str]] = None) -> str:
        return "\n\n".join(loaded.render(known_names) for loaded in self.classes)


class TypeScriptCleanEngineeringModel(CleanEngineeringModel):
    def load_module(self, source: Module) -> TypeScriptModule:
        loaded = TypeScriptModule(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    def load_class(self, source: OoadClass) -> TypeScriptOoadClass:
        loaded = TypeScriptOoadClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    @classmethod
    def parse(cls, text: str) -> "TypeScriptCleanEngineeringModel":
        return CFamilyParse(
            model_factory=lambda: cls(name="", sequential_order=1),
            class_factory=lambda **kw: TypeScriptOoadClass(**kw),
        ).parse(text)

    @classmethod
    def parse_detailed(cls, text: str):
        from practices.clean_engineering.model.python.python_class_model import ParsedPython

        model = cls.parse(text)
        return ParsedPython(model=model, content=text, lines=text.split("\n"), tree=None)

    @classmethod
    def parse_file(cls, path: Path):
        try:
            return cls.parse_detailed(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            return None

    def render(self, canonical: Optional[CleanEngineeringModel] = None, previous: Optional[str] = None) -> str:
        if canonical is not None:
            self.translate_from(canonical)
        known_names = [loaded.name for loaded in self.classes]
        rendered = "\n\n".join(module.render(known_names) for module in self.modules)
        return rendered + ("\n" if rendered else "")

    @classmethod
    def sync(cls, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(cls.parse(text))
