"""One code render for every language - the walk and the body rule. Each language's module, class, property, and
operation are subclasses of the domain parts that spell their own lines."""

from __future__ import annotations

import re
from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    is_interface_name,
)
from cdd_guidance.practices.clean_engineering.model.c_family_parse import CFamilyParse
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import DocComment
from cdd_guidance.practices.source_code import CodeBody, CodeLanguage
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.source_code import SourceText
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.model.source_facts import (
    CONSTRUCTOR_NAMES,
    CodeClassSourceFacts,
    OperationShape,
)
from cdd_guidance.practices.source_code import MeasuredBody
from harness.guidance.practice_formats import Written


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


# The dash a markdown model writes between a type and the note after it: `email: string — identity`.
_NOTE_DASH = " — "


class CodeOperation(Operation):
    """An operation as one language writes it. A brace-language parser gives it the statements inside its braces, and
    it measures them itself once its class holds it, so it reads its own class, body, and parameters."""

    language: CodeLanguage
    # The measures a tool supplies of a file a read names, each kept only once the tool has supplied it: the paths
    # through it and its readability score. Its lines and its parameters are facts every read already keeps.
    paths_through: int
    readability_score: int
    graph_facts = (
        *Operation.graph_facts,
        "max_control_flow_depth",
        "has_bare_catch",
        "swallows_exceptions",
        "unreadable_read_as_empty",
        "unnamed_literal_numbers",
        "paths_through",
        "readability_score",
    )

    def __init__(self, name: str, sequential_order: int = 0, return_type: str = "") -> None:
        super().__init__(name, sequential_order, return_type)
        # The measures the rules read from its written body, each at its clean value until the body is measured.
        self.max_control_flow_depth: int = 0
        self.has_bare_catch: bool = False
        self.swallows_exceptions: bool = False
        # The failure to parse or decode a catch of its body answers with an empty value, by name; empty when none does.
        self.unreadable_read_as_empty: str = ""
        self.unnamed_literal_numbers: list[str] = []
        # The statements inside its braces as written, which the brace-language measures read.
        self._brace_text = SourceText("")

    def take_brace_body(self, text: str, callees: List[str]) -> None:
        """Keep the statements inside its braces as its body, with the operations they call."""
        self.callees = callees
        self.source_facts.take_body(text, self.language)
        self._brace_text = SourceText(text)
        self.line_count = max(1, len([line for line in text.splitlines() if line.strip()]))
        self.source_facts.take_body_fingerprint(text)

    def load_brace_body_facts(self) -> None:
        """Fill the facts the rules measure on its brace-language body."""
        measured = self._brace_text
        self.measure_body(measured)
        self.peer_private_access = measured.collaborators.reaches_peer_private(self._own_objects(), self._own_members())
        if self.is_constructor_of(self.parent):
            parameters = frozenset(parameter.name for parameter in self.parameters if parameter.name)
            self.constructed_types = measured.collaborators.built(parameters, self.line or 1)

    def measure_body(self, body: MeasuredBody) -> None:
        """Keep what the rules measure in its body, which its parser read as a span of text or as a syntax tree."""
        self.max_control_flow_depth = body.control_flow_depth()
        self.has_bare_catch = body.catches_everything()
        self.swallows_exceptions = body.swallows()
        self.unreadable_read_as_empty = body.unreadable_read_as_empty()
        self.unnamed_literal_numbers = body.unnamed_numbers()

    def _copy_measures_from(self, source: "Operation") -> None:
        """Copy the measures the parser took of source's body as well, when source was read from code too."""
        super()._copy_measures_from(source)
        if not isinstance(source, CodeOperation):
            return
        self.max_control_flow_depth = source.max_control_flow_depth
        self.has_bare_catch = source.has_bare_catch
        self.swallows_exceptions = source.swallows_exceptions
        self.unreadable_read_as_empty = source.unreadable_read_as_empty
        self.unnamed_literal_numbers = list(source.unnamed_literal_numbers)

    def _own_objects(self) -> frozenset[str]:
        """The names its body holds an object of its own class by, since privacy is per class: the class itself, each
        parameter typed as it (``other: Money``), and each local it builds with ``new`` of it."""
        owner = self.owner
        if not owner:
            return frozenset()
        typed = re.compile(rf"\b{re.escape(owner)}\b")
        parameters = {parameter.name for parameter in self.parameters if parameter.name and typed.search(parameter.type_hint or "")}
        return frozenset({owner, *parameters, *self._brace_text.collaborators.locals_built_of(owner)})

    def _own_members(self) -> frozenset[str]:
        """The operations and fields the class that holds it declares, which any object of that class may read."""
        holder = self.parent
        if not isinstance(holder, OoadClass):
            return frozenset()
        return frozenset(member.name for member in [*holder.operations, *holder.properties])

    def doc_text(self) -> str:
        """The operation's own description. A description joined from its comments is not documentation."""
        joined = "\n".join(invariant.text for invariant in self.invariants)
        return "" if self.description == joined else self.description

    def signature(self, contract: bool) -> List[str]:
        """The lines that open the operation: its doc comment, decorators, and head."""
        raise NotImplementedError(f"{type(self).__name__} must spell its signature")

    def is_constructor_of(self, oclass: OoadClass) -> bool:
        return self.name == oclass.name or self.name in CONSTRUCTOR_NAMES

    def answers_to(self, oclass: OoadClass, operation_name: str) -> bool:
        """True for its own name; "constructor" finds the constructor in any language."""
        return self.name == operation_name or (operation_name in CONSTRUCTOR_NAMES and self.is_constructor_of(oclass))


