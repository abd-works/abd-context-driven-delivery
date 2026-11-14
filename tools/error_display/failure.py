"""*Failure*: something a person or the agent ran that did not work, shown the same way wherever it happened.

Every failure says what failed and why, the context it failed in, and offers Fix, which sends both to the chat to find
the cause and fix it. The chat bar shows one above its line until it is fixed or dismissed; an app outside Python builds
the same shape from the TypeScript this class's language adapter generates, so no failure is shown differently.
"""
from __future__ import annotations

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool
from harness.installation.data_class import data_field, language_adapter
from harness.mcp.mcp_annotations import mcp


@language_adapter(language="typescript")
@agent_toolset
class Failure:
    """One failure as a person sees it: what failed with the reason it gave, and the context it failed in."""

    def __init__(self, failure: str = "", context: str = "") -> None:
        self._failure = failure
        self._context = context

    @classmethod
    @mcp
    @agent_tool
    def describe(cls, failure: str, context: str) -> Failure:
        """The failure as it is shown: failure says what failed and the reason it gave, context what was being done
        and where, such as the action pressed and the tool it called."""
        return cls(failure, context)

    @property
    @data_field
    def failure(self) -> str:
        return self._failure

    @property
    @data_field
    def context(self) -> str:
        return self._context
