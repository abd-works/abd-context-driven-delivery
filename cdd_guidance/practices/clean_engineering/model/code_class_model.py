"""One code render for every language - the walk and the body rule. Each language's module, class, property, and
operation are subclasses of the domain parts that spell their own lines."""

from __future__ import annotations

from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    is_interface_name,
)
from cdd_guidance.practices.clean_engineering.model.c_family_parse import CFamilyParse
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import marked_intent
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property

_CONSTRUCTOR_NAMES = frozenset({"constructor", "__init__"})


class CodeProperty(Property):
    """A property as one language writes it."""

    language: CodeLanguage

    def note_lines(self) -> List[str]:
        """The stereotype the model names, then origin, cardinality, and invariants, each as a comment."""
        notes = [f"<< {self.stereotype} >>"] if self.stereotype else []
        notes.extend(self.notes())
        return [f"{self.language.indent}{self.language.comment(note)}" for note in notes]

    def lines(self, contract: bool) -> List[str]:
        """The property's declaration in a class, or in a contract when contract is true."""
        raise NotImplementedError(f"{type(self).__name__} must spell its lines")


class CodeOperation(Operation):
    """An operation as one language writes it."""

    language: CodeLanguage

    def doc_text(self) -> str:
        """The operation's own description. A description joined from its comments is not documentation."""
        return "" if self.invariants else self.description

    def signature(self, contract: bool) -> List[str]:
        """The lines that open the operation: its doc comment, decorators, and head."""
        raise NotImplementedError(f"{type(self).__name__} must spell its signature")

    def is_constructor_of(self, oclass: OoadClass) -> bool:
        return self.name == oclass.name or self.name in _CONSTRUCTOR_NAMES

    def answers_to(self, oclass: OoadClass, operation_name: str) -> bool:
        """True for its own name; "constructor" finds the constructor in any language."""
        return self.name == operation_name or (operation_name in _CONSTRUCTOR_NAMES and self.is_constructor_of(oclass))


class CodeClass(OoadClass):
    """A class as one language writes it: its doc comment, its declaration, its constructor, and its close."""

    language: CodeLanguage
    property_type: type = CodeProperty
    operation_type: type = CodeOperation

    def load_property(self, source: Property) -> CodeProperty:
        loaded = self.property_type(source.name, source.sequential_order)
        loaded.update_self(source)
        return loaded

    def load_operation(self, source: Operation) -> CodeOperation:
        loaded = self.operation_type(source.name, source.sequential_order)
        loaded.update_self(source)
        return loaded

    @property
    def is_contract(self) -> bool:
        return is_interface_name(self.name)

    def constructor(self) -> Optional[CodeOperation]:
        return next((operation for operation in self.operations if operation.is_constructor_of(self)), None)

    def stand_in_lines(self) -> Optional[List[str]]:
        """Lines a language writes instead of the class; none when it writes the class itself."""
        return None

    def opening(self, known_names: List[str]) -> List[str]:
        """A blank line, the class's doc comment, its stereotype decorators, then the declaration for its kind: an
        interface, or a class with the bases it declares. An interface takes no decorators, so its stereotypes are
        marked in its doc comment."""
        if self.is_contract:
            return [""] + self.doc(marked_intent(self.stereotypes, self.intent)) + self.interface_declaration()
        lines = [""] + self.doc(self.doc_intent()) + self.stereotype_decorators()
        return lines + self.class_declaration(self.declared_bases(known_names))

    def doc(self, intent: str) -> List[str]:
        return [f"/** {intent} */"] if intent else []

    def doc_intent(self) -> str:
        """What the class's doc comment says. A language with no decorators marks the stereotypes there."""
        return marked_intent(self.stereotypes, self.intent)

    def stereotype_decorators(self) -> List[str]:
        """The decorator lines that carry the class's stereotypes; none for a language that marks them in the doc."""
        return []

    def interface_declaration(self) -> List[str]:
        raise NotImplementedError(f"{type(self).__name__} must spell interface_declaration")

    def class_declaration(self, bases: List[str]) -> List[str]:
        """`class Name extends Base implements Contract, Other {`: the first base that is not an I{Class} contract is
        extended, and every other base is implemented."""
        extended, implemented = self.heritage(bases)
        extends = f" extends {extended}" if extended else ""
        implements = f" implements {', '.join(implemented)}" if implemented else ""
        return [f"{self.class_modifiers(implemented)}class {self.name}{extends}{implements} {{"]

    def heritage(self, bases: List[str]) -> tuple:
        """(the one base a class extends, the bases it implements). A brace language extends one class only."""
        extended = next((base for base in bases if not is_interface_name(base)), "")
        return extended, [base for base in bases if base != extended]

    def class_modifiers(self, implemented: List[str]) -> str:
        """The words before `class`, such as Java's `public`."""
        return ""

    def closing(self, has_members: bool) -> List[str]:
        return ["}"]

    def block_close(self) -> List[str]:
        """The line that closes an operation's block."""
        return [f"{self.language.indent}}}"]

    def constructor_lines(self, constructor: Optional[Operation], body: List[str]) -> List[str]:
        raise NotImplementedError(f"{type(self).__name__} must spell constructor_lines")

    def constructor_parameters(self, constructor: Optional[Operation]) -> List[tuple]:
        """(name, type hint) for each constructor parameter: the constructor's own, else the class properties.
        A ``(...)`` constructor names no parameters of its own, so it takes the properties too."""
        if constructor is None or _elides_parameters(constructor):
            return [(prop.name, prop.type_hint) for prop in self.properties]
        return [(parameter.name, parameter.type_hint) for parameter in constructor.parameters]


