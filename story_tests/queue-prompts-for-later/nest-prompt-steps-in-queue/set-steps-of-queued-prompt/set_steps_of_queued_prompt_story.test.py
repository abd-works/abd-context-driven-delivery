from __future__ import annotations

from expects import contain, equal, expect, raise_error

from tools.prompt_queue.examples.prompt_queue_examples import (
    MISSING_PROMPT,
    READ_THE_EPIC,
    RUN_THE_UNIT_TIER,
    VALIDATE_THE_SCENARIOS,
    WRITE_THE_SCENARIOS,
    WRITE_THE_STORIES,
    id_of,
    seed_queue,
    steps,
    steps_of,
    three_steps_pending,
)
from tools.prompt_queue.prompt_queue import PromptNotQueued
from story_test import and_, but_, given, scenario, story, then, when

# Epic: Queue Prompts For Later
# Sub-epic: Nest Prompt Steps In Queue
# Map: ../../../../.context/story-map.md#s-agent----set-steps-of-queued-prompt
# Scenarios: ../nest_prompt_steps_in_queue_story.test.md#story-set-steps-of-queued-prompt
# Requested 2026-11-17: the queue holds both levels, the prompts the person queued and, under each, the steps the agent
# planned for it, on the cdd server.

# Story: Set Steps Of Queued Prompt
# Actor: Agent
with story("Set Steps Of Queued Prompt"):
    with scenario("Give a queued prompt its steps"):
        with given("the chat's prompt queue holds WRITE_THE_SCENARIOS, then RUN_THE_UNIT_TIER"):
            self.queue = seed_queue(WRITE_THE_SCENARIOS, RUN_THE_UNIT_TIER)
        with but_("WRITE_THE_SCENARIOS has no steps"):
            expect(steps_of(self.queue, WRITE_THE_SCENARIOS)).to(equal([]))
        with when("the agent sets the steps of WRITE_THE_SCENARIOS to READ_THE_EPIC, WRITE_THE_STORIES, VALIDATE_THE_SCENARIOS, each pending"):
            # Agent -> PromptQueue.set_steps(prompt, steps)
            self.answered = self.queue.set_steps(id_of(self.queue, WRITE_THE_SCENARIOS), three_steps_pending())
        with then("the queue answers WRITE_THE_SCENARIOS with those three steps, in that order, none done"):
            expect(steps_of(self.answered, WRITE_THE_SCENARIOS)).to(equal(three_steps_pending()))
        with and_("RUN_THE_UNIT_TIER still has no steps"):
            expect(steps_of(self.answered, RUN_THE_UNIT_TIER)).to(equal([]))
    with scenario("Keep each step's state as given"):
        with given("the chat's prompt queue holds WRITE_THE_SCENARIOS"):
            self.queue = seed_queue(WRITE_THE_SCENARIOS)
        with when("the agent sets the steps of WRITE_THE_SCENARIOS to READ_THE_EPIC done, WRITE_THE_STORIES in progress, VALIDATE_THE_SCENARIOS pending"):
            self.planned = steps((READ_THE_EPIC, "done"), (WRITE_THE_STORIES, "in_progress"), (VALIDATE_THE_SCENARIOS, "pending"))
            self.answered = self.queue.set_steps(id_of(self.queue, WRITE_THE_SCENARIOS), self.planned)
        with then("the queue answers WRITE_THE_SCENARIOS with READ_THE_EPIC done, WRITE_THE_STORIES in progress and VALIDATE_THE_SCENARIOS pending"):
            expect(steps_of(self.answered, WRITE_THE_SCENARIOS)).to(equal(self.planned))
    with scenario("Replace the steps a prompt had"):
        with given("WRITE_THE_SCENARIOS has the steps READ_THE_EPIC, WRITE_THE_STORIES, VALIDATE_THE_SCENARIOS"):
            self.queue = seed_queue(WRITE_THE_SCENARIOS)
            self.queue.set_steps(id_of(self.queue, WRITE_THE_SCENARIOS), three_steps_pending())
        with when("the agent sets the steps of WRITE_THE_SCENARIOS to READ_THE_EPIC done, VALIDATE_THE_SCENARIOS pending"):
            self.planned = steps((READ_THE_EPIC, "done"), (VALIDATE_THE_SCENARIOS, "pending"))
            self.answered = self.queue.set_steps(id_of(self.queue, WRITE_THE_SCENARIOS), self.planned)
        with then("the queue answers WRITE_THE_SCENARIOS with only READ_THE_EPIC done and VALIDATE_THE_SCENARIOS pending"):
            expect(steps_of(self.answered, WRITE_THE_SCENARIOS)).to(equal(self.planned))
    with scenario("Refuse steps for a prompt the queue does not hold"):
        with given("the chat's prompt queue holds WRITE_THE_SCENARIOS"):
            self.queue = seed_queue(WRITE_THE_SCENARIOS)
        with but_("it holds no prompt with id MISSING_PROMPT"):
            expect([prompt["id"] for prompt in self.queue.prompts]).not_to(contain(MISSING_PROMPT))
        with when("the agent sets the steps of MISSING_PROMPT"):
            self.setting = lambda: self.queue.set_steps(MISSING_PROMPT, three_steps_pending())
        with then("the agent is told no prompt MISSING_PROMPT is on the queue"):
            expect(self.setting).to(raise_error(PromptNotQueued, contain(f"no prompt {MISSING_PROMPT!r} is on the queue")))
        with and_("the queue still holds WRITE_THE_SCENARIOS with no steps"):
            expect(steps_of(self.queue, WRITE_THE_SCENARIOS)).to(equal([]))
