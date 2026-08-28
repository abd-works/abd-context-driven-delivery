# BDD sketch — workflow action kit (usage story)

Design refs: `.context/research/git-knowledge-and-workflow-backbone.md` §8 (tickets,
GitHub, kanban), G-36 (ticket create/link), G-37 (PR/merge bridge).

Fidelity: behavior

**LOCKED — v1 command map:**

| User syntax | Toolset action | Project Status |
| --- | --- | --- |
| `/backlog` | `backlog` | **Backlog** |
| `/start-ticket` | `start` | **In Progress** |
| `/finish-ticket` | `finish` | **Done** + close issue |

**LOCKED — git trailers on start/finish turn commits (v1):**

- `GitHub-Issue:` — `owner/repo#num` (ticket id = GitHub issue `#` only)
- `Workflow-State:` — column name (`specification`, `engineering`, or `done`)
- `Reviewed-By:` — optional on finish merge commit

**LOCKED — handoff:** `/backlog` runs **Handoff** to capture ticket information; the
**created issue body** carries that handoff (canonical). `/start-ticket` reads via `gh issue view`
and either refers to the ticket or copies sections into the work session folder when needed.

---

a context tool
  that has an action run against it
    with a fidelity in play
    with a format in play
    with prompt context including commentary from the user
    with session artifacts in the working folder
      it should carry sketches grill progress and module context from the current work
    that is asked to backlog the current work
      it should run handoff to capture the backlog ticket information
      the created handoff
        it should hold forward-requirements from the current fidelity format and action as needed
        it should hold enough context for a fresh agent to resume the work
      it should create a github issue
      the created issue
        it should carry the handoff in the body of the issue
      the repository project
        it should list the issue with status Backlog
      it should not open a work session
      with a github issue from that backlog step
        that is asked to start that item
          the forward requirements
            it should be available from the issue body
          with issue body sufficient for the agent without local copies
            the agent context
              it should refer to that github issue
          with local session artifacts needed
            the work session folder
              it should hold copied sections from the issue body
          the repository project
            it should list the issue with status In Progress
          it should open a new work session named for that ticket
          it should set the current work session to that work session
          it should set the branch to the session branch for that work session
          it should open a turn for the action run
          that has a turn open
            that has finished its turn
              the session branch commit
                it should carry GitHub-Issue and Workflow-State trailers
              the turn envelope
                it should record additional instructions from the prompt when provided
          with an open work session from that start
            that is asked to finish that work
              it should finish its open turn for the action
              that has finished its turn
                it should merge its session branch into main
                it should check out the main branch
                the repository project
                  it should list the issue with status Done
                the github issue
                  it should be closed
                the work session
                  it should be closed with outcome when provided
                the merge commit
                  it should carry GitHub-Issue and Workflow-State done trailers
                  it should carry Reviewed-By when supplied
    that is asked to start an item
      with a github issue reference given
        with the issue not found
          it should report that the ticket was not found
          it should not open a work session
    that is asked to finish work
      with no open work session
        it should report that no work session is open

---

**LOCKED — v1 grill (2026-08-26, complete):**

| # | Decision | Status |
| --- | --- | --- |
| 1 | `/backlog` **without** WorkSession — GitHub issue + Project **Backlog** only | ✓ locked |
| 2 | Ticket id = **GitHub issue `#`** only (no CDD-N v1) | ✓ locked |
| 2b | **One Project per repo** — Status field drives Backlog / In Progress / Done | ✓ locked |
| 3 | `/start-ticket` → Project **In Progress** + WorkSession + `GitHub-Issue:` trailers | ✓ locked |
| 4 | `/finish-ticket` → **direct merge** to `main`; Project **Done** + **close issue** | ✓ locked |
| 5 | Handoff → **issue body** (canonical); `/start-ticket` **refers or copies** as needed | ✓ locked |

---

## Deferred (not v1)

- GitHub Projects column sync (read git Workflow-State; optional one-way push)
- PR open as separate step before merge (G-37 full — finish may call `gh pr merge` only when PR exists)
- `refs/cdd/tickets/*` fast index (notes + trailers first)
- Kanban HTML projection (G-34)
- Local backlog folder under `.context/sessions/backlog/`

---

## Implementation

- `workflow.workflow:Workflow` — `backlog` / `start` / `finish` tools (session `workflow-package`). `backlog` renders Handoff into the issue body in-process (no `compact_handoff` / session files). GitHub Status **Backlog** maps to **Todo** when that is the board option.
