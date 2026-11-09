"""A story file as its language finds the blocks in it: the file's own code around its stories, and the block each
story, background, scenario, and step was written as. The file is read once: each story is made from its own block (its
comment, its text, and its scenario blocks, `CodeStory.from_block`) and reads its code from that block, so no story is
matched to a block by its name.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Tuple


from cdd_guidance.practices.clean_engineering.model.code_body import CodeLanguage, WrittenBlock
from cdd_guidance.practices.stories.model.story_map_files import source_at


# One block of a story file as its language finds it (a story, background, scenario, or step call): a BraceBlock or a
# PythonBlock. Each answers `name` (its call's name), `line_span` (its first and last line, from 0), `inside_lines`,
# `body` (the code inside it, as a step holds it), `body_text` (that code as written), `text` (the whole block as
# written), `written(lead)` (its lines as read, the lead above it included),
# `split_inside(children)`, `scenarios()`, `backgrounds(scenarios)`, `steps(skip)`, and `setup(children)` (the lines
# no child holds), so a node reads its own code from it whichever language it was written in.
CodeBlock = Any


def flat_steps(steps: Sequence) -> List:
    """Every step with its ands after it, in the order the file has them."""
    return [line for step in steps for line in (step, *step.ands)]


def read_step_code(owner, blocks: Sequence[CodeBlock]) -> None:
    """Each of owner's steps, ands included, reads the step block in the same place in the file."""
    for step, block in zip(flat_steps(owner.steps), blocks):
        step.read_code(block)


class StoryFile:
    """One story file's text in a language: its story blocks, and the file's own code above the first story and
    below the last."""

    def __init__(self, language: CodeLanguage, content: str) -> None:
        self.language = language
        self.text = content
        self.lines = content.split("\n")

    def story_blocks(self) -> Optional[List[CodeBlock]]:
        """Each story block in the file, in order; None when the file cannot be read."""
        raise NotImplementedError(f"{type(self).__name__} must find its story blocks")

    def stories(self, story_type: type, path: str) -> Optional[Tuple[List, WrittenBlock]]:
        """The file's stories, each made from the block written for it and placed on its lines of path, and the file's
        own code around them; None when the file cannot be read, so the story type reads its text and its stories are
        written generically. A file with no story block is one story read from its text."""
        blocks = self.story_blocks()
        if blocks is None:
            return None
        written = WrittenBlock(self.language, None, [], [])
        written.path = path
        written.inside, leads, written.closing = WrittenBlock.split_inside(
            self.lines, (0, len(self.lines)), [block.line_span for block in blocks]
        )
        if not blocks:
            return story_type.load_all(self.text), written
        imports = story_type.example_imports(self.text)
        stories = []
        for block, lead in zip(blocks, leads):
            story = story_type.from_block(block, lead, "\n".join([imports, self.comment_above(block), block.text]))
            story.source = source_at(path, block.line_span[0] + 1, block.line_span[1] + 1)
            stories.append(story)
        return stories, written

    def comment_above(self, block: CodeBlock) -> str:
        """The comment lines right above block, which describe the story it holds, up to the code before them."""
        start = index = block.line_span[0]
        while index > 0 and _describes(self.lines[index - 1]):
            index -= 1
        return "\n".join(self.lines[index:start])


def _describes(line: str) -> bool:
    """Whether a line can be part of the comment above a block: a blank line or a comment line in any language."""
    return not line.strip() or line.strip().startswith(("/*", "*", "//", "#"))
