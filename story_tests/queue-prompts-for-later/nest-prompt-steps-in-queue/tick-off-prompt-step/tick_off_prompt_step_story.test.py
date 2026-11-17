from __future__ import annotations

from expects import contain, equal, expect, raise_error

from tools.prompt_queue.examples.prompt_queue_examples import (
    READ_THE_EPIC,
    VALIDATE_THE_SCENARIOS,
    WRITE_THE_SCENARIOS,
    WRITE_THE_STORIES,
    id_of,
    seed_queue,
    steps,
    steps_of,
    three_steps_pending,
)
from tools.prompt_queue.prompt_queue import StepNotPlanned
from story_test import and_, given, scenario, story, then, when

# Epic: Queue Prompts For Later
# Sub-epic: Nest Prompt Steps In Queue
# Map: ../../../../.context/story-map.md#s-agent----tick-off-prompt-step
# Scenarios: ../nest_prompt_steps_in_queue_story.test.md#story-tick-off-prompt-step

# Story: Tick Off Prompt Step
# Actor: Agent
with story("Tick Off Prompt Step"):
    with scenario("Mark one step done"):
        with given("WRITE_THE_SCENARIOS has three steps, none done"):
            self.queue = seed_queue(WRITE_THE_SCENARIOS)
            self.queue.set_steps(id_of(self.queue, WRITE_THE_SCENARIOS), three_steps_pending())
        with when("the agent marks the first step of WRITE_THE_SCENARIOS done"):
            # Agent -> PromptQueue.step_done(prompt, 1)
            self.answered = self.queue.step_done(id_of(self.queue, WRITE_THE_SCENARIOS), 1)
        with then("the queue answers WRITE_THE_SCENARIOS with READ_THE_EPIC done and the other two not done"):
            expected = steps((READ_THE_EPIC, "done"), (WRITE_THE_STORIES, "pending"), (VALIDATE_THE_SCENARIOS, "pending"))
            expect(steps_of(self.answered, WRITE_THE_SCENARIOS)).to(equal(expected))
    with scenario("Leave the prompt on the queue once every step is done"):
        with given("WRITE_THE_SCENARIOS has three steps, two of them done"):
            self.queue = seed_queue(WRITE_THE_SCENARIOS)
            planned = steps((READ_THE_EPIC, "done"), (WRITE_THE_STORIES, "done"), (VALIDATE_THE_SCENARIOS, "pending"))
            self.queue.set_steps(id_of(self.queue, WRITE_THE_SCENARIOS), planned)
        with when("the agent marks the last step of WRITE_THE_SCENARIOS done"):
            self.answered = self.queue.step_done(id_of(self.queue, WRITE_THE_SCENARIOS), 3)
        with then("the queue answers WRITE_THE_SCENARIOS with every step done"):
            expect([step["state"] for step in steps_of(self.answered, WRITE_THE_SCENARIOS)]).to(equal(["done", "done", "done"]))
        with and_("WRITE_THE_SCENARIOS stays on the queue until the agent marks it done"):
            expect([prompt["text"] for prompt in self.answered.prompts]).to(equal([WRITE_THE_SCENARIOS]))
    with scenario("Refuse a step the prompt does not have"):
        with given("WRITE_THE_SCENARIOS has three steps"):
            self.queue = seed_queue(WRITE_THE_SCENARIOS)
            self.queue.set_steps(id_of(self.queue, WRITE_THE_SCENARIOS), three_steps_pending())
        with when("the agent marks step 4 of WRITE_THE_SCENARIOS done"):
            self.marking = lambda: self.queue.step_done(id_of(self.queue, WRITE_THE_SCENARIOS), 4)
        with then("the agent is told WRITE_THE_SCENARIOS has three steps"):
            expect(self.marking).to(raise_error(StepNotPlanned, contain("has 3 steps")))
        with and_("WRITE_THE_SCENARIOS still has no step done"):
            expect(steps_of(self.queue, WRITE_THE_SCENARIOS)).to(equal(three_steps_pending()))
