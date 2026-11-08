"""Java code channel for the CleanEngineering model.

Reads classes, members, and bodies from Java source. Writes through the one code render; each Java class, property,
and operation spells its own lines.
"""
from __future__ import annotations

import re
from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.code_body import JAVA
from cdd_guidance.practices.clean_engineering.model.code_class_model import (
    BraceCleanEngineeringModel,
    CodeClass,
    CodeModule,
    CodeOperation,
    CodeProperty,
)
from cdd_guidance.practices.clean_engineering.model.operation import Operation


def _pascal(name: str) -> str:
    return "".join(part.title() for part in re.split(r"_+", name))


def _java_type(hint: str) -> str:
    return JAVA.type_name(hint) if hint else "Object"


class JavaProperty(CodeProperty):
    language = JAVA

    def lines(self, contract: bool) -> List[str]:
        type_name = _java_type(self.type_hint)
        if contract:
            return [f"    {type_name} get{_pascal(self.name)}();"]
        return [f"    private {type_name} {self.language.identifier(self.name)};"]


class JavaOperation(CodeOperation):
    language = JAVA

    def signature(self, contract: bool) -> List[str]:
        doc = self.doc_text()
        lines = [f"    /** {doc} */"] if doc else []
        parameters = ", ".join(
            f"{_java_type(parameter.type_hint)} {self.language.identifier(parameter.name)}" for parameter in self.parameters
        )
        returned = _java_type(self.return_type) if self.return_type else "void"
        name = self.language.identifier(self.name)
        if contract:
            return lines + [f"    {returned} {name}({parameters});"]
        access = "private" if self.name.startswith("_") else "public"
        return lines + [f"    {access} {returned} {name}({parameters}) {{"]


class JavaClass(CodeClass):
    language = JAVA
    property_type = JavaProperty
    operation_type = JavaOperation

    def interface_declaration(self) -> List[str]:
        return [f"public interface {self.name} {{"]

    def class_modifiers(self, implemented: List[str]) -> str:
        return "public "

    def constructor_lines(self, constructor: Optional[Operation], body: List[str]) -> List[str]:
        parameters = ", ".join(
            f"{_java_type(hint)} {self.language.identifier(name)}" for name, hint in self.constructor_parameters(constructor)
        )
        return [f"    public {self.name}({parameters}) {{"] + body + self.block_close()


class JavaModule(CodeModule):
    class_type = JavaClass


class JavaCleanEngineeringModel(BraceCleanEngineeringModel):
    language = JAVA
    module_type = JavaModule
    suffixes = language.suffixes
