"""One spec render for every language - the walk and the body rule; a language only spells the lines."""

from __future__ import annotations

import ast
import re
import textwrap
from typing import Callable, List, Optional, Tuple, Union

from cdd_guidance.practices.clean_engineering.model.code_body import JAVASCRIPT, PYTHON, TYPESCRIPT, BraceCall, CodeBody, CodeLanguage, WrittenBlock
from cdd_guidance.practices.bdd.model.bdd_model import BddModel
from cdd_guidance.practices.bdd.model.nodes import Context, Description, Observation
from cdd_guidance.practices.bdd.model.spec_source import SIGNATURE

_SPEC = "spec"
_MAMBA_BLOCKS = {"description": "description", "describe": "description", "context": "context", "it": "it", "_it": "it"}
# Playwright names its blocks through `test`: `test.describe(...)`, `test.describe.serial(...)`, and `test(...)`.
_SCRIPT_BLOCK = re.compile(
    r"(?<![.\w])(?:test\.)?(describe|context|it|test)(?:\.(?:serial|parallel|only|skip|fixme))?\s*\(\s*(['\"`])((?:\\.|(?!\2).)*)\2"
)

# (first line, last line, read) for one child block; read(lead, order) builds the child's node.
ChildBlock = Tuple[int, int, Callable[[List[str], int], object]]
BehaviorBlock = Union[Description, Context, Observation]
ParentBlock = Optional[Union[Description, Context]]


class UnreadableSpec(ValueError):
    """A spec file that is not valid code. Read as an empty spec, a render over it would replace every test body."""

    def __init__(self, language: str, error: SyntaxError) -> None:
        super().__init__(f"the {language} spec does not parse (line {error.lineno}: {error.msg}); fix it before reading or rendering over it")
        self.line = error.lineno


