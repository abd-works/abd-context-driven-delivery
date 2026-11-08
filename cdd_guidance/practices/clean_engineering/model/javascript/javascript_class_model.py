"""JavaScript code channel for the CleanEngineering model.

Reads classes, members, and bodies from JavaScript source. Writes through the one code render; each JavaScript class,
property, and operation spells its own lines.
"""
from __future__ import annotations

from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import base_type_name_for, example_extension_kind
from cdd_guidance.practices.clean_engineering.model.code_body import JAVASCRIPT
from cdd_guidance.practices.clean_engineering.model.code_class_model import (
    BraceCleanEngineeringModel,
    CodeClass,
    CodeModule,
    CodeOperation,
    CodeProperty,
)
from cdd_guidance.practices.clean_engineering.model.operation import Operation

_EXAMPLE_MODES = {
    "Fake": "mode: mock/stub framework + examples - not a generated class",
    "Isolated": "mode: new Type(...ctor-injected mocks...) - not a generated class",
    "Production": "mode: new Type(...real collaborators...) - use production class",
}


class JavaScriptProperty(CodeProperty):
    language = JAVASCRIPT

    def lines(self, contract: bool) -> List[str]:
        """JavaScript declares no fields; the constructor assigns them."""
        return []


class JavaScriptOperation(CodeOperation):
    language = JAVASCRIPT

    def signature(self, contract: bool) -> List[str]:
        doc = self.doc_text()
        lines = [f"  /** {doc} */"] if doc else []
        parameters = ", ".join(
            self.language.identifier(parameter.name) for parameter in self.parameters if parameter.name.strip()
        )
        access = "#" if self.name.startswith("_") else ""
        name = self.language.identifier(self.name)
        if contract:
            return lines + [f"  {name}({parameters}) {{}}"]
        return lines + [f"  {access}{name}({parameters}) {{"]


class JavaScriptClass(CodeClass):
    language = JAVASCRIPT
    property_type = JavaScriptProperty
    operation_type = JavaScriptOperation

    def stand_in_lines(self) -> Optional[List[str]]:
        """A Fake, Isolated, or Production example type is not a class of its own; it is written as a note."""
        kind = example_extension_kind(self.name)
        if not kind or self.is_contract:
            return None
        return [
            "",
            f"// {self.name} - deprecated as a type. {_EXAMPLE_MODES.get(kind, '')}",
            f"// Use {base_type_name_for(self.name)} directly.",
        ]

    def interface_declaration(self) -> List[str]:
        """JavaScript has no interfaces, so the contract is a class that says it is one."""
        return [f"// interface {self.name}"] + self.class_declaration([])

    def class_declaration(self, bases: List[str]) -> List[str]:
        """JavaScript extends one class and has no `implements`, so the other bases are named in an `// implements`
        line above the class, where the parse reads them back."""
        extended, implemented = self.heritage(bases)
        extends = f" extends {extended}" if extended else ""
        noted = [f"// implements {', '.join(implemented)}"] if implemented else []
        return noted + [f"class {self.name}{extends} {{"]

    def constructor_lines(self, constructor: Optional[Operation], body: List[str]) -> List[str]:
        parameters = ", ".join(self.language.identifier(name) for name, _hint in self.constructor_parameters(constructor))
        return [f"  constructor({parameters}) {{"] + body + self.block_close()


class JavaScriptModule(CodeModule):
    class_type = JavaScriptClass


class JavaScriptCleanEngineeringModel(BraceCleanEngineeringModel):
    language = JAVASCRIPT
    module_type = JavaScriptModule
    suffixes = language.suffixes
