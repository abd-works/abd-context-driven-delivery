# A ticket keeps its published tools and data fields, and hands the work to the parts it holds

Round 9 split `Ticket` by job (finding 1 of `round9-space-tools.md`; fix rule 10). It held three jobs: its progress, its git checkout, and the moves and marks a person makes on its stages. Each is now a part the ticket makes once, with a name from the board's language:

- *TicketWork* (`ticket.work`): its progress on each fidelity the board requires, read from its session's log once per ticket read, the one command that runs an action on its fidelities, and the one way a line is written for it (`record`).
- *TicketCheckout* (`ticket.checkout`, `ticket_checkout.py`): its own *Branch*, made once, the branch its work is on, its worktree and the chat working there, what opening, leaving, and closing it can do now, and doing it (`open`, `open_worktree`, `leave`).
- *StageMarks* (`ticket.marks`): its latest move and its latest mark in a stage, which its session's log answers (`SessionLog.latest`), and writing a move or a mark.

That took `Ticket` from 48 methods and a total complexity of 143 to 33 methods and a total complexity of 75. The rule asks for under 30 methods. We keep the 33 because 32 of them are what the ticket publishes:

- 15 MCP tools (`ticket.create`, `branch`, `work_branch`, `format_choices`, `close_choices`, `leave_choices`, `open_choices`, `activate`, `open_worktree`, `move_next`, `move_previous`, `move_to`, `close`, `archive`, `violations`). The chat bar, the CDD Kanban app, the installed slash commands, and the stub chat in `harness/chat-ui` call them by these names, and a toolset publishes a tool under its own class's name, so moving a tool onto a part would rename it.
- 15 data fields (`name`, `title`, `session`, `progress`, `column`, `is_closed`, `is_active`, `drop_targets`, `is_done`, `next`, `agent_context`, `last_activity`, `worktree`, `working_chat`, `stage_work`), which the generated TypeScript `TicketData` reads by these keys.
- Its constructor and its `@tool_subject` loader, which every tool needs.

Each published method is one line that asks a part, or the few lines that decide a column or a move from what the parts answer. The one private method left, `_return_to_backlog`, is shared by `move_previous` and `move_to`.

Revisit when the harness can publish a held part's tools under its owner's name: then the checkout's five tools can move onto `TicketCheckout` without renaming them, and `Ticket` drops under 30.

## Version 1 refactoring: four more parts

The Clean Engineering review of the version 1 refactoring found `Ticket` still changing for many reasons: its parent and child tree, its file listings and format and overlay choices, its stage moves, and closing, archiving, deleting, and shelving it. Each is now a part made once with the ticket, and each published tool or data field asks one of them in one line:

- *TicketTree* (`ticket.tree`, `ticket_tree.py`, with `ParentMovesWithChildrenError`, `NotAChildError`, and `ParentLoopError`): its ancestors, the tickets it can become a child of, whether it is stacked, the stage of its child furthest back, refusing to move a parent, and `add_child`, `pull_out`, and `reassign_parent`.
- *TicketChoices* (`ticket.choices`, `ticket_choices.py`): `fidelity_files`, `root_files`, `format_choices`, `choose_formats`, `overlay_choices`, and `choose_overlays`.
- *TicketMoves* (`ticket.moves`): `move_next`, `move_previous`, `move_to`, and where Move next and Move previous put it (`next_place`, `previous_place`).
- *TicketEnding* (`ticket.ending`): `close`, `archive`, `delete`, and `to_backlog`, each refusing main.

The published names still sit on `Ticket`, for the reason above: a toolset publishes a tool under its own class's name, and the generated TypeScript `TicketData` reads its data fields by key. What changes when a tree rule, a choice, a move, or an ending changes is now the part, not the ticket.

The same holds for `Board` (`board.folders`, `board.help`, `board.save_again`, `board.set_sends_fixes_directly`), `Repo` (`repo.push_commit`, `push_work`, `merge_to_main`, `push_to_main`, which ask its *Publishing*), `Session` (the graph tools, which ask its *SessionExplorer*; its graph and practices, which are its *PracticeOutputs*; a guidance selection's update, which its *GuidanceVersion* makes), and `Sessions` (`sessions.current` and `sessions.switch`, which ask its *OpenSessions*): each keeps its published names and asks the part that owns the reason to change.

## Version 1 refactoring, round 2: tools declared by job on mixed-in bases

The second Clean Engineering review still counted `Ticket` (28 public operations), `Session` (32), and `BacklogItem` (14) over the nine a class should expose, because every published tool was declared on the class itself. A toolset publishes every tool its class's bases declare, under its own name, so the declarations now sit by job on bases mixed in ahead of the class's own base. Each base is `@hosted_only`, so install and the hook server load no toolset of it on its own, and each tool on it is still one line that asks the part owning the work. Every published name, signature, and data field is unchanged.

- `Ticket`: *TicketCheckoutTools* (`branch`, `work_branch`, `assign_chat`, `close_choices`, `activate`), *TicketChoiceTools* (`fidelity_files`, `root_files`, `format_choices`, `choose_formats`, `overlay_choices`, `choose_overlays`), *TicketMoveTools* (`move_next`, `move_previous`, `move_to`, `move_before`), *TicketTreeTools* (`add_child`, `pull_out`, `reassign_parent`), *TicketEndingTools* (`close`, `archive`, `delete`), and *TicketTextTools* (`edit_text`, `tag`). `ticket.violations` asks its *TicketWork* (`work.violations`).
- `Session`: *SessionFileTools*, *SessionGraphTools*, *SessionGuidanceTools*, *SessionLogTools*, and *SessionDecisionTools*.
- `BacklogItem`: *BacklogOrderTools* (`move_before`, `move_after`). Its `move_next` and `move_previous`, which only a spec called, are gone, with `Card`'s abstract pair; `from_ticket` writes the idea file a ticket never had, so `write_if_missing` is gone too.

The operations that were not tools moved into parts instead:

- `Board` keeps its six tools, its loader, `column`, and `stage`. Finding and opening tickets (`ticket`, `ticket_called`, `open_ticket`) and starting a new read (`reread`) are its *CardPlacement* (`board.placement`), which now holds the current read; finding a backlog item (`backlog_item`, `backlog_item_called`) is that read, its *BoardReads* (`board.reads`).
- `Repo` keeps its five published tools, its `of_project` loader, `path_from_top`, and `branch_named`; its refs are its *Refs* (`repo.refs.has`), its uncommitted work and committing it are its *WorkingTree* (`repo.working_tree`: `is_dirty`, `is_merging`, `commit`), and the repository of another checkout is `repo.worktrees.repository_at(folder)`; `MockGit` keeps its branches in its *HeldBranches* (`held.branches`).
- `Sessions` lists its sessions through its *SessionListing* (`sessions.listing`) and keeps the sessions this process holds in its *HeldSessions* (`sessions.held`); a fidelity's *FidelitySessionOutput* answers for the files it wrote through its *WrittenFiles* (`session_output.written`).
