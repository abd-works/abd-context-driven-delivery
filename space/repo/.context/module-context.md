# git — module context

## Purpose

**Git** (`space/git/`): object-oriented domain for a local git clone plus
GitHub workflow surfaces. Models **Repo → Branch → Commit** for version control and
**Repo → Project → ProjectTicket → ProjectTicketState** for kanban/issue workflow. Tickets also
carry **research tags**, **notes**, and **flow** on that same graph (git notes and
commit trailers) — not a parallel yaml ticket index. Callers use domain objects, not
a subprocess helper module.

## Primary use case

**Workspace** composes `GitRepo` (`Repo` alias) on `WorkSession.git` for session-branch
checkout, commit, push, and eval notes. **Workflow** composes `Repo` for backlog/start/finish
(GitHub issue + Project Status) without duplicating gh logic. Tests use `Repo.memory()`
(legacy `NullGitRepo()`) — no git/gh on PATH required.

## Seam

`space.repo.repo:Repo` — chaining slash `/branch {name}` and `/worktree {name}` (MCP `repo.branch`, `repo.worktree`); skill `/branch-create` and slash `/new-branch` (MCP `repo.new_branch`); `/switch-branch`, `/close-branch`, `/new-worktree`, `/switch-worktree`, `/close-worktree` (instruction commands → matching `repo.*` MCP tools); skill `/branch-switch` (MCP `repo.branch_switch`). Branch primitives never add worktrees. `/push` (slash instructions → MCP `repo.push_commit`). Workflow board moves stay on `tools/workflow`. Seam terms: Repo, Branch, Commit, Project, ProjectTicket, ProjectTicketState, ResearchTag.

## Constraint

- Callers depend on **domain types** (`Repo`, `Branch`, `Project`, `ProjectTicket`, …).
- **Git-primary** for provenance: commit message trailers (`GitHub-Issue:`, `Workflow-State:`)
  and git notes (`refs/notes/eval-mistakes` and ticket/research notes) — not parallel yaml indexes.
  Research tags, ticket notes, and flow live on ProjectTicket / Project / ProjectTicketState (Backlog / In Progress / Done only).
- **Workflow** orchestrates; **Repo** executes git/gh — do not embed ticket or merge policy
  inside `Repo` beyond thin wrappers.
- `Repo.memory()` is for **tests and dry runs** — production paths use `Repo.open()`.

## Public API

- `Repo.find_root(start)` / `Repo.open(start)` — locate and open a real clone
- `Repo.memory(root)` / `NullGitRepo(root)` — in-memory clone for specs
- `Repo.branch_named(name)` → `Branch` (current: `branch_named(current_branch)`)
- `Branch.checkout()`, `Branch.commit(paths, message)` → `Commit`, `Branch.merge(other)` → `Commit`
- `Commit.format(subject, trailers)` / `Commit.from_message(sha, message)` — message + trailer `data`
- `Commit` marks `sha`, `subject`, `message`, and trailer `data` with `@data_field`, so `data_of(commit)` is the JSON result of `repo.push_commit`
- `Repo.attach_project(owner, number)` → `Project` (links the board onto this repository)
- `Project.link_repository()` — `gh project link` so the board appears on the repo Projects tab
- `Project.state_named(name)` — column on the board (any live Status option)
- `Project.refresh_states()` / `Project.status_option_names()` — hydrate columns from GitHub
- `GH_PROJECT_SCOPES_HINT` — `gh auth refresh -h github.com -s read:project,project` when board API calls fail
- `ProjectTicket.set_status(state)` / `ProjectTicket.parse_number(ref)` / `ProjectTicket.github_ref(...)` / `ProjectTicket.close()`
- `ProjectTicket.add_label(name)` / `ProjectTicket.add_theme(theme)` / `issue_theme_label(theme)` — issue-sidebar `theme:<slug>` (filter/group; not a Status column)
- `ProjectTicket.write_type(name)` — apply an org issue Type name (WorkTicket owns defect / small change / feature mapping)
- `Repo.list_issue_types()` / `Repo.ensure_issue_type(name, description=, color=)` — org issue types for the repo owner
- `ProjectTicket` — `number`, `title`, `body`, `url`, `state`, `issue_type`, `labels`, open `data` map, `parent_number`, `sub_issue_numbers`, `comments`, `project_theme`, `project_fields`, `archived`. Each ticket holds its own state; `Repo.memory()` keeps the tickets it created and changes them in place, so nothing about a ticket is stored on `Repo` under its number
- `ProjectTicketState` — column name (`Backlog`, `In Progress`, `Done`)
- `Project.github_status_option(state_name, option_names)` / `Project.github_theme_option(theme, option_names)` — exact GitHub field match first, then Status aliases (`Backlog` ↔ `Todo`)
- `Repo.ticket(ref)` / `Repo.create_ticket(title, body)`
- `Repo.workflow_commit_message(subject, issue_number, workflow_state, reviewed_by=...)`
- Flat legacy surface on `Repo` for workspace: `checkout_or_create`, `commit`, `push`,
  `merge_branch`, `note`, `read_notes`, `find_mistakes`,
  `write_annotated_tag` / `read_annotated_tag` / `list_annotated_tags`,
  `is_dirty` (ignores `events.log`), `current_branch`
