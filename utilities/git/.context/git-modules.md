**Sources / context:** `utilities/git/git.py`, `utilities/git/git_spec.py`, `.context/research/git-knowledge-and-workflow-backbone.md` §8, G-04, G-36, G-37; `workspace/.context/module-context.md`; `workflow/.context/module-context.md`

## Language companion

*Repo* is the root of a local git clone. It owns branches, the current HEAD, optional
GitHub project linkage, and tickets (issues). *Branch* names a line of development;
*Commit* records a snapshot with an open metadata map (trailers, notes payload).
*Project* is the repository's GitHub Project board; *Ticket* is a GitHub issue with
a kanban *TicketState*.

### repo

- Holds clone root path, default branch name, and optional attached *Project*
- Opens via filesystem (`Repo.open`) or in-memory for tests (`Repo.memory`)
- Creates and resolves *Ticket* references; formats workflow commit trailers
- **Invariant:** git notes and commit trailers are the canonical association surface — not parallel session yaml indexes

### branch

- Named ref on a *Repo* — checkout switches HEAD, commit records work, merge integrates another branch
- **Invariant:** refuses checkout/merge when the working tree is dirty (`DirtyBranchSwitchError`)

### commit

- Identified by `sha` and `message`; `data` holds parsed trailer key/value pairs
- **Invariant:** `Commit.from_message` derives `data` from message body lines after the subject

### project

- GitHub Project scoped to owner + number; defines *TicketState* columns
- Links onto the current repository (`gh project link`) so the board shows on the repo Projects tab
- Adds tickets to the board and moves them between states

### ticket

- GitHub issue identity (`number`, `title`, `body`, `url`) plus optional *TicketState*
- Open `data` map for extension (e.g. closed flag in memory mode)

### ticket_state

- Named kanban column — default set: Backlog, In Progress, Done
- **Invariant:** project state names must match a defined *TicketState* on the attached *Project*

## Modules

Build order: `git` → (`workspace` shim | `workflow`)

---

# utilities/git
- **Purpose:** OO git + GitHub domain for CDD workspace sessions and workflow commands
- **Seam (terms):** Repo, Branch, Commit, Project, Ticket, TicketState, Git
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
ticket(ref): Ticket | None
create_ticket(title, body): Ticket
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
states: list[TicketState]
----
state_named(name): TicketState
link_repository(): None

## Ticket

Ticket(number, title, body, url, state, data)
------
number: int
title: str
body: str
url: str
state: TicketState | None
data: dict
----
closed: bool
parse_number(ref): int
github_ref(owner, repo, number): str
set_status(state_name): Ticket
close(): None

## TicketState

TicketState(name)
------
name: str
----
backlog(): TicketState
in_progress(): TicketState
done(): TicketState
