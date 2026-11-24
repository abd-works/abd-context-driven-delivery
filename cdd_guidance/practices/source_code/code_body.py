"""Code bodies and the languages they are written in - the one body rule every code channel uses."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

from cdd_guidance.practices.source_code.bracket_structure import BracketStructure, split_top_level

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# An interaction the model writes as a whole call, `CredentialsRepository.create(this)`, up to its closing parenthesis,
# so a note after it stays out of the code.
_WHOLE_CALL = re.compile(r"^[A-Za-z_][\w.]*\([^()]*\)")
_PROSE = re.compile(
    r"\b(the|and|is|are|a|an|of|to|for|that|this|with|from|into|each|same|only|like)\b",
    re.I,
)
_PROSE_TOKENS = 3
# A generic type as either family of languages writes one, `list[CartLine]` or `Collection<Cart>`, and an array, `Cart[]`.
_GENERIC_TYPE = re.compile(r"^([A-Za-z_][\w.]*)\s*[\[<](.+)[\]>]$")
_ARRAY_TYPE = re.compile(r"^(.*[\w\]>])\s*\[\]$")
_LIST_NAMES = frozenset({"list", "List", "Array"})
_PLACEHOLDERS = frozenset({"...", "pass", "{}"})


@dataclass(frozen=True)
class CodeSpelling:
    """<<Value Object>> How a language writes the receiver, a constructor call, the end of a statement, and the base
    class's constructor and receiver."""

    receiver: str
    construct: str
    statement_end: str
    camel_case: bool
    base_constructor: str = "super"
    base_receiver: str = "super"
    # How it writes a list of a type, and the brackets it puts a generic type's arguments in.
    list_of: str = "{type}[]"
    generic_brackets: Tuple[str, str] = ("<", ">")
    # How it imports names from another module, as a statement it writes and a pattern it reads one by (its module and
    # its names), and whether it names a module with dots (`src.ordering.cart`) rather than as a path (`src/ordering/cart`).
    import_statement: str = 'import {{ {names} }} from "{module}";'
    import_pattern: str = r"^import\s*\{(?P<names>[^}]*)\}\s*from\s*[\"'](?P<module>[^\"']+)[\"'];?$"
    dotted_modules: bool = False


