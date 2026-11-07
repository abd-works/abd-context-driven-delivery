# space/repo
*Repo* is the local git clone of the project being worked on, together with its GitHub project, so callers open, switch, commit, push, merge, and close work without running `git` or `gh` themselves. `Repo.current()` is the clone of the project the running call names, so one cdd server answers chats on several projects and no repo tool takes a repository path.

*Branch* is a line of development on a *Repo*: it is saved, opened in a *Worktree*, merged, and closed. *Worktree* is a second checkout of the same clone where one branch is worked on while the main clone stays on another. *Commit* is a recorded snapshot whose message carries trailers such as `GitHub-Issue:` and `Workflow-State:`; git commit trailers are the record of why a change was made, so there is no second index of tickets to keep in step.

*Project* is the repository's GitHub project board; *ProjectTicket* is a GitHub issue on that board, and *ProjectTicketState* is the board column it sits in (Backlog, In Progress, Done). A ticket's identity is its GitHub issue number.

`Repo.session_named(name)` is the work session called `name`, such as a board ticket's; `Repo.current_session` is the one saved as open.

The MCP tools `repo.switch_branch`, `repo.close_branch`, `repo.switch_worktree`, `repo.close_worktree`, and `repo.push_commit` act on `Repo.current()`, and the commands `/switch-branch`, `/close-branch`, `/switch-worktree`, `/close-worktree`, and `/push` call them.

- **Purpose:** Give every caller one object graph for the clone, its branches and worktrees, its commits, and its GitHub tickets, so version control and ticket flow are never reimplemented with raw `git` or `gh` output.
- **Seam (terms):** Repo, Branch, Worktree, Commit, Project, ProjectTicket, ProjectTicketState, `Repo.current`, `Repo.session_named`, `repo.switch_branch`, `repo.close_branch`, `repo.switch_worktree`, `repo.close_worktree`, `repo.push_commit`
- **Dependencies (one-way):** `harness/agent_tools`, `harness/installation`, `harness/mcp`, `space` (*WorkState*, `project_checkout`), `space/session`, `tools/file_manager` (*FileManager*). `space` (*WorkState* reads the saved *Branch* and *Worktree*) and `space/session` import `space/repo` back, and `tools/file_manager` imports `space/session`, which imports `space/repo`; these cycles are tracked in `.sessions/_backlog/break-module-dependency-cycles.md`.

## Constraint

Callers pass the domain objects (*Repo*, *Branch*, *Worktree*, *Commit*, *ProjectTicket*), never branch names or `git` output as strings. A *Repo* acts only on the clone it was made for; to act on another clone, make a *Repo* for that clone, so a call can never change a clone it did not mean to. The repo tools take no repository path; they act on `Repo.current()`. `Repo.memory()` is for specs and dry runs only; production code uses `Repo(path)`, `Repo.open(start)`, or `Repo.current()`.
