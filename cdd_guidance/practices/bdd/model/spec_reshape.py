"""A rendered describe tree written onto a spec file that is already there: the file takes the tree's shape and keeps
every line it holds.

A spec holds what its describe tree does not: test bodies, setup (``before.each``, ``beforeEach``), helpers, imports,
comments. So the tree is never written over the file. Blocks are matched by the names of the description, the contexts
and the observation they sit under:

- A block both hold stays exactly as the file has it, with its body, its setup and the comments above it.
- A block the tree gained is added as the render wrote it, an observation with its ``BDD: SIGNATURE`` marker, at the end
  of the block it sits in; a description the file lacks is added after the ones it holds.
- A block the tree lost stays where it is, under a line saying it is no longer in the model, until whoever migrates
  moves what it proves into the block that replaced it and deletes it.

Everything else in the file is left where it was, since the only changes made are lines added.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING, Callable, Iterator

from cdd_guidance.practices.source_code import CodeLanguage
from harness.guidance.practice_formats import KEPT_MARK, OutlinedMember, Reshaped, lead_of

if TYPE_CHECKING:
    from cdd_guidance.practices.bdd.model.code_spec_model import DescribeCall, DescribeCalls

BlockPath = tuple[str, ...]
ScriptCalls = Callable[[str], object]
"""What reads a script spec's describe, context, it and test calls from its text: *DescribeCalls*."""


class SpecBlock(OutlinedMember):
    """One description, context or observation of a spec file: the names it sits under with its own, which name it as
    a person reads it, the lines it covers with the comments above it (``lead``, ``start``, ``last``), the line its
    children end before, and the blocks nested in it."""

    def __init__(self, path: BlockPath, lead: int, start: int, last: int, ends_before: int, indent: str) -> None:
        super().__init__(" ".join(path), lead, start, last + 1, indent)
        self.path = path
        # Its last line, and the line a new child goes before.
        self.last = last
        self.ends_before = ends_before
        self.children: list[SpecBlock] = []

    def every(self) -> Iterator[SpecBlock]:
        """This block and every block nested in it, outermost first."""
        yield self
        for child in self.children:
            yield from child.every()


class SpecOutline:
    """The blocks of one spec file with the lines each covers: a mamba spec read as Python reads it, a script spec by
    its describe, context, it and test calls (*DescribeCalls*). A spec that does not parse holds no block."""

    def __init__(self, text: str, language: CodeLanguage, python_kinds: dict[str, str], script_calls: ScriptCalls | None) -> None:
        self.lines = text.split("\n")
        self._comment = language.line_comment
        self._python_kinds = python_kinds
        self.roots = self._script_blocks(script_calls(text)) if script_calls is not None else self._python_blocks(text)

    @property
    def blocks(self) -> dict[BlockPath, SpecBlock]:
        return {block.path: block for root in self.roots for block in root.every()}

    def _lead_of(self, first: int, indent: str) -> int:
        return lead_of(self.lines, first, indent, (self._comment,))

    def _indent_of(self, line: int) -> str:
        written = self.lines[line]
        return written[: len(written) - len(written.lstrip())]

    def _python_blocks(self, text: str) -> list[SpecBlock]:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return []
        return self._python_children(tree.body, ())

    def _python_children(self, statements: list[ast.stmt], under: BlockPath) -> list[SpecBlock]:
        found: list[SpecBlock] = []
        for statement in statements:
            name = self._python_name(statement)
            if name is None:
                continue
            first, last = statement.lineno - 1, statement.end_lineno - 1
            indent = self._indent_of(first)
            block = SpecBlock(under + (name,), self._lead_of(first, indent), first, last, last + 1, indent)
            block.children = self._python_children(statement.body, block.path)
            found.append(block)
        return found

    def _python_name(self, statement: ast.stmt) -> str | None:
        """The name a ``with description("name"):`` statement gives its block; none for any other statement."""
        call = statement.items[0].context_expr if isinstance(statement, ast.With) and statement.items else None
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id in self._python_kinds and call.args):
            return None
        named = call.args[0]
        return named.value if isinstance(named, ast.Constant) and isinstance(named.value, str) else None

    def _script_blocks(self, calls: DescribeCalls) -> list[SpecBlock]:
        return [self._script_block(call, ()) for call in calls.roots]

    def _script_block(self, call: DescribeCall, under: BlockPath) -> SpecBlock:
        first, last = call.first_line, call.last_line
        indent = self._indent_of(first)
        block = SpecBlock(under + (call.name,), self._lead_of(first, indent), first, last, call.inside[1], indent)
        block.children = [self._script_block(child, block.path) for child in call.children]
        return block


