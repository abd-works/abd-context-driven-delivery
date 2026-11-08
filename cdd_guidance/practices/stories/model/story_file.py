"""A story file as its language finds the blocks in it: the file's own code around its stories, and the block each
story, background, scenario, and step was written as. Each node reads its own block (`CodeStory.read_code`,
`CodeScenario.read_code`, `Step.read_code`); the file only finds the blocks and hands each story the one written for it.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from cdd_guidance.practices.clean_engineering.model.code_body import CodeBody, CodeLanguage, WrittenBlock


class CodeBlock:
    """One block of a story file as its language finds it: a story, background, scenario, or step call, with what a
    node needs to read its own code from it."""

    @property
    def name(self) -> str:
        """The name the block's call was written with: a story's, a scenario's, or a step's text."""
        raise NotImplementedError(f"{type(self).__name__} must name its block")

    @property
    def line_span(self) -> Tuple[int, int]:
        """The block's first and last line in the file, counted from 0."""
        raise NotImplementedError(f"{type(self).__name__} must place its block")

    @property
    def inside_lines(self) -> List[str]:
        """The lines inside the block, between its opening and its close."""
        raise NotImplementedError(f"{type(self).__name__} must give its inside lines")

    @property
    def body(self) -> CodeBody:
        """The code inside the block, as a step holds it."""
        raise NotImplementedError(f"{type(self).__name__} must give its body")

    def written(self, lead: List[str]) -> WrittenBlock:
        """The block's lines as read: the lead above it, its opening, and its close; what is inside is the reader's."""
        raise NotImplementedError(f"{type(self).__name__} must give its written lines")

    def split_inside(self, children: Sequence["CodeBlock"]) -> Tuple[List[str], List[List[str]], List[str]]:
        """The lines inside the block above the first child, each child's lead, and the lines below the last child."""
        raise NotImplementedError(f"{type(self).__name__} must split its inside")

    def scenarios(self) -> List["CodeBlock"]:
        """The scenario blocks inside this block, in file order."""
        raise NotImplementedError(f"{type(self).__name__} must find its scenarios")

    def backgrounds(self, scenarios: Sequence["CodeBlock"]) -> List["CodeBlock"]:
        """The background blocks inside this block and outside its scenarios, in file order."""
        raise NotImplementedError(f"{type(self).__name__} must find its backgrounds")

    def steps(self, skip: Sequence["CodeBlock"]) -> List["CodeBlock"]:
        """Each step block inside this block and outside skip, chained steps included, in file order."""
        raise NotImplementedError(f"{type(self).__name__} must find its steps")

    def setup(self, children: Sequence["CodeBlock"]) -> CodeBody:
        """The lines inside the block that belong to none of children: shared fields and helpers."""
        raise NotImplementedError(f"{type(self).__name__} must give its setup")


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
