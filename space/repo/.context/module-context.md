# repo — module context

## Purpose

**Repo** (`space/repo/`): the object-oriented domain for a local git clone and its GitHub project. It models
**Repo → Branch → Commit** and **Repo → Worktree** for version control, and
**Repo → Project → ProjectTicket → ProjectTicketState** for GitHub issues on a project board. Tickets carry research
tags, notes, and flow in git itself (git notes and commit trailers), so there is no second ticket index to keep in step.
Callers work through these objects rather than running `git` or `gh` themselves.

## Primary use case

The session board (`harness/kanban`) and the session (`space/session`) use `Repo` to open, switch, commit, push, merge,
and close a ticket's branch and worktree, and to find `.sessions/`, the backlog folder, and the board file. Chats reach
the same operations through the MCP tools `repo.switch_branch`, `repo.close_branch`, `repo.switch_worktree`,
`repo.close_worktree`, and `repo.push_commit`. Specs use `Repo.memory()`, which needs no `git` or `gh` on PATH.

## Seam

`space.repo.repo:Repo` is the toolset. `Repo.current()` is its `@tool_subject` loader: every MCP call loads the clone of
the project the running call names (`project_checkout()`, read from the request through `working_on`), so one cdd server
can answer chats on several projects without a path parameter on each tool. The instruction commands `/switch-branch`,
`/close-branch`, `/switch-worktree`, `/close-worktree`, and `/push` call the matching MCP tools.

Seam terms: Repo, Branch, Worktree, Commit, Project, ProjectTicket, ProjectTicketState, CliAgentBinding.

## Constraint

- Callers depend on the domain types (`Repo`, `Branch`, `Worktree`, `Commit`, `Project`, `ProjectTicket`), not on
  `git` output or branch names passed around as strings.
- A `Repo` acts on the clone it was made for. Its operations never take a path to another clone; make a `Repo` for that
  clone instead, so a call can never act on a clone it did not mean to.
- The worktree a branch moved to is saved in `.sessions/session.json` (`WorkState.worktree`), not held in memory, so
  `push_commit` from the main clone commits in that worktree after a restart as well as before it.
- Git is the record of provenance: commit trailers (`GitHub-Issue:`, `Workflow-State:`) and git notes
  (`refs/notes/eval-mistakes` and ticket notes).
- `Repo.memory()` is for specs and dry runs; production code uses `Repo(path)`, `Repo.open(start)`, or `Repo.current()`.

## Public API

- `Repo(root)`, `Repo.open(start)`, `Repo.current()`, `Repo.memory(root)`; `find_root`, `is_clone`, `checkout_folder`,
  `primary_root`, `is_linked_worktree`
- Folders: `sessions_folder`, `session_folder(name)`, `backlog_folder`, `board_file`, `sessions`, `current_session`,
  `path_from_top(path)`, `files_changed_on(branch)`, `file_manager`
- Branches: `branch_named(name)` → `Branch` (`exists`, `is_checked_out`, `worktree`, `open_in_worktree()`, `save`,
  `close`), `has_branch`, `current_branch`, `checkout_from_default`, `create_branch`, `delete_branch`, `merge_from`,
  `merge_branch`, `push_to`, `fetch` / `pull` / `fetch_pull`
- Worktrees: `Worktree` (its `path`, its `Branch`, its `repository`), `list_worktrees`, `add_worktree(path, branch)`,
  `remove_worktree(worktree)`
- Commits: `commit(paths, message)`, `push_upstream`, `is_dirty`, `has_unpushed_commits`; `Commit.format(subject,
  trailers)` and `Commit.from_message(sha, message)`; `Commit` marks `sha`, `subject`, `message`, and `data` with
  `@data_field`, so `data_of(commit)` is the JSON result of `repo.push_commit`
- Tools: `switch_branch(name)`, `close_branch(name, commit_message)`, `switch_worktree(name)`,
  `close_worktree(commit_message)`, `push_commit(message, untracked, sync_remote)`
- Tags and notes: `write_annotated_tag` / `read_annotated_tag` / `list_annotated_tags`, `note`, `read_notes`,
  `find_mistakes`, `read_cli_agent_tag`
- GitHub: `attach_project(owner, number)` → `Project` (`link_repository`, `state_named`, `refresh_states`,
  `status_option_names`, `github_status_option`, `github_theme_option`); `ticket(ref)`, `create_ticket(title, body)` →
  `ProjectTicket` (`set_status`, `add_label`, `add_theme`, `write_type`, `comment`, `close`); `list_issue_types`,
  `ensure_issue_type`; `GH_PROJECT_SCOPES_HINT` names the `gh auth refresh` scopes board calls need
- `space.work_state.WorkState` saves the open branch, worktree, and session in `.sessions/session.json`;
  `project_checkout()` and `board_checkout()` answer through `Repo.checkout_folder` and `Repo.primary_root`
- `space.repo.latest_release.LatestRelease` keeps the landed release's end-to-end results when a branch closes

## Dependencies

- stdlib (`subprocess`, `pathlib`, `dataclasses`); `git` and `gh` on PATH for a real clone
- `harness.agent_tools` (`@agent_toolset`, `@agent_tool`, `@tool_subject`), `harness.mcp` (`@mcp`),
  `harness.installation` (`@command`, `@data_field`)
- `space.work_state` for the saved branch, worktree, and session
- Consumed by `harness/kanban` (Board, Ticket, Report), `space/session`, and `space/work_state`

## Mechanism

`Repo.git` and `Repo.gh` run the command-line tools; `Repo.memory()` keeps branches, commits, tickets, project status,
and notes in plain dicts and lists behind the same public API. Commit trailers are parsed into `Commit.data`.
`ProjectTicket.set_status` sends the live Status option to `gh` (workflow `Backlog` becomes GitHub `Todo` when that is
the board's option); memory mode records the workflow name.

## Rationale

Git and GitHub were once split across a workspace git wrapper and a workflow `gh` client, with duplicate subprocess
code and no shared ticket model. One object graph under `space/repo` gives every caller the same Branch, Worktree, and
Commit objects, keeps git as the record of what was decided at commit time, and leaves live collaboration state on
GitHub.
