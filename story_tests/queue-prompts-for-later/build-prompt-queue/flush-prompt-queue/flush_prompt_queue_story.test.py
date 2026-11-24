from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from expects import equal, expect

from tools.prompt_queue.examples.prompt_queue_examples import RUN_THE_UNIT_TIER, WRITE_THE_SCENARIOS, id_of, seed_queue_in
from tools.prompt_queue.prompt_queue import ARCHIVE_FOLDER, QUEUE_FILE
from story_test import and_, given, scenario, story, then, when

# Epic: Queue Prompts For Later
# Map: ../../../../.context/story-map.md#s-person----flush-prompt-queue
# Requested 2026-11-23 (the person): "add a flush button that does what I just asked when I click it, eg time stamped
# copy of queue file then delete finished bots".

# A copy flush keeps: prompt-queue, then the time it was flushed.
FLUSHED_COPY_NAME = r"^prompt-queue-\d{8}T\d{6}Z\.json$"

# Story: Flush Prompt Queue
# Actor: Person
with story("Flush Prompt Queue"):
    with scenario("Flush keeps a copy of the whole queue file, then takes the done prompts off"):
        with given("the chat's prompt queue holds WRITE_THE_SCENARIOS, done, then RUN_THE_UNIT_TIER"):
            self.folder = Path(tempfile.mkdtemp())
            self.queue = seed_queue_in(self.folder, WRITE_THE_SCENARIOS, RUN_THE_UNIT_TIER)
            self.queue.done(id_of(self.queue, WRITE_THE_SCENARIOS))
            self.as_it_stood = json.loads((self.folder / QUEUE_FILE).read_text(encoding="utf-8"))
        with when("the person flushes the queue"):
            # Prompt Queue mod flush button -> flushQueue -> prompt-queue.flush -> PromptQueue.flush()
            self.flushed = self.queue.flush()
        with then("the queue archive holds a copy of the whole queue file as it stood, named prompt-queue and the time it was flushed"):
            copies = sorted((self.folder / ARCHIVE_FOLDER).glob("prompt-queue-*.json"))
            kept = [(bool(re.match(FLUSHED_COPY_NAME, saved.name)), json.loads(saved.read_text(encoding="utf-8"))) for saved in copies]
            expect(kept).to(equal([(True, self.as_it_stood)]))
        with and_("the queue holds only RUN_THE_UNIT_TIER"):
            expect([prompt.text for prompt in self.flushed.prompts]).to(equal([RUN_THE_UNIT_TIER]))
    with scenario("Flush with no prompt done keeps the copy and takes nothing off"):
        with given("the chat's prompt queue holds WRITE_THE_SCENARIOS, then RUN_THE_UNIT_TIER, neither done"):
            self.folder = Path(tempfile.mkdtemp())
            self.queue = seed_queue_in(self.folder, WRITE_THE_SCENARIOS, RUN_THE_UNIT_TIER)
        with when("the person flushes the queue"):
            self.flushed = self.queue.flush()
        with then("the queue archive holds one copy of the whole queue file"):
            expect(len(list((self.folder / ARCHIVE_FOLDER).glob("prompt-queue-*.json")))).to(equal(1))
        with and_("the queue still holds WRITE_THE_SCENARIOS, then RUN_THE_UNIT_TIER"):
            expect([prompt.text for prompt in self.flushed.prompts]).to(equal([WRITE_THE_SCENARIOS, RUN_THE_UNIT_TIER]))
