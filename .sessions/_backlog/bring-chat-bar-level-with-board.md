# Bring Chat Bar Level With Board

Analysis and planning: the stories here are not built yet, or only partly built where a story says so. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** everything a person can do to one session on the board, they can do from the chat bar.

**Slicing notes:** Requested on 2026-11-06: each channel does what the other does for one session.

## Notes from the backlog

From `expand-panel-enhancements.md`:

> Make the chat bar's expanded session card do more:
>
> - Toggle practices on and off from the card.
> - Click a practice to get its file list, and open its validation report.
> - Toggle formats on the card, as the format chips do on the bar.
> - Show the file list, with each file clickable to open it.

Built today: pressing a fidelity on the card selects it, and several can be selected (Select Several Fidelities); each fidelity's folder chip on the card opens its files (Display Session Card); the files view has one tab per file (View Session Files); the bar's format chips turn formats on and off (Choose Format); the bar's violation count opens the report (Open Validation Report From Violation Count). What is left sits on existing stories rather than new ones: practices on and off from the card on Choose Session Practices, here; the card's own format chips on Choose Format and its report link on Open Validation Report From Violation Count, both noted on those stories.

From `board-enhancements.md`: "add feature to backlog widget for existing apps" and "repo actions". Requested on 2026-11-10: in the chat bar, an Add to backlog button, and buttons for common repo actions such as push, pull and commit (Add Backlog Item From Chat Bar, Commit Work From Chat Bar, Push Work From Chat Bar, Pull Latest From Chat Bar).

## Epic: Move Work Forward From Chat Bar

### Feature: Guide Work Through Practices In Chat Bar

#### Story: Move Session To Previous Stage

*Person*. Requested (2026-11-06, as the CDD Kanban does): the chat bar moves the session back a stage through `ticket.move_previous`.

#### Story: Mark Session Done In Stage

*Person*. Requested (2026-11-06, as the CDD Kanban does): the chat bar marks the active session Done in its stage and back to In progress.

#### Story: Choose Session Practices

*Person*. Requested (2026-11-06, as the CDD Kanban does): the chat bar turns the active session's practices on and off through `ticket.enable_practice`. Intended (`.sessions/_backlog/bring-chat-bar-level-with-board.md` "Toggle practices on and off from the card"): the practices turn on and off from the expanded session card.

#### Story: Open Fidelity Help

*Person*. Requested (2026-11-06, as the CDD Kanban does): the chat bar opens the same help for a fidelity or practice through `board.help`.

#### Story: Choose Session Folders From Chat Bar

*Person*. Requested (2026-11-10, "new session or session where folders aren't set on switch --> probably one dialog box, eg expand above chat bar"): when the chat bar creates a session that does not come from a backlog item, or switches to a session whose workpath and practice roots are not set, one dialog opens above the chat bar to choose the workpath and each practice's root, as the board's Choose Where A Backlog Item Works and Choose Session And Practice Roots (built today) do.

### Feature: Work Fidelity Outputs In Chat Bar → Review Fidelity Outputs In Chat Bar

#### Story: Fix Violations From Chat Bar

*Person*. Requested (2026-11-06, as the CDD Kanban does): the chat bar sends Fix and Fix all for the report it opens.

### Feature: Steer Sessions

#### Story: Add Backlog Item From Chat Bar

*Person*. Requested (2026-11-10, "add feature to backlog widget in chat ui --> have add feature to backlog button and buttons for common repo actions eg push, pull, commit"), from `.sessions/_backlog/bring-chat-bar-level-with-board.md`: an Add to backlog button on the chat bar adds a feature to the backlog, as the board's Add Backlog Item does.

#### Story: Commit Work From Chat Bar

*Person*. Requested (2026-11-10, "add feature to backlog widget in chat ui --> have add feature to backlog button and buttons for common repo actions eg push, pull, commit"): a Commit button commits the active session's changes (`Repo.commit` in `space/repo/repo.py`).

#### Story: Push Work From Chat Bar

*Person*. Requested (2026-11-10, "add feature to backlog widget in chat ui --> have add feature to backlog button and buttons for common repo actions eg push, pull, commit"): a Push button pushes the active session's branch (`repo.push_commit`).

#### Story: Pull Latest From Chat Bar

*Person*. Requested (2026-11-10, "add feature to backlog widget in chat ui --> have add feature to backlog button and buttons for common repo actions eg push, pull, commit"): a Pull button pulls the latest commits into the active session's checkout (`Repo.pull` in `space/repo/repo.py`).
