"""PromptQueue - the prompts one chat has queued to send next, in order, kept behind the cdd server so the chat's
prompt-queue mod, the agent working in the chat, and a session starting in it all add to the same queue."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import TypedDict

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.annotations.annotation import noCatalog
from harness.chat.chat import CHATS_FOLDER
from harness.installation.data_class import data_field, identity, language_adapter
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.mcp.mcp_annotations import mcp

# The file in a chat's own folder that holds its queue.
QUEUE_FILE = "prompt-queue.json"
# The section of a handoff that holds the numbered steps the next agent takes (space/session/HANDOFF-FORMAT.md).
_APPROACH_HEADING = re.compile(r"^##\s+Approach for Next Agent\s*$", re.IGNORECASE)
_NEXT_SECTION = re.compile(r"^##\s")
# A numbered step: `1. Read this handoff`, `2) Run the unit tier`.
_NUMBERED_STEP = re.compile(r"^\s*\d+[.)]\s+(.*)$")


class QueuedPrompt(TypedDict):
    """One prompt on the queue: its own id, which stays when the prompt moves or is edited, and its text."""

    id: str
    text: str


class PromptNotQueued(LookupError):
    """A call named a prompt the queue does not hold, such as one already sent or removed."""

    def __init__(self, prompt: str) -> None:
        super().__init__(f"no prompt {prompt!r} is on the queue: it was sent or removed")
        self.prompt = prompt


@noCatalog
@identity("chat")
@language_adapter(language="typescript")
@agent_toolset
class PromptQueue:
    """The prompts one chat has queued, in the order they will be sent. The chat's prompt-queue mod shows it and sends
    the next one as each turn ends; an agent in the chat queues work on it the same way; switching the chat to a session
    queues that session's handoff steps on it."""

    def __init__(self, chat: str, file: Path) -> None:
        self._chat = chat
        self._file = JsonFile(file)

    @classmethod
    @tool_subject
    def load(cls, chat: str, *, call: ToolCall) -> PromptQueue:
        """The queue of chat; with chat empty, of the chat the call came from, so an agent queues work on its own
        chat's queue without knowing its id."""
        return cls.of_chat(chat or call.chat_id)

    @classmethod
    def of_chat(cls, chat: str) -> PromptQueue:
        """The queue of the chat whose id is chat, kept in that chat's own folder."""
        return cls(chat, CHATS_FOLDER.path / chat / QUEUE_FILE)

    @property
    @data_field
    def chat(self) -> str:
        """The id of the chat whose queue this is."""
        return self._chat

    @property
    @data_field
    def prompts(self) -> list[QueuedPrompt]:
        """The prompts queued, first to be sent first."""
        return list(self._held().get("prompts", []))

    @mcp
    @agent_tool
    def show(self) -> PromptQueue:
        """Answer this chat's prompt queue: the prompts queued, first to be sent first."""
        return self

    @mcp
    @agent_tool
    def add(self, text: str) -> PromptQueue:
        """Queue text at the bottom of this chat's prompt queue, to be sent after every prompt already on it. A slash command queued runs as that command. Text that is only spaces queues nothing."""
        return self.add_all([text])

    @mcp
    @agent_tool
    def add_all(self, texts: list[str]) -> PromptQueue:
        """Queue each of texts at the bottom of this chat's prompt queue, in order, one prompt each: a list of work for the chat to do next. Texts that are only spaces queue nothing."""
        added = [{"id": uuid.uuid4().hex[:12], "text": text.strip()} for text in texts if text.strip()]
        return self._keep([*self.prompts, *added])

    @mcp
    @agent_tool
    def edit(self, prompt: str, text: str) -> PromptQueue:
        """Change the text of the queued prompt whose id is prompt, keeping its place."""
        return self._keep([{**held, "text": text.strip()} if held["id"] == prompt else held for held in self._holding(prompt)])

    @mcp
    @agent_tool
    def move(self, prompt: str, to: int) -> PromptQueue:
        """Move the queued prompt whose id is prompt to place to, counted from 0 at the front of the queue."""
        held = self._holding(prompt)
        moving = next(item for item in held if item["id"] == prompt)
        rest = [item for item in held if item["id"] != prompt]
        rest.insert(max(0, min(to, len(rest))), moving)
        return self._keep(rest)

    @mcp
    @agent_tool
    def remove(self, prompt: str) -> PromptQueue:
        """Take the queued prompt whose id is prompt off the queue."""
        return self._keep([item for item in self._holding(prompt) if item["id"] != prompt])

    @mcp
    @agent_tool
    def clear(self) -> PromptQueue:
        """Take every prompt off the queue."""
        return self._keep([])

    @mcp
    @agent_tool
    def take_next(self, passing_over: str = "") -> QueuedPrompt | None:
        """Take the first prompt off the queue to send it now, as the mod does when a turn ends while the queue plays, passing over the prompt whose id is passing_over, one the person is editing, which waits in its place until it is queued again; none when no prompt may be sent."""
        held = self.prompts
        sent = next((item for item in held if item["id"] != passing_over), None)
        if sent is None:
            return None
        self._keep([item for item in held if item is not sent])
        return sent

    def queue_handoff(self, handoff: Path) -> int:
        """Queue the numbered steps of handoff's Approach for Next Agent, in order, one prompt each, so a chat opening a
        session has its next work lined up; a handoff already queued on this chat queues nothing again. Answers how many
        steps it queued."""
        held = self._held()
        if handoff.name in held.get("handoffs", []):
            return 0
        steps = handoff_steps(handoff.read_text(encoding="utf-8")) if handoff.is_file() else []
        self.add_all(steps)
        self._file.write({**self._held(), "handoffs": [*held.get("handoffs", []), handoff.name]})
        return len(steps)

    def _holding(self, prompt: str) -> list[QueuedPrompt]:
        """The prompts queued, refusing a prompt id the queue does not hold."""
        held = self.prompts
        if not any(item["id"] == prompt for item in held):
            raise PromptNotQueued(prompt)
        return held

    def _held(self) -> dict:
        """What the queue's file holds; an empty queue when it has none yet."""
        if not self._file.exists():
            return {}
        try:
            return self._file.read()
        except JsonFileUnreadable:
            return {}

    def _keep(self, prompts: list[QueuedPrompt]) -> PromptQueue:
        self._file.path.parent.mkdir(parents=True, exist_ok=True)
        self._file.write({**self._held(), "prompts": prompts})
        return self


def handoff_steps(text: str) -> list[str]:
    """The numbered steps of a handoff's Approach for Next Agent, each with the lines that continue it; none when it has
    no such section."""
    steps: list[str] = []
    is_inside = False
    for line in text.splitlines():
        if _APPROACH_HEADING.match(line):
            is_inside = True
            continue
        if not is_inside:
            continue
        if _NEXT_SECTION.match(line):
            break
        step = _NUMBERED_STEP.match(line)
        if step:
            steps.append(step.group(1).strip())
        elif steps and line.strip() and line.startswith((" ", "\t")):
            steps[-1] = f"{steps[-1]} {line.strip()}"
    return steps
