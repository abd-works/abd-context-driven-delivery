"""TypeScript code channel for the CleanEngineering model.

Reads classes, members, and bodies from TypeScript source. Writes through the one code render;
this module only spells TypeScript lines.
"""
from __future__ import annotations

from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.code_body import TYPESCRIPT
from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass, is_interface_name
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import pascal_case_decorator
from cdd_guidance.practices.clean_engineering.model.code_class_model import BraceCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property



class TypeScriptCleanEngineeringModel(BraceCleanEngineeringModel):
    language = TYPESCRIPT

    def class_doc(self, intent: str) -> List[str]:
        notes = [f" * {note.strip()}" for note in intent.splitlines() if note.strip()]
        return ["/**", *notes, " */"] if notes else []

    def class_intent(self, oclass: OoadClass) -> str:
        return oclass.intent

    def stereotype_decorators(self, oclass: OoadClass) -> List[str]:
        return [f"@{pascal_case_decorator(item)}()" for item in oclass.stereotypes]

    def interface_declaration(self, oclass: OoadClass) -> List[str]:
        return [f"interface {oclass.name} {{"]

    def class_modifiers(self, implemented: List[str]) -> str:
        """A class that implements its I{Class} contract leaves the contract's members to its subclasses."""
        return "abstract " if any(is_interface_name(base) for base in implemented) else ""

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
