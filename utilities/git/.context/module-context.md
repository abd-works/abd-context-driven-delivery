# git — module context

## Purpose

**Git** utility (`utilities/git/`): object-oriented domain for a local git clone plus
GitHub workflow surfaces. Models **Repo → Branch → Commit** for version control and
**Repo → Project → Ticket → TicketState** for kanban/issue workflow. Subprocess
adapters stay in private `_cli.py`; callers use domain objects, not a monolithic
service class.

## Primary use case

**Workspace** composes `GitRepo` (`Repo` alias) on `WorkSession.git` for session-branch
checkout, commit, push, and eval notes. **Workflow** composes `Repo` for backlog/start/finish
(GitHub issue + Project Status) without duplicating gh logic. Tests use `Repo.memory()`
(legacy `NullGitRepo()`) — no git/gh on PATH required.

## Seam

`git.git:Git` manifest entry; domain types `Repo`, `Branch`, `Commit`, `Project`,
`Ticket`, `TicketState`. Legacy aliases `GitRepo` / `NullGitRepo` re-exported from
`workspace.git_repo` shim.

## Constraint

- Callers depend on **domain types** (`Repo`, `Branch`, …) — not `_cli.py` subprocess helpers.
- **Git-primary** for provenance: commit message trailers (`GitHub-Issue:`, `Workflow-State:`)
  and git notes (`refs/notes/eval-mistakes`) — not parallel yaml indexes.
- **Workflow** orchestrates; **Repo** executes git/gh — do not embed ticket or merge policy
  inside `Repo` beyond thin wrappers.
- `_cli.py` is **internal** — only imported by `git.py`.
- `Repo.memory()` is for **tests and dry runs** — production paths use `Repo.open()`.

## Public API

- `Repo.find_root(start)` / `Repo.open(start)` — locate and open a real clone
- `Repo.memory(root)` / `NullGitRepo(root)` — in-memory clone for specs
- `Repo.branch` / `Repo.branch_named(name)` → `Branch`
- `Branch.checkout()`, `Branch.commit(paths, message)` → `Commit`, `Branch.merge(other)` → `Commit`
- `Commit.format(subject, trailers)` / `Commit.from_message(sha, message)` — message + trailer `data`
- `Repo.attach_project(owner, number)` → `Project`
- `Project.add_ticket(ticket, state)`, `Project.set_ticket_state(ticket, state)`
- `Ticket.parse_number(ref)` / `Ticket.github_ref(owner, repo, number)`
- `Ticket` — `number`, `title`, `body`, `url`, `state`, open `data` map
- `TicketState` — column name (`Backlog`, `In Progress`, `Done`)
- `Repo.ticket(ref)`, `Repo.create_ticket(title, body)`, `Repo.close_ticket(ref)`
- `Repo.workflow_commit_message(subject, issue_number, workflow_state, reviewed_by=...)`
- Flat legacy surface on `Repo` for workspace: `checkout_or_create`, `commit`, `push`,
  `merge_branch`, `note`, `read_notes`, `find_mistakes`, `is_dirty`, `current_branch`

## Dependencies

- stdlib (`subprocess`, `pathlib`, `dataclasses`)
- `git` and `gh` on PATH for `Repo.open()` (optional for `Repo.memory()`)
- `tools.tool` — `@toolset` on manifest class `Git`
- consumed by `workspace` (shim), `workflow` (orchestration)

## Mechanism

Domain objects hold behavior; `_cli.py` runs `git -C` / `gh` subprocess calls. `Repo.memory()`
stores branches, commits, tickets, project status, and notes in plain dicts/lists — same
public API as CLI-backed `Repo.open()`. Commit trailers are parsed into `Commit.data`;
workflow helpers format `GitHub-Issue:` and `Workflow-State:` lines. Project status maps
to GitHub Projects via `gh project item-add` / `item-edit` when not in memory mode.

## Rationale

Git and GitHub were split across `workspace/git_repo.py` and `workflow/gh_client.py` —
duplicate subprocess wrappers and no shared ticket/project model. Consolidating under
`utilities/git` gives one OO graph aligned with the backbone (G-04, G-36, G-37): git
records decisions at commit time; GitHub holds live collaboration state. Small focused
types replace a fat `GhClient`/`GitRepo` service.
