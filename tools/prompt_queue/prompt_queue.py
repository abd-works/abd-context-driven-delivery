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
from typing import Callable, Literal, TypedDict, get_args

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.annotations.annotation import noCatalog
from harness.chat.chat import CHATS_FOLDER
from harness.installation.data_class import data_field, identity, language_adapter
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.mcp.mcp_annotations import mcp
from space.session.open_sessions import OpenSessions
from space.session.session import Session

# The file in a chat's own folder that holds its queue.
QUEUE_FILE = "prompt-queue.json"
# How many hex characters of a random id name a queued prompt: short enough to read in the queue, enough not to repeat.
_PROMPT_ID_LENGTH = 12
# The folder beside a chat's queue file that holds the images and documents queued with its prompts.
ATTACHMENTS_FOLDER = "attachments"
# The folder that keeps a JSON copy of every prompt clear, remove or flush took off, and of the whole queue file each flush
# found, so the work stays on record: in the session's folder the queue's chat works in, else beside the chat's queue file.
ARCHIVE_FOLDER = "queue-archive"
# How a copy of the whole queue file that flush keeps in the queue archive is named, before the time it was copied: it
# holds the queue as it stood, not prompts taken off, so the lookup of when a prompt was taken off reads past it.
WHOLE_FILE_COPY = "prompt-queue-"
# What marks a step that came from a message the person sent: a correction or comment filed under the goal it belongs to.
INTERRUPTION_MARK = "[interruption]"
# The state the Claude app puts before a message the person sends while a board viewer is open: the viewer's live state
# as JSON with a note about it, written by the viewer's page, never by the person, so the queue keeps none of it.
_VIEWER_STATE = re.compile(r"\s*<artifact-view-context\b[^>]*>.*?(?:</artifact-view-context>\s*|$)", re.DOTALL)
# What marks a prompt that waits for the person's answer to a decision: the queue's pointer passes over it.
DECISION_MARK = "[decision required]"
# The key under which the queue's file lists each source, such as a handoff, whose prompts were queued once.
_QUEUED_SOURCES = "handoffs"
# What a chat that opened a session is told once its latest handoff's next steps are on its queue.
_HANDOFF_QUEUED_NOTE = (
    "**Handoff queued.** The {count} steps of {handoff}'s Approach for Next Agent are on this chat's prompt queue, in "
    "order: work through them first to last, calling prompt-queue.done with each prompt's id as you finish it; "
    "prompt-queue.show lists them.\n\n"
)


# Where a step stands: not started, the one being worked, or finished.
StepState = Literal["pending", "in_progress", "done"]
STEP_STATES: tuple[str, ...] = get_args(StepState)
# What a chat id may not hold, since each would make it a path to another folder: a folder separator, a drive's colon,
# and the two dots that name the folder above.
_PATH_MARKS = ("/", "\\", ":", "..")


def persons_words(text: str) -> str:
    """text as the person wrote it: any board viewer's state the Claude app put in the message taken out, so a step or
    card says what the person asked for instead of where their viewer stood, and outer spaces trimmed."""
    return _VIEWER_STATE.sub(" ", text).strip()


# A markdown line's own marks, so a heading or a list item reads as its words.
_LINE_MARKS = re.compile(r"^\s*(?:#+|[-*>]|\d+[.)])\s+")
# A message that is only an answer or an acknowledgement, such as yes, no, ok or thanks.
_ANSWER = re.compile(
    r"^(?:y|n|yes|yeah|yep|no|nope|ok|okay|k|sure|thanks|thank you|thx|agreed|agree|done|good|great|fine|right|correct"
    r"|got it|go|go ahead|do it)[\s.!]*$", re.IGNORECASE)
# A message that is only marks, such as ??? or !.
_ONLY_MARKS = re.compile(r"^[\s?!.,]*$")
# The words a question opens with.
_QUESTION_OPENING = re.compile(
    r"^(?:why|what|where|when|who|which|how|is|are|was|were|do|does|did|can|could|should|would|will|has|have|isn't"
    r"|aren't|doesn't|don't|didn't)\b", re.IGNORECASE)
