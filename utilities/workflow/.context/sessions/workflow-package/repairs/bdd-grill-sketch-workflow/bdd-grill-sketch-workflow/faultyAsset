# BDD sketch — workflow action kit

Design refs: `.context/research/git-knowledge-and-workflow-backbone.md` §8 (tickets,
GitHub, kanban), G-36 (ticket create/link), G-37 (PR/merge bridge).

Fidelity: behavior

**SCOPE (v1 — simple):** three slash commands — `/backlog`, `/start`, `/finish`.
GitHub Issues for team tickets; git turn commits for durable association.

**LOCKED — command map:**

| User syntax | Toolset action | Workflow-State transition |
| --- | --- | --- |
| `/backlog` | `backlog` | → `backlog` (issue created) |
| `/start` | `start` | → `specification` or `engineering` (session open) |
| `/finish` | `finish` | → `done` (merged + session closed) |

**LOCKED — git trailers on turn commits (backbone §7):**

- `Ticket:` — session-scoped id (e.g. `CDD-42`)
- `GitHub-Issue:` — `owner/repo#num`
- `Workflow-State:` — column name
- `Handoff:` — path to handoff doc when backlog ran

---

a context tool
  with a workflow kit
    that is invoked with backlog
      with prompt context including commentary from the user
        it should collect the working context for the idea
        it should compose a handoff document focused on what is required to move the idea forward
        it should persist the handoff under the session docs layout
        it should create a github issue for the idea via gh
        it should attach or post the handoff content to that github issue
        it should assign a ticket identity for the idea
        it should open a turn for the backlog action
        it should finish its turn with ticket and github issue trailers on the session branch commit
          it should record Workflow-State backlog on that commit
      with no github remote configured
        it should still persist the handoff document
        it should assign a local ticket identity only
        it should not require a github issue trailer
    that is invoked with start
      with a ticket id or github issue number
        it should find the ticket and its linked github issue when present
        it should read handoff and issue body for forward requirements and additional instructions
        it should open a new work session named for that ticket
        it should set that work session as the current work session
        with a clean working tree not on the session branch
          with an existing session branch for that ticket
            it should check out that session branch
          with no session branch yet
            it should create the session branch for that work session
        with a dirty working tree not on the session branch
          it should refuse to switch branch
        it should open a turn for the start action
        it should finish its turn with ticket and workflow state trailers on the session branch commit
          it should record the additional instructions from the prompt on the turn envelope
      with a ticket that cannot be found
        it should report that the ticket was not found
        it should not open a work session
    that is invoked with finish
      with an open work session on its session branch
        with a clean mergeable session branch
          it should finish its open turn for the finish action
          it should merge its session branch into main
          it should check out the main branch
          it should close the work session with outcome and handoff pointer when provided
          it should finish with Workflow-State done on the merge or finish turn commit
          it should record Reviewed-By or merge metadata when supplied
        with a dirty working tree
          it should refuse to merge until the tree is clean
        with merge conflicts
          it should report the conflict and leave the session open
      with no current work session
        it should report that no work session is open
    that collaborates with handoff on backlog
      it should use handoff write patterns for the forward-requirements document
      it should name the handoff slug from the ticket or idea focus
    that collaborates with workspace on start and finish
      it should delegate session open branch and turn lifecycle to workspace
      it should not duplicate git note or eval mistake logic owned by workspace eval turns

---

**LOCKED — v1 grill (2026-08-26):**

| # | Decision |
| --- | --- |
| 1 | `/backlog` runs **without** an open WorkSession — destination `.context/sessions/backlog/{slug}/` |
| 2 | Ticket id: **CDD-N** in `.context/workflow/tickets.jsonl` plus **GitHub-Issue:** when remote |
| 3 | `/finish`: **direct merge** to `main` (PR-only deferred) |
| 4 | Backlog handoff via **`handoff.write_handoff`** under backlog session folder |

---

## Deferred (not v1)

- GitHub Projects column sync (read git Workflow-State; optional one-way push)
- PR open as separate step before merge (G-37 full — finish may call `gh pr merge` only when PR exists)
- `refs/cdd/tickets/*` fast index (notes + trailers first)
- Kanban HTML projection (G-34)

---

## Implementation

- `workflow.workflow:Workflow` — agent instructions + path/ticket tools (session `workflow-package`)
