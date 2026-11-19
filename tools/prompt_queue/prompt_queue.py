"""PromptQueue - the prompts one chat has queued to send next, in order, kept behind the cdd server so the chat's
prompt-queue mod, the agent working in the chat, and a session starting in it all add to the same queue."""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
import mimetypes
import re
import uuid
from pathlib import Path
from typing import Literal, NotRequired, TypedDict

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
# How many hex characters of a random id name a queued prompt: short enough to read in the queue, enough not to repeat.
_PROMPT_ID_LENGTH = 12
# The folder beside a chat's queue file that holds the images and documents queued with its prompts.
ATTACHMENTS_FOLDER = "attachments"
# The folder that keeps a JSON copy of every prompt clear or remove took off, so the work stays on record: in the session's
# folder the queue's chat works in, else beside the chat's queue file.
ARCHIVE_FOLDER = "queue-archive"
# What marks a step that came from a message the person sent: a correction or comment filed under the goal it belongs to.
INTERRUPTION_MARK = "[interruption]"
# The section of a handoff that holds the numbered steps the next agent takes (space/session/HANDOFF-FORMAT.md).
_APPROACH_HEADING = re.compile(r"^##\s+Approach for Next Agent\s*$", re.IGNORECASE)
_NEXT_SECTION = re.compile(r"^##\s")
# A numbered step: `1. Read this handoff`, `2) Run the unit tier`.
_NUMBERED_STEP = re.compile(r"^\s*\d+[.)]\s+(.*)$")


# Where a step stands: not started, the one being worked, or finished.
StepState = Literal["pending", "in_progress", "done"]


class PromptStep(TypedDict):
    """One thing the agent plans to do for a queued prompt: its text and where it stands."""

    text: str
    state: StepState


class QueuedPrompt(TypedDict):
    """One prompt on the queue: its own id, which stays when the prompt moves or is edited, its text, the steps the
    agent planned for it, none until it plans them, and whether its work is done; a finished prompt stays on the queue,
    drawn dim, until the queue is cleared."""

    id: str
    text: str
    steps: NotRequired[list[PromptStep]]
    attachments: NotRequired[list[str]]
    is_done: NotRequired[bool]
    robot: NotRequired[str]


class StepNotPlanned(LookupError):
    """A call named a step of a queued prompt that the prompt's steps do not reach."""

    def __init__(self, prompt: str, step: int, planned: int) -> None:
        super().__init__(f"prompt {prompt!r} has {planned} steps, so it has no step {step}")
        self.prompt = prompt
        self.step = step
        self.planned = planned


class PromptNotQueued(LookupError):
    """A call named a prompt the queue does not hold, such as one already sent or removed."""

    def __init__(self, prompt: str, chat: str, held: list[str], taken_off: str = "") -> None:
        """The queue of chat, which holds the prompts held, was read: a call that names another chat reads another
        queue. taken_off is when the chat's queue archive says the prompt was taken off it; empty when it never was."""
        told = f"no prompt {prompt!r} is on the queue of chat {chat}, which holds {', '.join(held) or 'nothing'}"
        super().__init__(f"{told}; {prompt} was taken off the queue at {taken_off}" if taken_off else told)
        self.prompt = prompt


