# workflow — module context

## Purpose

**Workflow** action kit (`context_tools/actions/workflow/`): thin commands that connect
**backlog → start → finish** to GitHub Issues, issue-body handoff, and **WorkSession** /
session-branch lifecycle. Implements the ticket/workflow slice of the git backbone
(see `.context/research/git-knowledge-and-workflow-backbone.md` §8, G-36, G-37).

## Commands (target syntax)

| Command | Action | Role |
| --- | --- | --- |
| `/backlog` | `backlog` | Compose forward-requirements → GitHub issue body → Project **Backlog** |
| `/start` | `start` | Read issue → Project **In Progress** → open WorkSession + session branch |
| `/finish` | `finish` | Merge session branch → main → Project **Done** → close issue → close session |

## Seam

`Workflow` toolset — `workflow.workflow:Workflow`

## Dependencies

- `workspace` — `WorkSession`, `GitRepo`, turn commit + trailers
- `handoff` — forward-requirements **content patterns** (issue body at backlog; not local write v1)
- `gh` CLI — issue create/view/close; project item-add + Status field edit; merge when applicable
- `utilities/trace_graph` *(future)* — workflow-index regen

## Public API

- `backlog(focus, context)` — issue body handoff + GitHub issue + Project Backlog (no WorkSession)
- `start(ticket, instructions, workspace)` — `gh issue view` → `open_work_session` + branch + trailers
- `finish(outcome, workspace)` — direct merge to main, Project Done, close issue, close session

## v1 decisions (locked grill)

| Question | Decision |
| --- | --- |
| Backlog without WorkSession? | **Yes** — GitHub issue + Project Backlog only; no repo artifact changes |
| Ticket id | **GitHub issue `#` only** — no CDD-N / `tickets.jsonl` v1 |
| Project scope | **One Project per repo** (owner + project number in workflow config) |
| Finish merge | **Direct to main** (v1); PR gate deferred |
| Handoff destination (backlog) | **GitHub issue body** (canonical); `/start` refers or copies into session folder |

## Status

BDD sketch (usage-story shape) + `workflow.py` agent instructions (session `workflow-package`). Specs and deploy skill next.
