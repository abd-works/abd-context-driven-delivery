---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Chat Bar

**Sources / context:** `harness/kanban/.context/story-map.md` (the Session Board map this one follows, story for story); `harness/chat-ui/.context/cdr/0001-stage-strip-band.md` (option B, the stage strip); `harness/chat-ui/design/StageStrip.dc.html` (Claude Design canvas version 48, board "B · Stage strip with action bar"); `harness/chat-ui/pane/.context/module-context.md` and `harness/chat-ui/pane/hooks/register.ts` (the `cdd-board` plugin and `/board`); `harness/chat-ui/pane/hooks/health/server-health-view.tsx` and `server-health-client.ts` (the server health band that works today); `harness/kanban/ticket.py` (`ticket.create`, `ticket.activate`, `ticket.close`, `ticket.files`, `ticket.read_file`, `ticket.finish_review`, `ticket.move_next`).

**Evidence:** The chat bar is a smaller view of the Session Board, so each Story mirrors a board Story and calls the same `ticket.*` tools. The bar has no tickets: a person in the chat works in a session, so where the board's Story says ticket, the bar's says session (confirmed by the person on 2026-11-04). The line under each Story names the board Story it mirrors and what the bar does differently. Those Stories are **Inferred**: the canvas and the CDR describe them, and no code or spec does them yet. The Stories under Check CDD Server Health are **Observed**: the server health band in `harness/chat-ui/pane/hooks/health/` does them today, as the chat bar's leftmost part.

**Actors:** Person, Chat Bar, Claude Code.

---

# (E) Move Work Forward From Chat Bar

## (E) Check CDD Server Health

### (S) Chat Bar --> Display Server Health Mark

Observed: `ServerHealthBandView` draws one glyph for the connection, ✓ connected, ⟳ reconnecting, ✕ disconnected, ! tools missing, in its colour. In the bar it sits left of the session name (requested by the person on 2026-11-04; canvas version 48).

### (S) Person --> Open Server Health Panel

Observed: `ExpandedView` opens above the mark while the pointer is over it, and a click pins it. Connected, it shows MCP host, Tools with the loaded count, Kanban app and Graph app with their ports, and Hook server, each part's name on hover; in the bar they sit on one line, colour alone saying running, as the person asked on 2026-11-04; otherwise a headline says what is wrong.

### (S) Person --> Reconnect CDD Server

Observed: when disconnected, the panel's Reconnect retries `cdd` up to three times (`RECONNECT_TRIES`), then reads the active session again.

### (S) Person --> Reinstall CDD Tools

Observed: when disconnected or tools are missing, Run install runs the installer and the panel says installing, installed (open a new session) or failed; Details shows the tool, error, server and fix.

## (E) See Work In Chat Bar

### (S) Chat Bar --> Display Stage Strip

Mirrors Display Board, for the active session only: one line with the session name, fidelity dots, action button, stage icons, then handoff, files and close (CDR "The line reads left to right").

### (S) Chat Bar --> Display Fidelity Progress

Mirrors Display Fidelity Progress and Display Violations Band: one dot per practice in its colour, shaded by state, with the violation count in red (CDR "Fidelity dots").

### (S) Person --> Display Session Card

Mirrors Display Ticket Card: hovering the session name opens the card over the strip, each fidelity's name and state over its dot and the stage name over the stage icons (CDR "Session name and session list").

### (S) Person --> Open Board

Mirrors Open Board: clicking a dot opens `/board` on that session and fidelity (CDR "Fidelity dots").

## (E) Steer Sessions

### (S) Person --> Create New Session

Mirrors Open Ticket Session: a field in the session list box names a new session, which `ticket.create` creates; the activation dialog then opens it (CDR "Session name and session list").

### (S) Person --> Open Session

Mirrors Activate Ticket: picking a session from the session list box opens the activation dialog, then calls `ticket.activate` (CDR "Session name and session list").

### (S) Person --> Write Session Handoff

Mirrors Write Ticket Handoff: the handoff button on the line (CDR "Handoff, files, close").

### (S) Person --> Close Active Session

Mirrors Close Active Session: the close button on the line closes the active session through `ticket.close`, asking what to do with its work as the board does (CDR "Handoff, files, close"; confirmed by the person on 2026-11-04).

## (E) Guide Work Through Practices

### (S) Person --> Invoke Next Fidelity Action

Mirrors Send Next Fidelity Action, for one fidelity: the action button runs generate, validate or review on the fidelity whose dot was clicked (CDR "Action button and ▾ picker"; "Actions run on one fidelity at a time").

### (S) Person --> Choose Fidelity Action

Mirrors Choose Action And Formats, without formats: the ▾ picker offers generate, validate, review, iterate, sketch, render and document (CDR "Action button and ▾ picker").

### (S) Person --> Display Stage Fidelities

Mirrors Open Practice Tile at stage level: clicking a stage icon shows that stage's fidelities on the dots (CDR "Stage icons").

### (S) Person --> Move Session To Next Stage

Mirrors Move Ticket, forward only: once every fidelity of the stage is reviewed, the action button calls `ticket.move_next` (CDR "Action button and ▾ picker").

## (E) Review Fidelity Outputs

### (S) Person --> List Session Files

Mirrors List Ticket Files, for the focused fidelity only: files opens a tab per file `ticket.files` declares (CDR "Handoff, files, close").

### (S) Person --> View Fidelity Files

Mirrors View Fidelity Files: each tab's text comes from `ticket.read_file` (CDR "Handoff, files, close").

### (S) Chat Bar --> Browse Session Folder

Mirrors Browse Ticket Folder: the session card shows each fidelity's folders beside it (CDR "Session name and session list").

### (S) Person --> Review Fidelity

Mirrors Review Fidelity: review calls `ticket.finish_review` with one fidelity, which needs its latest Validate to have passed (CDR "Actions run on one fidelity at a time").

---

## Scope boundary

**In scope:** the stage strip above the chat prompt for the active session, doing what the Session Board does for one session and one fidelity at a time through the same `ticket.*` tools.

**Out of scope:** tickets as a bar concept; the board's whole-board work (Backlog items, WIP limits, side panels, split, archive, moving back a stage), validation reports and Fix, format chips, an expanded bar mode (CDR "Considered options"), and options A and C.
