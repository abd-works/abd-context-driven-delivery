---
fidelity: [acceptance_tests]
artifact: [desktop-story-test]
format: md
---

# Desktop story test: Open Stage Files From Chat Bar

Walked in the real Claude desktop app by computer control, with `/desktop-walk target="Open Stage Files From Chat Bar"`; no test tier runs it. Each scenario is copied word for word from [review_files_in_files_app_story.test.md](review_files_in_files_app_story.test.md). Under each step, Do is what the walking agent does on the screen of the test chat, and See is what the step's screenshot must show. The scenario's example values stand for the test chat's live ones.

## Story: Open Stage Files From Chat Bar

#### Scenario: Open the files beside the chat, never in it

*Given* checkout-flow's Discovery stage holds the fidelities stories-story-map and ddd-bounded-context

- See: the chat bar's line shows the stage's buttons and the ▤ files button; the test chat's stage and its fidelities stand for Discovery, stories-story-map and ddd-bounded-context.

*And* checkout-flow is assigned the chat *checkout-chat*

- See: the test chat is the chat in front, its first prompt holding the walk's mark; it stands for checkout-chat.

*When* the Person opens the stage's files from *checkout-chat*'s chat bar

- Do: press the ▤ files button on the chat bar's line.

*Then* the [Files app](../../../harness/files_app/.context/files-app-model.md#filespage-filesfiles-pagets) opens beside the chat, naming checkout-flow and *checkout-chat*

- See: a pane is open beside the chat, showing the Files app, and it names the test chat's session.

*And* its link names both fidelities, stories-story-map and ddd-bounded-context, the [practice](../../../harness/files_app/.context/files-app-model.md#session-practicesessionoutput-python-spacesession) turned off among them

- Do: read the address the pane shows, zooming on it when it is small.
- See: the page lists the stage's fidelities, those of a practice that is turned off among them.

*And* the chat bar draws no file, and no diagram is read into the chat

- See: the chat bar's line is unchanged: no file's text and no diagram is drawn in the chat bar or added to the chat's messages.

*And* the Person can Toggle Practice In Files App there

- See: the Files app's header shows a toggle for each practice.
