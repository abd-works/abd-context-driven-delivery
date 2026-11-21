---
fidelity: [acceptance_tests]
artifact: [desktop-story-test]
format: md
---

# Desktop story test: Select Fidelity

Walked in the real Claude desktop app by computer control, with `/desktop-walk target="Select Fidelity"`; no test tier runs it. Each scenario is copied word for word from [see_work_in_chat_bar_story.test.md](see_work_in_chat_bar_story.test.md). Under each step, Do is what the walking agent does on the screen of the test chat, and See is what the step's screenshot must show. The scenario's example values stand for the test chat's live ones.

## Story: Select Fidelity

#### Scenario: Pick a fidelity from anywhere on its line

*Given* the session card for checkout-flow is open

- Do: press the session's name on the chat bar's line, unless the session card is already open.
- See: the session card with its FIDELITY list.

*When* the Person presses the line of clean-engineering-model

- Do: press the state text at the right end of the clean-engineering-model line (the stage's Clean Engineering fidelity when the stage shown is another), not its name.

*Then* the press covers the square, the name and the state, the whole line

- See: that fidelity's line is marked as picked, by a press that landed on its state text.

*And* clean-engineering-model is the fidelity the action button acts on

- See: the action button on the chat bar's line names that fidelity, or its practice's dot is the one marked selected.
