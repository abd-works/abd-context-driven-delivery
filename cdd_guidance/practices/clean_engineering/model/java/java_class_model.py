"""Java code channel for the CleanEngineering model.

Reads classes, members, and bodies from Java source. Writes through the one code render;
this module only spells Java lines.
"""
from __future__ import annotations

import re
from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass
from cdd_guidance.practices.clean_engineering.model.code_body import CodeLanguage
from cdd_guidance.practices.clean_engineering.model.code_class_model import BraceCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property

_JAVA = CodeLanguage.named("java")


def _pascal(name: str) -> str:
    return "".join(part.title() for part in re.split(r"_+", name))


class JavaCleanEngineeringModel(BraceCleanEngineeringModel):
    language = _JAVA

    def interface_declaration(self, oclass: OoadClass) -> List[str]:
        return [f"public interface {oclass.name} {{"]

    def class_modifiers(self, implemented: List[str]) -> str:
        return "public "

    def property_line(self, prop: Property, contract: bool) -> List[str]:
        type_name = self._type(prop.type_hint)
        if contract:
            return [f"    {type_name} get{_pascal(prop.name)}();"]
        return [f"    private {type_name} {self.language.identifier(prop.name)};"]

    def constructor_lines(self, oclass: OoadClass, constructor: Optional[Operation], body: List[str]) -> List[str]:
        parameters = ", ".join(
            f"{self._type(hint)} {self.language.identifier(name)}"
            for name, hint in self.constructor_parameters(oclass, constructor)
        )
        return [f"    public {oclass.name}({parameters}) {{"] + body + self.block_close()

    def signature(self, operation: Operation, contract: bool) -> List[str]:
        doc = self.doc_text(operation)
        lines = [f"    /** {doc} */"] if doc else []
        parameters = ", ".join(
            f"{self._type(parameter.type_hint)} {self.language.identifier(parameter.name)}"
            for parameter in operation.parameters
        )
        returned = self._type(operation.return_type) if operation.return_type else "void"
        name = self.language.identifier(operation.name)
        if contract:
            return lines + [f"    {returned} {name}({parameters});"]
        access = "private" if operation.name.startswith("_") else "public"
        return lines + [f"    {access} {returned} {name}({parameters}) {{"]

    def _type(self, hint: str) -> str:
        return self.language.type_name(hint) if hint else "Object"
