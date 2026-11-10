# Enter Commands Faster

Analysis and planning: the stories here are not built yet, or only partly built where a story says so. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** a person types a CDD command with the actions, practices, fidelities and formats offered as they go.

**Slicing notes:** mod-ideas build order 2, command entry and autocomplete; Choose Format sits here because a format is one of the command's parameters.

## Notes from the backlog

From `mod-ideas.md`, build order 2, "Command entry and autocomplete":

> The `prompt.autocomplete` event adds suggestions to the typeahead as you type, so it can offer an action, then a practice-fidelity, then content or a file. `argumentHint` shows the expected parameters after a command's name. Take the options from the CDD catalog so they cannot drift from what is installed.

From `mod-ideas.md`, "Hooks and notifications":

> Toasts exist only for ticket moves and finished fidelities. `tools/prompt_notify` writes a toast file for Cursor only. Port "which action or practice just ran" to `$.ui.toast`, and use `tool.call` to react to every CDD call. `$.audio.play` is available for sounds.

From `chat-enhancements.md`: "constrainned lists params on commands". From `board-enhancements.md`, "Actions": "add comment to command sent to chat".

Built today: Select Several Fidelities and Choose Format (the chat bar's fidelity selection and format chips) moved to Built Today.

## Epic: Move Work Forward From Chat Bar

### Feature: Enter CDD Commands Faster

#### Story: Autocomplete CDD Commands

*Claude Code*. Intended (`.sessions/_backlog/enter-commands-faster.md` "Command entry and autocomplete"; `.sessions/_backlog/enter-commands-faster.md` "constrained lists params on commands"): `prompt.autocomplete` offers an action, then a practice-fidelity, then content or a file, taken from the installed CDD catalog so the lists cannot drift.

#### Story: Show Command Argument Hints

*Claude Code*. Intended (`.sessions/_backlog/enter-commands-faster.md` "argumentHint"): after a command's name, the prompt shows the parameters it expects.

#### Story: Announce CDD Tool Calls

*Claude Code*. Intended (`.sessions/_backlog/enter-commands-faster.md` "Hooks and notifications"): every CDD tool call shows a toast naming the action or practice that ran, with an optional sound, as `tools/prompt_notify` does for Cursor.

### Feature: Work Fidelity Outputs In Chat Bar → Generate Fidelity Outputs In Chat Bar

#### Story: Display Action Before Fidelity Dots

*Chat Bar*. Requested (2026-11-06, "reorder buttons; action then practices"): the action button and its picker come first on the line, then the practices' fidelity dots, so the person chooses what to do before choosing where.

## Epic: Move Work Forward On Session Board

### Feature: Work Fidelity Outputs On Board → Generate Fidelity Outputs On Board

#### Story: Add Comment To Sent Command

*Person*. Intended (`.sessions/_backlog/enter-commands-faster.md` "add comment to command sent to chat"): a person adds their own words to the command the board sends to the chat. Built today (checked 2026-11-10): Split, Handoff, + Ticket and Run next put the command into the prompt for the person to edit before sending (`chat-client.tsx:144-148`). Missing: tile Run, Validate and Fix send at once, and there is no comment field.