class CodeModule(Module):
    """A module as one language reads and writes it: its classes and nested modules are that language's."""

    class_type: type = CodeClass

    def load_module(self, source: Module) -> "CodeModule":
        return type(self)(name=source.name, sequential_order=source.sequential_order)

    def load_class(self, source: OoadClass) -> CodeClass:
        return self.class_type(name=source.name, sequential_order=source.sequential_order)


def _elides_parameters(constructor: Operation) -> bool:
    return bool(constructor.parameters) and all(parameter.name.strip() == "..." for parameter in constructor.parameters)


class CodeCleanEngineeringModel(CleanEngineeringModel):
    """A class model written as code. Python, TypeScript, JavaScript, and Java parts spell their own lines."""

    language: CodeLanguage
    module_type: type = CodeModule
    # The source files this model reads, by extension.
    suffixes: tuple = ()

    @property
    def class_type(self) -> type:
        return self.module_type.class_type

    @property
    def operation_type(self) -> type:
        return self.class_type.operation_type

    @property
    def property_type(self) -> type:
        return self.class_type.property_type

    def load_module(self, source: Module) -> CodeModule:
        return self.module_type(name=source.name, sequential_order=source.sequential_order)

    def file_module(self) -> Module:
        """The module the last text this model parsed forms, with that text kept, whether or not it holds a class."""
        return self._file_module

    def render(self, canonical: CleanEngineeringModel, previous: Optional[str] = None) -> str:
        """Become the canonical model once, then write this model as code, keeping the bodies the previous file had."""
        kept = type(self)(name="", sequential_order=1)
        if previous:
            kept.parse(previous)
        if canonical is not self:
            self.translate_from(canonical)
        known_names = [oclass.name for oclass in self.every_class()]
        lines = self.file_header(self._preamble(kept))
        for module in self.modules:
            lines.extend(self._render_module(module, known_names, kept))
        return "\n".join(lines).strip("\n") + "\n"

    def operation_body(self, class_name: str, operation_name: str) -> CodeBody:
        """The body this model read for one operation; "constructor" finds the constructor in any language."""
        for oclass in self.every_class():
            if oclass.name != class_name:
                continue
            for operation in oclass.operations:
                if operation.answers_to(oclass, operation_name):
                    return operation.body
        return CodeBody()

    def render_class(self, oclass: CodeClass, known_names: List[str], kept: "CodeCleanEngineeringModel") -> List[str]:
        stand_in = oclass.stand_in_lines()
        if stand_in is not None:
            return stand_in
        contract = oclass.is_contract
        groups: List[List[str]] = []
        properties = [line for prop in oclass.properties for line in prop.note_lines() + prop.lines(contract)]
        if properties:
            groups.append(properties)
        constructor = oclass.constructor()
        if not contract and (constructor is not None or oclass.properties):
            groups.append(oclass.constructor_lines(constructor, self._constructor_body(oclass, constructor, kept)))
        for operation in oclass.operations:
            if operation is constructor or (contract and operation.name.startswith("_")):
                continue
            previous = kept.operation_body(oclass.name, operation.name)
            groups.append(self.render_operation(oclass, operation, previous))
        lines = oclass.opening(known_names)
        for index, group in enumerate(groups):
            lines.extend(([""] if index else []) + group)
        return lines + oclass.closing(bool(groups))

    def render_operation(self, oclass: CodeClass, operation: CodeOperation, previous: CodeBody) -> List[str]:
        signature = operation.signature(oclass.is_contract)
        if oclass.is_contract:
            return signature
        return signature + self.render_body(operation, previous) + oclass.block_close()

    def render_body(self, operation: Operation, previous: CodeBody) -> List[str]:
        body = operation.body.in_language_of(previous, self.language)
        indent = self.language.indent * 2
        if body.language is self.language:
            return body.lines_in(self.language, indent, self.language.unfinished)
        return self._scaffold(operation, body, indent) + body.lines_in(self.language, indent, self.language.unfinished)

    def file_header(self, preamble: CodeBody) -> List[str]:
        return preamble.lines_in(self.language, "", "")

    def _render_module(self, module: Module, known_names: List[str], kept: "CodeCleanEngineeringModel") -> List[str]:
        lines = self._module_banner(module)
        for oclass in module.classes:
            lines.extend(self.render_class(oclass, known_names, kept))
        for child in module.modules:
            lines.extend(self._render_module(child, known_names, kept))
        return lines

    def _module_banner(self, module: Module) -> List[str]:
        if not module.name:
            return []
        lines = ["", self.language.comment(f"=== {module.name} ===")]
        lines.extend(self.language.comment(line) for line in module.description.splitlines())
        return lines

    def _preamble(self, kept: "CodeCleanEngineeringModel") -> CodeBody:
        for model in (self, kept):
            for module in model.modules:
                if module.preamble.language is self.language:
                    return module.preamble
        return CodeBody()

    def _constructor_body(
        self, oclass: CodeClass, constructor: Optional[Operation], kept: "CodeCleanEngineeringModel"
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
            for name, _hint in oclass.constructor_parameters(constructor)
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


class BraceCleanEngineeringModel(CFamilyParse, CodeCleanEngineeringModel):
    """A class model written in a brace language: TypeScript, JavaScript, or Java. Each reads its own text through
    the brace-language reading it shares."""
