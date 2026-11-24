# Enter Commands Faster

**Outcome:** a person types a CDD command with the actions, practices, fidelities and formats offered as they go, and the chat proposes the next command and captures handoffs, corrections and decisions.

**Slicing notes:** mod-ideas build order 2, command entry and autocomplete; Choose Format sits here because a format is one of the command's parameters. Merged with Suggest The Next Step (mod-ideas build order 3, next-step suggestions) on 2026-11-23, at the person's request.

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

## Notes from the backlog: Suggest The Next Step

From `board-enhancements.md`, "Chat integration":

> - open associated chat on session open / manually
> - log chat id in session log

and under "done":

> - persist chat with session; associate each log entry with its chats

Built today: every session log line ends with its chat's pointer (chat id, transcript path and lines), so "log chat id in session log" is done. Opening the ticket's chat is built too: Open Ticket Chat On Session Open is in Built Today (a press on a card points the board at the ticket's chat, and the chat button opens one on its worktree).

From `mod-ideas.md`, build order 3, "Mini panel above the chat bar, with next-step suggestions":

> The `AbovePrompt` band exists but shows only violations. Make it always on, with the session, a breadcrumb of stage, practice, and fidelity, the violation count, and buttons for next, validate, and handoff.

Built today: the chat bar line (Display Stage Strip) is that band, with the session name, the stage, fidelity dots with violation counts, the action button and handoff. The next-step suggestion is Suggest Next Command.

From `mod-ideas.md`, "Flow" and "Capturing knowledge":

> **Next-step suggestion.** After each turn, use `$.prompt.suggest` to pre-fill the next command from `ticket.generate_commands`.
>
> **Automatic handoff.** Write the handoff when a session ends, so the next session never starts cold.
>
> **Correction capture.** Use `$.model.classify` to spot when the user is correcting generated work, then offer to add it to `corrections.log`. Do the same for decisions and offer a CDR.

## Epic: Move Work Forward From Chat Bar

### Feature: Enter CDD Commands Faster

#### Story: Suggest Next Command

*Claude Code*. Intended (`.sessions/_backlog/suggest-the-next-step.md` "Next-step suggestion"): after each turn, `$.prompt.suggest` fills in the next command from `ticket.generate_commands`. Requested (2026-11-06, "the list box of actions should be on the next action recommended"): the recommendation shows on the chat band's action list box, marked recommended and set on ▶, not in the chat panel. Built today (checked 2026-11-10): the action button shows the fidelity's next action and the action list marks it next (`action-button-view.tsx:20-25,77-83`), which covers the 2026-11-06 request. Missing: `prompt.suggest` after a turn.

### Feature: Work Fidelity Outputs In Chat Bar → Capture Session Knowledge

#### Story: Write Handoff When Session Ends

*Claude Code*. Intended (`.sessions/_backlog/suggest-the-next-step.md` "Automatic handoff"): the handoff is written when a session ends, so the next session never starts cold. Built today (checked 2026-11-10): closing or leaving a session from the chat bar offers Create handoff, on by default (`session-dialogs-view.tsx:34`). Missing: writing one when a Claude Code session ends.

#### Story: Offer Correction Log Entry

*Claude Code*. Intended (`.sessions/_backlog/suggest-the-next-step.md` "Correction capture"): `$.model.classify` spots when the person corrects generated work and offers, in the chat panel, to add it to `corrections.log` beside that work.

#### Story: Offer Decision Record

*Claude Code*. Intended (`.sessions/_backlog/suggest-the-next-step.md` "Correction capture"): the same check spots a decision and offers to write a CDR for it.

### Feature: Steer Sessions

#### Story: Display Latest Session Handoff

*Chat Bar*. Requested (2026-11-06, as the CDD Kanban does): the chat bar shows the active session's latest handoff.

Analysis and planning: the stories here are not built yet, or only partly built where a story says so. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.
