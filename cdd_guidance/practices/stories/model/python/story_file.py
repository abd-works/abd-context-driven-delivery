"""A Python story file as its blocks: `with story`, `with background`, `with scenario`, and step blocks."""

from __future__ import annotations

import ast
import re
from typing import List, Optional, Sequence, Tuple

from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage, WrittenBlock
from cdd_guidance.practices.stories.model.story_file import CodeBlock, StoryFile

_STEP_CALLS = frozenset({"given", "when", "then", "and_", "but_"})
# Comments the scenario writes for itself; they are not code the scenario holds.
_OWN_COMMENT = re.compile(r"^\s*#\s*(?:background|background-step|examples):")


class PythonStoryFile(StoryFile):
    """One Python story file, parsed once: its `with story(...)` blocks and the blocks inside each."""

    def __init__(self, language: CodeLanguage, content: str) -> None:
        super().__init__(language, content)
        try:
            self._tree: Optional[ast.Module] = ast.parse(content)
        except SyntaxError:
            self._tree = None

    def story_blocks(self) -> Optional[List[CodeBlock]]:
        if self._tree is None:
            return None
        return [PythonBlock(self, item) for item in self._tree.body if call_of(item) == "story"]


def call_of(item: ast.AST) -> str:
    """The block's call: story, scenario, given, ... ; background for `with background.<scope>`."""
    if not isinstance(item, ast.With) or not item.items:
        return ""
    expression = item.items[0].context_expr
    if isinstance(expression, ast.Attribute) and isinstance(expression.value, ast.Name):
        return "background" if expression.value.id == "background" else ""
    if isinstance(expression, ast.Call) and isinstance(expression.func, ast.Name):
        return expression.func.id
    return ""


class PythonBlock(CodeBlock):
    """One `with` block in a Python story file."""

    def __init__(self, file: PythonStoryFile, node: ast.With) -> None:
        self.file = file
        self.node = node

    @property
    def name(self) -> str:
        expression = self.node.items[0].context_expr
        if isinstance(expression, ast.Call) and expression.args and isinstance(expression.args[0], ast.Constant):
            return str(expression.args[0].value)
        return ""

    @property
    def line_span(self) -> Tuple[int, int]:
        return self.node.lineno - 1, self.node.end_lineno - 1

    @property
    def inside_lines(self) -> List[str]:
        return self.file.lines[slice(*self._inside)]

    @property
    def body(self) -> CodeBody:
        return CodeBody("\n".join(self.inside_lines), self.file.language)

    def written(self, lead: List[str]) -> WrittenBlock:
        heading = self.file.lines[self.node.lineno - 1 : self._inside[0]]
        return WrittenBlock(self.file.language, None, lead, heading)

    def split_inside(self, children: Sequence[CodeBlock]) -> Tuple[List[str], List[List[str]], List[str]]:
        return WrittenBlock.split_inside(self.file.lines, self._inside, [child.line_span for child in children])

    def scenarios(self) -> List[CodeBlock]:
        return self._within("scenario")

    def backgrounds(self, scenarios: Sequence[CodeBlock]) -> List[CodeBlock]:
        return [item for item in self._within("background") if not item._is_inside(scenarios)]

    def steps(self, skip: Sequence[CodeBlock]) -> List[CodeBlock]:
        found = [PythonBlock(self.file, item) for item in ast.walk(self.node) if call_of(item) in _STEP_CALLS]
        return [item for item in found if not item._is_inside(skip)]

    def setup(self, children: Sequence[CodeBlock]) -> CodeBody:
        """The lines in the block that are no child and none of the comments a scenario writes for itself."""
        first, last = self._inside
        covered = {line for child in children for line in range(child.line_span[0], child.line_span[1] + 1)}
        lines = self.file.lines
        kept = [lines[index] for index in range(first, last) if index not in covered and not _OWN_COMMENT.match(lines[index])]
        return CodeBody("\n".join(kept), self.file.language)

    def _within(self, call: str) -> List["PythonBlock"]:
        """The blocks of one kind inside this block, outermost first and in file order."""
        found = [PythonBlock(self.file, item) for item in ast.walk(self.node) if item is not self.node and call_of(item) == call]
        found.sort(key=lambda item: item.node.lineno)
        return [item for item in found if not item._is_inside([other for other in found if other is not item])]

    def _is_inside(self, blocks: Sequence[CodeBlock]) -> bool:
        return any(block.node.lineno < self.node.lineno <= block.node.end_lineno for block in blocks)

    @property
    def _inside(self) -> Tuple[int, int]:
        """The lines below the `with ...:` opening; comments and blank lines below it belong inside."""
        lines = self.file.lines
        index = self.node.body[0].lineno - 2
        while index > self.node.lineno - 1 and (not lines[index].strip() or lines[index].strip().startswith("#")):
            index -= 1
        return index + 1, self.node.end_lineno
