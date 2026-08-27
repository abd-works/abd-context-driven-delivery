# workflow — module context

## Purpose

**Workflow** action kit (`context_tools/actions/workflow/`): thin commands that connect
**backlog → start → finish** to GitHub Issues, issue-body handoff, and **WorkSession** /
session-branch lifecycle. Implements the ticket/workflow slice of the git backbone
(see `.context/research/git-knowledge-and-workflow-backbone.md` §8, G-36, G-37).

## Commands (target syntax)

| Command | Action | Role |
| --- | --- | --- |
| `/backlog` | `backlog` `@prompt(name="backlog")` | Compose forward-requirements → GitHub issue body → Project **Backlog** (GitHub Status **Todo** when the board uses that option) |
| `/start-ticket` | `start` `@prompt(name="start-ticket")` | Read issue → Project **In Progress** → open WorkSession + session branch |
| `/finish-ticket` | `finish` `@prompt(name="finish-ticket")` | Merge session branch → main → Project **Done** → close issue → close session |

There is no `/workflow` command — the kit name is not a slash file.

## Seam

`Workflow` toolset — `workflow.workflow:Workflow`

## Dependencies

- `git` (`utilities/git`) — `Repo`, `Branch`, `Commit`, `Project`, `Ticket`
- `workspace` — `WorkSession`, session branch, turns
- `handoff` — forward-requirements content patterns
- `gh` CLI — via `Repo` when not using `Repo.memory()`

## Public API

- `backlog(focus, context)` — `@agent_tool`: collect+render Handoff in-process (no session files), then `capture_backlog` (issue + Project Backlog)
- `start(ticket, instructions, workspace)` — In Progress + WorkSession + session branch
- `finish(outcome, workspace)` — merge to main, Project Done, close issue, close session

## v1 decisions (locked grill)

| Question | Decision |
| --- | --- |
| Backlog without WorkSession? | **Yes** — GitHub issue + Project Backlog only; no repo artifact changes |
| Ticket id | **GitHub issue `#` only** — no CDD-N / `tickets.jsonl` v1 |
| Project scope | **One Project per repo** (owner + project number in workflow config) |
| Finish merge | **Direct to main** (v1); PR gate deferred |
| Handoff destination (backlog) | **GitHub issue body** (canonical); `/start-ticket` refers or copies into session folder |

## Status

BDD sketch (usage-story shape) + `workflow.py`: `backlog` / `start` / `finish` tools (session `workflow-package`). `backlog` builds the issue body in-process; GitHub Status maps workflow **Backlog** → **Todo** when needed.
