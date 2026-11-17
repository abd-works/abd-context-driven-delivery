"""The examples the Nest Prompt Steps In Queue stories share: a chat's prompt queue in a throwaway folder, the prompts
queued on it, and the steps the agent plans for one of them.

Scenarios: story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/, one folder per story.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from tools.prompt_queue.prompt_queue import PromptQueue, PromptStep

# Seed: the chat whose queue the stories work on.
CHAT = "chat-1"
# Seed: the prompts the person queued, first to be done first.
WRITE_THE_SCENARIOS = "Write the scenarios"
RUN_THE_UNIT_TIER = "Run the unit tier"
# Interaction: the steps the agent plans for Write the scenarios, in order.
READ_THE_EPIC = "Read the epic"
WRITE_THE_STORIES = "Write the stories"
VALIDATE_THE_SCENARIOS = "Validate the scenarios"
# Interaction: a prompt id the queue does not hold.
MISSING_PROMPT = "z"


def steps(*planned: tuple[str, str]) -> list[PromptStep]:
    """The steps planned, each its text and its state: pending, in_progress, or done."""
    return [{"text": text, "state": state} for text, state in planned]


def three_steps_pending() -> list[PromptStep]:
    """Read the epic, Write the stories and Validate the scenarios, none started."""
    return steps((READ_THE_EPIC, "pending"), (WRITE_THE_STORIES, "pending"), (VALIDATE_THE_SCENARIOS, "pending"))


def seed_queue(*texts: str) -> PromptQueue:
    """CHAT's queue in a folder of its own, holding texts in order."""
    queue = PromptQueue(CHAT, Path(tempfile.mkdtemp()) / "prompt-queue.json")
    queue.add_all(list(texts))
    return queue


def id_of(queue: PromptQueue, text: str) -> str:
    """The id of the queued prompt whose text is text."""
    return next(prompt["id"] for prompt in queue.prompts if prompt["text"] == text)


def steps_of(queue: PromptQueue, text: str) -> list[PromptStep]:
    """The steps the queue answers for the prompt whose text is text; none when it has none."""
    return next(prompt for prompt in queue.prompts if prompt["text"] == text).get("steps", [])
