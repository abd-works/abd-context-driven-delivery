# git — module context

## Purpose

**Git** utility (`utilities/git/`): object-oriented domain for a local git clone plus
GitHub workflow surfaces. Models **Repo → Branch → Commit** for version control and
**Repo → Project → Ticket → TicketState** for kanban/issue workflow. Tickets also
carry **research tags**, **notes**, and **flow** on that same graph (git notes and
commit trailers) — not a parallel yaml ticket index. Callers use domain objects, not
a subprocess helper module.

## Primary use case

**Workspace** composes `GitRepo` (`Repo` alias) on `WorkSession.git` for session-branch
checkout, commit, push, and eval notes. **Workflow** composes `Repo` for backlog/start/finish
(GitHub issue + Project Status) without duplicating gh logic. Tests use `Repo.memory()`
(legacy `NullGitRepo()`) — no git/gh on PATH required.

## Seam

`git.git:Git` is a **manifest facade** for the domain types — not an IDE skill. Do not deploy `/git`. Slash commands belong on Workflow (`/backlog`, `/start-ticket`, `/finish-ticket`). Mark a git operation with `@prompt` only if a dedicated command is needed. Seam terms: Repo, Branch, Commit, Project, Ticket, TicketState, Git, ResearchTag.

## Constraint

- Callers depend on **domain types** (`Repo`, `Branch`, `Project`, `Ticket`, …).
- **Git-primary** for provenance: commit message trailers (`GitHub-Issue:`, `Workflow-State:`)
  and git notes (`refs/notes/eval-mistakes` and ticket/research notes) — not parallel yaml indexes.
  Research tags, ticket notes, and flow live on Ticket / Project / TicketState (Backlog / In Progress / Done only).
- **Workflow** orchestrates; **Repo** executes git/gh — do not embed ticket or merge policy
  inside `Repo` beyond thin wrappers.
- `Repo.memory()` is for **tests and dry runs** — production paths use `Repo.open()`.

## Public API

- `Repo.find_root(start)` / `Repo.open(start)` — locate and open a real clone
- `Repo.memory(root)` / `InMemoryRepo(root)` / `NullGitRepo(root)` — in-memory clone for specs
- `Repo.branch` / `Repo.branch_named(name)` → `Branch`
- `Repo.agent_sessions` / `Repo.put_agent_session` / `Repo.default_session_name` — AgentSession registry on primary repo
- `Branch.checkout()` / `Branch.checkout_or_create()` → `Branch`
- `Branch.worktree` → `Worktree`; `Branch.bind_agent_session` / `Branch.agent_session`
- `Branch.commit(paths, message)` → `Commit`, `Branch.merge(other)` → `Commit`
- `Commit.format(subject, trailers)` / `Commit.from_message(sha, message)` — message + trailer `data`
- `Repo.attach_project(owner, number)` → `Project` (links the board onto this repository)
- `Project.link_repository()` — `gh project link` so the board appears on the repo Projects tab
- `Project.state_named(name)` — column on the board
- `Ticket.set_status(state)` / `Ticket.parse_number(ref)` / `Ticket.github_ref(...)` / `Ticket.close()`
- `Ticket.add_label(name)` / `Ticket.add_theme(theme)` / `issue_theme_label(theme)` — issue-sidebar `theme:<slug>` (filter/group; not a Status column)
- `Ticket.set_type(name)` — apply an org issue Type name (WorkTicket owns defect / small change / feature mapping)
- `Repo.list_issue_types()` / `Repo.ensure_issue_type(name, description=, color=)` — org issue types for the repo owner
- `Ticket` — `number`, `title`, `body`, `url`, `state`, `issue_type`, `labels`, open `data` map
- `TicketState` — column name (`Backlog`, `In Progress`, `Done`)
- `resolve_github_status_option(name, options)` — exact GitHub Status match first, then aliases (`Backlog` ↔ `Todo`)
- `Repo.ticket(ref)` / `Repo.create_ticket(title, body)`
- `Repo.workflow_commit_message(subject, issue_number, workflow_state, reviewed_by=...)`
- Flat legacy surface on `Repo` for workspace: `checkout_or_create`, `commit`, `push`,
  `merge_branch`, `note`, `read_notes`, `find_mistakes`,
  `write_annotated_tag` / `read_annotated_tag` / `list_annotated_tags`,
  `is_dirty` (ignores `events.log`), `current_branch`
- Worktree surface: `Worktree`, `list_worktrees`, `worktree_for`, `add_worktree`,
  `remove_worktree`, `fetch` / `pull` / `fetch_pull`, `merge_from` (merge into the
  current branch without checking the other out), `push_to`, `has_stash`,
  `is_linked_worktree`, `primary_root`

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
`Ticket.set_status` sends the live Status option to gh (workflow `Backlog` → GitHub `Todo` when
that is the board option). Memory mode still records the workflow name (`Backlog`).

## Rationale

Git and GitHub were split across `workspace/git_repo.py` and `workflow/gh_client.py` —
duplicate subprocess wrappers and no shared ticket/project model. Consolidating under
`utilities/git` gives one OO graph aligned with the backbone (G-04, G-36, G-37): git
records decisions at commit time; GitHub holds live collaboration state. Small focused
types replace a fat `GhClient`/`GitRepo` service.
