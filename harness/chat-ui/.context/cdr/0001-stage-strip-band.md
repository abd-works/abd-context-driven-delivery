# The chat bar is option B, the stage strip

The bar above the chat prompt shows the active session as one line, the stage strip, built from the session board's ideas within what a Claude Code mod can draw. Its design is `harness/.context/ux/ChatBar.dc.html`, published as version 48 of the Claude Design canvas https://claude.ai/artifact/RRarviRS8Hw74sQhWSaWXn (board "B · Stage strip with action bar"). The icons it draws are written into that artboard, each as a single filled path.

The line reads left to right:

- **Server health mark.** The server health band (`harness/chat-ui/pane/hooks/health/`) is the chat bar's first part: one glyph (✓ connected, ⟳ reconnecting, ✕ disconnected, ! tools missing) left of the session name. Hovering it opens the health panel above the line, and a click pins it. Hovering the session name stacks the same panel on top of the session card. Connected, the panel is one line of MCP host, Tools, Kanban app, Graph app and Hook server: each icon is green when running and grey when not, with only the tool count or port written, and each part's name on hover. Otherwise the panel shows a headline with Details, Run install and Reconnect. Canvas version 48 draws it.
- **Session name and session list.** The bar has no tickets: a person in the chat works in a session. A ▾ opens a list box of the sessions with their stages, plus a field to type a new session. Picking or creating one opens the board's activation dialog (LEAVE: commit, push, merge; OPEN: create branch, create worktree). Hovering the name opens the session card, laid out over the strip beneath it: each fidelity's colour, name and state sits over the dots, the stage name over the stage icons, and each fidelity's folders beside it.
- **Fidelity dots.** One square per practice in its practice colour, shaded by state as on the board. A fidelity with violations keeps its colour and shows its count in red. Clicking a dot opens `/board` on that session and fidelity and makes it the fidelity the action button acts on.
- **Action button and ▾ picker.** The button shows the next action for one fidelity as an icon (generate, validate, review), with the action and fidelity on hover. The picker offers every builder action (generate, validate, review, iterate, sketch, render, document). When every fidelity of the stage is reviewed, the button moves the session to the next stage (`ticket.move_next`).
- **Stage icons.** Backlog, Discovery (magnifier), Specification (document), Implementation (gear), Complete (check), in orange; stages not yet reached are faint, and only the stage in progress has an outline. Clicking a stage shows that stage's fidelities.
- **Handoff, files, close.** Close closes the active session (`ticket.close`), as Close does on the board; it does not just hide the bar. Files opens the board's files view for the selected fidelity only: a tab per file `fidelity-progress.files` declares, its text from `session.read_file`.

Actions run on one fidelity at a time. Each fidelity goes generate, then validate, and is done once its latest validate passes.

## Considered options

- **A · One-line rail.** A rail with a hover card and a single "▶ next" button that acted on every fidelity at once. Rejected: it had no way to act on one fidelity, and the stage reading was three dots that said little.
- **C · Status line and one glyph.** A ◆ glyph whose card held the whole action bar, with a status line below the prompt. Rejected: every action was two steps away, behind the card.
- **An expanded mode for B** with session, context and generated file lists. Tried and removed: it repeated what the collapsed line and the files view already give, so the collapsed line alone carries the bar.