@dataclass(frozen=True, eq=False)
class CodeLanguage:
    """How one programming language spells what every code channel writes the same way. Each language is one object,
    compared by identity."""

    name: str
    line_comment: str
    indent: str
    unfinished: str
    spelling: CodeSpelling
    type_names: Dict[str, str] = field(default_factory=dict)
    # The file extensions source in this language is written with; the one table every reader of code asks.
    suffixes: tuple[str, ...] = ()

    def comment(self, text: str) -> str:
        return f"{self.line_comment} {text}".rstrip()

    def translation_note(self, other: "CodeLanguage") -> str:
        """The comment this language writes above a body kept in other, which nobody has translated yet."""
        return self.comment(f"{other.name} body to translate:")

    def is_unfinished(self, text: str) -> bool:
        stripped = text.strip()
        return not stripped or stripped in _PLACEHOLDERS or stripped == self.unfinished

    def identifier(self, name: str) -> str:
        raw = name.split(":", 1)[0].strip()
        if not self.spelling.camel_case:
            return raw
        parts = re.split(r"_+", raw.lstrip("_"))
        return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:] if part)

    def type_name(self, hint: str) -> str:
        """hint as this language spells it, whichever language wrote it: its own word for a built-in type, a list as
        it writes one, and a generic type's arguments in its own brackets."""
        written = hint.strip()
        if written in self.type_names:
            return self.type_names[written]
        marks = BracketStructure(written).top_level_indexes("|")
        choices = [written[start + 1:end].strip() for start, end in zip([-1, *marks], [*marks, len(written)])]
        if len(choices) > 1:
            return " | ".join(self.type_name(choice) for choice in choices)
        array = _ARRAY_TYPE.match(written)
        if array:
            return self.spelling.list_of.format(type=self.type_name(array.group(1)))
        generic = _GENERIC_TYPE.match(written)
        if generic is None:
            return written
        arguments = [self.type_name(argument) for argument in split_top_level(generic.group(2))]
        if generic.group(1) in _LIST_NAMES and len(arguments) == 1:
            return self.spelling.list_of.format(type=arguments[0])
        opening, closing = self.spelling.generic_brackets
        return f"{generic.group(1)}{opening}{', '.join(arguments)}{closing}"

    def interaction(self, callee: str) -> str:
        end = self.spelling.statement_end
        written = _WHOLE_CALL.match(callee.strip())
        if written and not written.group(0).startswith("super"):
            return f"{written.group(0)}{end}"
        tokens = callee.strip().split()
        if not tokens or (len(tokens) >= _PROSE_TOKENS and _PROSE.search(callee)):
            return ""
        head, arguments = tokens[0], ", ".join(tokens[1:])
        if head == "super" or head.startswith("super."):
            return self._super_call(head[len("super."):], arguments) + end
        if "." not in head and head[0].isupper() and _IDENTIFIER.match(head):
            target = self.identifier(tokens[1] if len(tokens) > 1 else head)
            created = self.spelling.construct.format(type=head, arguments=arguments)
            return f"{self.spelling.receiver}.{target} = {created}{end}"
        owner, *members = head.split(".")
        called = ".".join([owner, *(self.identifier(member) for member in members)])
        return f"{called}({arguments}){end}"

    def scaffold_calls(self, text: str) -> Optional[List[str]]:
        """The calls a body holds when it is only what a render writes from the model for a body nobody has written
        yet (``CodeCleanEngineeringModel._scaffold``): its notes as comments, its interactions as whole calls, then
        the line that fails until it is written. Each call as written, without its statement end. None for a body that
        holds anything else, or that is a body of another language kept under its translation note."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines or lines[-1] != self.unfinished:
            return None
        if any(lines[0] == self.translation_note(other) for other in CODE_LANGUAGES if other is not self):
            return None
        calls: List[str] = []
        for line in lines[:-1]:
            if line.startswith(self.line_comment):
                continue
            statement = line.removesuffix(self.spelling.statement_end).strip()
            if not _WHOLE_CALL.fullmatch(statement):
                return None
            calls.append(statement)
        return calls

    def base_constructor_arguments(self, text: str) -> Optional[List[str]]:
        """The arguments a body written in this language passes to its base class's constructor (`super().__init__(order,
        address)`, `super(order, address);`); None when it calls none."""
        call = re.search(rf"^\s*{re.escape(self.spelling.base_constructor)}\((.*)\)\s*;?\s*$", text, re.MULTILINE)
        return [argument.strip() for argument in split_top_level(call.group(1)) if argument.strip()] if call else None

    def base_constructor_call(self, arguments: List[str]) -> str:
        """The call to the base class's constructor with arguments, named as this language names them."""
        named = ", ".join(self.identifier(argument) for argument in arguments)
        return f"{self.spelling.base_constructor}({named}){self.spelling.statement_end}"

    def imports_in(self, text: str) -> List[Tuple[str, List[str]]]:
        """Each import of names a module written in this language states, as (the module as a path, such as
        `src/ordering/cart` or `./cart`, the names it imports). An import of a whole module, or of what the language
        itself provides (`__future__`), names nothing to carry into another language."""
        found = []
        for line in text.splitlines():
            statement = re.match(self.spelling.import_pattern, line.strip())
            if statement is None or statement.group("module") == "__future__":
                continue
            names = [name.strip() for name in statement.group("names").split(",") if name.strip()]
            found.append((self._module_path(statement.group("module")), names))
        return found

    def import_line(self, module: str, names: List[str]) -> str:
        """The statement that imports names from module, a path as ``imports_in`` gives one, as this language writes it."""
        return self.spelling.import_statement.format(module=self._module_name(module), names=", ".join(names))

    def _module_path(self, written: str) -> str:
        """A module as this language writes it, as a path: `..cart.line` is `../cart/line`, `./cart.ts` is `./cart`."""
        if not self.spelling.dotted_modules:
            return re.sub(r"\.(ts|tsx|js|jsx|mjs)$", "", written)
        dots = len(written) - len(written.lstrip("."))
        path = written[dots:].replace(".", "/")
        if not dots:
            return path
        return ("./" if dots == 1 else "../" * (dots - 1)) + path

    def _module_name(self, path: str) -> str:
        """A module path as this language writes a module: dotted, a leading `./` one dot and each `../` one more."""
        if not self.spelling.dotted_modules:
            return path
        parts = [part for part in path.split("/") if part]
        ups = sum(1 for part in parts if part == "..")
        dots = "." * (ups + 1) if parts and parts[0] in (".", "..") else ""
        return dots + ".".join(part for part in parts if part not in (".", ".."))

    def assignment(self, name: str) -> str:
        field_name = self.identifier(name)
        return f"{self.spelling.receiver}.{field_name} = {field_name}{self.spelling.statement_end}"

    def _super_call(self, member: str, arguments: str) -> str:
        if not member or member[0].isupper():
            return f"{self.spelling.base_constructor}({arguments})"
        return f"{self.spelling.base_receiver}.{member}({arguments})"


class CodeBody:
    """<<Value Object>> The statements inside one operation, test, or step, kept with the language they were read in.
    It never changes once made; a body in another language is a new one (``in_language_of``)."""

    def __init__(self, text: str = "", language: Optional[CodeLanguage] = None) -> None:
        lines = [line if line.strip() else "" for line in text.split("\n")]
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        base = next((line[: len(line) - len(line.lstrip())] for line in lines if line.strip()), "")
        # WHY: a line without the first code line's indentation is inside a multi-line string, so it never moves.
        self._lines = [(line.startswith(base), line[len(base) :] if line.startswith(base) else line) for line in lines]
        relative = "\n".join(line for _moves, line in self._lines)
        finished = language is not None and not language.is_unfinished(relative)
        self.text = relative if finished else ""
        self.language = language if finished else None
        if not finished:
            self._lines = []

    @property
    def is_empty(self) -> bool:
        return not self.text

    def mentions(self, word: str) -> bool:
        """The body uses this word as written, such as await in a callback that must be async."""
        return re.search(rf"\b{re.escape(word)}\b", self.text) is not None

    def lines_in(self, language: CodeLanguage, indent: str, unfinished: str) -> List[str]:
        if self.language is language:
            return [f"{indent}{line}" if moves and line.strip() else line for moves, line in self._lines]
        marker = [f"{indent}{unfinished}"] if unfinished else []
        if self.is_empty:
            return marker
        note = [f"{indent}{language.translation_note(self.language)}"]
        original = [f"{indent}{language.comment(line)}" for line in self.text.splitlines()]
        return note + original + marker

    @classmethod
    def from_written(cls, text: str, language: CodeLanguage) -> "CodeBody":
        """The body text holds, as language wrote it: another language's when text is that body kept as comments under
        a translation note, as ``lines_in`` writes one, else language's own. Read back so, a body taken to another
        language and back is not wrapped in a second layer of comments."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        notes = {language.translation_note(other): other for other in CODE_LANGUAGES if other is not language}
        other = notes.get(lines[0]) if lines else None
        sign = language.line_comment
        if other is None or not all(line.startswith(sign) for line in lines):
            return cls(text, language)
        return cls("\n".join(line[len(sign):].removeprefix(" ") for line in lines[1:]), other)

    def in_language_of(self, other: "CodeBody", language: CodeLanguage) -> "CodeBody":
        if self.language is language or other.language is not language:
            return self
        return other


WrittenKey = Union[str, Tuple, None]
# What a node says in code when it is read: a name, or a tuple of names, steps, and bodies.


_QUOTED_START = re.compile(r"""\s*(['"`])(?:\\.|(?!\1).)*\1""")


class BraceCall:
    """One call whose last argument is a callback, such as `describe("a cart", () => { ... })` or `story(...)`: where it
    starts, its parentheses, its callback's braces, and where it ends. A quoted first argument, the block's name, is
    skipped, so a brace or an arrow inside the name is not taken for the callback's."""

    def __init__(self, text: str, start: int, name: str) -> None:
        source = BracketStructure(text)
        # The text of the file the call was read from, which its body is part of.
        self.text = text
        self.start = start
        self.name = name
        open_paren = text.index("(", start)
        self.close = source.closing_bracket(open_paren, "(", ")")
        limit = self.close if self.close is not None else len(text)
        quoted = _QUOTED_START.match(text, open_paren + 1)
        head = quoted.end() if quoted else open_paren
        arrow = text.find("=>", head, limit)
        self.brace = text.find("{", arrow if arrow >= 0 else head, limit)
        self.inner_end = source.closing_bracket(self.brace) if self.brace >= 0 else None
        end = (self.close + 1) if self.close is not None else start
        self.end = end + 1 if text.startswith(";", end) else end

    @property
    def is_whole(self) -> bool:
        return self.close is not None and self.brace >= 0 and self.inner_end is not None

    @property
    def body(self) -> str:
        """The text inside its callback's braces; empty for a call that does not close."""
        return self.text[self.brace + 1 : self.inner_end] if self.is_whole else ""


