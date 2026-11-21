---
fidelity: [acceptance_tests]
artifact: [desktop-story-test]
format: md
---

# Desktop story test: Open Prompt Queue

Walked in the real Claude desktop app by computer control, with `/desktop-walk target="Open Prompt Queue"`; no test tier runs it. Each scenario is copied word for word from [build_prompt_queue_story.test.md](build_prompt_queue_story.test.md). Under each step, Do is what the walking agent does on the screen of the test chat, and See is what the step's screenshot must show. The scenario's example values stand for the test chat's live ones.

## Story: Open Prompt Queue

#### Scenario: Open the queue as a stack of cards

*Given* the chat's prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)

- Do: type Write the scenarios in the test chat's prompt box and press the queue's + button, above the chat bar; then the same for Run the unit tier. Send neither to the chat.
- See: the prompt box is empty after each.

*And* the queue is closed, its stack showing 2

- Do: if the queue is open, press the stack image to close it.
- See: only the stack image shows above the chat bar, with 2 drawn on it.

*When* the person opens the prompt queue

- Do: press the stack image.

*Then* a card shows for ++Write the scenarios++, then for ++Run the unit tier++

- See: two cards above the stack: Write the scenarios first, then Run the unit tier.

*And* the open queue and each card fill the chat box's width

- See: the open queue and each card are as wide as the chat's prompt box.

*And* each card's buttons sit on a solid dark bar over its right end

- Do: move the pointer over the first card.
- See: the card's buttons show on a solid dark bar at its right end, readable over the card's text.

#### Scenario: Close the open queue

*Given* the open prompt queue holds ++Write the scenarios++ (a), then ++Run the unit tier++ (b)

- See: the queue is open with its two cards, as the scenario before left it.

*When* the person closes the prompt queue

- Do: press the stack image.

*Then* only the stack shows, with its count, 2

- See: no card shows; only the stack image, with 2 drawn on it.

### Not walked on the desktop

- Draw a done prompt dim in its place: a prompt is marked done by the agent of the test chat (prompt-queue.done), which the walk does not drive yet.
- Show a queue change that failed on the failure line: the cdd server would have to be stopped under the test chat.
