# Chat pilot results, 2026-11-02

Claude desktop app, Code tab, Claude Code 2.1.309 skill build, Windows 11. Local server on
127.0.0.1:8777, page in the Browser pane, mod `chat-pilot` loaded by hot reload into a live chat.
Each press was a real click on the page button.

## Chain

Page button -> `POST /press` -> server queue -> mod polls `GET /next` every second -> `$.prompt.submit` or `$.prompt.fill`.

## Measured

Seconds since the server started.

| Step | Submit | Fill |
|---|---|---|
| Pressed | 41.98 | 61.64 |
| Mod received it | 42.95 | 61.98 |
| Mod's report | 42.95 `submitting` | 62.00 `isFilled=true` |

## Proven

- `$.prompt.submit` starts a real turn in the desktop chat, and the model replies. It arrived as
  "The chat-pilot plugin sent a message", so the model can tell it came from a plugin.
- The submitted prompt waits until the session is idle. A button pressed during a turn runs after it.
- `$.prompt.fill` works in the desktop chat while the session is idle. Pressed at 776.83, delivered
  at 776.89, and after the mod's 15-second wait, filled and read back at 791.92. The text reached
  the user's box, and sending it arrived in the chat as an ordinary user message.
- `$.prompt.fill` during a running turn is not dependable. The first press, mid-turn, reported
  `isFilled=true`, but the user saw nothing in the box. Hold a fill until the turn has ended.
- The mod's `$.session.id()` gave the chat's id, so the board can target a specific chat.
- A hot reload runs `session.start`, so the mod registered without a restart.
- A POST with another site's `Origin` gets 403.

## Found

- `$.prompt.submit` resolves before the turn ends: 9.64 seconds after it was called, while the
  turn was still running. The mod's `turn finished` label in that run is wrong. It cannot be used
  to tell the page when a turn is over; that needs its own signal, such as a turn event.
- `$.prompt.fill` defaults to `replace`, which overwrites a draft the user is typing. The real
  board should use `append` or `insert`, or read the box first with `$.prompt.read`. The second
  run used `append`.
- A fill sent by the user arrives as the user's own message, not as a plugin message, so the model
  cannot tell it came from the board.
- Polling costs up to one second of delay and one local request a second per chat.

## The thin mod, same chat

`harness/kanban/chat-mod` loaded by hot reload and connected to the board server on port 8778.

- `turn.start` and `turn.complete` drive `isBusy`: true during a turn, false after it.
- `submit` started a turn. `command` ran the `/harness-guidance` skill from the mod's timer, which
  is how the board's Run buttons reach a skill.
- A `fill` sent during a turn was held by the board server and reached the user's box after the
  turn ended. The user confirmed it. This fixes the mid-turn fill that showed nothing in the pilot.
- `/board` sent by the mod itself did not answer: "registered /board but no command.run hook
  answered it". A plugin's own `$.command.run` is under the engine's re-entry rule, so this may not
  affect a person typing `/board`. Not yet checked.

## Not proven

- Timing with more than one chat registered. The page takes the first chat in the list.
- `claude plugin validate` and a type-check did not run, because no `claude` CLI is on the PATH.
- The MCP connection from Node, and whether a mod can open the Browser pane from `/board`.
