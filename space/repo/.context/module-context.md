# space/repo
*Repo* is the local git clone of the project being worked on — its branches and its commits — so callers switch, commit, push, merge, and close work without running `git` themselves. `Repo.current(project)` is the clone holding the project a tool call names; the cdd server hands each repo tool its call's project, so one server answers chats on several projects and no repo tool takes a repository path.

*Branch* is a line of development on a *Repo*: it is checked out, switched to, saved (committed and pushed), moved into its own worktree, landed on the default branch, and closed. *Worktrees* (`repo.worktrees`) are the checkouts of the repository — the main clone and each linked worktree beside it — and a *Worktree* is one of them, where one branch is worked on while the main clone stays on another. *Commit* is a recorded snapshot whose message carries trailers such as `Ticket:`; git commit trailers are the record of why a change was made, so there is no second index of work to keep in step. *Git* (`repo.git`) runs the git command line in the clone, with one set of time limits and one error, *RepoConnectError*, for every operation. *LatestRelease* keeps the end-to-end results of the release that just landed and removes older ones.

The work sessions kept in the clone's `.sessions` folder are not the repository's concern: `space/session` owns them (*Sessions*).

The MCP tools `repo.switch_branch`, `repo.close_branch`, `repo.switch_worktree`, `repo.close_worktree`, and `repo.push_commit` act on `Repo.current(project)`; each finds the branch it names (else the branch saved as open in `.sessions/session.json`) and calls one operation on it. The commands `/switch-branch`, `/close-branch`, `/switch-worktree`, `/close-worktree`, and `/push` call them.

- **Purpose:** Give every caller one object graph for the clone, its branches and worktrees, and its commits, so version control is never reimplemented with raw `git` output.
- **Seam (terms):** Repo, Branch, Worktrees, Worktree, Commit, Git, RepoConnectError, `Repo.current`, `repo.switch_branch`, `repo.close_branch`, `repo.switch_worktree`, `repo.close_worktree`, `repo.push_commit`
- **Dependencies (one-way):** `harness/agent_tools`, `harness/installation`, `harness/mcp`, `space/work_state` (*WorkState*, which saves the open branch by its name and the open worktree by its folder; the repository turns them back into a *Branch* and a *Worktree*), `tools/file_manager` (*FileManager*, imported when first used).

## Constraint

Callers pass the domain objects (*Repo*, *Branch*, *Worktree*, *Commit*), never `git` output as strings. A *Repo* acts only on the clone it was made for; to act on another clone, make a *Repo* for that clone, so a call can never change a clone it did not mean to. The repo tools take no repository path; they act on the clone of the project their call names. Run git only through `repo.git`, so every command gets the same time limits and the same error. Specs that need a repository make a real one in a temporary folder; there is no in-memory repository.
