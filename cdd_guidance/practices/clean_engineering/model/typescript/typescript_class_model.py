"""TypeScript code channel for the CleanEngineering model.

Reads classes, members, and bodies from TypeScript source. Writes through the one code render; each TypeScript class,
property, and operation spells its own lines.
"""
from __future__ import annotations

from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import is_interface_name
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import DocumentedIntent, pascal_case_decorator
from cdd_guidance.practices.clean_engineering.model.code_body import TYPESCRIPT
from cdd_guidance.practices.clean_engineering.model.code_class_model import (
    BraceCleanEngineeringModel,
    CodeClass,
    CodeModule,
    CodeOperation,
    CodeProperty,
)
from cdd_guidance.practices.clean_engineering.model.operation import Operation


class TypeScriptProperty(CodeProperty):
    language = TYPESCRIPT

    def lines(self, contract: bool) -> List[str]:
        type_name = self.language.type_name(self.type_hint) if self.type_hint else "any"
        return [f"  {self.language.identifier(self.name)}: {type_name};"]


class TypeScriptOperation(CodeOperation):
    language = TYPESCRIPT

    def signature(self, contract: bool) -> List[str]:
        doc = self.doc_text()
        lines = [f"  /** {doc} */"] if doc else []
        parameters = ", ".join(parameter.save() for parameter in self.parameters)
        returned = self.language.type_name(self.return_type) if self.return_type else "void"
        name = self.language.identifier(self.name)
        if contract:
            return lines + [f"  {name}({parameters}): {returned};"]
        access = "private " if self.name.startswith("_") else ""
        return lines + [f"  {access}{name}({parameters}): {returned} {{"]


class TypeScriptClass(CodeClass):
    language = TYPESCRIPT
    property_type = TypeScriptProperty
    operation_type = TypeScriptOperation

    def doc(self, intent: str) -> List[str]:
        notes = [f" * {note.strip()}" for note in intent.splitlines() if note.strip()]
        return ["/**", *notes, " */"] if notes else []

    def doc_intent(self) -> str:
        return DocumentedIntent.of(self, marked=False).text()

    def stereotype_decorators(self) -> List[str]:
        return [f"@{pascal_case_decorator(item)}()" for item in self.stereotypes]

    def interface_declaration(self) -> List[str]:
        return [f"interface {self.name} {{"]

    def class_modifiers(self, implemented: List[str]) -> str:
        """A class that implements its I{Class} contract leaves the contract's members to its subclasses."""
        return "abstract " if any(is_interface_name(base) for base in implemented) else ""

    def constructor_lines(self, constructor: Optional[Operation], body: List[str]) -> List[str]:
        parameters = ", ".join(
            f"{self.language.identifier(name)}: {self.language.type_name(hint) if hint else 'any'}"
            for name, hint in self.constructor_parameters(constructor)
        )
        return [f"  constructor({parameters}) {{"] + body + self.block_close()


class TypeScriptModule(CodeModule):
    class_type = TypeScriptClass


class TypeScriptCleanEngineeringModel(BraceCleanEngineeringModel):
    language = TYPESCRIPT
    module_type = TypeScriptModule
    suffixes = language.suffixes
