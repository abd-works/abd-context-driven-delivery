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

from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    OoadNode,
    companion_interface_name,
    is_interface_name,
)
from practices.clean_engineering.model.c_family_parse import CFamilyParse
from practices.clean_engineering.model.field_types import OperationField, PropertyField
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


class TypeScriptProperty(PropertyField):
    def ts_type(self) -> str:
        return _ts_type(self.type_hint) if self.type_hint else "any"

    def constructor_parameter(self) -> str:
        return f"{_camel_identifier(self.name)}: {self.ts_type()}"

    def render(self) -> str:
        return f"  {_camel_identifier(self.name)}: {self.ts_type()};"


class TypeScriptOperation(OperationField):
    def render(self, *, signature_only: bool = False) -> str:
        if self.name.startswith("_") and signature_only:
            return ""
        params = ", ".join(self.parameters)
        ret = _ts_type(self.return_type) if self.return_type else "void"
        camel = _camel_identifier(self.name)
        if signature_only:
            return f"  {camel}({params}): {ret};"
        access = "private " if self.name.startswith("_") else ""
        return f"  {access}{camel}({params}): {ret} {{ }}"


class TypeScriptOoadClass(OoadClass):
    def load_property_field(self, source: PropertyField) -> TypeScriptProperty:
        loaded = TypeScriptProperty(name=source.name)
        loaded.update_self(source)
        return loaded

    def load_operation_field(self, source: OperationField) -> TypeScriptOperation:
        loaded = TypeScriptOperation(name=source.name)
        loaded.update_self(source)
        return loaded

    def child_collections(self, source: OoadNode) -> List[ChildCollectionPair]:
        assert isinstance(source, OoadClass)
        return [
            ChildCollectionPair(self.properties, source.properties, self.load_property_field),
            ChildCollectionPair(self.operations, source.operations, self.load_operation_field),
            ChildCollectionPair(self.relationships, source.relationships, self.load_relationship),
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
            lines.append(f"/** {self.intent} */")
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
        if iface:
            lines.append(f"abstract class {self.name} implements {iface} {{")
        else:
            lines.append(f"class {self.name} {{")
        for property_row in self.properties:
            lines.append(property_row.render())
        if self.properties:
            lines.append("")
            params = ", ".join(
                property_row.constructor_parameter()
                if hasattr(property_row, "constructor_parameter")
                else _camel_identifier(property_row.name)
                for property_row in self.properties
            )
            lines.append(f"  constructor({params}) {{")
            for property_row in self.properties:
                camel = _camel_identifier(property_row.name)
                lines.append(f"    this.{camel} = {camel};")
            lines.append("  }")
            lines.append("")
        for operation in self.operations:
            lines.append(operation.render())
        lines.append("}")
        return "\n".join(lines)


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
