## Language

*Tools* are utilities beside the lifecycle kits — workspace, git, echo, handoff, diagnose — not practices and not `/generate`.

Build order: `tools/workspace` → `tools/git` → `tools/record_decisions` → `tools/echo` → `tools/handoff` → `tools/workflow` → `tools/plan` → `tools/diagnose` → `tools/context_setup` → `tools/catalog_generator`

---

# tools
- **Purpose:** Hold utilities the kits and practices compose — session, git, fence, handoff — without turning them into lifecycle slash kits.
- **Seam (terms):** *(children own the terms)*
- **Dependencies (one-way):** `harness/agent_tools`

## Constraint

Do not put `/generate` here. Scan lives under `actions/`. Echo and handoff are utilities, not GuidanceAction kits.

---

# tools/workspace
- **Purpose:** Open a work session so turns, branches, and decision records hang off one folder.
- **Seam (terms):** Workspace, WorkSession, Turn
- **Dependencies (one-way):** `tools/git`

---

# tools/git
- **Purpose:** Talk to a local clone and GitHub as *Repo*, *Branch*, *Commit*, *Project*, *Ticket* — not a subprocess helper.
- **Seam (terms):** Repo, Branch, Commit, Project, Ticket, TicketState
- **Dependencies (one-way):** *(none)*

## Constraint

Do not deploy `/git`. Slash commands for issues live on *Workflow*. Callers use domain types.

---

# tools/record_decisions
- **Purpose:** Offer and write Context Decision Records when a choice is hard to reverse, surprising, and a real trade-off.
- **Seam (terms):** RecordDecisions
- **Dependencies (one-way):** `harness/agent_tools`

## Constraint

Do not batch or invent CDRs. Number them sequentially under `{root}/.context/cdr/`.

---

# tools/echo
- **Purpose:** Wrap instructions in a DO-NOT-FOLLOW fence so a human can read them without the agent executing them.
- **Seam (terms):** Echo, fence
- **Dependencies (one-way):** `harness/agent_tools`

---

# tools/handoff
- **Purpose:** Compact the current session so the next agent can resume without the full chat.
- **Seam (terms):** Handoff
- **Dependencies (one-way):** `tools/workspace`

---

# tools/workflow
- **Purpose:** Move GitHub issues across Project columns (`/backlog`, `/start-ticket`, `/finish-ticket`).
- **Seam (terms):** Workflow
- **Dependencies (one-way):** `tools/git`, `tools/workspace`, `tools/handoff`

---

# tools/plan
- **Purpose:** Run a named *Workflow* (including small-work) as a plan over themed tickets.
- **Seam (terms):** Plan, PlanCommands, SmallWorkRunner
- **Dependencies (one-way):** `tools/workflow`, `tools/workspace`, `tools/git`

---

# tools/diagnose
- **Purpose:** Run a sequenced bug-hunting loop as a sub-agent so hosts do not inline the six phases.
- **Seam (terms):** Diagnose
- **Dependencies (one-way):** `harness/agent_tools`

---

# tools/context_setup
- **Purpose:** Convert a folder of documents to markdown, partition through selected practices, and embed a FAISS index you can ask.
- **Seam (terms):** ContextSetup, ContextIndex
- **Dependencies (one-way):** `actions/partition`, `practices/clean_engineering`, `practices/ddd`, `practices/stories`, `practices/ux`

---

# tools/catalog_generator
- **Purpose:** Render the CDD catalog HTML from live toolsets — no scraped parallel schema.
- **Seam (terms):** Catalog
- **Dependencies (one-way):** `harness/agent_tools`, `harness/guidance`
