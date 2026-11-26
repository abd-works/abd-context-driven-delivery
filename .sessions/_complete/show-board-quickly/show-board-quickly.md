# Show Board Quickly

Analysis and planning: the stories here are not built yet, or only partly built where a story says so. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** `board.show` stops repeating git checks, guidance parsing and session file reads, so the board and the chat bar answer faster and `space/kanban/kanban_tools_spec.py` runs in under 60 s.

**Slicing notes:** `.sessions/_backlog/show-board-quickly.md`. Technical stories in shared modules (`space/repo`, `harness/guidance`, `harness/installation`), so reinstall after; small, and can go in at any point.

## Notes from the backlog

From `speed-up-board-show.md`:

> board.show takes about 1.6 s per call (profiled), which makes space/kanban/kanban_tools_spec.py take about 200 s for 198 examples and slows the chat bar and the board.
>
> Causes:
> 1. Git checks per ticket: TicketCheckout._found_branch -> Branch.exists -> Repo.has_ref runs one `git show-ref` per check (~70 ms each, ~7 per board.show). space/kanban/ticket_checkout.py, space/repo/repo.py.
> 2. Practice guidance markdown re-read and parsed for every session (harness/guidance/guidance.py, harness/markdown/markdown.py). Cache by file and modification time.
> 3. session.json read thousands of times per few board.show calls (harness/installation/json_file.py). Read each once per board build.
>
> Goal: kanban_tools_spec under 60 s and a faster chat bar. Production change in shared modules; reinstall after.

## Epic: Move Work Forward On Session Board

### Feature: Show Board Quickly

#### Story: Check Ticket Branches Once Per Board Build

*Board App* (technical). Intended (`.sessions/_backlog/show-board-quickly.md` cause 1): `TicketCheckout._found_branch` → `Branch.exists` → `Repo.has_ref` runs one `git show-ref` per check, about 70 ms each and about 7 per `board.show` (`space/kanban/ticket_checkout.py`, `space/repo/repo.py`); one board build checks each branch once.

#### Story: Cache Practice Guidance By File And Change Time

*Board App* (technical). Intended (`.sessions/_backlog/show-board-quickly.md` cause 2): practice guidance markdown is read and parsed again for every session (`harness/guidance/guidance.py`, `harness/markdown/markdown.py`); it is cached by file and modification time.

#### Story: Read Session File Once Per Board Build

*Board App* (technical). Intended (`.sessions/_backlog/show-board-quickly.md` cause 3): `session.json` is read thousands of times over a few `board.show` calls (`harness/installation/json_file.py`); one board build reads each session file once.
