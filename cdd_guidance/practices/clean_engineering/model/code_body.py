"""Code bodies and the languages they are written in - the one body rule every code channel uses."""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple, Union

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_PROSE = re.compile(
    r"\b(the|and|is|are|a|an|of|to|for|that|this|with|from|into|each|same|only|like)\b",
    re.I,
)
_PROSE_TOKENS = 3
_PLACEHOLDERS = frozenset({"...", "pass", "{}"})


class CodeSpelling:
    """How a language writes the receiver, a constructor call, and the end of a statement."""

    def __init__(
        self,
        receiver: str,
        construct: str,
        statement_end: str,
        camel_case: bool,
        base_call: tuple = ("super", "super"),
    ) -> None:
        self.receiver = receiver
        self.construct = construct
        self.statement_end = statement_end
        self.camel_case = camel_case
        self.base_constructor, self.base_receiver = base_call


class CodeLanguage:
    """How one programming language spells what every code channel writes the same way."""

    _languages: Dict[str, "CodeLanguage"] = {}

    def __init__(
        self,
        name: str,
        line_comment: str,
        indent: str,
        unfinished: str,
        spelling: CodeSpelling,
        type_names: Dict[str, str],
    ) -> None:
        self.name = name
        self.line_comment = line_comment
        self.indent = indent
        self.unfinished = unfinished
        self._spelling = spelling
        self._type_names = type_names
        CodeLanguage._languages[name] = self

    @classmethod
    def named(cls, name: str) -> "CodeLanguage":
        return cls._languages[name.lower()]

    def comment(self, text: str) -> str:
        return f"{self.line_comment} {text}".rstrip()

    def is_unfinished(self, text: str) -> bool:
        stripped = text.strip()
        return not stripped or stripped in _PLACEHOLDERS or stripped == self.unfinished

    def identifier(self, name: str) -> str:
        raw = name.split(":", 1)[0].strip()
        if not self._spelling.camel_case:
            return raw
        parts = re.split(r"_+", raw.lstrip("_"))
        return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:] if part)

    def type_name(self, hint: str) -> str:
        return self._type_names.get(hint.strip(), hint.strip())

    def interaction(self, callee: str) -> str:
        tokens = callee.strip().split()
        if not tokens or (len(tokens) >= _PROSE_TOKENS and _PROSE.search(callee)):
            return ""
        head, arguments = tokens[0], ", ".join(tokens[1:])
        end = self._spelling.statement_end
        if head == "super" or head.startswith("super."):
            return self._super_call(head[len("super."):], arguments) + end
        if "." not in head and head[0].isupper() and _IDENTIFIER.match(head):
            target = self.identifier(tokens[1] if len(tokens) > 1 else head)
            created = self._spelling.construct.format(type=head, arguments=arguments)
            return f"{self._spelling.receiver}.{target} = {created}{end}"
        return f"{head}({arguments}){end}"

    def assignment(self, name: str) -> str:
        field = self.identifier(name)
        return f"{self._spelling.receiver}.{field} = {field}{self._spelling.statement_end}"

    def _super_call(self, member: str, arguments: str) -> str:
        if not member or member[0].isupper():
            return f"{self._spelling.base_constructor}({arguments})"
        return f"{self._spelling.base_receiver}.{member}({arguments})"


class CodeBody:
    """The statements inside one operation, test, or step, kept with the language they were read in."""

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
        note = [f"{indent}{language.comment(f'{self.language.name} body to translate:')}"]
        original = [f"{indent}{language.comment(line)}" for line in self.text.splitlines()]
        return note + original + marker

    def in_language_of(self, other: "CodeBody", language: CodeLanguage) -> "CodeBody":
        if self.language is language or other.language is not language:
            return self
        return other


WrittenKey = Union[str, Tuple, None]
# What a node says in code when it is read: a name, or a tuple of names, steps, and bodies.


class WrittenBlock:
    """The source lines around one block of code that no node holds, kept exactly as read.

    A BDD describe, context, or it, a story, scenario, or step chain: the language writes these lines back
    unchanged while the node still has the key it was read with."""

    def __init__(self, language: CodeLanguage, key: WrittenKey, lead: List[str], heading: List[str]) -> None:
        self.language = language
        self.key = key
        self.path = ""
        self.lead = lead
        self.heading = heading
        self.inside: List[str] = []
        self.inline = ""
        self.closing: List[str] = []
        self.close: List[str] = []

    def is_in(self, language: CodeLanguage, key: WrittenKey) -> bool:
        return self.language is language and self.key == key

    @staticmethod
    def split_inside(lines: List[str], inside: Tuple[int, int], children: List[Tuple[int, int]]) -> Tuple[List[str], List[List[str]], List[str]]:
        """The lines inside one block as (setup, the lines above each child, the lines after the last child).
        Blank lines right above the first child belong to it; with no child they close the block."""
        start, end = inside
        region = lines[start : children[0][0]] if children else lines[start:end]
        kept = len(region)
        while kept and not region[kept - 1].strip():
            kept -= 1
        if not children:
            return region[:kept], [], region[kept:]
        leads = [region[kept:]] + [lines[previous[1] + 1 : child[0]] for previous, child in zip(children, children[1:])]
        return region[:kept], leads, lines[children[-1][1] + 1 : end]

    def inside_for(self, body: CodeBody) -> List[str] | None:
        """The setup or test body lines exactly as read, while the model's body still says the same.
        A block written on one line keeps its body in the heading, so it has no inside lines."""
        as_read = CodeBody(self.inline or "\n".join(self.inside), self.language)
        return self.inside if as_read.text == body.text else None

    def lead_body(self) -> CodeBody:
        return CodeBody("\n".join(self.lead), self.language)

    def closing_body(self) -> CodeBody:
        return CodeBody("\n".join(self.closing), self.language)


PYTHON_SPELLING = CodeSpelling(
    receiver="self",
    construct="{type}({arguments})",
    statement_end="",
    camel_case=False,
    base_call=("super().__init__", "super()"),
)
C_FAMILY_SPELLING = CodeSpelling(receiver="this", construct="new {type}({arguments})", statement_end=";", camel_case=True)

PYTHON = CodeLanguage(
    "python",
    "#",
    "    ",
    "raise NotImplementedError",
    PYTHON_SPELLING,
    type_names={},
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
    },
)
JAVASCRIPT = CodeLanguage(
    "javascript",
    "//",
    "  ",
    'throw new Error("not implemented");',
    C_FAMILY_SPELLING,
    type_names={},
)
JAVA = CodeLanguage(
    "java",
    "//",
    "    ",
    'throw new UnsupportedOperationException("not implemented");',
    C_FAMILY_SPELLING,
    type_names={
        "str": "String",
        "int": "int",
        "float": "double",
        "bool": "boolean",
        "None": "void",
        "list": "List<?>",
        "dict": "Map<String, Object>",
        "object": "Object",
    },
)
