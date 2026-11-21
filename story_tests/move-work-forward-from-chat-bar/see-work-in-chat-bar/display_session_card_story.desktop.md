---
fidelity: [acceptance_tests]
artifact: [desktop-story-test]
format: md
---

# Desktop story test: Display Session Card

Walked in the real Claude desktop app by computer control, with `/desktop-walk target="Display Session Card"`; no test tier runs it. Each scenario is copied word for word from [see_work_in_chat_bar_story.test.md](see_work_in_chat_bar_story.test.md). Under each step, Do is what the walking agent does on the screen of the test chat, and See is what the step's screenshot must show. The scenario's example values stand for the test chat's live ones.

## Story: Display Session Card

#### Scenario: List each folder once

*Given* checkout-flow is in Discovery with its five practices all writing under harness

- See: the chat bar's line names the test chat's session and a stage; that session and its stage stand for checkout-flow in Discovery, and the throwaway repository's own folder for harness.

*When* the Person opens the session card for checkout-flow

- Do: press the session's name on the chat bar's line.

*Then* harness is listed once, beside the first fidelity

- See: the session card is open above the line, with a list headed FIDELITY.
- See: each folder's name shows once in the card, beside the first fidelity that writes to it, and is not repeated on the lines below.

*And* every fidelity of Discovery is still listed

- See: one line for each fidelity of the stage shown, each with its coloured square, its name and its state.
