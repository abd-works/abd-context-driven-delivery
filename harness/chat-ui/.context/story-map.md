---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Chat Bar

**Sources / context:** `harness/kanban/.context/story-map.md` (the Session Board map this one follows, story for story); `harness/chat-ui/.context/cdr/0001-stage-strip-band.md` (option B, the stage strip); `harness/chat-ui/design/StageStrip.dc.html` (Claude Design canvas version 48, board "B · Stage strip with action bar"); `harness/chat-ui/pane/.context/module-context.md` and `harness/chat-ui/pane/hooks/register.ts` (the `cdd-board` plugin and `/board`); `harness/chat-ui/pane/hooks/health/server-health-view.tsx` and `server-health-client.ts` (the server health band); `harness/chat-ui/pane/hooks/chat-bar/` (the chat bar's clients and views, wired to cdd in commit 5899d88a8); `harness/chat-ui/pane/test/move-work-forward-from-chat-bar/` (one acceptance test per Story, each scenario naming its evidence); `harness/kanban/ticket.py` (`ticket.create`, `ticket.close`, `ticket.move_next`, `fidelity-progress.files`, `fidelity-progress.report`, `fidelity-progress.finish_review`), `harness/kanban/board.py` (`board.activate`), `space/session/session.py` (`session.read_file`).

**Evidence:** The chat bar is a smaller view of the Session Board, so each Story mirrors a board Story and calls the same `ticket.*` tools. The bar has no tickets: a person in the chat works in a session, so where the board's Story says ticket, the bar's says session (confirmed by the person on 2026-11-04). The line under each Story names the board Story it mirrors and what the bar does differently. Each Story heading links to its acceptance test. The Stories under Check CDD Server Health are **Observed**: the server health band in `harness/chat-ui/pane/hooks/health/` does them, as the chat bar's leftmost part. The other Stories are **Inferred** from the canvas and the CDR; `pane/hooks/chat-bar/` now implements them and their tests press them. Behaviour the person asked for while the bar was built is marked **Requested**; each such scenario's Evidence line records the request.

**Actors:** Person, Chat Bar, Claude Code.

---

# (E) Move Work Forward From Chat Bar

## (E) Check CDD Server Health

### (S) Chat Bar --> [Display Server Health Mark](../pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/display-server-health-mark/display_server_health_mark_story.test.ts)

Observed: `ServerHealthBandView` draws one glyph for the connection, ✓ connected, ⟳ reconnecting, ✕ disconnected, ! tools missing, in its colour. In the bar it sits left of the session name (requested by the person on 2026-11-04; canvas version 48).

### (S) Person --> [Open Server Health Panel](../pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/open-server-health-panel/open_server_health_panel_story.test.ts)

Observed: the panel opens with the session card, stacked on top of it, while the pointer is over the mark. Connected, it shows MCP host, Tools with the loaded count, Kanban app and Graph app with their ports, and Hook server on one line, colour alone saying running and each part's name on hover (asked by the person on 2026-11-04); otherwise a headline says what is wrong. Requested: pressing the mark pins the card and its panel open after the pointer leaves.

### (S) Person --> [Reconnect CDD Server](../pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/reconnect-cdd-server/reconnect_cdd_server_story.test.ts)

Observed: when disconnected, the panel's Reconnect retries `cdd` up to three times (`RECONNECT_TRIES`), then reads the active session again.

### (S) Person --> [Reinstall CDD Tools](../pane/test/move-work-forward-from-chat-bar/check-cdd-server-health/reinstall-cdd-tools/reinstall_cdd_tools_story.test.ts)

Observed: when disconnected or tools are missing, Run install runs the installer and the panel says installing, installed (open a new session) or failed; Details shows the tool, error, server and fix.

## (E) See Work In Chat Bar

### (S) Chat Bar --> [Display Stage Strip](../pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-stage-strip/display_stage_strip_story.test.ts)

Mirrors Display Board, for the active session only: one line with the health mark, the session name, fidelity dots, action button, stage icons, then handoff, files and close (CDR "The line reads left to right").

### (S) Chat Bar --> [Display Fidelity Progress](../pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-fidelity-progress/display_fidelity_progress_story.test.ts)

Mirrors Display Fidelity Progress and Display Violations Band: one dot per practice in its colour, shaded by state, with the violation count in red (CDR "Fidelity dots").

### (S) Person --> [Display Session Card](../pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/display-session-card/display_session_card_story.test.ts)

Mirrors Display Ticket Card and Browse Ticket Folder: resting the pointer on the session name shows the card over the strip, each fidelity's name and state over its dot, the stage name over the stage icons, and each fidelity's folders beside it, with the server health panel on top (CDR "Session name and session list"). Requested: the person closes a pinned card, after which it shows only while the pointer is on the name.

### (S) Person --> [Open Board](../pane/test/move-work-forward-from-chat-bar/see-work-in-chat-bar/open-board/open_board_story.test.ts)

Requested: pressing a dot selects its fidelity as the one the action button acts on and sends nothing to the chat. This replaces the CDR's "clicking a dot opens `/board`"; nothing on the bar opens the board now.

## (E) Steer Sessions

### (S) Person --> [Create New Session](../pane/test/move-work-forward-from-chat-bar/steer-sessions/create-new-session/create_new_session_story.test.ts)

Mirrors Open Ticket Session: a field in the session list box names a new session, which `ticket.create` creates; the activation dialog then opens it (CDR "Session name and session list").

### (S) Person --> [Open Session](../pane/test/move-work-forward-from-chat-bar/steer-sessions/open-session/open_session_story.test.ts)

Mirrors Activate Ticket: picking a session from the session list box opens the activation dialog, then calls `board.activate` (CDR "Session name and session list").

### (S) Person --> [Write Session Handoff](../pane/test/move-work-forward-from-chat-bar/steer-sessions/write-session-handoff/write_session_handoff_story.test.ts)

Mirrors Write Ticket Handoff: the handoff button on the line fills the prompt with the handoff command (CDR "Handoff, files, close").

### (S) Person --> [Close Active Session](../pane/test/move-work-forward-from-chat-bar/steer-sessions/close-active-session/close_active_session_story.test.ts)

Mirrors Close Active Session: the close button on the line closes the active session through `ticket.close`, asking what to do with its work as the board does (CDR "Handoff, files, close"; confirmed by the person on 2026-11-04).

## (E) Guide Work Through Practices

### (S) Person --> [Invoke Next Fidelity Action](../pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/invoke-next-fidelity-action/invoke_next_fidelity_action_story.test.ts)

Mirrors Send Next Fidelity Action, for one fidelity: the action button runs generate, validate or review on the selected fidelity (CDR "Action button and ▾ picker"; "Actions run on one fidelity at a time").

### (S) Person --> [Choose Fidelity Action](../pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/choose-fidelity-action/choose_fidelity_action_story.test.ts)

Mirrors Choose Action And Formats, without formats: the ▾ picker offers generate, validate, review, iterate, sketch, render and document (CDR "Action button and ▾ picker"). Requested: selecting another fidelity drops the picked action, so the button follows that fidelity's state, such as to do → generate.

### (S) Person --> [Display Stage Fidelities](../pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/display-stage-fidelities/display_stage_fidelities_story.test.ts)

Mirrors Open Practice Tile at stage level: clicking a stage icon shows that stage's fidelities on the dots (CDR "Stage icons").

### (S) Person --> [Move Session To Next Stage](../pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/move-session-to-next-stage/move_session_to_next_stage_story.test.ts)

Mirrors Move Ticket, forward only: once every fidelity of the stage is reviewed, the action button calls `ticket.move_next` (CDR "Action button and ▾ picker").

### (S) Person --> [List Session Files](../pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/list-session-files/list_session_files_story.test.ts)

Mirrors List Ticket Files, for the selected fidelity only: files opens a tab per file `fidelity-progress.files` declares (CDR "Handoff, files, close").

### (S) Person --> [View Fidelity Files](../pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/view-fidelity-files/view_fidelity_files_story.test.ts)

Mirrors View Fidelity Files: each tab's text comes from `session.read_file`, which refuses a file outside the session's roots (CDR "Handoff, files, close"). Requested: pressing a fidelity's red violation count opens its latest validation report, from `fidelity-progress.report`, in its own tab drawn as markdown, as the board does.

### (S) Person --> [Review Fidelity](../pane/test/move-work-forward-from-chat-bar/guide-work-through-practices/review-fidelity/review_fidelity_story.test.ts)

Mirrors Review Fidelity: review calls `fidelity-progress.finish_review` on one fidelity, which needs its latest Validate to have passed (CDR "Actions run on one fidelity at a time").

---

## Scope boundary

**In scope:** the stage strip above the chat prompt for the active session, doing what the Session Board does for one session and one fidelity at a time through the same `ticket.*` tools, including reading a fidelity's latest validation report from its violation count.

**Out of scope:** tickets as a bar concept; the board's whole-board work (Backlog items, WIP limits, side panels, split, archive, moving back a stage), Fix from a validation report, format chips, an expanded bar mode (CDR "Considered options"), and options A and C.