# The words that ask for work, so a message holding them is work even when it also asks something.
_ASKS_FOR_WORK = re.compile(
    r"\b(?:please|pls|fix|add|make|change|remove|delete|move|rename|build|write|run|deploy|pin|repin|commit|push|merge"
    r"|update|create|implement|refactor|restart|install|open|close|start|stop|put|send|show|hide)\b", re.IGNORECASE)
# Where a paste starts: a paste is the person's material for work, so a message holding one is never only talk.
_PASTE_OPENING = re.compile(r"<pasted_content\b", re.IGNORECASE)
# The most words a message that is only talk holds; a longer one is likely to ask for something.
_TALK_WORDS = 15


class SentMessage:
    """A message the person sent straight to the chat, read for whether it asks for work."""

    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def is_only_talk(self) -> bool:
        """Whether the message is only talk, not work to do: an answer or an acknowledgement (yes, ok, thanks), only
        marks (???), or a short question that asks for no work (why is there no flush button?). The chat answers talk,
        so the agent is not asked to place it on the queue. A board viewer's state is not the person's words, and a
        message that is nothing else is talk; a message holding a paste never is."""
        if _PASTE_OPENING.search(self._text):
            return False
        words = self._words
        if _ONLY_MARKS.match(words) or _ANSWER.match(words):
            return True
        return self._is_question(words) and len(words.split(" ")) <= _TALK_WORDS and not _ASKS_FOR_WORK.search(words)

    @property
    def _words(self) -> str:
        """The person's words as one line, each markdown line's own marks taken off."""
        lines = (_LINE_MARKS.sub("", line).strip() for line in persons_words(self._text).splitlines())
        return re.sub(r"\s+", " ", " ".join(line for line in lines if line))

    def _is_question(self, words: str) -> bool:
        return words.rstrip().endswith("?") or bool(_QUESTION_OPENING.match(words))


class PromptStep(TypedDict):
    """One thing the agent plans to do for a queued prompt, as the queue's file and set_steps hold it: its text and
    where it stands. A step has no behaviour of its own: its prompt's *PromptSteps* change it."""

    text: str
    state: StepState


class StepNotPlanned(LookupError):
    """A call named a step of a queued prompt that the prompt's steps do not reach."""

    def __init__(self, prompt: str, step: int, planned: int) -> None:
        super().__init__(f"prompt {prompt!r} has {planned} steps, so it has no step {step}")
        self.prompt = prompt
        self.step = step
        self.planned = planned


class StepStateUnknown(ValueError):
    """A call gave a step a state that is none of the states a step has."""

    def __init__(self, state: str) -> None:
        super().__init__(f"{state!r} is not a step's state, which is one of {', '.join(STEP_STATES)}")
        self.state = state


class PromptSteps:
    """*PromptSteps* are the steps the agent planned for one queued prompt, in order, and their pointer: the first step
    not done, which the agent works next. Each change moves a step or its state; steps are numbered from 1, as a person
    counts them."""

    def __init__(self, prompt: str, steps: list[PromptStep]) -> None:
        self._prompt = prompt
        self._steps = [dict(step) for step in steps]

    @property
    def listed(self) -> list[PromptStep]:
        """The steps, in order, each its text and its state."""
        return [{"text": step["text"], "state": step["state"]} for step in self._steps]

    @property
    def pointer(self) -> int:
        """The place, from 0, of the first step not done; past the last step when every step is done."""
        return next((place for place, step in enumerate(self._steps) if step["state"] != "done"), len(self._steps))

    def done(self, number: int) -> None:
        """Mark step number done."""
        self._step(number)["state"] = "done"

    def move(self, step: int, place: int) -> None:
        """Move step number step to place place among the steps, both counted from 1; a place past either end moves
        nothing."""
        moving = self._step(step)
        if not 1 <= place <= len(self._steps):
            return
        self._steps.remove(moving)
        self._steps.insert(place - 1, moving)

    def remove(self, step: int) -> None:
        """Take step number step off."""
        self._steps.remove(self._step(step))

    def back(self) -> None:
        """The pointer moves up: the done step above it is worked again, and every step after that is not started.
        With no step done, nothing changes."""
        above = self.pointer - 1
        if above < 0:
            return
        for place, step in enumerate(self._steps):
            if place >= above:
                step["state"] = "in_progress" if place == above else "pending"

    def on(self) -> None:
        """The pointer moves down: its step is done, and the step after it is the one worked. With every step done,
        nothing changes."""
        pointed = self.pointer
        if pointed >= len(self._steps):
            return
        self._steps[pointed]["state"] = "done"
        if pointed + 1 < len(self._steps):
            self._steps[pointed + 1]["state"] = "in_progress"

    def restarted(self) -> None:
        """Every step not started, as when its prompt opens again."""
        for step in self._steps:
            step["state"] = "pending"

    def plan(self, steps: list[PromptStep]) -> None:
        """Replace the steps with steps, in order: a step whose text is only spaces is left out, and a state that is
        none of a step's states is refused."""
        unknown = next((step["state"] for step in steps if step["state"] not in STEP_STATES), None)
        if unknown is not None:
            raise StepStateUnknown(unknown)
        self._steps = [{"text": step["text"].strip(), "state": step["state"]} for step in steps if step["text"].strip()]

    def add(self, text: str) -> None:
        """Add text as the last step, not started."""
        self._steps.append({"text": text, "state": "pending"})

    def take_off_interruptions(self) -> list[str]:
        """Take off the person's interruptions not done yet and answer their texts, in order; the agent's own steps and
        the interruptions already done stay."""
        taken = [step for step in self._steps if step["text"].startswith(INTERRUPTION_MARK) and step["state"] != "done"]
        self._steps = [step for step in self._steps if step not in taken]
        return [step["text"] for step in taken]

    def _step(self, number: int) -> dict:
        if not 1 <= number <= len(self._steps):
            raise StepNotPlanned(self._prompt, number, len(self._steps))
        return self._steps[number - 1]


