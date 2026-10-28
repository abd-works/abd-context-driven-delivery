"""One spec render for every language - the walk and the body rule; a language only spells the lines."""

from __future__ import annotations

import ast
import re
import textwrap
from typing import Callable, List, Optional, Tuple, Union

from cdd_guidance.practices.bdd.model.bdd_model import BddModel
from cdd_guidance.practices.bdd.model.nodes import Context, Description, Observation, WrittenBlock
from cdd_guidance.practices.clean_engineering.model.call_graph import render_call_graph_block
from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage

_SIGNATURE = "BDD: SIGNATURE"
_SPEC = "spec"
_MAMBA_BLOCKS = {"description": "description", "describe": "description", "context": "context", "it": "it", "_it": "it"}
_SCRIPT_BLOCK = re.compile(r"(?<![.\w])(describe|context|it|test)\s*\(\s*(['\"`])((?:\\.|(?!\2).)*)\2")

# (first line, last line, read) for one child block; read(lead, order) builds the child's node.
ChildBlock = Tuple[int, int, Callable[[List[str], int], object]]
BehaviorBlock = Union[Description, Context, Observation]
ParentBlock = Optional[Union[Description, Context]]


class CodeBddModel(BddModel):
    """A spec written as code. Python and TypeScript only spell the lines."""

    language: CodeLanguage

    def parse(self, text: str) -> "CodeBddModel":
        return self.parse_code(text)

    def render(self, canonical: BddModel, previous: Optional[str] = None) -> str:
        # The previous file is read once per render and consulted for any block the canonical spec
        # did not read in this language.
        self._kept = type(self)().parse_code(previous) if previous else type(self)()
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
        lines.extend(self.top_level_gap() + self._foreign(canonical, "closing_body", ""))
        return "\n".join(lines).strip("\n") + "\n"

    def _render_block(self, node: BehaviorBlock, parents: tuple, first: bool) -> List[str]:
        """Written in this language under the same name: every line as read. Otherwise the generic spelling."""
        path = parents + (node.name,)
        indent, inner = self._indents(path)
        written = self._written(node, path)
        if written is not None:
            opened, closing, closed = written.lead + written.heading, written.closing, written.close
        else:
            opened = self._gap(len(parents), first) + self._foreign(node, "lead_body", indent)
            opened.append(f"{indent}{self.block_open(self._kind(node, len(parents)), node.name)}")
            closing = self._foreign(node, "closing_body", inner)
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
        return self.language.comment(_SIGNATURE)

    def _read_block(self, node: Union[BddModel, BehaviorBlock], inside: Tuple[int, int], children: List[ChildBlock]) -> List[str]:
        """Read the lines inside one block: setup before the first child, each child with the lines above it,
        and return the lines after the last child. Blank lines right above the first child belong to it."""
        lines = self._lines
        start, end = inside
        region = lines[start : children[0][0]] if children else lines[start:end]
        kept = len(region)
        while kept and not region[kept - 1].strip():
            kept -= 1
        node.setup = CodeBody("\n".join(region[:kept]), self.language)
        node.written.inside = region[:kept]
        if not children:
            return region[kept:]
        previous_end = None
        for order, (first, last, read) in enumerate(children, 1):
            lead = region[kept:] if previous_end is None else lines[previous_end + 1 : first]
            read(lead, order)
            previous_end = last
        return lines[previous_end + 1 : end]

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

    def _foreign(self, node: Union[BddModel, BehaviorBlock], part: str, indent: str) -> List[str]:
        """Lines another language wrote around this block, commented out so nothing is lost."""
        if node.written is None:
            return []
        return getattr(node.written, part)().lines_in(self.language, indent, "")

    def _kind(self, node: BehaviorBlock, depth: int) -> str:
        if isinstance(node, Observation):
            return "it"
        return "description" if depth == 0 else "context"

    def _children(self, node: Union[Description, Context]) -> List[BehaviorBlock]:
        """Observations and contexts in the order the file had them; a sketch lists observations first."""
        return sorted(list(node.observations) + list(node.contexts), key=lambda child: child.sequential_order)

    def _realization(self, observation: Observation) -> List[str]:
        """The realization call graph for an it nobody has written: surface lines, then calls, as comments."""
        graph = textwrap.dedent(render_call_graph_block(observation.call_graph)).splitlines()
        lines = [f"-> {surface}" for surface in observation.surface_lines] + graph
        return [self.language.comment(line) for line in lines]

    def _body(self, text: str) -> CodeBody:
        marker = text.strip() in {self.marker_line(), self.language.comment(_SIGNATURE)}
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
        self._roots = []
        self.written = WrittenBlock(self.language, _SPEC, [], [])
        self.written.closing = self._read_block(self, (0, len(lines)), children)
        self.preamble, self.setup = self.setup, CodeBody()
        self.descriptions = list(self._roots)


