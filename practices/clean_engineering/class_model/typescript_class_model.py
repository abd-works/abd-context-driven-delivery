"""TypeScript code channel for the CleanEngineering model — model fidelity.

Renders typed class stubs with property declarations and stub method bodies.
Parses class names from TypeScript source.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional

_repo = Path(__file__).resolve().parents[2]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
)
from clean_engineering.class_model.update_report import UpdateReport

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


def _camel(name: str) -> str:
    parts = re.split(r"_+", name)
    return parts[0] + "".join(p.title() for p in parts[1:])


class TypeScriptOoadClass(OoadClass):
    pass


class TypeScriptCleanEngineeringModel(CleanEngineeringModel):

    def create_child_class(self, source: OoadClass) -> TypeScriptOoadClass:
        return TypeScriptOoadClass(name=source.name, sequential_order=source.sequential_order)

    # ------------------------------------------------------------------
    # Uniform callable surface
    # ------------------------------------------------------------------

    @classmethod
    def parse(cls, text: str) -> "TypeScriptCleanEngineeringModel":
        from clean_engineering.class_model.c_family_parse import parse_c_family

        return parse_c_family(
            text,
            model_factory=lambda: cls(name="", sequential_order=1),
            class_factory=lambda **kw: TypeScriptOoadClass(**kw),
        )

    @classmethod
    def parse_detailed(cls, text: str):
        from clean_engineering.class_model.python_class_model import ParsedPython

        model = cls.parse(text)
        return ParsedPython(model=model, content=text, lines=text.split("\n"), tree=None)

    @classmethod
    def parse_file(cls, path: Path):
        try:
            return cls.parse_detailed(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            return None

    @classmethod
    def render(cls, canonical: CleanEngineeringModel, previous: Optional[str] = None) -> str:
        parts = [cls._render_class(c) for c in canonical.classes]
        return "\n\n".join(parts) + "\n"

    @classmethod
    def _render_class(cls, oclass: OoadClass) -> str:
        lines: List[str] = []
        if oclass.intent:
            lines.append(f"/** {oclass.intent} */")
        lines.append(f"class {oclass.name} {{")
        # Properties
        for prop in oclass.properties:
            ts_t = _ts_type(prop.type_hint) if prop.type_hint else "any"
            lines.append(f"  {_camel(prop.name)}: {ts_t};")
        if oclass.properties:
            lines.append("")
        # Constructor
        if oclass.properties:
            params = ", ".join(
                f"{_camel(p.name)}: {_ts_type(p.type_hint) if p.type_hint else 'any'}"
                for p in oclass.properties
            )
            lines.append(f"  constructor({params}) {{")
            for prop in oclass.properties:
                lines.append(f"    this.{_camel(prop.name)} = {_camel(prop.name)};")
            lines.append("  }")
            lines.append("")
        # Operations
        for op in oclass.operations:
            params = ", ".join(op.parameters)
            ret = _ts_type(op.return_type) if op.return_type else "void"
            access = "private " if op.name.startswith("_") else ""
            lines.append(f"  {access}{_camel(op.name)}({params}): {ret} {{ }}")
        lines.append("}")
        return "\n".join(lines)

    @classmethod
    def sync(cls, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(cls.parse(text))