class CodeBddModel(BddModel):
    """A spec written as code. Python and TypeScript only spell the lines."""

    language: CodeLanguage

    def parse(self, text: str) -> "CodeBddModel":
        self.check_readable(text)
        return self.parse_code(text)

    def check_readable(self, text: str) -> None:
        """Raise UnreadableSpec when text is not valid code in this language. A language with no syntax check accepts any text."""

    def render(self, canonical: BddModel, previous: Optional[str] = None) -> str:
        # The previous file is read once per render and consulted for any block the canonical spec
        # did not read in this language.
        self._kept = type(self)().parse(previous) if previous else type(self)()
        written = self._written(canonical, ())
        preamble = canonical.preamble.in_language_of(self._kept.preamble, self.language)
        # WHY: imports from another language name nothing this file can load, so only this language's are kept.
        own = preamble.lines_in(self.language, "", "") if preamble.language is self.language else []
        as_read = written.inside_for(preamble) if written is not None and own else None
        lines = as_read if as_read is not None else (own or self.default_imports())
        for description in canonical.descriptions:
            lines = lines + self._render_block(description, (), first=False)
        if written is not None:
            return "\n".join(lines + written.closing)
        lines.extend(self.top_level_gap() + self._foreign(canonical.written and canonical.written.closing_body, ""))
        return "\n".join(lines).strip("\n") + "\n"

    def _render_block(self, node: BehaviorBlock, parents: tuple, first: bool) -> List[str]:
        """Written in this language under the same name: every line as read. Otherwise the generic spelling."""
        path = parents + (node.name,)
        indent, inner = self._indents(path)
        written = self._written(node, path)
        if written is not None:
            opened, closing, closed = written.lead + written.heading, written.closing, written.close
        else:
            opened = self._gap(len(parents), first) + self._foreign(node.written and node.written.lead_body, indent)
            opened.append(f"{indent}{self.block_open(self._kind(node, len(parents)), node.name)}")
            closing = self._foreign(node.written and node.written.closing_body, inner)
            closed = [f"{indent}{line}" for line in self.block_close()]
        if isinstance(node, Observation):
            return opened + self._render_body(node, path, written) + closed
        return opened + self._render_inside(node, path, written) + closing + closed

    def _render_body(self, observation: Observation, path: tuple, written: Optional[WrittenBlock]) -> List[str]:
        inner = self._indents(path)[1]
        body = observation.body.in_language_of(self._kept.body_at(path), self.language)
        as_read = written.inside_for(body) if written is not None else None
        if as_read is not None:
            return as_read
        if body.language is self.language:
            return body.lines_in(self.language, inner, self.marker_line())
        scaffold = self._realization(observation) if body.is_empty else []
        return [f"{inner}{line}" for line in scaffold] + body.lines_in(self.language, inner, self.marker_line())

    def _indents(self, path: tuple) -> Tuple[str, str]:
        """The indent of the block at this path, and of the lines inside it."""
        return self.language.indent * (len(path) - 1), self.language.indent * len(path)

    def default_imports(self) -> List[str]:
        raise NotImplementedError(f"{type(self).__name__} must spell default_imports")

    def top_level_gap(self) -> List[str]:
        return [""]

    def block_open(self, kind: str, name: str) -> str:
        raise NotImplementedError(f"{type(self).__name__} must spell block_open")

    def block_close(self) -> List[str]:
        return []

    def empty_block(self) -> List[str]:
        return []

    def marker_line(self) -> str:
        return self.language.comment(SIGNATURE)

    def _read_block(self, node: Union[BddModel, BehaviorBlock], inside: Tuple[int, int], children: List[ChildBlock]) -> List[str]:
        """Read the lines inside one block: setup before the first child, each child with the lines above it,
        and return the lines after the last child. Blank lines right above the first child belong to it."""
        setup, leads, closing = WrittenBlock.split_inside(self._lines, inside, [(first, last) for first, last, _ in children])
        node.setup = CodeBody("\n".join(setup), self.language)
        node.written.inside = setup
        for order, ((_first, _last, read), lead) in enumerate(zip(children, leads), 1):
            read(lead, order)
        return closing

    def _render_inside(self, node: Union[Description, Context], path: tuple, written: Optional[WrittenBlock]) -> List[str]:
        inner = self._indents(path)[1]
        body = node.setup.in_language_of(self._kept.setup_at(path), self.language)
        as_read = written.inside_for(body) if written is not None and body.language is self.language else None
        setup = as_read if as_read is not None else body.lines_in(self.language, inner, "")
        lines = list(setup)
        for index, child in enumerate(self._children(node)):
            lines.extend(self._render_block(child, path, first=index == 0 and not setup))
        if lines or as_read is not None:
            return lines
        return [f"{inner}{line}" for line in self.empty_block()]

    def _written(self, node: Union[BddModel, BehaviorBlock], path: tuple) -> Optional[WrittenBlock]:
        """The node's own lines when it was read in this language, else the previous file's for the same block."""
        name = path[-1] if path else _SPEC
        for written in (node.written, self._kept.written if not path else self._kept.written_at(path)):
            if written is not None and written.is_in(self.language, name):
                return written
        return None

    def _gap(self, depth: int, first: bool) -> List[str]:
        if depth == 0:
            return self.top_level_gap()
        return [] if first else [""]

    def _foreign(self, written_part: Optional[CodeBody], indent: str) -> List[str]:
        """Lines another language wrote around a block, commented out so nothing is lost."""
        if written_part is None:
            return []
        return written_part.lines_in(self.language, indent, "")

    def _kind(self, node: BehaviorBlock, depth: int) -> str:
        if isinstance(node, Observation):
            return "it"
        return "description" if depth == 0 else "context"

    def _children(self, node: Union[Description, Context]) -> List[BehaviorBlock]:
        """Observations and contexts in the order the file had them; a sketch lists observations first."""
        return sorted(list(node.observations) + list(node.contexts), key=lambda child: child.sequential_order)

    def _realization(self, observation: Observation) -> List[str]:
        """The realization call graph for an it nobody has written: surface lines, then calls, as comments."""
        graph = textwrap.dedent(observation.call_graph.block()).splitlines()
        lines = [f"-> {surface}" for surface in observation.surface_lines] + graph
        return [self.language.comment(line) for line in lines]

    def _body(self, text: str) -> CodeBody:
        marker = text.strip() in {self.marker_line(), self.language.comment(SIGNATURE)}
        return CodeBody("" if marker else text, self.language)

    def _inline(self, node: BehaviorBlock, lead: List[str], heading: List[str], inline: str) -> BehaviorBlock:
        """A block written on one line: the line is its heading and holds its body."""
        node.written = WrittenBlock(self.language, node.name, lead, heading)
        node.written.inline = inline
        if isinstance(node, Observation):
            node.body = self._body(inline)
        else:
            node.setup = CodeBody(inline, self.language)
        return node

    def _read_spec(self, lines: List[str], children: List[ChildBlock]) -> None:
        """The whole file as one block: the preamble above the first description, then the descriptions,
        then whatever follows the last one. An it outside every describe stays text."""
        self.descriptions = []
        self.written = WrittenBlock(self.language, _SPEC, [], [])
        self.written.closing = self._read_block(self, (0, len(lines)), children)
        self.preamble, self.setup = self.setup, CodeBody()

    def _add_block(self, kind: str, parent: ParentBlock, name: str, order: int) -> BehaviorBlock:
        """A block read from the file, added where it stands: an outermost describe is one of this spec's descriptions,
        and any other block is a context or an observation of the block that holds it."""
        if parent is None:
            return self.add_description(name, order)
        return parent.add_child(kind, name, order)


