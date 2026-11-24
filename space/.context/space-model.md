# space/work_state

A *WorkState* is what one chat has open — its branch, its worktree, and its session — kept by the cdd server in `~/.cdd/open-sessions.json`, never in the checkout.

- **Purpose:** Keep what is open true for one chat on one machine, so it is never committed and never clashes between worktrees.
- **Seam (terms):** WorkState, SESSIONS_FOLDER, E2E_RESULTS_FOLDER
- **Dependencies (one-way):** harness/installation, harness/mcp

## WorkState

The open branch, worktree, and session of one chat, or of one checkout folder for a call that names no chat. It keeps names only: the repository turns a branch name into its *Branch* and a worktree's folder into its *Worktree*.

+ WorkState(repo_root: Path | str, chat: str = '', home: Path | str | None = None)
------
+ root: Path
+ chat: str
+ sessions_folder: Path
+ path: Path
+ key: str
+ branch_name: str
+ worktree_folder: Path | None
+ session: str
----
+ load(): dict[str, str]
	// every chat's call reaches the one file in the one server process, so its read-change-write runs one at a time
---<<reads and writes>>--> JsonFile
---<<finds its file through>>--> CddHome
