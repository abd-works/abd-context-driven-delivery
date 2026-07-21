"""JavaScript code channel for the CleanEngineering model — language fidelity.

Renders ES6 class stubs with constructor and stub method bodies (no types).
Parses class names from JavaScript source.
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


def _camel(name: str) -> str:
    parts = re.split(r"_+", name.lstrip("_"))
    return parts[0] + "".join(p.title() for p in parts[1:])


class JavaScriptOoadClass(OoadClass):
    pass


class JavaScriptCleanEngineeringModel(CleanEngineeringModel):

    def create_child_class(self, source: OoadClass) -> JavaScriptOoadClass:
        return JavaScriptOoadClass(name=source.name, sequential_order=source.sequential_order)

    # ------------------------------------------------------------------
    # Uniform callable surface
    # ------------------------------------------------------------------

    @classmethod
    def parse(cls, text: str) -> "JavaScriptCleanEngineeringModel":
        from clean_engineering.class_model.c_family_parse import parse_c_family

        return parse_c_family(
            text,
            model_factory=lambda: cls(name="", sequential_order=1),
            class_factory=lambda **kw: JavaScriptOoadClass(**kw),
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
        # Constructor
        params = ", ".join(_camel(p.name) for p in oclass.properties)
        lines.append(f"  constructor({params}) {{")
        for prop in oclass.properties:
            lines.append(f"    this.{_camel(prop.name)} = {_camel(prop.name)};")
        lines.append("  }")
        # Methods
        for op in oclass.operations:
            op_params = ", ".join(op.parameters)
            access = "#" if op.name.startswith("_") else ""
            lines.append("")
            lines.append(f"  {access}{_camel(op.name)}({op_params}) {{ }}")
        lines.append("}")
        return "\n".join(lines)

    @classmethod
    def sync(cls, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(cls.parse(text))
