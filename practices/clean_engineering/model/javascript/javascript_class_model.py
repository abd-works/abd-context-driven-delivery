"""JavaScript code channel for the CleanEngineering model.

Renders ES6 class stubs with constructor and stub method bodies (no types).
Parses class names from JavaScript source.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

_repo = Path(__file__).resolve().parents[3]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    OoadNode,
    base_type_name_for,
    companion_interface_name,
    example_extension_kind,
    is_example_factory_name,
    is_interface_name,
)
from practices.clean_engineering.model.c_family_parse import CFamilyParse
from practices.clean_engineering.model.field_types import OperationField, PropertyField
from practices.clean_engineering.model.update_report import ChildCollectionPair, UpdateReport

if TYPE_CHECKING:
    from practices.clean_engineering.clean_engineering import CleanEngineering as CleanEngineeringGuidance


def _camel_identifier(name: str) -> str:
    raw = (name or "").strip()
    if not raw:
        return raw
    raw = raw.split(":", 1)[0].strip()
    parts = re.split(r"_+", raw.lstrip("_"))
    if not parts:
        return raw
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:] if part)


class JavaScriptProperty(PropertyField):
    def render(self) -> str:
        camel = _camel_identifier(self.name)
        return f"    this.{camel} = {camel};"

    def constructor_parameter(self) -> str:
        return _camel_identifier(self.name)


class JavaScriptOperation(OperationField):
    def render(self) -> str:
        access = "#" if self.name.startswith("_") else ""
        camel = _camel_identifier(self.name)
        params = ", ".join(_camel_identifier(param) for param in self.parameters if param and param.strip())
        return f"  {access}{camel}({params}) {{ }}"


class JavaScriptOoadClass(OoadClass):
    def load_property_field(self, source: PropertyField) -> JavaScriptProperty:
        loaded = JavaScriptProperty(name=source.name)
        loaded.update_self(source)
        return loaded

    def load_operation_field(self, source: OperationField) -> JavaScriptOperation:
        loaded = JavaScriptOperation(name=source.name)
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
        self.narration_comment_lines = list(source.narration_comment_lines)
        self.commented_code_lines = list(source.commented_code_lines)

    def render(self, known_names: Optional[List[str]] = None) -> str:
        names = known_names or []
        if self.intent:
            lines = [f"/** {self.intent} */"]
        else:
            lines = []
        iface = companion_interface_name(self.name, names)
        kind = example_extension_kind(self.name)
        if is_interface_name(self.name):
            return self._render_interface(lines)
        if is_example_factory_name(self.name):
            return self._render_example_factory(lines, iface)
        if kind:
            return self._render_deprecated_mode(kind)
        if iface:
            lines.append(f"// implements {iface}")
        return self._render_production_class(lines)

    def _render_interface(self, lines: List[str]) -> str:
        lines.append(f"// interface {self.name}")
        lines.append(f"class {self.name} {{")
        for operation in self.operations:
            if operation.name.startswith("_"):
                continue
            lines.append(operation.render())
        lines.append("}")
        return "\n".join(lines)

    def _render_example_factory(self, lines: List[str], iface: Optional[str]) -> str:
        lines.append("// example factory - plain class; no ExampleLoader base")
        if iface:
            lines.append(f"// implements {iface}")
        lines.append(f"class {self.name} {{")
        for operation in self.operations:
            lines.append(operation.render())
        if not self.operations and not self.properties:
            lines.append("  // load{ExampleKey}() - examples[{example_key}] multi-type bundle")
        lines.append("}")
        return "\n".join(lines)

    def _render_deprecated_mode(self, kind: str) -> str:
        note = {
            "Fake": "mode: mock/stub framework + examples - not a generated class",
            "Isolated": "mode: new Type(...ctor-injected mocks...) - not a generated class",
            "Production": "mode: new Type(...real collaborators...) - use production class",
        }.get(kind, "")
        return (
            f"// {self.name} - deprecated as a type. {note}\n"
            f"// Use {base_type_name_for(self.name)}ExampleFactory modes instead."
        )

    def _render_production_class(self, lines: List[str]) -> str:
        lines.append(f"class {self.name} {{")
        params = ", ".join(
            property_row.constructor_parameter()
            if hasattr(property_row, "constructor_parameter")
            else _camel_identifier(property_row.name)
            for property_row in self.properties
        )
        lines.append(f"  constructor({params}) {{")
        for property_row in self.properties:
            lines.append(property_row.render())
        lines.append("  }")
        for operation in self.operations:
            lines.append("")
            lines.append(operation.render())
        lines.append("}")
        return "\n".join(lines)


class JavaScriptModule(Module):
    def load_class(self, source: OoadClass) -> JavaScriptOoadClass:
        loaded = JavaScriptOoadClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    def render(self, known_names: Optional[List[str]] = None) -> str:
        return "\n\n".join(loaded.render(known_names) for loaded in self.classes)


class JavaScriptCleanEngineeringModel(CleanEngineeringModel):
    def __init__(
        self,
        name: str = "",
        sequential_order: int = 1,
        guidance: Optional["CleanEngineeringGuidance"] = None,
    ) -> None:
        super().__init__(name, sequential_order)
        self._guidance = guidance

    def load_module(self, source: Module) -> JavaScriptModule:
        loaded = JavaScriptModule(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    def load_class(self, source: OoadClass) -> JavaScriptOoadClass:
        loaded = JavaScriptOoadClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    def parse(self, text: str) -> "JavaScriptCleanEngineeringModel":
        return CFamilyParse(
            model_factory=lambda: type(self)(name="", sequential_order=1),
            class_factory=lambda **kw: JavaScriptOoadClass(**kw),
        ).parse(text)

    def parse_detailed(self, text: str):
        from practices.clean_engineering.model.python.python_class_model import ParsedPython

        model = self.parse(text)
        return ParsedPython(model=model, content=text, lines=text.split("\n"), tree=None)

    @classmethod
    def parse_file(cls, path: Path):
        try:
            return cls().parse_detailed(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            return None

    def render(self, canonical: Optional[CleanEngineeringModel] = None, previous: Optional[str] = None) -> str:
        if canonical is not None:
            self.translate_from(canonical)
        known_names = [loaded.name for loaded in self.classes]
        rendered = "\n\n".join(module.render(known_names) for module in self.modules)
        return rendered + ("\n" if rendered else "")

    def sync(self, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(self.parse(text))
