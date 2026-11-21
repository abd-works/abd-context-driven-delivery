"""A front-end view, the production screen the front-end code fidelity writes (`*View.tsx`, `*View.jsx`), and the two
formats that render it: TypeScript and JavaScript.

A view is rendered between the two by its text. To JavaScript, every type annotation is dropped: interfaces, type
aliases, type-only imports, the types of parameters, variables and results, type arguments, `as` casts, and non-null
marks. To TypeScript, a view written in JavaScript is kept as it is: JavaScript is TypeScript with no annotation, and
none is made up for it. The view's components, the props each takes, and its handlers are read from its text, and stay
the same through both renders.

Only code is changed: the words a screen shows, strings, comments, and tags are read apart from the code first
(*ViewText*), so `<p>Total: {total}</p>` is never taken for an annotation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property

# What stands for each character that is not code, where the code is searched.
_NOT_CODE = "\0"
_OPENERS = {"(": ")", "[": "]", "{": "}", "<": ">"}
_CLOSERS = frozenset(_OPENERS.values())
# What may come before a `<` that opens a tag: the start of an expression. After a name or a closing bracket, `<` is a
# comparison or opens type arguments.
_BEFORE_TAG = frozenset("(,=:?[{};&|>!")
_WORDS_BEFORE_TAG = ("return", "default", "yield")
_IDENTIFIER = re.compile(r"[A-Za-z_$][\w$]*")
# Declarations that have no JavaScript once their type is dropped; a view that holds one is not converted.
_NOT_CONVERTED = re.compile(
    r"^[ \t]*(?:export[ \t]+)?(?:declare[ \t]+)?(?:const[ \t]+)?(?P<construct>(?:enum|namespace)[ \t]+[\w$]+)"
    r"|^[ \t]*(?P<member>(?:abstract|declare)[ \t]+[\w$]+)"
    r"|\bconstructor[ \t]*\([^)]*?\b(?P<parameter>(?:(?:private|protected|public|readonly)[ \t]+)+[\w$]+)",
    re.MULTILINE,
)
_CLASS = re.compile(r"(?<![\w$.])class[ \t]+[\w$]+")
_IMPLEMENTS = re.compile(r"[ \t]+implements\b[^{]*")
# What a class writes before a member's name only for its type: who may reach it, and whether it may change.
_MEMBER_MODIFIERS = re.compile(r"(?:(?:private|protected|public|readonly|override)[ \t]+)+")
_FIELD = re.compile(r"[ \t]*(?:static[ \t]+)?(?P<name>[\w$]+)(?P<mark>[?!]?)[ \t]*:")
# The name written straight before a method's parameters, and the words that are a statement's there, not a name.
_METHOD_NAME = re.compile(r"(?<![\w$.])(?P<name>[\w$]+)$")
_NOT_A_METHOD = frozenset({
    "if", "for", "while", "switch", "catch", "with", "function",
    "async", "return", "await", "yield", "of", "in", "case", "default", "void", "typeof", "else", "throw", "new", "delete",
})
_INTERFACE = re.compile(r"^[ \t]*(?:export[ \t]+)?(?:declare[ \t]+)?interface\b[^{\n]*\{", re.MULTILINE)
_TYPE_ALIAS = re.compile(r"^[ \t]*(?:export[ \t]+)?(?:declare[ \t]+)?type[ \t]+[\w$]+[^=\n]*=", re.MULTILINE)
_TYPE_ONLY_STATEMENT = re.compile(r"^[ \t]*(?:import[ \t]+type\b|export[ \t]+type[ \t]*\{)", re.MULTILINE)
_IMPORT = re.compile(r"^[ \t]*import\b", re.MULTILINE)
_REEXPORT = re.compile(r"^[ \t]*export[ \t]*[{*]", re.MULTILINE)
_DECLARATION = re.compile(r"\b(?:const|let|var)[ \t]+")
_TYPE_ARGUMENTS = re.compile(r"(?<=[\w$])<")
_CAST = re.compile(r"[ \t]+(?:as|satisfies)[ \t]+(?=[A-Za-z_{(\[])")
_NON_NULL = re.compile(r"(?<=[\w$)\]])!(?=[.)\];,\s\[(])")
_SPECIFIER = re.compile(r"^(?P<type>type\s+)?(?P<name>[\w$]+)(?:\s+as\s+(?P<alias>[\w$]+))?$")
_FUNCTION_COMPONENT = re.compile(r"^(?:export[ \t]+)?(?:default[ \t]+)?(?:async[ \t]+)?function[ \t]+(?P<name>[A-Z][\w$]*)[^(\n]*\(", re.MULTILINE)
_ARROW_COMPONENT = re.compile(r"^(?:export[ \t]+)?const[ \t]+(?P<name>[A-Z][\w$]*)[^=\n]*=[ \t]*(?:async[ \t]*)?\(", re.MULTILINE)
_EVENT_ATTRIBUTE = re.compile(r"\b(?P<event>on[A-Z]\w*)=\{")
_HANDLER_NAME = re.compile(r"\s*(?P<name>[\w$.]+)\s*\}")


class ViewSyntaxNotConverted(ValueError):
    """A view was rendered to JavaScript, and it declares something that has no JavaScript once its type is dropped,
    such as an enum; the view is left as it is rather than written without it."""

    def __init__(self, construct: str) -> None:
        super().__init__(f"The view declares `{construct}`, which has no JavaScript once its types are dropped; write it as plain values first.")
        self.construct = construct


class ViewText:
    """A view's text with its code told apart from what a screen shows: strings, comments, template text, tags, and
    the words between tags are not code; the expressions in braces among them are."""

    def __init__(self, text: str) -> None:
        self.text = text
        self._is_code = [False] * len(text)
        self._is_tag = [False] * len(text)
        self._is_string = [False] * len(text)
        self._read_code(0, "")

    @cached_property
    def code(self) -> str:
        """The text with every character that is not code blanked, and its lines kept, so a place found in it is the
        same place in the text."""
        return "".join(
            character if is_code or character == "\n" else _NOT_CODE
            for character, is_code in zip(self.text, self._is_code)
        )

    @cached_property
    def names(self) -> str:
        """The text with everything but its code and its tags blanked: where a name the view uses can be written, as
        a string, a comment, and the words a screen shows cannot."""
        return "".join(
            character if is_code or is_tag or character == "\n" else _NOT_CODE
            for character, is_code, is_tag in zip(self.text, self._is_code, self._is_tag)
        )

    def is_code_at(self, position: int) -> bool:
        return self._is_code[position]

    def is_string_at(self, position: int) -> bool:
        """Whether the character at position is part of a string in quotes, which a type may be written with."""
        return self._is_string[position]

    def closing(self, opening: int) -> int:
        """The place of the bracket that closes the one at opening; the end of the code when none does."""
        code = self.code
        opener = code[opening]
        closer, depth = _OPENERS[opener], 0
        for position in range(opening, len(code)):
            character = code[position]
            closes = character == closer and not (closer == ">" and code[position - 1] == "=")
            depth += (character == opener) - closes
            if closes and depth == 0:
                return position
        return len(code) - 1

    def past_space(self, position: int) -> int:
        """position moved on over the blanks and line ends after it."""
        code = self.code
        while position < len(code) and code[position].isspace():
            position += 1
        return position

    def _read_code(self, position: int, closer: str) -> int:
        """Mark the code from position on, up to the brace that closes it when closer names one; answers the place
        after it."""
        text, depth = self.text, 0
        while position < len(text):
            after = self._after_what_is_not_code(position)
            if after:
                position = after
                continue
            character = text[position]
            self._is_code[position] = True
            position += 1
            if closer and character == closer and depth == 0:
                return position
            depth += (character == "{") - (character == "}") if closer else 0
        return position

    def _after_what_is_not_code(self, position: int) -> int:
        """The place after the string, template, comment, or element that starts at position; 0 when code does."""
        text, character = self.text, self.text[position]
        if character in "\"'":
            return self._after_string(position)
        if character == "`":
            return self._read_template(position)
        if text.startswith("//", position):
            return self._found(text.find("\n", position))
        if text.startswith("/*", position):
            return self._found(text.find("*/", position), 2)
        if character == "<" and self._opens_tag(position):
            return self._read_element(position)
        return 0

    def _after_expression(self, position: int) -> int:
        """The place after the expression in braces that opens at position, read as code; 0 when none opens there."""
        if self.text[position] != "{":
            return 0
        self._is_code[position] = True
        return self._read_code(position + 1, "}")

    def _found(self, place: int, length: int = 0) -> int:
        return len(self.text) if place < 0 else place + length

    def _after_string(self, position: int) -> int:
        quote, text, start = self.text[position], self.text, position
        position += 1
        while position < len(text) and text[position] not in (quote, "\n"):
            position += 2 if text[position] == "\\" else 1
        end = min(position + 1, len(text))
        self._is_string[start:end] = [True] * (end - start)
        return end

    def _read_template(self, position: int) -> int:
        text = self.text
        position += 1
        while position < len(text) and text[position] != "`":
            if not text.startswith("${", position):
                position += 2 if text[position] == "\\" else 1
                continue
            self._is_code[position] = True
            position = self._after_expression(position + 1)
        return min(position + 1, len(text))

    def _opens_tag(self, position: int) -> bool:
        """Whether the `<` at position opens a tag: a name or `>` follows it, an expression may start there, and what
        follows the name is not a type parameter's comma or `extends`."""
        text = self.text
        named = _IDENTIFIER.match(text, position + 1)
        if named is None:
            return text.startswith(">", position + 1)
        rest = text[named.end():].lstrip()
        if rest.startswith(",") or rest.startswith("extends "):
            return False
        before = text[:position].rstrip()
        return not before or before[-1] in _BEFORE_TAG or before.endswith(_WORDS_BEFORE_TAG)

    def _read_element(self, position: int) -> int:
        """Read the element whose tag opens at position: its tag, with the expressions among its attributes, then what
        it holds; answers the place after its closing tag."""
        text = self.text
        position += 1
        while position < len(text):
            character = text[position]
            if text.startswith("/>", position):
                return position + 2
            if character == ">":
                return self._read_children(position + 1)
            held = self._after_string(position) if character in "\"'" else self._after_expression(position)
            self._is_tag[position] = not held
            position = held or position + 1
        return position

    def _read_children(self, position: int) -> int:
        text = self.text
        while position < len(text):
            if text.startswith("</", position):
                end = self._found(text.find(">", position), 1)
                self._is_tag[position + 2:end - 1] = [True] * max(0, end - position - 3)
                return end
            element = self._read_element(position) if text[position] == "<" else 0
            position = element or self._after_expression(position) or position + 1
        return position


