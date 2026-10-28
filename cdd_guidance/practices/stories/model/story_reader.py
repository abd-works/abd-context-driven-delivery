"""The one way a story file is read for the code it holds; each language finds its own blocks."""

from __future__ import annotations

from typing import Generic, List, Optional, Tuple, TypeVar

from cdd_guidance.practices.clean_engineering.model.code_body import CodeLanguage, WrittenBlock
from cdd_guidance.practices.stories.model.story_model import Story


Block = TypeVar("Block")
# One block of a story file as a language reader finds it: a brace call or a Python with statement.


class StoryReader(Generic[Block]):
    """Reads one story file: the file's own code around its stories, then each story the file and the model share."""

    def __init__(self, language: CodeLanguage, content: str) -> None:
        self._language = language
        self._lines = content.split("\n")

    def read(self, stories: List[Story], path: str) -> Optional[WrittenBlock]:
        """The file's code above the first story and below the last; each matched story gets its own code."""
        blocks = self.story_blocks()
        if blocks is None:
            return None
        written = WrittenBlock(self._language, None, [], [])
        written.path = path
        written.inside, leads, written.closing = WrittenBlock.split_inside(
            self._lines, (0, len(self._lines)), [self.line_span(block) for block in blocks]
        )
        pending = list(stories)
        for block, lead in zip(blocks, leads):
            story = self.take(pending, self.name_of(block))
            if story is not None:
                self.read_story(story, block, lead)
        return written

    def take(self, pending: list, name: str):
        """The next node with this name; nodes before it that do not match keep no code."""
        for index, node in enumerate(pending):
            if node.name == name:
                del pending[: index + 1]
                return node
        return None

    def story_blocks(self) -> Optional[List[Block]]:
        """Each story block in the file, in order; None when the file cannot be read."""
        raise NotImplementedError(f"{type(self).__name__} must find its story blocks")

    def name_of(self, block: Block) -> str:
        raise NotImplementedError(f"{type(self).__name__} must name its blocks")

    def line_span(self, block: Block) -> Tuple[int, int]:
        raise NotImplementedError(f"{type(self).__name__} must place its blocks")

    def read_story(self, story: Story, block: Block, lead: List[str]) -> None:
        raise NotImplementedError(f"{type(self).__name__} must read its stories")