class PythonBddModel(CodeBddModel):
    """Mamba specs: `with description(...)`, `with context(...)`, `with it(...)` blocks."""

    language = CodeLanguage.named("python")

    def parse_code(self, text: str) -> "PythonBddModel":
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
        return f"pass  {self.language.comment(_SIGNATURE)}"

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
        node = _behavior_node(self._block_kind(item), parent, name, order, item.lineno, item.end_lineno)
        if parent is None:
            self._roots.append(node)
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

    language = CodeLanguage.named("typescript")

    def parse_code(self, text: str) -> "TypeScriptBddModel":
        self._text = text
        self._lines = text.split("\n")
        blocks = [block for block in (self._block(match) for match in _SCRIPT_BLOCK.finditer(text)) if block]
        descriptions = [block for block in self._tree(blocks) if block["kind"] == "describe"]
        self._read_spec(self._lines, self._child_blocks(descriptions, None))
        return self

    def default_imports(self) -> List[str]:
        return ['import { describe, it } from "vitest";']

    def block_open(self, kind: str, name: str) -> str:
        call = "it" if kind == "it" else "describe"
        return f'{call}("{_escape(name)}", () => {{'

    def block_close(self) -> List[str]:
        return ["});"]

    def _block(self, match: re.Match) -> Optional[dict]:
        """One describe/it/test call: kind, name, and the lines of its call, its opening brace, and its closing brace."""
        close = self._matching(self._text.index("(", match.start()), "(", ")")
        if close is None:
            return None
        arrow = self._text.find("=>", match.end(), close)
        brace = self._text.find("{", arrow if arrow >= 0 else match.end(), close)
        inner_end = self._matching(brace, "{", "}") if brace >= 0 else None
        if inner_end is None:
            return None
        end = close + 1 if not self._text.startswith(";", close + 1) else close + 2
        return {
            "kind": match.group(1),
            "name": match.group(3),
            "span": (match.start(), end),
            "inner": (brace + 1, inner_end),
            "lines": tuple(self._text.count("\n", 0, index) for index in (match.start(), brace, inner_end, end - 1)),
            "children": [],
        }

    def _tree(self, blocks: List[dict]) -> List[dict]:
        """Each block under the innermost enclosing describe; a call inside an it body stays part of that body."""
        roots: List[dict] = []
        open_blocks: List[dict] = []
        inside_it_until = -1
        for block in blocks:
            if block["span"][0] < inside_it_until:
                continue
            while open_blocks and open_blocks[-1]["inner"][1] < block["span"][0]:
                open_blocks.pop()
            (open_blocks[-1]["children"] if open_blocks else roots).append(block)
            if block["kind"] in {"it", "test"}:
                inside_it_until = block["span"][1]
            else:
                open_blocks.append(block)
        return roots

    def _child_blocks(self, blocks: List[dict], parent: ParentBlock) -> List[ChildBlock]:
        return [(block["lines"][0], block["lines"][3], self._reader(block, parent)) for block in blocks]

    def _reader(self, block: dict, parent: ParentBlock) -> Callable[[List[str], int], object]:
        return lambda lead, order: self._node(block, parent, lead, order)

    def _node(self, block: dict, parent: ParentBlock, lead: List[str], order: int) -> BehaviorBlock:
        kind = block["kind"]
        mapped = "it" if kind in {"it", "test"} else ("description" if kind == "describe" and parent is None else "context")
        start, brace, inner_end, end = block["lines"]
        node = _behavior_node(mapped, parent, block["name"], order, start + 1, end + 1)
        if parent is None:
            self._roots.append(node)
        if brace == inner_end:
            return self._inline(node, lead, self._lines[start : end + 1], self._text[slice(*block["inner"])])
        node.written = WrittenBlock(self.language, block["name"], lead, self._lines[start : brace + 1])
        node.written.close = self._lines[inner_end : end + 1]
        if isinstance(node, Observation):
            node.written.inside = self._lines[brace + 1 : inner_end]
            node.body = self._body("\n".join(node.written.inside))
            return node
        children = self._child_blocks(block["children"], node)
        node.written.closing = self._read_block(node, (brace + 1, inner_end), children)
        return node

    def _matching(self, open_index: int, opener: str, closer: str) -> Optional[int]:
        """The index of the bracket that closes the one at open_index; None when the text never closes it."""
        depth = 0
        for index in range(open_index, len(self._text)):
            if self._text[index] == opener:
                depth += 1
            elif self._text[index] == closer:
                depth -= 1
                if depth == 0:
                    return index
        return None


def _behavior_node(kind: str, parent: ParentBlock, name: str, order: int, line: int, end_line: int):
    if kind == "description" and parent is None:
        node = Description(name, order)
    elif kind == "it":
        node = Observation(name, order)
    else:
        node = Context(name, order)
    node.line, node.end_line = line, end_line
    if parent is not None:
        (parent.observations if isinstance(node, Observation) else parent.contexts).append(node)
    return node



def _escape(name: str) -> str:
    return name.replace("\\", "\\\\").replace('"', '\\"')
