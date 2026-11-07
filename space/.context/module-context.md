# space
*Project being worked on* is the project a call acts on: the one the running call names, else `CDD_PROJECT`, else the current folder. One cdd server answers every chat, so the project belongs to the call, not to the process; `working_on(project)` runs one call on a project, and `project_folder()`, `project_checkout()`, and `board_checkout()` answer which folder, which checkout, and which checkout holds the board's `.sessions/`.

*WorkState* is the branch, worktree, and session saved as open in a checkout's `.sessions/session.json`, so the repo and session commands agree on what is open after a restart as well as before it. Its release folder, `.sessions/{release}/`, holds a release's session files, design canvas, and end-to-end results.

*ContextConfig* is a project's `.context/config.json`: the guidelines that apply to file patterns and the folder each practice writes in.

The work itself is kept by the child modules, each with its own card: the *Session* an agent works in, with the handoff the next agent resumes from and its Context Decision Records (`space/session`), and the *Repo* that session sits in (`space/repo`).

- **Purpose:** Tell every tool which project, checkout, and open work a call is about, and what the project configured, so sessions, the board, and the repo tools all find the same `.sessions/` and the same settings.
- **Seam (terms):** WorkState, ContextConfig, `working_on`, `project_folder`, `project_checkout`, `board_checkout`
- **Dependencies (one-way):** `space/repo` (*Repo*, *Branch*, *Worktree*, imported when first used). `space/repo` imports this module back — a cycle tracked in `.sessions/_backlog/break-module-dependency-cycles.md`.

## Constraint

Find the project through `project_folder()` or `project_checkout()`, never `Path.cwd()`, because a call from another chat names another project. Run a call on a project inside `with working_on(project):`; outside it, the project is `CDD_PROJECT` or the current folder. `CDD_REPO` names the CDD checkout that serves the tools, never the project. Read and write `session.json` through *WorkState* and `config.json` through *ContextConfig*, which keep the values other callers store there.
