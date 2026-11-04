**Sources / context:** `space/git/git.py`, `space/git/git_spec.py`, `.context/research/git-knowledge-and-workflow-backbone.md` §8, G-04, G-36, G-37; `workspace/.context/module-context.md`; `workflow/.context/module-context.md`

## Language

*Repo* is the root of a local git clone. It owns branches, the current HEAD, optional
GitHub project linkage, and tickets (issues). *Branch* names a line of development;
*Commit* records a snapshot with an open metadata map (trailers, notes payload).
*Project* is the repository's GitHub Project board; *ProjectTicket* is a GitHub issue with
a kanban *ProjectTicketState* (Backlog / In Progress / Done). *ResearchTag* is research/flow
metadata on that *ProjectTicket*, stored git-primary (notes and trailers), not a second issue identity.

### repo

- Holds clone root path, default branch name, and optional attached *Project*
- Opens via filesystem (`Repo.open`) or in-memory for tests (`Repo.memory`)
- Creates and resolves *ProjectTicket* references; formats workflow commit trailers
- **Invariant:** git notes and commit trailers are the canonical association surface — not parallel session yaml indexes

### branch

- Named ref on a *Repo* — checkout switches HEAD, commit records work, merge integrates another branch
- **Invariant:** refuses checkout/merge when the working tree is dirty (`DirtyBranchSwitchError`)

### commit

- Identified by `sha` and `message`; `data` holds parsed trailer key/value pairs
- **Invariant:** `Commit.from_message` derives `data` from message body lines after the subject

### project

- GitHub Project scoped to owner + number; defines *ProjectTicketState* columns
- Links onto the current repository (`gh project link`) so the board shows on the repo Projects tab
- Adds tickets to the board and moves them between states

### project ticket

- GitHub issue identity (`number`, `title`, `body`, `url`) plus optional *ProjectTicketState*
- Open `data` map for extension (e.g. closed flag in memory mode)
- Holds *ResearchTag*s and notes; flow is *ProjectTicketState* plus git trailers/notes — not extra kanban columns
- **Invariant:** ticket identity remains GitHub issue `#`; tags/notes/flow do not mint a parallel store

### researchtag

- Research or session-flow label associated with a *ProjectTicket* on the existing git API
- **Invariant:** canonical association is git notes and commit trailers, not session yaml indexes

### ticket_state

- Named kanban column — default set: Backlog, In Progress, Done
- **Invariant:** project state names must match a defined *ProjectTicketState* on the attached *Project*
- GitHub Status field may use `Todo` for workflow `Backlog`; exact option name wins, then the synonym map

## Modules

Build order: `git` → (`workspace` shim | `workflow`)

---

# space/git
- **Purpose:** OO git + GitHub domain for CDD workspace sessions and workflow commands. Callers manage research tags, notes, and ticket/session flow on the existing Repo / Project / ProjectTicket / ProjectTicketState graph — git-primary notes and trailers, not a second ticket store.
- **Seam (terms):** Repo, Branch, Commit, Project, ProjectTicket, ProjectTicketState, Git, ResearchTag
- **Dependencies (one-way):** `tools.tool`; consumed by `workspace`, `workflow`

## Repo

Repo(root, memory=False)
------
<< composition >> project: Project | None
default_branch: str
root: Path
----
find_root(start): Path | None
open(start): Repo
memory(root): Repo
git(root, *args): str
gh(*args): str
branch: Branch
branch_named(name): Branch
checkout_or_create(name): str
commit(paths, message): str
push(): None
merge_branch(source, into, message): str
list_worktrees(): list
worktree_for(branch): Worktree | None
add_worktree(path, branch): Path
remove_worktree(path): None
fetch(): None
pull(): None
fetch_pull(): None
merge_from(other, message): str
push_to(branch): None
has_stash(): bool
is_linked_worktree(): bool
primary_root(): Path
ticket(ref): ProjectTicket | None
create_ticket(title, body): ProjectTicket
attach_project(owner, number): Project
workflow_commit_message(subject, issue_number, workflow_state, reviewed_by): str
note(sha, payload): None
read_notes(sha): dict
find_mistakes(entry_ids): list

## Branch

Branch(repo, name)
------
name: str
----
checkout(): Branch
commit(paths, message): Commit
merge(other, message): Commit
head: Commit

## Commit

Commit(sha, message, data)
------
sha: str
message: str
data: dict
----
format(subject, trailers): str
from_message(sha, message): Commit
trailers(message): dict
note_text(fields): str
note_payload(text): dict

## Project

Project(repo, owner, number)
------
owner: str
number: int
states: list[ProjectTicketState]
----
state_named(name): ProjectTicketState
link_repository(): None

## ProjectTicket

ProjectTicket(number, title, body, url, state, data)
------
number: int
title: str
body: str
url: str
state: ProjectTicketState | None
data: dict
----
closed: bool
parse_number(ref): int
github_ref(owner, repo, number): str
set_status(state_name): ProjectTicket
write_type(name): ProjectTicket
close(): None

## ProjectTicketState

ProjectTicketState(name)
------
name: str
----
backlog(): ProjectTicketState
in_progress(): ProjectTicketState
done(): ProjectTicketState