class PythonBddModel(CodeBddModel):
    """Mamba specs: `with description(...)`, `with context(...)`, `with it(...)` blocks."""

    language = PYTHON
    # The spec files this model reads.
    suffixes = language.suffixes

    def check_readable(self, text: str) -> None:
        try:
            ast.parse(text)
        except SyntaxError as error:
            raise UnreadableSpec(self.language.name, error) from error

    def parse_code(self, text: str) -> "PythonBddModel":
        """The describe tree of a mamba spec. The graph scan reads every spec file this way and still records the source
        facts of one that does not parse, so such a file reads as a spec with no describe tree; `parse` refuses it."""
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return self
        self._lines = text.split("\n")
        descriptions = [item for item in tree.body if self._block_kind(item) == "description"]
        self._read_spec(self._lines, self._child_blocks(descriptions, None))
        return self

    def default_imports(self) -> List[str]:
        return ["from mamba import description, context, it", "from expects import expect"]

    def top_level_gap(self) -> List[str]:
        return ["", ""]

    def block_open(self, kind: str, name: str) -> str:
        return f'with {kind}("{_escape(name)}"):'

    def empty_block(self) -> List[str]:
        return ["pass"]

    def marker_line(self) -> str:
        return f"pass  {self.language.comment(SIGNATURE)}"

    def _child_blocks(self, statements: List[ast.stmt], parent: ParentBlock) -> List[ChildBlock]:
        return [
            (item.lineno - 1, item.end_lineno - 1, self._reader(item, parent))
            for item in statements
            if self._block_kind(item)
        ]

    def _reader(self, item: ast.With, parent: ParentBlock) -> Callable[[List[str], int], object]:
        return lambda lead, order: self._node(item, parent, lead, order)

    def _block_kind(self, item: ast.stmt) -> str:
        if not isinstance(item, ast.With) or not item.items:
            return ""
        call = item.items[0].context_expr
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.args):
            return ""
        if not (isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str)):
            return ""
        return _MAMBA_BLOCKS.get(call.func.id, "")

    def _node(self, item: ast.With, parent: ParentBlock, lead: List[str], order: int) -> BehaviorBlock:
        """One `with <block>("name"):` statement as a Description, Context, or Observation."""
        name = item.items[0].context_expr.args[0].value
        node = self._add_block(self._block_kind(item), parent, name, order)
        node.line, node.end_line = item.lineno, item.end_lineno
        if item.body[0].lineno == item.lineno:
            source = "\n".join(self._lines)
            inline = "\n".join(ast.get_source_segment(source, statement) or "" for statement in item.body)
            return self._inline(node, lead, self._lines[item.lineno - 1 : item.end_lineno], inline)
        heading_last = self._heading_last(item)
        inside = (heading_last + 1, item.end_lineno)
        node.written = WrittenBlock(self.language, name, lead, self._lines[item.lineno - 1 : heading_last + 1])
        if isinstance(node, Observation):
            node.written.inside = self._lines[slice(*inside)]
            node.body = self._body("\n".join(node.written.inside))
            return node
        node.written.closing = self._read_block(node, inside, self._child_blocks(item.body, node))
        return node

    def _heading_last(self, item: ast.With) -> int:
        """The last line of the `with ...:` opening; comments and blank lines below it belong to the body."""
        index = item.body[0].lineno - 2
        while index > item.lineno - 1 and (not self._lines[index].strip() or self._lines[index].strip().startswith("#")):
            index -= 1
        return index


class TypeScriptBddModel(CodeBddModel):
    """Vitest / Jest specs: `describe(...)`, `it(...)`, `test(...)` blocks found by bracket matching."""

    language = TYPESCRIPT
    # The spec files this model reads: a JavaScript spec's describe tree is written the same way.
    suffixes = language.suffixes + JAVASCRIPT.suffixes

    def parse_code(self, text: str) -> "TypeScriptBddModel":
        self._lines = text.split("\n")
        self._read_spec(self._lines, self._child_blocks(DescribeCalls(text).describes, None))
        return self

    def default_imports(self) -> List[str]:
        return ['import { describe, it } from "vitest";']

    def block_open(self, kind: str, name: str) -> str:
        call = "it" if kind == "it" else "describe"
        return f'{call}("{_escape(name)}", () => {{'

    def block_close(self) -> List[str]:
        return ["});"]

    def _child_blocks(self, calls: List["DescribeCall"], parent: ParentBlock) -> List[ChildBlock]:
        return [(call.first_line, call.last_line, self._reader(call, parent)) for call in calls]

    def _reader(self, call: "DescribeCall", parent: ParentBlock) -> Callable[[List[str], int], object]:
        return lambda lead, order: self._node(call, parent, lead, order)

    def _node(self, call: "DescribeCall", parent: ParentBlock, lead: List[str], order: int) -> BehaviorBlock:
        node = self._add_block(call.behavior_kind, parent, call.name, order)
        node.line, node.end_line = call.first_line + 1, call.last_line + 1
        if call.is_inline:
            return self._inline(node, lead, call.whole_lines, call.body)
        node.written = WrittenBlock(self.language, call.name, lead, call.heading_lines)
        node.written.close = call.close_lines
        if isinstance(node, Observation):
            node.written.inside = call.inside_lines
            node.body = self._body("\n".join(node.written.inside))
            return node
        node.written.closing = self._read_block(node, call.inside, self._child_blocks(call.children, node))
        return node


