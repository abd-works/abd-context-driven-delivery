"""JavaScript code channel for the CleanEngineering model.

Renders ES6 class stubs with constructor and stub method bodies (no types).
Parses class names from JavaScript source.

Companion resolution: production {Type} -> I{Type}.
Legacy Fake|Isolated|Production{Type} names still resolve to I{Type} if present.
{Type}ExampleFactory stays a plain class (no ExampleLoader base).
Do not emit Fake/Isolated/Production subclasses - those are factory modes.
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
    Operation,
    Property,
    base_type_name_for,
    companion_interface_name,
    example_extension_kind,
    is_example_factory_name,
    is_interface_name,
)
from practices.clean_engineering.model.update_report import UpdateReport


class JavaScriptOoadClass(OoadClass):
    pass


class JavaScriptCleanEngineeringModel(CleanEngineeringModel):

    def load_class(self, source: OoadClass) -> JavaScriptOoadClass:
        return JavaScriptOoadClass(name=source.name, sequential_order=source.sequential_order)

    # ------------------------------------------------------------------
    # Uniform callable surface
    # ------------------------------------------------------------------

    def parse(self, text: str) -> "JavaScriptCleanEngineeringModel":
        from practices.clean_engineering.model.c_family_parse import CFamilyParse

        return CFamilyParse(
            model_factory=lambda: type(self)(name="", sequential_order=1),
            class_factory=lambda **kw: JavaScriptOoadClass(**kw),
        ).parse(text)

    def parse_detailed(self, text: str):
        from practices.clean_engineering.model.python.python_class_model import ParsedPython

        model = self.parse(text)
        return ParsedPython(model=model, content=text, lines=text.split("\n"), tree=None)

    def parse_file(self, path: Path):
        try:
            return self.parse_detailed(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            return None

    def render(self, canonical: CleanEngineeringModel, previous: Optional[str] = None) -> str:
        known = [c.name for c in canonical.classes]
        parts = [self._render_class(c, known_names=known) for c in canonical.classes]
        return "\n\n".join(parts) + "\n"

    def _camel(self, name: str) -> str:
        raw = (name or "").strip()
        if not raw:
            return raw
        raw = raw.split(":", 1)[0].strip()
        parts = re.split(r"_+", raw.lstrip("_"))
        if not parts:
            return raw
        return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:] if p)

    def _camel_params(self, parameters: List[str]) -> str:
        return ", ".join(self._camel(p) for p in parameters if p and p.strip())

    def _render_class(self, oclass: OoadClass, known_names: List[str] | None = None) -> str:
        known_names = known_names or []
        lines: List[str] = []
        if oclass.intent:
            lines.append(f"/** {oclass.intent} */")

        iface = companion_interface_name(oclass.name, known_names)
        kind = example_extension_kind(oclass.name)

        if is_interface_name(oclass.name):
            lines.append(f"// interface {oclass.name}")
            lines.append(f"class {oclass.name} {{")
            for op in oclass.operations:
                if op.name.startswith("_"):
                    continue
                lines.append(f"  {self._camel(op.name)}({self._camel_params(op.parameters)}) {{ }}")
            lines.append("}")
            return "\n".join(lines)

        if is_example_factory_name(oclass.name):
            lines.append("// example factory - plain class; no ExampleLoader base")
            if iface:
                lines.append(f"// implements {iface}")
            lines.append(f"class {oclass.name} {{")
            for op in oclass.operations:
                lines.append(f"  {self._camel(op.name)}({self._camel_params(op.parameters)}) {{ }}")
            if not oclass.operations and not oclass.properties:
                lines.append("  // load{ExampleKey}() - examples[{example_key}] multi-type bundle")
            lines.append("}")
            return "\n".join(lines)

        if kind:
            # Legacy Fake/Isolated/Production class names - do not emit subclasses.
            note = {
                "Fake": "mode: mock/stub framework + examples - not a generated class",
                "Isolated": "mode: new Type(...ctor-injected mocks...) - not a generated class",
                "Production": "mode: new Type(...real collaborators...) - use production class",
            }.get(kind, "")
            return (
                f"// {oclass.name} - deprecated as a type. {note}\n"
                f"// Use {base_type_name_for(oclass.name)}ExampleFactory modes instead."
            )

        if iface:
            lines.append(f"// implements {iface}")

        lines.append(f"class {oclass.name} {{")
        params = ", ".join(self._camel(p.name) for p in oclass.properties)
        lines.append(f"  constructor({params}) {{")
        for prop in oclass.properties:
            lines.append(f"    this.{self._camel(prop.name)} = {self._camel(prop.name)};")
        lines.append("  }")
        for op in oclass.operations:
            access = "#" if op.name.startswith("_") else ""
            lines.append("")
            lines.append(f"  {access}{self._camel(op.name)}({self._camel_params(op.parameters)}) {{ }}")
        lines.append("}")
        return "\n".join(lines)

    def sync(self, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(self.parse(text))
