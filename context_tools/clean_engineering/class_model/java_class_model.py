"""Java code channel for the CleanEngineering model — model fidelity.

Renders Java class stubs with typed fields and abstract method signatures.
Parses class names from Java source.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional

_repo = Path(__file__).resolve().parents[3]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from context_tools.clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    companion_interface_name,
    is_interface_name,
)
from context_tools.clean_engineering.class_model.update_report import UpdateReport

_TYPE_MAP = {
    "str": "String",
    "int": "int",
    "float": "double",
    "bool": "boolean",
    "None": "void",
    "list": "List<?>",
    "dict": "Map<String, Object>",
    "object": "Object",
}


def _java_type(py_type: str) -> str:
    return _TYPE_MAP.get(py_type.strip(), py_type.strip())


def _pascal(name: str) -> str:
    return "".join(p.title() for p in re.split(r"_+", name))


def _camel(name: str) -> str:
    parts = re.split(r"_+", name.lstrip("_"))
    return parts[0] + "".join(p.title() for p in parts[1:])


class JavaOoadClass(OoadClass):
    pass


class JavaCleanEngineeringModel(CleanEngineeringModel):

    def create_child_class(self, source: OoadClass) -> JavaOoadClass:
        return JavaOoadClass(name=source.name, sequential_order=source.sequential_order)

    # ------------------------------------------------------------------
    # Uniform callable surface
    # ------------------------------------------------------------------

    @classmethod
    def parse(cls, text: str) -> "JavaCleanEngineeringModel":
        from context_tools.clean_engineering.class_model.c_family_parse import parse_c_family

        return parse_c_family(
            text,
            model_factory=lambda: cls(name="", sequential_order=1),
            class_factory=lambda **kw: JavaOoadClass(**kw),
        )

    @classmethod
    def parse_detailed(cls, text: str):
        from context_tools.clean_engineering.class_model.python_class_model import ParsedPython

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
        known = [c.name for c in canonical.classes]
        parts = [cls._render_class(c, known_names=known) for c in canonical.classes]
        return "\n\n".join(parts) + "\n"

    @classmethod
    def _render_class(cls, oclass: OoadClass, known_names: List[str] | None = None) -> str:
        known_names = known_names or []
        lines: List[str] = []
        if oclass.intent:
            lines.append(f"/** {oclass.intent} */")
        if is_interface_name(oclass.name):
            lines.append(f"public interface {oclass.name} {{")
            for prop in oclass.properties:
                jt_t = _java_type(prop.type_hint) if prop.type_hint else "Object"
                lines.append(f"    {jt_t} get{_pascal(prop.name)}();")
            for op in oclass.operations:
                if op.name.startswith("_"):
                    continue  # privates never on I{Class}
                ret = _java_type(op.return_type) if op.return_type else "void"
                params = ", ".join(op.parameters)
                lines.append(f"    {ret} {_camel(op.name)}({params});")
            lines.append("}")
            return "\n".join(lines)
        iface = companion_interface_name(oclass.name, known_names)
        if iface:
            lines.append(f"public abstract class {oclass.name} implements {iface} {{")
        else:
            lines.append(f"public abstract class {oclass.name} {{")
        for prop in oclass.properties:
            jt_t = _java_type(prop.type_hint) if prop.type_hint else "Object"
            lines.append(f"    private {jt_t} {_camel(prop.name)};")
        if oclass.properties:
            lines.append("")
        if oclass.properties:
            params = ", ".join(
                f"{_java_type(p.type_hint) if p.type_hint else 'Object'} {_camel(p.name)}"
                for p in oclass.properties
            )
            lines.append(f"    public {oclass.name}({params}) {{")
            for prop in oclass.properties:
                lines.append(f"        this.{_camel(prop.name)} = {_camel(prop.name)};")
            lines.append("    }")
            lines.append("")
        for op in oclass.operations:
            ret = _java_type(op.return_type) if op.return_type else "void"
            access = "private" if op.name.startswith("_") else "public abstract"
            params = ", ".join(op.parameters)
            method_name = _camel(op.name)
            lines.append(f"    {access} {ret} {method_name}({params});")
        lines.append("}")
        return "\n".join(lines)

    @classmethod
    def sync(cls, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(cls.parse(text))
