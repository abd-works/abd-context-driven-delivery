"""Where a bracket of source text closes, and what a function a module's text declares writes: the return type its
signature names and its body, in Python or a script language. The call resolver reads a function this way where no
class model holds it, such as one declared inside a block."""
import re
from functools import lru_cache

_PYTHON_DEF = r"(?m)^([ \t]*)(?:async[ \t]+)?def[ \t]+{name}[ \t]*\("
_SCRIPT_FUNCTION = r"(?<![\w$.])(?:function\s*\*?\s*{name}\s*(?:<[^>()]*>)?\s*|(?:const|let|var)\s+{name}\s*=\s*(?:async\s*)?)\("
_SIGNATURE_END = re.compile(r"[ \t]*(?:->[ \t]*([^:\n]+?))?[ \t]*:")
_QUOTES = frozenset("'\"`")


@lru_cache(maxsize=None)
def named_pattern(template: str, name: str) -> re.Pattern:
    """The pattern template writes for name, its ``{name}`` the name escaped, compiled once: a read of the whole working
    copy searches for thousands of names, more than the regular expression module keeps compiled."""
    return re.compile(template.format(name=re.escape(name)))


def closing_bracket(code: str, opening: int) -> "int | None":
    """Where the bracket that opens at opening closes, skipping strings; none when it does not close."""
    depth = 0
    position = opening
    quote = ""
    while position < len(code):
        character = code[position]
        if quote:
            if character == "\\":
                position += 1
            elif character == quote:
                quote = ""
        elif character in _QUOTES:
            quote = character
        elif character in "([{":
            depth += 1
        elif character in ")]}":
            depth -= 1
            if depth == 0:
                return position
        position += 1
    return None


def python_function(text: str, name: str) -> "tuple[str, str] | None":
    """The return type a Python function's signature writes, and its body's lines."""
    declared = named_pattern(_PYTHON_DEF, name).search(text)
    closing = closing_bracket(text, declared.end() - 1) if declared else None
    signature = _SIGNATURE_END.match(text, closing + 1) if closing is not None else None
    if signature is None:
        return None
    indent = len(declared.group(1))
    body = []
    for line in text[signature.end():].splitlines()[1:]:
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        body.append(line)
    return (signature.group(1) or "").strip(), "\n".join(body)


def script_function(text: str, name: str) -> "tuple[str, str] | None":
    """The return type a script function's signature writes, `function opened(): Promise<{ page: FilesPage }> {` or
    `const opened = async (): Promise<Page> => {`, and its body's block."""
    declared = named_pattern(_SCRIPT_FUNCTION, name).search(text)
    closing = closing_bracket(text, declared.end() - 1) if declared else None
    if closing is None:
        return None
    position = _past(text, closing + 1, " \t")
    hint = ""
    if text[position:position + 1] == ":":
        hint, position = _script_return_type(text, position + 1)
    arrow = re.match(r"\s*=>\s*", text[position:])
    if arrow is not None:
        position += arrow.end()
    position = _past(text, position, " \t\n")
    if text[position:position + 1] != "{":
        return hint, ("return " + text[position:text.find("\n", position)]) if arrow is not None else ""
    body_end = closing_bracket(text, position)
    return hint, text[position + 1:body_end] if body_end is not None else ""


def _past(text: str, position: int, spaces: str) -> int:
    """The first position from position whose character is none of spaces."""
    while position < len(text) and text[position] in spaces:
        position += 1
    return position


def _script_return_type(text: str, start: int) -> "tuple[str, int]":
    """The return type written from start, up to the body's brace or arrow: an object type's braces are part of it."""
    depth = 0
    position = start
    while position < len(text):
        if depth == 0 and _type_ends_at(text, start, position):
            break
        depth += _depth_change(text, position)
        position += 1
    return text[start:position].strip(), position


def _type_ends_at(text: str, start: int, position: int) -> bool:
    """Whether a return type written from start ends at position, outside any bracket: at an arrow, or at a brace
    that opens the body rather than an object type, since the type before it is complete."""
    if text.startswith("=>", position):
        return True
    if text[position] != "{":
        return False
    written = text[start:position].strip()
    return bool(written) and not written.endswith(("|", "&", ":", "<", ","))


def _depth_change(text: str, position: int) -> int:
    """How the bracket at position changes the depth of a return type: one deeper for an opening one, one shallower
    for a closing one, where the `>` of an arrow `=>` closes nothing."""
    character = text[position]
    if character in "<({[":
        return 1
    if character in ")}]" or (character == ">" and text[position - 1] != "="):
        return -1
    return 0