@identity("id")
class QueuedPrompt:
    """*QueuedPrompt* is one prompt on a chat's queue: its own id, which stays when the prompt moves or is edited, its
    text, the steps the agent planned for it, the files queued with it, the robot it is given to in sub-agent mode, and
    whether its work is done; a finished prompt stays on the queue, drawn dim, until the queue is cleared. It changes
    itself, and ``record`` is what the queue's file keeps of it, in the keys every lane's server reads."""

    def __init__(self, record: dict) -> None:
        self._id: str = record["id"]
        self._text: str = record["text"]
        # Whether the file named each optional field, so record writes back exactly the keys it read.
        self._has_steps = "steps" in record
        self.steps = PromptSteps(self._id, list(record.get("steps", [])))
        self._attachments: list[str] | None = list(record["attachments"]) if "attachments" in record else None
        self._is_done: bool | None = record.get("is_done") if "is_done" in record else None
        self._robot: str = record.get("robot", "")
        self._deleted_attachments: list[str] = list(record.get("deleted_attachments", []))

    @classmethod
    def new(cls, text: str) -> QueuedPrompt:
        """A new prompt of text, with an id of its own."""
        return cls({"id": uuid.uuid4().hex[:_PROMPT_ID_LENGTH], "text": persons_words(text)})

    @property
    @data_field
    def id(self) -> str:
        return self._id

    @property
    @data_field
    def text(self) -> str:
        return self._text

    @property
    @data_field(key="steps")
    def listed_steps(self) -> list[PromptStep]:
        """The steps planned for it, in order; none until the agent plans them."""
        return self.steps.listed

    @property
    @data_field
    def step_pointer(self) -> int:
        """The place, from 0, of its first step not done, where its steps' pointer stands."""
        return self.steps.pointer

    @property
    @data_field
    def attachments(self) -> list[str]:
        """The files queued with it, each a path in the chat's folder."""
        return list(self._attachments or [])

    @property
    @data_field
    def is_done(self) -> bool:
        return bool(self._is_done)

    @property
    @data_field
    def robot(self) -> str:
        """The robot it is given to in sub-agent mode; empty for none."""
        return self._robot

    @property
    @data_field
    def is_waiting(self) -> bool:
        """Whether it waits to be done: not done, and asking no decision of the person, which a prompt whose text
        starts with [decision required] does. The queue's pointer stands on the first prompt that waits."""
        return not self.is_done and not self._text.startswith(DECISION_MARK)

    def edit(self, text: str) -> None:
        """Change its text to text; text that is only spaces changes nothing."""
        if text.strip():
            self._text = text.strip()

    def mark_done(self) -> None:
        self._is_done = True

    def reopen(self) -> None:
        """Not done, and each of its steps not started, so it runs again."""
        self._is_done = False
        self.steps.restarted()

    def assign(self, robot: str) -> None:
        """Give it to robot; an empty robot takes it off its robot."""
        self._robot = robot.strip()

    def plan(self, steps: list[PromptStep]) -> None:
        """Give it steps, in place of any it had."""
        self.steps.plan(steps)
        self._has_steps = True

    def interrupt(self, text: str) -> None:
        """File a message the person sent under it: its last step, not started, marked as an interruption; a done
        prompt opens again, since it has work again. Only the person's words are filed, so a message that is only spaces,
        or only a board viewer's state, files nothing."""
        words = persons_words(text)
        if not words:
            return
        self.steps.add(f"{INTERRUPTION_MARK} {words}")
        self._has_steps = True
        self._is_done = False

    def split_off(self) -> list[QueuedPrompt]:
        """Each interruption filed under it and not done yet, taken off its steps as a card of its own, given its robot."""
        split = [QueuedPrompt.new(text) for text in self.steps.take_off_interruptions()]
        for card in split:
            card.assign(self._robot)
        return split

    def attach(self, file: Path) -> None:
        """List file among the files queued with it."""
        self._attachments = [*(self._attachments or []), str(file)]

    def delete_attachments(self, folder: Path) -> None:
        """Delete the files queued with it that folder, the chat's attachments folder, holds, as it leaves the queue:
        nothing reads them once the card is gone, so they would only grow the chat's folder. It then names them as
        deleted, no longer as attached. A file listed outside folder is not the queue's to delete, so it stays listed."""
        held = folder.resolve()
        deleted = [file for file in self.attachments if Path(file).resolve().parent == held]
        for file in deleted:
            Path(file).unlink(missing_ok=True)
        self._deleted_attachments = [*self._deleted_attachments, *deleted]
        self._attachments = [file for file in self.attachments if file not in deleted] or None

    @property
    def record(self) -> dict:
        """What the queue's file keeps of it: id and text, and steps, attachments, is_done and robot only when it has
        them, the keys the stable and dev lanes' servers both read; and, once it has left the queue, the files deleted
        with it, which only its copy in the queue archive keeps."""
        kept: dict = {"id": self._id, "text": self._text}
        if self._has_steps:
            kept["steps"] = self.steps.listed
        if self._attachments is not None:
            kept["attachments"] = list(self._attachments)
        if self._is_done is not None:
            kept["is_done"] = self._is_done
        if self._robot:
            kept["robot"] = self._robot
        if self._deleted_attachments:
            kept["deleted_attachments"] = list(self._deleted_attachments)
        return kept