@dataclass(frozen=True)
class Edit:
    """One change to a view's text: the characters from start up to end become replacement."""

    start: int
    end: int
    replacement: str = ""


class TypeAnnotations:
    """The type annotations of one view written in TypeScript, as the edits that drop them from its text."""

    def __init__(self, view: ViewText) -> None:
        self._view = view
        self._text = view.text
        self._code = view.code

    def dropped(self) -> str:
        """The view's text with every annotation dropped; a view that declares what has no JavaScript without its
        type is refused as *ViewSyntaxNotConverted*."""
        refused = _NOT_CONVERTED.search(self._code)
        if refused is not None:
            raise ViewSyntaxNotConverted(refused.group("construct") or refused.group("member") or refused.group("parameter"))
        removed = self._merged([
            *self._type_statements(), *self._function_annotations(), *self._declaration_annotations(),
            *self._class_annotations(), *self._type_arguments(), *self._casts(), *self._non_null_marks(),
        ])
        edits = sorted([*removed, *self._import_edits(removed)], key=lambda edit: edit.start)
        text, last = [], 0
        for edit in edits:
            if edit.start < last:
                continue
            text.extend([self._text[last:edit.start], edit.replacement])
            last = edit.end
        return "".join([*text, self._text[last:]])

    def _merged(self, edits: list[Edit]) -> list[Edit]:
        """The removals with those that overlap joined into one."""
        merged: list[Edit] = []
        for edit in sorted(edits, key=lambda edit: (edit.start, -edit.end)):
            if merged and edit.start <= merged[-1].end:
                merged[-1] = Edit(merged[-1].start, max(merged[-1].end, edit.end))
            else:
                merged.append(edit)
        return merged

    # -- whole statements -------------------------------------------------------------------------------------------

    def _type_statements(self) -> list[Edit]:
        """Each interface, type alias, and type-only import or export, with the blank lines after one that stands
        apart, so dropping it leaves no gap."""
        code, found = self._code, []
        for interface in _INTERFACE.finditer(code):
            found.append(self._statement(interface.start(), self._view.closing(interface.end() - 1) + 1))
        for alias in _TYPE_ALIAS.finditer(code):
            found.append(self._statement(alias.start(), self._alias_end(alias.end())))
        for statement in _TYPE_ONLY_STATEMENT.finditer(code):
            found.append(self._statement(statement.start(), self._statement_end(statement.end())))
        return found

    def _statement(self, start: int, end: int) -> Edit:
        """The statement from start to end as a removal: through its semicolon and the end of its line, and through
        the blank lines after it when a blank line or the start of the file comes before it."""
        text = self._text
        line_end = re.compile(r"[ \t]*;?[ \t]*\n?").match(text, end).end()
        stands_apart = start == 0 or text[:start].endswith("\n\n")
        if stands_apart:
            line_end = re.compile(r"(?:[ \t]*\n)*").match(text, line_end).end()
        return Edit(start, line_end)

    def _alias_end(self, position: int) -> int:
        """Where the type alias whose `=` ends at position ends: at its semicolon, or at the end of the line its type
        ends on, since a union goes on over lines that start with `|`."""
        code = self._code
        while True:
            end = self._type_end(position, frozenset(";\n"))
            if end >= len(code) or code[end] == ";":
                return end
            ahead = code[end:].lstrip()
            behind = code[:end].rstrip(" \t" + _NOT_CODE)
            if ahead[:1] in ("|", "&") or behind[-1:] in ("|", "&", "="):
                position = end + 1
                continue
            return end

    def _statement_end(self, position: int) -> int:
        """Where the statement that holds position ends: its semicolon, or the end of its line, outside any brace."""
        code, depth = self._code, 0
        while position < len(code):
            character = code[position]
            if depth == 0 and character in ";\n":
                return position
            depth += (character == "{") - (character == "}")
            position += 1
        return position

    # -- functions --------------------------------------------------------------------------------------------------

    def _function_annotations(self) -> list[Edit]:
        """The annotations of each function's parameters, its result, and its type parameters."""
        code, found = self._code, []
        for opening in (place for place, character in enumerate(code) if character == "("):
            closing = self._view.closing(opening)
            result = self._result_annotation(opening, closing)
            if result is None:
                continue
            found.extend([*result, *self._parameter_annotations(opening, closing), *self._type_parameters(opening)])
        return found

    def _result_annotation(self, opening: int, closing: int) -> list[Edit] | None:
        """The annotation of the result of the function whose parameters sit between opening and closing; none when
        the brackets hold no function's parameters. A function declared with `function`, and a method, has its body
        in braces after its parameters; any other function is followed by `=>`, and its brackets follow no name and no
        closing bracket, which would make them a call's."""
        code = self._code
        after = self._view.past_space(closing + 1)
        annotated = code[after:after + 1] == ":"
        if self._is_declared_function(opening) or self._is_method(opening):
            end = self._type_end(after + 1, frozenset("{;\n")) if annotated else after
            return self._result_before("{", after, end)
        if code[:opening].rstrip()[-1:] in (")", "]"):
            return None
        end = self._type_end(after + 1, frozenset({"=>", ";", "\n", ","})) if annotated else after
        return self._result_before("=>", after, end)

    def _result_before(self, body_mark: str, after: int, end: int) -> list[Edit] | None:
        """The removal of the result's annotation between after and end, when the function's body_mark follows it;
        none when it does not, so the brackets were no function's."""
        if not self._code.startswith(body_mark, end):
            return None
        return [Edit(after, self._before_space(end))] if end > after else []

    def _is_declared_function(self, opening: int) -> bool:
        """Whether the `(` at opening follows `function`, with or without a name and type parameters."""
        before = self._code[:opening].rstrip()
        if before.endswith(">") and not before.endswith("=>"):
            before = before[:self._opening_angle(len(before) - 1)].rstrip()
        return re.search(r"\bfunction(?:[ \t]+[\w$]+)?$", before) is not None

    def _is_method(self, opening: int) -> bool:
        """Whether the `(` at opening follows a method's name, in a class or in an object: a name that is no
        statement's keyword. Only a method's brackets are followed by the brace of a body, which the caller checks."""
        before = self._code[:opening].rstrip(" \t")
        if before.endswith(">") and not before.endswith("=>"):
            before = before[:self._opening_angle(len(before) - 1)].rstrip(" \t")
        named = _METHOD_NAME.search(before[before.rfind("\n") + 1:])
        return named is not None and named.group("name") not in _NOT_A_METHOD

    def _parameter_annotations(self, opening: int, closing: int) -> list[Edit]:
        """The `: Type` after each parameter between opening and closing, and the `?` of an optional one. A default
        value and what a parameter takes apart in braces are left as they are."""
        code, found, position, in_default = self._code, [], opening + 1, False
        while position < closing:
            character = code[position]
            if character in _OPENERS and character != "<":
                position = self._view.closing(position) + 1
                continue
            if character == "," or (character == "=" and not in_default):
                in_default, position = character == "=", position + 1
                continue
            if character not in "?:" or in_default:
                position += 1
                continue
            end = min(self._parameter_annotation_end(position), closing)
            found.append(Edit(position, self._before_space(end)))
            position = end
        return found

    def _parameter_annotation_end(self, position: int) -> int:
        """Where the annotation that starts at position, with a parameter's `?` or its `:`, ends."""
        code = self._code
        colon = self._view.past_space(position + 1) if code[position] == "?" else position
        return self._type_end(colon + 1, frozenset(",=")) if code[colon:colon + 1] == ":" else position + 1

    def _type_parameters(self, opening: int) -> list[Edit]:
        """The `<T>` written straight before a function's parameters."""
        before = len(self._code[:opening].rstrip())
        if before == 0 or self._code[before - 1] != ">" or self._code[before - 2:before] == "=>":
            return []
        return [Edit(self._opening_angle(before - 1), before)]

    # -- classes ----------------------------------------------------------------------------------------------------

    def _class_annotations(self) -> list[Edit]:
        """What a class writes only for its types: the type arguments and type parameters of its heading, what it
        `implements`, and, on each member, the words that say who may reach it and the `: Type` after a field's name."""
        code, found = self._code, []
        for heading in _CLASS.finditer(code):
            opening = self._body_opening(heading.end())
            implemented = _IMPLEMENTS.search(code, heading.start(), opening)
            if implemented is not None:
                found.append(Edit(implemented.start(), self._before_space(opening)))
            for angle in (place for place in range(heading.start(), opening) if code[place] == "<"):
                found.append(Edit(angle, self._view.closing(angle) + 1))
            found.extend(self._member_annotations(opening, self._view.closing(opening)))
        return found

    def _body_opening(self, position: int) -> int:
        """The place of the brace that opens the body of the class whose heading goes on from position: the first
        brace outside the heading's type arguments, which may themselves be written in braces."""
        code = self._code
        while position < len(code) - 1 and code[position] != "{":
            position = self._view.closing(position) + 1 if code[position] == "<" else position + 1
        return position

    def _member_annotations(self, opening: int, closing: int) -> list[Edit]:
        """The annotations of the members written between a class's braces, each where a line of the class's own
        starts; lines inside a member's brackets are that member's code."""
        code, found, depth = self._code, [], 0
        for position in range(opening + 1, closing):
            character = code[position]
            depth += (character in "([{") - (character in ")]}")
            if character != "\n" or depth != 0:
                continue
            start = self._past_blank(position + 1)
            modifiers = _MEMBER_MODIFIERS.match(code, start)
            if modifiers is not None:
                found.append(Edit(start, modifiers.end()))
                start = modifiers.end()
            field = _FIELD.match(code, start)
            if field is not None:
                end = self._type_end(field.end(), frozenset("=;\n"))
                found.append(Edit(field.end("name"), self._before_space(end)))
        return found

    def _past_blank(self, position: int) -> int:
        while position < len(self._code) and self._code[position] in " \t":
            position += 1
        return position

    # -- variables, type arguments, casts ---------------------------------------------------------------------------

    def _declaration_annotations(self) -> list[Edit]:
        """The `: Type` after the name a `const`, `let`, or `var` declares."""
        code, found = self._code, []
        for declaration in _DECLARATION.finditer(code):
            position = declaration.end()
            named = _IDENTIFIER.match(code, position)
            if code[position:position + 1] in ("[", "{"):
                position = self._view.closing(position) + 1
            elif named is not None:
                position = named.end()
            colon = self._view.past_space(position)
            if code[colon:colon + 1] == ":":
                found.append(Edit(position, self._before_space(self._type_end(colon + 1, frozenset("=;\n,")))))
        return found

    def _type_arguments(self) -> list[Edit]:
        """The `<Type>` between a function's name and the brackets of a call to it, as in `useState<string>("")`."""
        code, found = self._code, []
        for opening in _TYPE_ARGUMENTS.finditer(code):
            closing = self._view.closing(opening.start())
            held = code[opening.start():closing]
            if code[closing + 1:closing + 2] == "(" and not any(mark in held for mark in ("&&", "||")):
                found.append(Edit(opening.start(), closing + 1))
        return found

    def _casts(self) -> list[Edit]:
        """Each `as Type` and `satisfies Type` after an expression; the `as` of an import or an export names, and stays."""
        code = self._code
        naming = [(start.start(), self._statement_end(start.end())) for pattern in (_IMPORT, _REEXPORT) for start in pattern.finditer(code)]
        found = []
        for cast in _CAST.finditer(code):
            if not any(start <= cast.start() < end for start, end in naming):
                found.append(Edit(cast.start(), self._before_space(self._type_end(cast.end(), frozenset(",;\n?:=")))))
        return found

    def _non_null_marks(self) -> list[Edit]:
        return [Edit(mark.start(), mark.end()) for mark in _NON_NULL.finditer(self._code)]

    # -- imports ----------------------------------------------------------------------------------------------------

    def _import_edits(self, removed: list[Edit]) -> list[Edit]:
        """Each import with the names it imports only for types taken out of its braces: a name marked `type`, and a
        name the view used only in the annotations that are dropped. An import left with no name goes whole."""
        code, text, found = self._code, self._text, []
        statements = [(start.start(), self._statement_end(start.end())) for start in _IMPORT.finditer(code)]
        statements = [(start, end) for start, end in statements if not any(edit.start <= start < edit.end for edit in removed)]
        dropped = " ".join(text[edit.start:edit.end] for edit in removed)
        kept = self._names_without([*removed, *(Edit(start, end) for start, end in statements)])
        for start, end in statements:
            brace = code.find("{", start, end)
            if brace < 0:
                continue
            braces = Edit(brace, self._view.closing(brace) + 1)
            names = [name.strip() for name in text[brace + 1:braces.end - 1].split(",") if name.strip()]
            staying = [name for name in names if self._stays(name, dropped, kept)]
            if len(staying) < len(names):
                found.append(self._import_edit(Edit(start, end), braces, staying))
        return found

    def _stays(self, specifier: str, dropped: str, kept: str) -> bool:
        """Whether an imported name stays: it is not marked `type`, and the view uses it outside the annotations that
        are dropped, or never used it in one."""
        named = _SPECIFIER.match(specifier)
        if named is None:
            return True
        local = re.compile(rf"(?<![\w$.]){re.escape(named.group('alias') or named.group('name'))}(?![\w$])")
        return not named.group("type") and (local.search(kept) is not None or local.search(dropped) is None)

    def _import_edit(self, statement: Edit, braces: Edit, staying: list[str]) -> Edit:
        """The change to one import statement whose braces keep only the names staying: the braces rewritten, or,
        with no name left, the braces gone after a default import, else the whole statement gone."""
        if staying:
            return Edit(braces.start, braces.end, "{ " + ", ".join(staying) + " }")
        before = self._text[statement.start:braces.start].rstrip()
        if before.endswith(","):
            return Edit(statement.start + len(before) - 1, braces.end, "")
        return self._statement(statement.start, statement.end)

    def _names_without(self, edits: list[Edit]) -> str:
        """The view's code and tags outside edits: where a name that stays in the view is used."""
        names, kept, last = self._view.names, [], 0
        for edit in sorted(edits, key=lambda edit: edit.start):
            kept.append(names[last:max(last, edit.start)])
            last = max(last, edit.end)
        return " ".join([*kept, names[last:]])

    # -- reading brackets and types ---------------------------------------------------------------------------------

    def _opening_angle(self, closing: int) -> int:
        """The place of the `<` that the `>` at closing closes."""
        code, depth = self._code, 0
        for position in range(closing, -1, -1):
            opens = code[position] == "<"
            depth += (code[position] == ">" and code[position - 1:position] != "=") - opens
            if opens and depth == 0:
                return position
        return 0

    def _type_end(self, position: int, stops: frozenset[str]) -> int:
        """Where the type that starts at position ends: at the first of stops outside the type's own brackets, at
        the bracket that closes what holds the type, or at a tag or a comment, which no type is written with. A `{`
        is a stop only once the type has words before it, since a type may itself be written in braces; a `=>` that is
        no stop belongs to a function's type."""
        code, written = self._code, False
        while position < len(code):
            if self._ends_type(position, stops, written):
                return position
            if code.startswith("=>", position):
                position += 2
                continue
            if code[position] in _OPENERS:
                position, written = self._view.closing(position) + 1, True
                continue
            written = written or not code[position].isspace()
            position += 1
        return position

    def _ends_type(self, position: int, stops: frozenset[str], written: bool) -> bool:
        """Whether the type being read ends at position, with or without words written so far."""
        code, character = self._code, self._code[position]
        if character == _NOT_CODE:
            return not self._view.is_string_at(position)
        if code.startswith("=>", position):
            return "=>" in stops
        if character in stops:
            return character != "{" or self._is_whole_type(code[:position], written)
        return character in _CLOSERS

    def _is_whole_type(self, before: str, written: bool) -> bool:
        """Whether the type written so far can end here: it has words, and the last of them is no operator that
        needs another type after it."""
        return written and before.rstrip()[-1:] not in ("|", "&", ":", ",", "<", "(", "=")

    def _before_space(self, position: int) -> int:
        """position moved back over the blanks before it, so the blank between what stays on either side is kept."""
        while position > 0 and self._code[position - 1] in " \t":
            position -= 1
        return position