class WrittenBlock:
    """The source lines around one block of code that no node holds, kept exactly as read.

    A BDD describe, context, or it, a story, scenario, or step chain: the language writes these lines back
    unchanged while the node still has the key it was read with."""

    def __init__(self, language: CodeLanguage, key: WrittenKey, heading: List[str]) -> None:
        self.language = language
        self.key = key
        self.path = ""
        self.heading = heading
        self.close: List[str] = []
        self._inline = ""
        self._inside: List[str] = []
        # The lines above the block that lead into it, which its reader sets once it has read them.
        self.lead = []
        self.closing = []
        self.inside = []

    @property
    def lead(self) -> List[str]:
        return self._lead

    @lead.setter
    def lead(self, lines: List[str]) -> None:
        self._lead = lines
        # The lines above the block as a body, made once when the reader sets them.
        self.lead_body = CodeBody("\n".join(lines), self.language)

    @property
    def closing(self) -> List[str]:
        return self._closing

    @closing.setter
    def closing(self, lines: List[str]) -> None:
        self._closing = lines
        self.closing_body = CodeBody("\n".join(lines), self.language)

    @property
    def inside(self) -> List[str]:
        return self._inside

    @inside.setter
    def inside(self, lines: List[str]) -> None:
        self._inside = lines
        self._read_inside()

    @property
    def inline(self) -> str:
        return self._inline

    @inline.setter
    def inline(self, text: str) -> None:
        self._inline = text
        self._read_inside()

    def _read_inside(self) -> None:
        """The setup or test body as read: the heading's own text for a one-line block, else the inside lines."""
        self.inside_body = CodeBody(self._inline or "\n".join(self._inside), self.language)

    def is_in(self, language: CodeLanguage, key: WrittenKey) -> bool:
        return self.language is language and self.key == key

    def inside_for(self, body: CodeBody) -> List[str] | None:
        """The setup or test body lines exactly as read, while the model's body still says the same.
        A block written on one line keeps its body in the heading, so it has no inside lines."""
        return self.inside if self.inside_body.text == body.text else None


