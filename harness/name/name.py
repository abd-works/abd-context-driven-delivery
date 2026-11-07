"""A name written in camel, kebab, or snake case, and the same name in each of the other cases."""

from __future__ import annotations

import re

_CAMEL_BOUNDARY = re.compile(r"([a-z0-9])([A-Z])")
_NOT_LETTER_OR_DIGIT = re.compile(r"[^a-z0-9]+")


class Name:
    """*Name* is one name, such as a class, an event, or a fidelity, that CDD writes in several cases: `StoryMap`,
    `story_map`, and `story-map` are the same name. Every case conversion reads it, so a class name, a toolset slug, and
    a published tool name always agree.

    The words of a name are split where a lower-case letter or digit meets a capital and wherever a character other than
    a letter or digit stands, so `PreToolUse`, `pre-tool-use`, and `pre_tool_use` have the same words. A run of capitals
    stays one word, so `MCPServer` is `mcpserver`.
    """

    def __init__(self, text: str) -> None:
        self._text = str(text or "")

    @property
    def words(self) -> list[str]:
        spaced = _CAMEL_BOUNDARY.sub(r"\1 \2", self._text).lower()
        return [word for word in _NOT_LETTER_OR_DIGIT.split(spaced) if word]

    @property
    def snake(self) -> str:
        """`story_map`: how Python names a module, a function, or a field."""
        return "_".join(self.words)

    @property
    def kebab(self) -> str:
        """`story-map`: how a slug, a skill, a command, or a published tool is named."""
        return "-".join(self.words)

    @property
    def camel(self) -> str:
        """`storyMap`: how TypeScript names a member."""
        return self._camel_case(self.words)

    @property
    def spellings(self) -> list[str]:
        """The name as written, then in kebab and then snake case, each once: the file and folder names something
        named this may be saved under, so `story_map` finds `story-map.md`."""
        return list(dict.fromkeys(spelling for spelling in (self._text, self.kebab, self.snake) if spelling))

    @property
    def title_words(self) -> list[str]:
        """The words of a title, such as a story or scenario name, in lower case. A title's capitals do not split its
        words, so `iPhone notes` is `iphone` and `notes`, as file, branch, and test names made from titles have always
        been."""
        return [word for word in _NOT_LETTER_OR_DIGIT.split(self._text.lower()) if word]

    @property
    def title_slug(self) -> str:
        """`pet-visits` for `Pet visits`: the title's words joined by hyphens, as a file or folder name."""
        return "-".join(self.title_words)

    @property
    def title_snake(self) -> str:
        """`pet_visits` for `Pet visits`: the title's words joined by underscores, as a Python name."""
        return "_".join(self.title_words)

    @property
    def title_pascal(self) -> str:
        """`PetVisits` for `Pet visits`: each of the title's words capitalised, as a class name."""
        return self._pascal_case(self.title_words)

    @property
    def title_camel(self) -> str:
        """`petVisits` for `Pet visits`: the title in Pascal case with its first word in lower case, as a member name."""
        return self._camel_case(self.title_words)

    def _camel_case(self, words: list[str]) -> str:
        head, *rest = words or [""]
        return head + self._pascal_case(rest)

    def _pascal_case(self, words: list[str]) -> str:
        return "".join(word.capitalize() for word in words)
