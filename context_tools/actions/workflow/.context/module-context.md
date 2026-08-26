# workflow — module context

## Purpose

**Workflow** action kit (`context_tools/actions/workflow/`): thin commands that connect
**backlog → start → finish** to GitHub Issues, handoff docs, and **WorkSession** /
session-branch lifecycle. Implements the ticket/workflow slice of the git backbone
(see `.context/research/git-knowledge-and-workflow-backbone.md` §8, G-36, G-37).

## Commands (target syntax)

| Command | Action | Role |
| --- | --- | --- |
| `/backlog` | `backlog` | Capture idea context → handoff doc → GitHub issue |
| `/start` | `start` | Resolve ticket → open WorkSession + session branch |
| `/finish` | `finish` | Finish turn → merge session branch → checkout main → close session |

## Seam

`Workflow` toolset — `workflow.workflow:Workflow`

## Dependencies

- `workspace` — `WorkSession`, `GitRepo`, turn commit + trailers
- `handoff` — handoff doc for backlog forward-requirements
- `gh` CLI — issue create/view; merge when applicable
- `utilities/trace_graph` *(future)* — workflow-index regen

## Public API

- `backlog(focus, context)` — handoff + GitHub issue + ticket record + git trailers
- `start(ticket, instructions, workspace)` — find ticket → `open_work_session` + branch
- `finish(outcome, workspace)` — merge session branch → main, close session

## v1 decisions (locked grill)

| Question | Decision |
| --- | --- |
| Backlog without WorkSession? | **Yes** — writes to `.context/sessions/backlog/{slug}/` |
| Ticket id | **CDD-N** in `.context/workflow/tickets.jsonl` + `GitHub-Issue:` when remote |
| Finish merge | **Direct to main** (v1); PR gate deferred |
| Handoff destination (backlog) | `.context/sessions/backlog/{focus-slug}/` via `handoff.write_handoff` |

## Status

BDD sketch + `workflow.py` agent instructions (session `workflow-package`). Specs and deploy skill next.