class FrontEndView:
    """One front-end view: its text, whether that text is written with types, and what is read from it: its
    components, the props each takes, and its handlers."""

    def __init__(self, text: str, typed: bool) -> None:
        self.text = text
        self.typed = typed
        self._view = ViewText(text)

    def semantic_type(self) -> str:
        return "FrontEndView"

    @property
    def without_types(self) -> str:
        """The view as JavaScript: its own text when it is written without types, else its text with every type
        annotation dropped."""
        return TypeAnnotations(self._view).dropped() if self.typed else self.text

    @property
    def components(self) -> list[str]:
        """The name of each component the view declares, in the order it declares them."""
        return [name for name, _parameters in self._declared_components()]

    @property
    def props(self) -> dict[str, list[str]]:
        """The props each component takes: the names it takes apart in its parameter, or, for a component that takes
        its props whole, each one it reads from them."""
        return {name: self._props_of(parameters) for name, parameters in self._declared_components()}

    @property
    def handlers(self) -> list[str]:
        """What each event of the view is handed, once each: the name of the function, or, for a function written in
        place, the event itself."""
        found: list[str] = []
        for attribute in _EVENT_ATTRIBUTE.finditer(self.text):
            if self._view.is_code_at(attribute.start()):
                continue
            named = _HANDLER_NAME.match(self.text, attribute.end())
            handler = named.group("name") if named is not None else attribute.group("event")
            if handler not in found:
                found.append(handler)
        return found

    def _declared_components(self) -> list[tuple[str, int]]:
        """Each component's name with the place its parameters open, in the order of the text."""
        code = self._view.code
        found = [(match.start(), match.group("name"), match.end() - 1) for pattern in (_FUNCTION_COMPONENT, _ARROW_COMPONENT) for match in pattern.finditer(code)]
        return [(name, opening) for _start, name, opening in sorted(found)]

    def _props_of(self, opening: int) -> list[str]:
        code = self._view.code
        inner = self._view.past_space(opening + 1)
        if code[inner:inner + 1] == "{":
            taken = self._top_level_parts(code[inner + 1:self._view.closing(inner)])
            return [re.split(r"[:=]", part, 1)[0].strip().lstrip(".") for part in taken if part.strip()]
        whole = _IDENTIFIER.match(code, inner)
        if whole is None:
            return []
        following = [start for _name, start in self._declared_components() if start > opening]
        body = code[opening:following[0] if following else len(code)]
        read: list[str] = []
        for prop in re.finditer(rf"(?<![\w$.]){re.escape(whole.group())}\.([\w$]+)", body):
            if prop.group(1) not in read:
                read.append(prop.group(1))
        return read

    def _top_level_parts(self, held: str) -> list[str]:
        """What held lists between its commas, leaving the commas inside brackets alone."""
        parts, depth, start = [], 0, 0
        for position, character in enumerate(held):
            depth += (character in "([{") - (character in ")]}")
            if character == "," and depth == 0:
                parts.append(held[start:position])
                start = position + 1
        return [*parts, held[start:]]


class TypeScriptView:
    """The ``typescript`` format of a front-end view: it reads a view written with types, and writes a view as
    TypeScript, which for a view read from JavaScript is that JavaScript as it is."""

    def parse(self, content: str) -> FrontEndView:
        return FrontEndView(content or "", typed=True)

    def render(self, view: FrontEndView) -> str:
        return view.text


class JavaScriptView:
    """The ``javascript`` format of a front-end view: it reads a view written without types, and writes a view as
    JavaScript, its type annotations dropped."""

    def parse(self, content: str) -> FrontEndView:
        return FrontEndView(content or "", typed=False)

    def render(self, view: FrontEndView) -> str:
        return view.without_types