class CodeClass(OoadClass):
    """A class as one language writes it: its doc comment, its declaration, its constructor, and its close. Only a
    class read from code is one, so only it declares the measures of its code, which its source facts fill when they
    load; a class read from a markdown model document has none of them."""

    language: CodeLanguage
    property_type: type = CodeProperty
    operation_type: type = CodeOperation
    # The measures the reader keeps of a file a read names, each kept only once a tool has supplied it: its total complexity, the
    # classes it depends on, and the groups of its methods that share no data with one another.
    total_complexity: int
    classes_depended_on: int
    unshared_method_groups: int
    graph_facts = (
        *OoadClass.graph_facts,
        "method_count",
        "operation_shapes",
        "property_names",
        "constructs",
        "prose_comment",
        "prototype_swap",
        "total_complexity",
        "classes_depended_on",
        "unshared_method_groups",
    )

    def __init__(self, name: str, sequential_order: int, intent: str = "") -> None:
        super().__init__(name, sequential_order, intent)
        self.method_count = 0
        self.operation_shapes: List[OperationShape] = []
        self.property_names: List[str] = []
        # The classes its constructor builds that its caller cannot hand it.
        self.constructs: List[str] = []
        # Whether a `#` comment in the lines it spans narrates what the code already says.
        self.prose_comment = False
        # The code that swaps an object's class, and its line; empty when the class swaps none.
        self.prototype_swap: dict[str, str | int] = {}

    def _source_facts(self) -> CodeClassSourceFacts:
        return CodeClassSourceFacts(self)

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
            return [""] + self._doc(DocComment.from_class(self, marked=True).text()) + self._interface_declaration()
        lines = [""] + self._doc(self._doc_intent()) + self._stereotype_decorators()
        return lines + self._class_declaration(self.declared_bases(known_names))

    def _doc(self, intent: str) -> List[str]:
        return [f"/** {intent} */"] if intent else []

    def _doc_intent(self) -> str:
        """What the class's doc comment says. A language with no decorators marks the stereotypes there."""
        return DocComment.from_class(self, marked=True).text()

    def _stereotype_decorators(self) -> List[str]:
        """The decorator lines that carry the class's stereotypes; none for a language that marks them in the doc."""
        return []

    def _interface_declaration(self) -> List[str]:
        raise NotImplementedError(f"{type(self).__name__} must spell interface_declaration")

    def _class_declaration(self, bases: List[str]) -> List[str]:
        """`class Name extends Base implements Contract, Other {`: the first base that is not an I{Class} contract is
        extended, and every other base is implemented."""
        extended, implemented = self._heritage(bases)
        extends = f" extends {extended}" if extended else ""
        implements = f" implements {', '.join(implemented)}" if implemented else ""
        return [f"{self._class_modifiers(implemented)}class {self.name}{extends}{implements} {{"]

    def _heritage(self, bases: List[str]) -> tuple:
        """(the one base a class extends, the bases it implements). A brace language extends one class only."""
        extended = next((base for base in bases if not is_interface_name(base)), "")
        return extended, [base for base in bases if base != extended]

    def _class_modifiers(self, implemented: List[str]) -> str:
        """The words before `class`, such as TypeScript's `abstract`."""
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
        if constructor is None or self._elides_parameters(constructor):
            return [(prop.name, prop.type_hint) for prop in self.properties]
        return [(parameter.name, parameter.type_hint) for parameter in constructor.parameters]

    def _elides_parameters(self, constructor: Operation) -> bool:
        """True for a ``(...)`` constructor, which leaves its parameters to the class's properties."""
        return bool(constructor.parameters) and all(parameter.name.strip() == "..." for parameter in constructor.parameters)


