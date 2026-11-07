"""JavaScript code channel for the CleanEngineering model.

Reads classes, members, and bodies from JavaScript source. Writes through the one code render;
this module only spells JavaScript lines.
"""
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    OoadClass,
    base_type_name_for,
    example_extension_kind,
    is_interface_name,
)
from cdd_guidance.practices.clean_engineering.model.c_family_parse import CFamilyParse
from cdd_guidance.practices.clean_engineering.model.code_body import CodeLanguage
from cdd_guidance.practices.clean_engineering.model.code_class_model import CodeCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering as CleanEngineeringGuidance

_JAVASCRIPT = CodeLanguage.named("javascript")
_EXAMPLE_MODES = {
    "Fake": "mode: mock/stub framework + examples - not a generated class",
    "Isolated": "mode: new Type(...ctor-injected mocks...) - not a generated class",
    "Production": "mode: new Type(...real collaborators...) - use production class",
}


class JavaScriptCleanEngineeringModel(CodeCleanEngineeringModel):
    language = _JAVASCRIPT

    def __init__(
        self,
        name: str = "",
        sequential_order: int = 1,
        guidance: Optional["CleanEngineeringGuidance"] = None,
    ) -> None:
        super().__init__(name, sequential_order)
        self._guidance = guidance

    def parse(self, text: str) -> "JavaScriptCleanEngineeringModel":
        return CFamilyParse(
            model_factory=lambda: type(self)(name="", sequential_order=1),
            class_factory=OoadClass,
            language=_JAVASCRIPT,
        ).parse(text)

    def render_class(self, oclass: OoadClass, known_names: List[str], kept: CodeCleanEngineeringModel) -> List[str]:
        kind = example_extension_kind(oclass.name)
        if kind and not is_interface_name(oclass.name):
            return [
                "",
                f"// {oclass.name} - deprecated as a type. {_EXAMPLE_MODES.get(kind, '')}",
                f"// Use {base_type_name_for(oclass.name)} directly.",
            ]
        return super().render_class(oclass, known_names, kept)

    def interface_declaration(self, oclass: OoadClass) -> List[str]:
        """JavaScript has no interfaces, so the contract is a class that says it is one."""
        return [f"// interface {oclass.name}"] + self.class_declaration(oclass)

    def implementing_declaration(self, oclass: OoadClass, interface: str) -> List[str]:
        return [f"// implements {interface}"] + self.class_declaration(oclass)

    def property_line(self, prop: Property, contract: bool) -> List[str]:
        return []

    def constructor_lines(self, oclass: OoadClass, constructor: Optional[Operation], body: List[str]) -> List[str]:
        parameters = ", ".join(
            self.language.identifier(name) for name, _hint in self.constructor_parameters(oclass, constructor)
        )
        return [f"  constructor({parameters}) {{"] + body + self.block_close()

    def signature(self, operation: Operation, contract: bool) -> List[str]:
        doc = self.doc_text(operation)
        lines = [f"  /** {doc} */"] if doc else []
        parameters = ", ".join(
            self.language.identifier(parameter.name) for parameter in operation.parameters if parameter.name.strip()
        )
        access = "#" if operation.name.startswith("_") else ""
        name = self.language.identifier(operation.name)
        if contract:
            return lines + [f"  {name}({parameters}) {{}}"]
        return lines + [f"  {access}{name}({parameters}) {{"]
