from __future__ import annotations

import base64
from pathlib import Path

from expects import contain, equal, expect, raise_error

from tools.prompt_queue.examples.prompt_queue_examples import (
    MISSING_PROMPT,
    SCREENSHOT_NAME,
    SCREENSHOT_PNG,
    WRITE_THE_SCENARIOS,
    id_of,
    seed_queue,
)
from tools.prompt_queue.prompt_queue import PromptNotQueued
from story_test import and_, given, scenario, story, then, when

# Epic: Queue Prompts For Later
# Map: ../../../.context/story-map.md#s-person----attach-images-to-queued-prompt
# Requested 2026-11-17 (the person's /queue): "add images / attachments in chat along with text". A plugin cannot send
# images with a prompt, so a queued draft's images are kept as files beside its prompt, and the agent opens them.

# Story: Attach Images To Queued Prompt
# Actor: Person
with story("Attach Images To Queued Prompt"):
    with scenario("Keep a queued draft's image beside its prompt"):
        with given("the chat's prompt queue holds WRITE_THE_SCENARIOS, queued with SCREENSHOT_PNG pasted in its draft"):
            self.queue = seed_queue(WRITE_THE_SCENARIOS)
        with when("the queue attaches SCREENSHOT_PNG to WRITE_THE_SCENARIOS"):
            # Prompt Queue mod -> PromptQueue.attach(prompt, filename, media_type, data)
            self.answered = self.queue.attach(id_of(self.queue, WRITE_THE_SCENARIOS), SCREENSHOT_NAME, "image/png", base64.b64encode(SCREENSHOT_PNG).decode())
        with then("WRITE_THE_SCENARIOS lists one attached file"):
            expect(len(self.answered.prompts[0].get("attachments", []))).to(equal(1))
        with and_("that file holds SCREENSHOT_PNG's bytes, named for the prompt"):
            attached = Path(self.answered.prompts[0]["attachments"][0])
            expect(attached.read_bytes()).to(equal(SCREENSHOT_PNG))
            expect(attached.name).to(contain(id_of(self.answered, WRITE_THE_SCENARIOS)))
    with scenario("Refuse an image for a prompt the queue does not hold"):
        with given("the chat's prompt queue holds WRITE_THE_SCENARIOS"):
            self.queue = seed_queue(WRITE_THE_SCENARIOS)
        with when("the queue attaches SCREENSHOT_PNG to MISSING_PROMPT"):
            self.attaching = lambda: self.queue.attach(MISSING_PROMPT, SCREENSHOT_NAME, "image/png", base64.b64encode(SCREENSHOT_PNG).decode())
        with then("it is told no prompt MISSING_PROMPT is on the queue"):
            expect(self.attaching).to(raise_error(PromptNotQueued, contain(f"no prompt {MISSING_PROMPT!r} is on the queue")))
