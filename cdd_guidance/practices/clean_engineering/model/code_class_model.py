"""One code render for every language - the walk and the body rule; a language only spells the lines."""

from __future__ import annotations

from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    is_interface_name,
)
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property, property_notes

_CONSTRUCTOR_NAMES = frozenset({"constructor", "__init__"})
_DEFAULT_STEREOTYPES = frozenset({"", "association"})


class CodeCleanEngineeringModel(CleanEngineeringModel):
    """A class model written as code. Python, TypeScript, JavaScript, and Java only spell the lines."""

    language: CodeLanguage

    def render(self, canonical: CleanEngineeringModel, previous: Optional[str] = None) -> str:
        kept = self.parse(previous) if previous else type(self)(name="", sequential_order=1)
        known_names = [oclass.name for oclass in canonical.classes]
        lines = self.file_header(canonical, self._preamble(canonical, kept))
        for module in canonical.modules:
            lines.extend(self._render_module(module, known_names, kept))
        return "\n".join(lines).strip("\n") + "\n"

    def operation_body(self, class_name: str, operation_name: str) -> CodeBody:
        """The body this model read for one operation; "constructor" finds the constructor in any language."""
        for oclass in self.classes:
            if oclass.name != class_name:
                continue
            for operation in oclass.operations:
                if self._answers_to(oclass, operation, operation_name):
                    return operation.body
        return CodeBody()

    def _answers_to(self, oclass: OoadClass, operation: Operation, operation_name: str) -> bool:
        if operation.name == operation_name:
            return True
        return operation_name in _CONSTRUCTOR_NAMES and self._is_constructor(oclass, operation)

    def render_class(self, oclass: OoadClass, known_names: List[str], kept: "CodeCleanEngineeringModel") -> List[str]:
        contract = is_interface_name(oclass.name)
        groups: List[List[str]] = []
        properties = [
            line for prop in oclass.properties for line in self._property_notes(prop) + self.property_line(prop, contract)
        ]
        if properties:
            groups.append(properties)
        constructor = self._constructor(oclass)
        if not contract and (constructor is not None or oclass.properties):
            groups.append(self.constructor_lines(oclass, constructor, self._constructor_body(oclass, constructor, kept)))
        for operation in oclass.operations:
            if operation is constructor or (contract and operation.name.startswith("_")):
                continue
            previous = kept.operation_body(oclass.name, operation.name)
            groups.append(self.render_operation(operation, contract, previous))
        lines = self.class_open(oclass, known_names)
        for index, group in enumerate(groups):
            lines.extend(([""] if index else []) + group)
        return lines + self.class_close(bool(groups))

    def doc_text(self, operation: Operation) -> str:
        """The operation's own description. A description joined from its comments is not documentation."""
        return "" if operation.invariants else operation.description

    def render_operation(self, operation: Operation, contract: bool, previous: CodeBody) -> List[str]:
        signature = self.signature(operation, contract)
        if contract:
            return signature
        return signature + self.render_body(operation, previous) + self.block_close()

    def render_body(self, operation: Operation, previous: CodeBody) -> List[str]:
        body = operation.body.in_language_of(previous, self.language)
        indent = self.language.indent * 2
        if body.language is self.language:
            return body.lines_in(self.language, indent, self.language.unfinished)
        return self._scaffold(operation, body, indent) + body.lines_in(self.language, indent, self.language.unfinished)

    def file_header(self, canonical: CleanEngineeringModel, preamble: CodeBody) -> List[str]:
        return preamble.lines_in(self.language, "", "")

    def class_open(self, oclass: OoadClass, known_names: List[str]) -> List[str]:
        raise NotImplementedError(f"{type(self).__name__} must spell class_open")

    def class_close(self, has_members: bool) -> List[str]:
        return ["}"]

    def property_line(self, prop: Property, contract: bool) -> List[str]:
        raise NotImplementedError(f"{type(self).__name__} must spell property_line")

    def constructor_lines(self, oclass: OoadClass, constructor: Optional[Operation], body: List[str]) -> List[str]:
        raise NotImplementedError(f"{type(self).__name__} must spell constructor_lines")

    def signature(self, operation: Operation, contract: bool) -> List[str]:
        raise NotImplementedError(f"{type(self).__name__} must spell signature")

    def block_close(self) -> List[str]:
        return [f"{self.language.indent}}}"]

    def constructor_parameters(self, oclass: OoadClass, constructor: Optional[Operation]) -> List[tuple]:
        """(name, type hint) for each constructor parameter: the constructor's own, else the class properties."""
        if constructor is not None and constructor.parameters:
            return [(parameter.name, parameter.type_hint) for parameter in constructor.parameters]
        if constructor is not None:
            return []
        return [(prop.name, prop.type_hint) for prop in oclass.properties]

    def _render_module(self, module: Module, known_names: List[str], kept: "CodeCleanEngineeringModel") -> List[str]:
        lines = self._module_banner(module)
        for oclass in module.classes:
            lines.extend(self.render_class(oclass, known_names, kept))
        for child in module.modules:
            lines.extend(self._render_module(child, known_names, kept))
        return lines

    def _property_notes(self, prop: Property) -> List[str]:
        """The stereotype when the model names one other than the default, then origin, cardinality, and invariants."""
        notes = [f"<< {prop.stereotype} >>"] if prop.stereotype not in _DEFAULT_STEREOTYPES else []
        notes.extend(property_notes(prop))
        return [f"{self.language.indent}{self.language.comment(note)}" for note in notes]

    def _module_banner(self, module: Module) -> List[str]:
        if not module.name:
            return []
        lines = ["", self.language.comment(f"=== {module.name} ===")]
        lines.extend(self.language.comment(line) for line in module.description.splitlines())
        return lines

    def _preamble(self, canonical: CleanEngineeringModel, kept: "CodeCleanEngineeringModel") -> CodeBody:
        for model in (canonical, kept):
            for module in model.modules:
                if module.preamble.language is self.language:
                    return module.preamble
        return CodeBody()

    def _constructor(self, oclass: OoadClass) -> Optional[Operation]:
        return next((operation for operation in oclass.operations if self._is_constructor(oclass, operation)), None)

    def _is_constructor(self, oclass: OoadClass, operation: Operation) -> bool:
        return operation.name == oclass.name or operation.name in _CONSTRUCTOR_NAMES

    def _constructor_body(
        self, oclass: OoadClass, constructor: Optional[Operation], kept: "CodeCleanEngineeringModel"
    ) -> List[str]:
        """The constructor as read in this language, else its scaffold, then a field assignment per parameter."""
        own = constructor.body if constructor is not None else CodeBody()
        body = own.in_language_of(kept.operation_body(oclass.name, "constructor"), self.language)
        indent = self.language.indent * 2
        if body.language is self.language:
            return body.lines_in(self.language, indent, "")
        scaffold = self._scaffold(constructor, body, indent) if constructor is not None else []
        assignments = [
            f"{indent}{self.language.assignment(name)}"
            for name, _hint in self.constructor_parameters(oclass, constructor)
        ]
        return scaffold + body.lines_in(self.language, indent, "") + assignments

    def _scaffold(self, operation: Operation, body: CodeBody, indent: str) -> List[str]:
        """What the model says about a body nobody has written yet: its invariants, then its interactions.
        A body from another language already carries its own comments and calls, so it gets none."""
        if not body.is_empty:
            return []
        notes = [self.language.comment(invariant.text) for invariant in operation.invariants]
        calls = [self.language.interaction(callee) for callee in operation.callees]
        return [f"{indent}{line}" for line in notes + calls if line]
