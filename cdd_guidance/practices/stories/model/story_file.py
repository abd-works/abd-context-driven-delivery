"""A story file as its language finds the blocks in it: the file's own code around its stories, and the block each
story, background, scenario, and step was written as. Each node reads its own block (`CodeStory.read_code`,
`CodeScenario.read_code`, `Step.read_code`); the file only finds the blocks and hands each story the one written for it.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence

from cdd_guidance.practices.clean_engineering.model.code_body import CodeLanguage, WrittenBlock


# One block of a story file as its language finds it (a story, background, scenario, or step call): a BraceBlock or a
# PythonBlock. Each answers `name` (its call's name), `line_span` (its first and last line, from 0), `inside_lines`,
# `body` (the code inside it, as a step holds it), `written(lead)` (its lines as read, the lead above it included),
# `split_inside(children)`, `scenarios()`, `backgrounds(scenarios)`, `steps(skip)`, and `setup(children)` (the lines
# no child holds), so a node reads its own code from it whichever language it was written in.
CodeBlock = Any


def paired(nodes: Sequence, blocks: Sequence[CodeBlock], leads: Sequence[List[str]]) -> List[tuple]:
    """(node, block, lead) for each block whose name is the next node of that name, in file order. Nodes and blocks
    are read from the same file, so the name is what the two readings share; a node passed over keeps no code."""
    pending = list(nodes)
    found: List[tuple] = []
    for block, lead in zip(blocks, leads):
        index = next((at for at, node in enumerate(pending) if node.name == block.name), None)
        if index is None:
            continue
        found.append((pending[index], block, lead))
        del pending[: index + 1]
    return found


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

    def read(self, stories: Sequence, path: str) -> Optional[WrittenBlock]:
        """The file's own code, with each story given the block written for it to read; None when the file cannot be
        read, so its stories are written generically."""
        blocks = self.story_blocks()
        if blocks is None:
            return None
        written = WrittenBlock(self.language, None, [], [])
        written.path = path
        written.inside, leads, written.closing = WrittenBlock.split_inside(
            self.lines, (0, len(self.lines)), [block.line_span for block in blocks]
        )
        for story, block, lead in paired(stories, blocks, leads):
            story.read_code(block, lead)
        return written