class InsideLines:
    """The lines inside one block of a file, from the line after its heading up to its closing line, which its child
    blocks divide."""

    def __init__(self, lines: List[str], inside: Tuple[int, int]) -> None:
        # Every line of the file, and the first and last-plus-one index of the block's inside.
        self.lines = lines
        self.start, self.end = inside

    def split(self, children: List[Tuple[int, int]]) -> Tuple[List[str], List[List[str]], List[str]]:
        """The lines inside the block as (setup, the lines above each child, the lines after the last child), each
        child given by its first and last line. Blank lines right above the first child belong to it; with no child
        they close the block."""
        lines = self.lines
        region = lines[self.start : children[0][0]] if children else lines[self.start : self.end]
        kept = len(region)
        while kept and not region[kept - 1].strip():
            kept -= 1
        if not children:
            return region[:kept], [], region[kept:]
        leads = [region[kept:]] + [lines[previous[1] + 1 : child[0]] for previous, child in zip(children, children[1:])]
        return region[:kept], leads, lines[children[-1][1] + 1 : self.end]


# Python's own failures, each Error in TypeScript and JavaScript, which a class extends as it extends any base.
_PYTHON_ERRORS = {name: "Error" for name in ("Exception", "ValueError", "RuntimeError", "LookupError", "KeyError", "TypeError")}

PYTHON_SPELLING = CodeSpelling(
    receiver="self",
    construct="{type}({arguments})",
    statement_end="",
    camel_case=False,
    base_constructor="super().__init__",
    base_receiver="super()",
    list_of="list[{type}]",
    generic_brackets=("[", "]"),
    import_statement="from {module} import {names}",
    import_pattern=r"^from\s+(?P<module>[\w.]+)\s+import\s+(?P<names>[^()]+)$",
    dotted_modules=True,
)
C_FAMILY_SPELLING = CodeSpelling(receiver="this", construct="new {type}({arguments})", statement_end=";", camel_case=True)

PYTHON = CodeLanguage(
    "python",
    "#",
    "    ",
    "raise NotImplementedError",
    PYTHON_SPELLING,
    type_names={
        "string": "str",
        "number": "float",
        "boolean": "bool",
        "void": "None",
        "null": "None",
        "undefined": "None",
        "any": "object",
        "Error": "Exception",
    },
    suffixes=(".py",),
)
TYPESCRIPT = CodeLanguage(
    "typescript",
    "//",
    "  ",
    'throw new Error("not implemented");',
    C_FAMILY_SPELLING,
    type_names={
        "str": "string",
        "int": "number",
        "float": "number",
        "bool": "boolean",
        "None": "void",
        "list": "Array<any>",
        "dict": "Record<string, any>",
        "object": "any",
        **_PYTHON_ERRORS,
    },
    suffixes=(".ts", ".tsx"),
)
JAVASCRIPT = CodeLanguage(
    "javascript",
    "//",
    "  ",
    'throw new Error("not implemented");',
    C_FAMILY_SPELLING,
    type_names=dict(_PYTHON_ERRORS),
    suffixes=(".js", ".jsx"),
)

# Every programming language the code channels read.
CODE_LANGUAGES = (PYTHON, TYPESCRIPT, JAVASCRIPT)