class ChatIdNotAnId(ValueError):
    """A call named a chat by something that is not a chat id: empty, or a path that leads out of the chat's own folder."""

    def __init__(self, chat: str) -> None:
        super().__init__(f"{chat!r} is not a chat id: a chat id names one chat's folder, so it is not empty and holds no /, \\, : or ..")
        self.chat = chat


class ChatNotKnown(LookupError):
    """A call from one chat named another chat that no folder in the chats folder is kept for: a mistyped chat id, or a
    chat that never connected. Queued there, the card would wait on a queue nobody reads while the caller is told it
    worked."""

    def __init__(self, chat: str, chats_folder: Path) -> None:
        super().__init__(f"no chat {chat!r} is known: the chats folder {chats_folder} keeps no folder for it; check the chat id, or name no chat to use the calling chat's own queue")
        self.chat = chat


class QueueFileUnreadable(JsonFileUnreadable):
    """A chat's queue file does not hold a prompt queue: it is damaged, cut off, empty, or holds something other than
    cards that each have an id of their own and a text. Nothing is written over it, so what it holds stays for a person
    to repair."""

    def message(self, path: Path, cause: Exception) -> str:
        return f"the prompt queue file {path} does not hold a prompt queue ({cause}); nothing is written over it, so repair it or move it away"


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
    queues work on it the same way; switching the chat to a session queues that session's handoff steps on it. Several
    processes change one chat's queue, the stable lane's cdd server and the dev lane's among them, so each change holds
    the queue's file from its read to its write and no caller's change is lost."""

    def __init__(self, chat: str, file: Path, archive: Path | None = None) -> None:
        self._chat = chat
        self._folder = file.parent
        self._file = JsonFile(file, QueueFileUnreadable)
        self._archive_folder = archive or file.parent / ARCHIVE_FOLDER
        self._attachments_folder = file.parent / ATTACHMENTS_FOLDER

    @classmethod
    @tool_subject
    def load(cls, chat: str, *, call: ToolCall) -> PromptQueue:
        """The queue of chat; with chat empty, of the chat the call came from, so an agent queues work on its own
        chat's queue without knowing its id. Another chat must be one the chats folder keeps a folder for, else
        *ChatNotKnown* is raised and nothing is written, so a mistyped chat id never makes a queue nobody reads. Prompts taken off it are archived in the folder of the session the call
        works in: its work folder, in the ticket's worktree, beside the rest of that session's work; in no session,
        beside the queue in the chat's folder."""
        session = call.session
        archive = session.work_folder / ARCHIVE_FOLDER if session is not None and session.work_folder is not None else None
        named = chat.strip() or call.chat_id
        queue = cls.of_chat(named, archive)
        if named != call.chat_id and not queue.is_kept:
            raise ChatNotKnown(named, CHATS_FOLDER.path)
        return queue

    @classmethod
    def of_chat(cls, chat: str, archive: Path | None = None) -> PromptQueue:
        """The queue of the chat whose id is chat, kept in that chat's own folder, its archive in the folder archive
        when one is given. A chat id is never a path: an empty one, or one holding a folder separator, a drive or two
        dots, is refused, so no queue is written outside the chats folder."""
        if not chat.strip() or any(mark in chat for mark in _PATH_MARKS):
            raise ChatIdNotAnId(chat)
        return cls(chat, CHATS_FOLDER.path / chat / QUEUE_FILE, archive)

    @property
    def is_kept(self) -> bool:
        """Whether the chat's own folder is there, which its first check-in or its first queued card makes."""
        return self._folder.is_dir()

    @property
    @data_field
    def chat(self) -> str:
        """The id of the chat whose queue this is."""
        return self._chat

    @property
    @data_field
    def prompts(self) -> list[QueuedPrompt]:
        """The prompts queued, first to be sent first. A file whose prompts are not cards that each have a text and an
        id of their own is refused, since a change made to such a file changes the wrong card or none."""
        cards = self._file.read().get("prompts", [])
        if not isinstance(cards, list):
            raise self._misshapen(f"its prompts are {type(cards).__name__}, not a list of cards")
        places: dict[str, int] = {}
        for place, card in enumerate(cards, start=1):
            if not isinstance(card, dict) or not isinstance(card.get("text"), str):
                raise self._misshapen(f"card {place} has no text: {card!r}")
            if not isinstance(card.get("id"), str) or not card["id"]:
                raise self._misshapen(f"card {place} has no id: {card!r}")
            if card["id"] in places:
                raise self._misshapen(f"cards {places[card['id']]} and {place} share the id {card['id']!r}")
            places[card["id"]] = place
        return [QueuedPrompt(card) for card in cards]

    @property
    @data_field(reference=True)
    def next(self) -> QueuedPrompt | None:
        """The prompt to do next, where the queue's pointer stands: the first that waits, neither done nor asking a
        decision of the person; none when no prompt waits."""
        return next((prompt for prompt in self.prompts if prompt.is_waiting), None)

    def prompt(self, prompt: str) -> QueuedPrompt:
        """The queued prompt whose id is prompt, refused with PromptNotQueued when the queue holds none."""
        return self._found(self.prompts, prompt)

    @mcp
    @agent_tool
    def show(self) -> PromptQueue:
        """Answer this chat's prompt queue: the prompts queued, first to be sent first, and the one to do next."""
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
        with self._file.held():
            return self._keep([*self.prompts, *self._new_prompts(texts)])

    @mcp
    @agent_tool
    def edit(self, prompt: str, text: str) -> PromptQueue:
        """Change the text of the queued prompt whose id is prompt, keeping its place. Text that is only spaces changes nothing."""
        return self._changing(prompt, lambda found: found.edit(text))

    @mcp
    @agent_tool
    def move(self, prompt: str, to: int) -> PromptQueue:
        """Move the queued prompt whose id is prompt to place to, counted from 0 at the front of the queue."""
        with self._file.held():
            held = self.prompts
            moving = self._found(held, prompt)
            rest = [item for item in held if item is not moving]
            rest.insert(max(0, min(to, len(rest))), moving)
            return self._keep(rest)

    @mcp
    @agent_tool
    def remove(self, prompt: str) -> PromptQueue:
        """Take the queued prompt whose id is prompt off the queue, keeping a copy of it in the chat's queue archive; the files attached to it are deleted with it."""
        with self._file.held():
            held = self.prompts
            removed = self._found(held, prompt)
            self._take_off([removed])
            return self._keep([item for item in held if item is not removed])

    @mcp
    @agent_tool
    def clear(self) -> PromptQueue:
        """Take the done prompts off the queue, keeping a copy of them in the chat's queue archive and deleting the files attached to them, and leave the work still to do. With no prompt done, nothing is done to clear: every prompt stays, so a second clear never takes off work a robot may be doing. Answers the queue as it then stands."""
        with self._file.held():
            return self._take_off_done()

    @mcp
    @agent_tool
    def flush(self) -> PromptQueue:
        """Keep a copy of the whole queue file as it stands in the chat's queue archive, named prompt-queue and the time, such as prompt-queue-20261124T044511Z.json, then take the done prompts off as clear does, leaving the work still to do in order. With no prompt done, the copy is still kept and nothing is taken off. Answers the queue as it then stands."""
        with self._file.held():
            self._copy_whole_file()
            return self._take_off_done()

    @mcp
    @agent_tool
    def done(self, prompt: str) -> PromptQueue:
        """Mark the prompt whose id is prompt done once its work is done: it stays in its place, drawn dim, so the person sees it finish, and the next prompt not done is the next to do. An agent working through the queue does each prompt in order, first to last, and calls this as it finishes each one."""
        return self._changing(prompt, QueuedPrompt.mark_done)

    @mcp
    @agent_tool
    def reopen(self, prompt: str) -> PromptQueue:
        """Open the done prompt whose id is prompt again so it runs again: it is no longer done, and its steps are not started. The person moves the queue's pointer back onto it to rerun its work."""
        return self._changing(prompt, QueuedPrompt.reopen)

    @mcp
    @agent_tool
    def assign(self, prompt: str, robot: str) -> PromptQueue:
        """Give the queued prompt whose id is prompt to the robot named robot, the sub-agent that works it in sub-agent mode: the queue keeps it, so each robot's queue comes back after a reload. An empty robot takes the prompt off its robot. A robot already on the queue is matched with no regard to case or outer spaces and keeps the spelling the queue first held, so bOLT and Bolt are one robot."""
        return self._changing(prompt, lambda found: found.assign(self._robot_as_spelled(robot)))

    @mcp
    @agent_tool
    def set_steps(self, prompt: str, steps: list[PromptStep]) -> PromptQueue:
        """Give the queued prompt whose id is prompt the steps planned for it, in order, each its text and its state: pending, in_progress, or done. They replace any steps it had, so the agent's task list for the prompt is copied whole each time it changes. A step whose text is only spaces is left out, and a state that is none of the three is refused."""
        unknown = next((step["state"] for step in steps if step["state"] not in STEP_STATES), None)
        if unknown is not None:
            raise StepStateUnknown(unknown)
        return self._changing(prompt, lambda found: found.plan(steps))

    @mcp
    @agent_tool
    def add_interruption(self, prompt: str, text: str) -> PromptQueue:
        """File a message the person sent under the goal whose id is prompt: it becomes that goal's last step, not started, its text starting [interruption], and a done goal opens again, since it has work again. The agent moves it to a card of its own with add when it is separate work. A message that is only spaces files nothing and opens nothing."""
        return self._changing(prompt, lambda found: found.interrupt(text))

    @mcp
    @agent_tool
    def split(self, prompt: str) -> PromptQueue:
        """Split the goal whose id is prompt when it has gathered the person's interruptions: each [interruption] step not done yet becomes a card of its own, in order, right after the goal and given the goal's robot, and comes off the goal's steps. The goal keeps its own steps and the interruptions already done. A goal with no interruption still to do changes nothing."""
        with self._file.held():
            held = self.prompts
            goal = self._found(held, prompt)
            place = held.index(goal) + 1
            return self._keep([*held[:place], *goal.split_off(), *held[place:]])

    @mcp
    @agent_tool
    def step_done(self, prompt: str, step: int) -> PromptQueue:
        """Mark step number step, counted from 1, of the queued prompt whose id is prompt done. The prompt stays on the queue until it is marked done with done, even once every step is done."""
        return self._changing(prompt, lambda found: found.steps.done(step))

    @mcp
    @agent_tool
    def move_step(self, prompt: str, step: int, place: int) -> PromptQueue:
        """Move step number step of the queued prompt whose id is prompt to place place among its steps, both counted from 1, as the step's up and down buttons do; a place past either end moves nothing."""
        return self._changing(prompt, lambda found: found.steps.move(step, place))

    @mcp
    @agent_tool
    def remove_step(self, prompt: str, step: int) -> PromptQueue:
        """Take step number step, counted from 1, off the queued prompt whose id is prompt."""
        return self._changing(prompt, lambda found: found.steps.remove(step))

    @mcp
    @agent_tool
    def step_back(self, prompt: str) -> PromptQueue:
        """Move the step pointer of the queued prompt whose id is prompt up, as its ▲ does: the done step above the pointer is worked again, and every step after it is not started."""
        return self._changing(prompt, lambda found: found.steps.back())

    @mcp
    @agent_tool
    def step_on(self, prompt: str) -> PromptQueue:
        """Move the step pointer of the queued prompt whose id is prompt down, as its ▼ does: the step it points at is done, and the step after it is the one worked."""
        return self._changing(prompt, lambda found: found.steps.on())

    @mcp
    @agent_tool
    def attach(self, prompt: str, filename: str, media_type: str, data: str) -> PromptQueue:
        """Keep an image or document pasted in a queued draft beside the queued prompt whose id is prompt: data is its bytes in base64, saved as a file in this chat's folder whose path the prompt lists under attachments, for the agent to open when it takes the prompt."""
        return self._changing(prompt, lambda found: found.attach(self._saved_attachment(prompt, len(found.attachments) + 1, filename, media_type, data)))

    @mcp
    @agent_tool
    def is_only_talk(self, message: str) -> dict[str, bool]:
        """Answer whether message, one the person sent straight to the chat, is only talk: an answer, an acknowledgement, only marks, or a short question that asks for no work. The chat answers talk and queues none of it; a board viewer's state in the message is not the person's words, and a message holding a paste is never only talk."""
        return {"is_only_talk": SentMessage(message).is_only_talk}

    def queue_once(self, source: str, texts: list[str]) -> int:
        """Queue texts, in order, one prompt each, once for source, such as the steps of a handoff called source: a
        source already queued on this chat queues nothing again. Answers how many it queued."""
        with self._file.held():
            held = self._file.read()
            if source in held.get(_QUEUED_SOURCES, []):
                return 0
            queued = [*self.prompts, *self._new_prompts(texts)]
            self._file.write({**held, "prompts": [prompt.record for prompt in queued], _QUEUED_SOURCES: [*held.get(_QUEUED_SOURCES, []), source]})
            return len([text for text in texts if text.strip()])

    def _changing(self, prompt: str, change: Callable[[QueuedPrompt], None]) -> PromptQueue:
        """Make change to the queued prompt whose id is prompt and keep the queue, holding the queue's file from its
        read to its write; a prompt the queue does not hold is refused, and nothing changes."""
        with self._file.held():
            held = self.prompts
            change(self._found(held, prompt))
            return self._keep(held)

    def _robot_as_spelled(self, robot: str) -> str:
        """robot as the queue first spelled it: the robot of the first card whose name is robot's, with no regard to case
        or outer spaces; robot without its outer spaces when no card has it. Its caller holds the queue's file."""
        named = robot.strip()
        return next((item.robot for item in self.prompts if item.robot.casefold() == named.casefold()), named)

    def _new_prompts(self, texts: list[str]) -> list[QueuedPrompt]:
        """One prompt, with an id of its own, for each of texts that holds more than spaces and a board viewer's state."""
        return [QueuedPrompt.new(text) for text in texts if persons_words(text)]

    def _misshapen(self, fault: str) -> QueueFileUnreadable:
        """The refusal of the queue's file for fault, what in it is not a prompt queue."""
        return QueueFileUnreadable(self._file.path, ValueError(fault))

    def _saved_attachment(self, prompt: str, number: int, filename: str, media_type: str, data: str) -> Path:
        """The file an attachment is saved as: named for its prompt and its place among the prompt's attachments, with
        the extension of its name, else of its media type."""
        extension = Path(filename).suffix or mimetypes.guess_extension(media_type) or ""
        saved = self._attachments_folder / f"{prompt}-{number}{extension}"
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(base64.b64decode(data))
        return saved

    def _take_off(self, prompts: list[QueuedPrompt]) -> None:
        """Delete the files attached to prompts, which leave the queue, and keep a copy of them in the queue archive."""
        for prompt in prompts:
            prompt.delete_attachments(self._attachments_folder)
        self._archive(prompts)

    def _archive(self, prompts: list[QueuedPrompt]) -> None:
        """Keeps a JSON copy of prompts taken off the queue in the chat's queue archive, one file for each time, named
        for when they were taken off; nothing taken off writes nothing."""
        if not prompts:
            return
        taken_off = datetime.now(timezone.utc)
        self._archive_folder.mkdir(parents=True, exist_ok=True)
        saved = self._archive_folder / f"{taken_off.strftime('%Y%m%dT%H%M%S%fZ')}.json"
        kept = {"chat": self._chat, "taken_off": taken_off.isoformat(), "prompts": [prompt.record for prompt in prompts]}
        saved.write_text(json.dumps(kept, indent=2), encoding="utf-8")

    def _take_off_done(self) -> PromptQueue:
        """Take the done prompts off the queue into its archive and keep the rest in order. Its caller holds the file."""
        held = self.prompts
        self._take_off([item for item in held if item.is_done])
        return self._keep([item for item in held if not item.is_done])

    def _copy_whole_file(self) -> None:
        """Keeps a copy of the queue's file, every field it holds, in the chat's queue archive, named for when it was
        copied; a second copy in the same second gets a number after the time rather than replacing the first."""
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self._archive_folder.mkdir(parents=True, exist_ok=True)
        saved = self._archive_folder / f"{WHOLE_FILE_COPY}{stamp}.json"
        copies = 1
        while saved.exists():
            copies += 1
            saved = self._archive_folder / f"{WHOLE_FILE_COPY}{stamp}-{copies}.json"
        saved.write_text(json.dumps(self._file.read(), indent=2), encoding="utf-8")

    def _found(self, held: list[QueuedPrompt], prompt: str) -> QueuedPrompt:
        """The prompt of held whose id is prompt, refusing an id the queue does not hold."""
        found = next((item for item in held if item.id == prompt), None)
        if found is None:
            raise PromptNotQueued(prompt, self._chat, [item.id for item in held], self._taken_off(prompt))
        return found

    def _taken_off(self, prompt: str) -> str:
        """When the chat's queue archive says prompt was taken off the queue, the latest time; empty when it holds none."""
        if not self._archive_folder.is_dir():
            return ""
        archived = (json.loads(saved.read_text(encoding="utf-8")) for saved in sorted(self._archive_folder.glob("*.json"), reverse=True) if not saved.name.startswith(WHOLE_FILE_COPY))
        return next((record.get("taken_off", "") for record in archived if any(item.get("id") == prompt for item in record.get("prompts", []))), "")

    def _keep(self, prompts: list[QueuedPrompt]) -> PromptQueue:
        """Write prompts as the queue, beside whatever else the queue's file holds. Its caller holds the file from the
        read prompts were made from, so no other caller's change comes between that read and this write."""
        self._file.write({**self._file.read(), "prompts": [prompt.record for prompt in prompts]})
        return self


def _queue_latest_handoff(session: Session, chat: str) -> str:
    """Queue the next steps of the latest handoff of session, which chat just opened, on chat's prompt queue, once per
    handoff, and say so; nothing for a call from no chat, or a session with no handoff."""
    handoff = session.handoffs.latest
    if not chat or handoff is None:
        return ""
    queued = PromptQueue.of_chat(chat).queue_once(handoff.name, handoff.next_steps)
    return _HANDOFF_QUEUED_NOTE.format(count=queued, handoff=handoff.name) if queued else ""


# A chat that opens a session has its latest handoff's next steps lined up on its queue.
OpenSessions.on_session_opened(_queue_latest_handoff)