- Worktree surface: `Worktree` (one checkout: its `path` and the `Branch` checked out there, `None` when detached; `Worktree.from_repo(repo)` and `Worktree.from_checkout(path, branch_name)` build one), `Branch.worktree` (the worktree that has the branch checked out), `Branch.open_in_worktree()` (returns that `Worktree`), `list_worktrees`, `add_worktree(path, branch: Branch) -> Worktree`,
  `remove_worktree(worktree)`, `fetch` / `pull` / `fetch_pull`, `merge_from` (merge into the
  current branch without checking the other out), `push_to`, `has_stash`,
  `is_linked_worktree`, `checkout_folder` (the checkout holding the folder, else the folder itself), `primary_root` (the main checkout, read from a linked worktree's `.git` file and its `commondir`)
- `space.work_state.WorkState` saves the open branch, worktree, and session in `.sessions/session.json`: `branch` is a `Branch` and `worktree` a `Worktree`, `None` when none is saved. `project_checkout()` and `board_checkout()` answer through `Repo.checkout_folder` and `Repo.primary_root`. The MCP repo operations keep string `name` and `repo_path` parameters and turn them into a `Branch` or `Repo` straight away

## Dependencies

- stdlib (`subprocess`, `pathlib`, `dataclasses`)
- `git` and `gh` on PATH for `Repo.open()` (optional for `Repo.memory()`)
- `tools.tool` — `@toolset` on manifest class `Git`
- consumed by `workspace` (shim), `workflow` (orchestration)

## Mechanism

Domain objects hold behavior; `Repo.git` / `Repo.gh` run the CLIs. `Repo.memory()`
stores branches, commits, tickets, project status, and notes in plain dicts/lists — same
public API as CLI-backed `Repo.open()`. Commit trailers are parsed into `Commit.data`;
workflow helpers format `GitHub-Issue:` and `Workflow-State:` lines. Project status maps
to GitHub Projects via `gh project link` / `item-add` / `item-edit` when not in memory mode.
`ProjectTicket.set_status` sends the live Status option to gh (workflow `Backlog` → GitHub `Todo` when
that is the board option). Memory mode still records the workflow name (`Backlog`).

## Rationale

Git and GitHub were split across `workspace/git_repo.py` and `workflow/gh_client.py` —
duplicate subprocess wrappers and no shared ticket/project model. Consolidating under
`space/git` gives one OO graph aligned with the backbone (G-04, G-36, G-37): git
records decisions at commit time; GitHub holds live collaboration state. Small focused
types replace a fat `GhClient`/`GitRepo` service.