class CodeModule(Module):
    """A module as one language reads and writes it: its classes and nested modules are that language's."""

    class_type: type = CodeClass


class CodeCleanEngineeringModel(CleanEngineeringModel):
    """A class model written as code. Python, TypeScript, and JavaScript parts spell their own lines."""

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

    def file_module(self) -> Module:
        """The module the last text this model parsed forms, with that text kept, whether or not it holds a class."""
        return self._file_module

    def render(self, canonical: CleanEngineeringModel, written: Written = Written()) -> str:
        """Write canonical as code, keeping the bodies the previous file had. A practice keeps one channel per format
        and renders every model through it, so another model is written from a model of its own, never translated into
        this one, whose classes would keep the names of the model rendered before."""
        if canonical is not self:
            own = type(self)(name="", sequential_order=1)
            own.translate_from(canonical)
            own.keep_notes_out_of_code()
            return own.render(own, written)
        kept = type(self)(name="", sequential_order=1)
        if written.previous:
            kept.parse(written.previous)
        known_names = [oclass.name for oclass in self.every_class()]
        lines = self.file_header(self._preamble(kept))
        for module in self.modules:
            lines.extend(self._render_module(module, known_names, kept))
        return "\n".join(lines).strip("\n") + "\n"

    def keep_notes_out_of_code(self) -> None:
        """Move what a markdown model writes beside a name or type into comments, so the code parses: the words a class
        heading writes after the class's name go into its description, and a note written after a type with a dash
        (`email: string — identity`) becomes the member's note."""
        for oclass in self.every_class():
            self._keep_class_name_alone(oclass)
            for prop in oclass.properties:
                prop.type_hint = self._type_alone(prop, prop.type_hint)
            for operation in oclass.operations:
                operation.return_type = self._type_alone(operation, operation.return_type)
                for parameter in operation.parameters:
                    parameter.type_hint = self._without_note(parameter.type_hint)[0]

    def _keep_class_name_alone(self, oclass: OoadClass) -> None:
        """Name oclass by the identifier its heading starts with, keeping the rest in its description, and its
        constructor, named after the class, by that name too."""
        named = re.match(r"\w+", oclass.name or "")
        if named is None or named.group(0) == oclass.name:
            return
        written, oclass.name = oclass.name, named.group(0)
        oclass.intent = " ".join(part for part in (oclass.intent, written[named.end():].strip()) if part)
        for operation in oclass.operations:
            if operation.name == written:
                operation.name = oclass.name

    def _type_alone(self, member: Operation | Property, written: str) -> str:
        """written without the note after its dash, which member keeps as a note."""
        type_hint, note = self._without_note(written)
        if note:
            member.add_invariant(note)
        return type_hint

    def _without_note(self, written: str) -> tuple:
        """(the type written before a note's dash, the note after it); the note is empty when there is none."""
        type_hint, _dash, note = (written or "").partition(_NOTE_DASH)
        return type_hint.strip(), note.strip()

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
        groups = self._member_groups(oclass, kept)
        lines = oclass.opening(known_names)
        for index, group in enumerate(groups):
            lines.extend(([""] if index else []) + group)
        return lines + oclass.closing(bool(groups))

    def _member_groups(self, oclass: CodeClass, kept: "CodeCleanEngineeringModel") -> List[List[str]]:
        """The class's members as blocks a blank line separates: its properties, its constructor, then each operation
        with the body kept from the previous file. A contract writes no constructor and no private operation."""
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
        return groups

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
    """A class model written in a brace language: TypeScript or JavaScript. Each reads its own text through
    the brace-language reading it shares."""