class DescribeCall(BraceCall):
    """A `describe`, `context`, `it`, or `test` call read from a script spec: the call with its kind, the lines of the
    file it spans, from its start through its opening brace, its body, and its closing brace to its end, and the calls
    nested in its callback, which it adopts."""

    def __init__(self, text: str, match: re.Match, file_lines: List[str]) -> None:
        super().__init__(text, match.start(), text.index("(", match.start()), match.group(3))
        self.kind = match.group(1)
        self.children: List[DescribeCall] = []
        self._file_lines = file_lines
        points = (self.start, self.brace, self.inner_end or 0, self.end - 1)
        self._start_line, self._brace_line, self._inner_end_line, self._end_line = (text.count("\n", 0, index) for index in points)

    @property
    def is_observation(self) -> bool:
        """True for an `it` or a `test`, whose callback is a test body."""
        return self.kind in {"it", "test"}

    @property
    def is_describe(self) -> bool:
        return self.kind == "describe"

    @property
    def behavior_kind(self) -> str:
        """The describe-tree block this call is inside another block: an observation for an `it` or a `test`, else a
        context."""
        return "it" if self.is_observation else "context"

    @property
    def first_line(self) -> int:
        """The index of the file line the call starts on."""
        return self._start_line

    @property
    def last_line(self) -> int:
        """The index of the file line the call ends on."""
        return self._end_line

    @property
    def is_inline(self) -> bool:
        """True when its callback opens and closes on one line."""
        return self._brace_line == self._inner_end_line

    @property
    def inside(self) -> Tuple[int, int]:
        """The indexes of the first line inside its callback and of the line its callback closes on."""
        return self._brace_line + 1, self._inner_end_line

    @property
    def whole_lines(self) -> List[str]:
        return self._file_lines[self._start_line : self._end_line + 1]

    @property
    def heading_lines(self) -> List[str]:
        """The lines from its start through its callback's opening brace."""
        return self._file_lines[self._start_line : self._brace_line + 1]

    @property
    def inside_lines(self) -> List[str]:
        return self._file_lines[slice(*self.inside)]

    @property
    def close_lines(self) -> List[str]:
        """The lines from its callback's closing brace to its end."""
        return self._file_lines[self._inner_end_line : self._end_line + 1]

    def encloses(self, other: "DescribeCall") -> bool:
        """True when other starts inside this call's callback."""
        return self.inner_end is not None and other.start <= self.inner_end

    def adopt(self, child: "DescribeCall") -> None:
        """Hold child as a call nested straight inside its callback."""
        self.children.append(child)


class DescribeCalls:
    """Every describe, context, it, and test call of a script spec whose parentheses and callback both close, each
    adopted by the innermost describe or context around it. A call inside a test body stays part of that body."""

    def __init__(self, text: str) -> None:
        lines = text.split("\n")
        found = (DescribeCall(text, match, lines) for match in _SCRIPT_BLOCK.finditer(text))
        self.roots: List[DescribeCall] = []
        open_calls: List[DescribeCall] = []
        inside_test_until = -1
        for call in (call for call in found if call.is_whole):
            if call.start < inside_test_until:
                continue
            while open_calls and not open_calls[-1].encloses(call):
                open_calls.pop()
            if open_calls:
                open_calls[-1].adopt(call)
            else:
                self.roots.append(call)
            if call.is_observation:
                inside_test_until = call.end
            else:
                open_calls.append(call)

    @property
    def describes(self) -> List[DescribeCall]:
        """The outermost describe calls: the spec's descriptions."""
        return [call for call in self.roots if call.is_describe]



def _escape(name: str) -> str:
    return name.replace("\\", "\\\\").replace('"', '\\"')