class SpecReshape:
    """One language's way to write a rendered describe tree onto a spec file already there: blocks the tree gained are
    added, blocks it lost are marked, and nothing else in the file is touched."""

    def __init__(self, language: CodeLanguage, python_kinds: dict[str, str] | None = None, script_calls: ScriptCalls | None = None) -> None:
        self._language = language
        # The mamba block names a Python spec opens its blocks with, or the reader of a script spec's describe calls.
        self._python_kinds = dict(python_kinds or {})
        self._script_calls = script_calls

    def onto(self, existing: str, rendered: str) -> Reshaped:
        """existing in the shape of the tree rendered holds, with the blocks kept and the observations added."""
        file, tree = self._outline(existing), self._outline(rendered)
        held, shaped = file.blocks, tree.blocks
        gained = [block for path, block in shaped.items() if path not in held and (path[:-1] in held or len(path) == 1)]
        lost = [block for path, block in held.items() if path not in shaped and (path[:-1] in shaped or len(path) == 1)]
        added_lines = [(self._goes_before(file, held, block), self._written_in(file, held, tree, block)) for block in gained]
        marked_lines = [(block.lead, [self._marking(block)]) for block in lost if not self._is_marked(file, block)]
        lines = list(file.lines)
        # From the last line up, so the lines above stay where the outline found them; blocks added at one place keep
        # the order the tree gives them.
        for at, new in sorted(added_lines + marked_lines, key=lambda edit: edit[0], reverse=True):
            lines[at:at] = new
        added = [observation.name for block in gained for observation in block.every() if not observation.children]
        return Reshaped("\n".join(lines), sorted(block.name for block in lost), sorted(added))

    def _outline(self, text: str) -> SpecOutline:
        return SpecOutline(text, self._language, self._python_kinds, self._script_calls)

    def _goes_before(self, file: SpecOutline, held: dict[BlockPath, SpecBlock], block: SpecBlock) -> int:
        """The line a gained block is written before: where the block it sits in ends, or the file's end for a
        description, before the blank lines the file ends with."""
        owner = held.get(block.path[:-1])
        if owner is not None:
            return owner.ends_before
        end = len(file.lines)
        while end > 0 and not file.lines[end - 1].strip():
            end -= 1
        return end

    def _written_in(self, file: SpecOutline, held: dict[BlockPath, SpecBlock], tree: SpecOutline, block: SpecBlock) -> list[str]:
        """The gained block's lines as the tree wrote them, under a blank line, at the indent its new owner gives its
        blocks; two blank lines above a description, as a file parts its top-level blocks."""
        owner = held.get(block.path[:-1])
        written = tree.lines[block.lead:block.last + 1]
        if owner is None:
            return ["", "", *written]
        indent = owner.children[0].indent if owner.children else block.indent
        return ["", *(f"{indent}{line[len(block.indent):]}" if line.strip() else line for line in written)]

    def _is_marked(self, file: SpecOutline, block: SpecBlock) -> bool:
        return KEPT_MARK.marks(file.lines[block.lead:block.start])

    def _marking(self, block: SpecBlock) -> str:
        said = KEPT_MARK.line_for(block.name, "Move what it proves into the block that replaced it, then delete it.")
        return f"{block.indent}{self._language.comment(said)}"