@noCatalog
@identity("chat")
@language_adapter(language="typescript")
@agent_toolset
class PromptQueue:
    """The prompts one chat has queued, in the order they will be done. The chat's prompt-queue mod draws it and shows
    it to the agent while it plays; the agent does the prompts in order and marks each one done; an agent in the chat
    queues work on it the same way; switching the chat to a session queues that session's handoff steps on it."""

    def __init__(self, chat: str, file: Path, archive: Path | None = None) -> None:
        self._chat = chat
        self._file = JsonFile(file)
        self._archive_folder = archive or file.parent / ARCHIVE_FOLDER

    @classmethod
    @tool_subject
    def load(cls, chat: str, *, call: ToolCall) -> PromptQueue:
        """The queue of chat; with chat empty, of the chat the call came from, so an agent queues work on its own
        chat's queue without knowing its id. Prompts taken off it are archived in the folder of the session the call
        works in: its work folder, in the ticket's worktree, beside the rest of that session's work; in no session,
        beside the queue in the chat's folder."""
        chat = chat or call.chat_id
        session = call.session
        archive = session.work_folder / ARCHIVE_FOLDER if session is not None and session.work_folder is not None else None
        return cls(chat, CHATS_FOLDER.path / chat / QUEUE_FILE, archive)

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
        added = [{"id": uuid.uuid4().hex[:_PROMPT_ID_LENGTH], "text": text.strip()} for text in texts if text.strip()]
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
        """Take the queued prompt whose id is prompt off the queue, keeping a copy of it in the chat's queue archive."""
        held = self._holding(prompt)
        self._archive([item for item in held if item["id"] == prompt])
        return self._keep([item for item in held if item["id"] != prompt])

    @mcp
    @agent_tool
    def clear(self) -> PromptQueue:
        """Take the finished prompts off the queue, leaving the work still to do; with none finished, take every prompt off."""
        held = self.prompts
        unfinished = [item for item in held if not item.get("is_done", False)]
        kept = [] if len(unfinished) == len(held) else unfinished
        self._archive([item for item in held if item not in kept])
        return self._keep(kept)

    @mcp
    @agent_tool
    def done(self, prompt: str) -> PromptQueue:
        """Mark the prompt whose id is prompt done once its work is done: it stays in its place, drawn dim, so the person sees it finish, and the next prompt not done is the next to do. An agent working through the queue does each prompt in order, first to last, and calls this as it finishes each one."""
        return self._keep([{**held, "is_done": True} if held["id"] == prompt else held for held in self._holding(prompt)])

    @mcp
    @agent_tool
    def reopen(self, prompt: str) -> PromptQueue:
        """Open the done prompt whose id is prompt again so it runs again: it is no longer done, and its steps are not started. The person moves the queue's pointer back onto it to rerun its work."""
        return self._keep([self._reopened(held) if held["id"] == prompt else held for held in self._holding(prompt)])

    @mcp
    @agent_tool
    def assign(self, prompt: str, robot: str) -> PromptQueue:
        """Give the queued prompt whose id is prompt to the robot named robot, the sub-agent that works it in sub-agent mode: the queue keeps it, so each robot's queue comes back after a reload. An empty robot takes the prompt off its robot."""
        return self._keep([self._assigned(held, robot.strip()) if held["id"] == prompt else held for held in self._holding(prompt)])

    @mcp
    @agent_tool
    def set_steps(self, prompt: str, steps: list[PromptStep]) -> PromptQueue:
        """Give the queued prompt whose id is prompt the steps planned for it, in order, each its text and its state: pending, in_progress, or done. They replace any steps it had, so the agent's task list for the prompt is copied whole each time it changes."""
        planned = [{"text": step["text"].strip(), "state": step["state"]} for step in steps]
        return self._keep([{**held, "steps": planned} if held["id"] == prompt else held for held in self._holding(prompt)])

    @mcp
    @agent_tool
    def add_interruption(self, prompt: str, text: str) -> PromptQueue:
        """File a message the person sent under the goal whose id is prompt: it becomes that goal's last step, not started, its text starting [interruption], and a done goal opens again, since it has work again. The agent moves it to a card of its own with add when it is separate work."""
        held = self._holding(prompt)
        goal = next(item for item in held if item["id"] == prompt)
        filed = [*goal.get("steps", []), {"text": f"{INTERRUPTION_MARK} {text.strip()}", "state": "pending"}]
        return self._keep([{**item, "steps": filed, "is_done": False} if item["id"] == prompt else item for item in held])

    @mcp
    @agent_tool
    def step_done(self, prompt: str, step: int) -> PromptQueue:
        """Mark step number step, counted from 1, of the queued prompt whose id is prompt done. The prompt stays on the queue until it is marked done with done, even once every step is done."""
        held = self._holding(prompt)
        planned = next(item for item in held if item["id"] == prompt).get("steps", [])
        if not 1 <= step <= len(planned):
            raise StepNotPlanned(prompt, step, len(planned))
        ticked = [{**planned_step, "state": "done"} if number == step else planned_step for number, planned_step in enumerate(planned, start=1)]
        return self._keep([{**item, "steps": ticked} if item["id"] == prompt else item for item in held])

    @mcp
    @agent_tool
    def attach(self, prompt: str, filename: str, media_type: str, data: str) -> PromptQueue:
        """Keep an image or document pasted in a queued draft beside the queued prompt whose id is prompt: data is its bytes in base64, saved as a file in this chat's folder whose path the prompt lists under attachments, for the agent to open when it takes the prompt."""
        held = self._holding(prompt)
        listed = next(item for item in held if item["id"] == prompt).get("attachments", [])
        saved = self._saved_attachment(prompt, len(listed) + 1, filename, media_type, data)
        return self._keep([{**item, "attachments": [*listed, str(saved)]} if item["id"] == prompt else item for item in held])

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

    def _saved_attachment(self, prompt: str, number: int, filename: str, media_type: str, data: str) -> Path:
        """The file an attachment is saved as: named for its prompt and its place among the prompt's attachments, with
        the extension of its name, else of its media type."""
        extension = Path(filename).suffix or mimetypes.guess_extension(media_type) or ""
        saved = self._file.path.parent / ATTACHMENTS_FOLDER / f"{prompt}-{number}{extension}"
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(base64.b64decode(data))
        return saved

    def _archive(self, prompts: list[QueuedPrompt]) -> None:
        """Keeps a JSON copy of prompts taken off the queue in the chat's queue archive, one file for each time, named
        for when they were taken off; nothing taken off writes nothing."""
        if not prompts:
            return
        taken_off = datetime.now(timezone.utc)
        self._archive_folder.mkdir(parents=True, exist_ok=True)
        saved = self._archive_folder / f"{taken_off.strftime('%Y%m%dT%H%M%S%fZ')}.json"
        saved.write_text(json.dumps({"chat": self._chat, "taken_off": taken_off.isoformat(), "prompts": prompts}, indent=2), encoding="utf-8")

    def _holding(self, prompt: str) -> list[QueuedPrompt]:
        """The prompts queued, refusing a prompt id the queue does not hold."""
        held = self.prompts
        if not any(item["id"] == prompt for item in held):
            raise PromptNotQueued(prompt, self._chat, [item["id"] for item in held], self._taken_off(prompt))
        return held

    def _taken_off(self, prompt: str) -> str:
        """When the chat's queue archive says prompt was taken off the queue, the latest time; empty when it holds none."""
        if not self._archive_folder.is_dir():
            return ""
        archived = (json.loads(saved.read_text(encoding="utf-8")) for saved in sorted(self._archive_folder.glob("*.json"), reverse=True))
        return next((record.get("taken_off", "") for record in archived if any(item.get("id") == prompt for item in record.get("prompts", []))), "")

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

    def _reopened(self, prompt: QueuedPrompt) -> QueuedPrompt:
        """The prompt not done, each of its steps not started."""
        steps = {"steps": [{**step, "state": "pending"} for step in prompt["steps"]]} if "steps" in prompt else {}
        return {**prompt, "is_done": False, **steps}

    def _assigned(self, prompt: QueuedPrompt, robot: str) -> QueuedPrompt:
        """The prompt given to robot, or to no robot when robot is empty."""
        unassigned = {key: value for key, value in prompt.items() if key != "robot"}
        return {**unassigned, "robot": robot} if robot else unassigned


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
