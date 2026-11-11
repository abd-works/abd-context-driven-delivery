# Suggest The Next Step

Analysis and planning: the stories here are not built yet, or only partly built where a story says so. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** the chat proposes the next command, and captures handoffs, corrections and decisions.

**Slicing notes:** mod-ideas build order 3, next-step suggestions.

## Notes from the backlog

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
