"""TypeScript code channel for the CleanEngineering model.

Reads classes, members, and bodies from TypeScript source. Writes through the one code render;
this module only spells TypeScript lines.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

_repo = Path(__file__).resolve().parents[3]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    companion_interface_name,
    is_interface_name,
)
from cdd_guidance.practices.clean_engineering.model.c_family_parse import CFamilyParse
from cdd_guidance.practices.clean_engineering.model.code_body import CodeLanguage
from cdd_guidance.practices.clean_engineering.model.code_class_model import CodeCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property

_TYPESCRIPT = CodeLanguage.named("typescript")


class TypeScriptOoadClass(OoadClass):
    pass


class TypeScriptModule(Module):
    def load_class(self, source: OoadClass) -> TypeScriptOoadClass:
        loaded = TypeScriptOoadClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded


class TypeScriptCleanEngineeringModel(CodeCleanEngineeringModel):
    language = _TYPESCRIPT

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
            language=_TYPESCRIPT,
        ).parse(text)

    def class_open(self, oclass: OoadClass, known_names: List[str]) -> List[str]:
        lines = [""]
        if oclass.intent:
            lines.append("/**")
            lines.extend(f" * {note.strip()}" for note in oclass.intent.splitlines() if note.strip())
            lines.append(" */")
        if is_interface_name(oclass.name):
            return lines + [f"interface {oclass.name} {{"]
        iface = companion_interface_name(oclass.name, known_names)
        if iface:
            return lines + [f"abstract class {oclass.name} implements {iface} {{"]
        if oclass.collaborators:
            return lines + [f"class {oclass.name} extends {oclass.collaborators[0]} {{"]
        return lines + [f"class {oclass.name} {{"]

    def property_line(self, prop: Property, contract: bool) -> List[str]:
        type_name = self.language.type_name(prop.type_hint) if prop.type_hint else "any"
        return [f"  {self.language.identifier(prop.name)}: {type_name};"]

    def constructor_lines(self, oclass: OoadClass, constructor: Optional[Operation], body: List[str]) -> List[str]:
        parameters = ", ".join(
            f"{self.language.identifier(name)}: {self.language.type_name(hint) if hint else 'any'}"
            for name, hint in self.constructor_parameters(oclass, constructor)
        )
        return [f"  constructor({parameters}) {{"] + body + self.block_close()

    def signature(self, operation: Operation, contract: bool) -> List[str]:
        doc = self.doc_text(operation)
        lines = [f"  /** {doc} */"] if doc else []
        parameters = ", ".join(parameter.save() for parameter in operation.parameters)
        returned = self.language.type_name(operation.return_type) if operation.return_type else "void"
        name = self.language.identifier(operation.name)
        if contract:
            return lines + [f"  {name}({parameters}): {returned};"]
        access = "private " if operation.name.startswith("_") else ""
        return lines + [f"  {access}{name}({parameters}): {returned} {{"]
