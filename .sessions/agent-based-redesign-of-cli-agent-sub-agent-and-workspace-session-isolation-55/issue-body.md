# Handoff — abd-context-driven-delivery (2026-08-30)

## Workspace layout

New implementation for this ticket lives under **`agents/`** at the repo root (in the ticket worktree).

| Path | Role |
|------|------|
| **`agents/`** | **New code** — `AgentSession`, `Agent`, `CliAgent`, `SubAgent`, task queue, ticket workflow, etc. |
| **`agents/.context/`** | **Canonical `.context`** for #55 — redesign sketches, BDD strategy, design notes |

Do not treat repo-root `.context/agent-session-redesign-*` as canonical; use **`agents/.context/`**.

### Context artifacts (`agents/.context/`)

| File | Purpose |
|------|---------|
| `agent-session-redesign-sketch.md` | Clean engineering modules sketch |
| `agent-session-redesign-stories-sketch.md` | Story map + nested BDD behavior trees |
| `bdd-testing-strategy.md` | Vanilla vs agent BDD strategy (lessons from #44) |
| `README.md` | Index |

## Resume

- **Stage:** stories sketch complete; BDD strategy captured
- **Last work:** CE modules + stories sketches in `agents/.context/`; vanilla vs agent BDD strategy documented
- **Next action:** Generate vanilla BDD signatures increment 1 (session + queue)
- **Next focus:** Implement under `agents/` with /bdd first, then thin agent BDD

## Turn Context

- **Noticed in:** Parent chat [session-on-main / redesign](9e9a8eee-ac53-4b34-8ea4-414852c651da), **second user turn** (after the session-on-main vs worktree Q&A). User asked for an agent-based refactor of `cli_agent` / `sub_agent` / `workspace` (and related `workflow`), citing trouble getting the CLI to work from giving the agent too much responsibility without a proper design. First user turn in that chat only asked about staying on `main` vs sibling worktree (related prior context, not the redesign itself).
- **Assigned capture transcript:** `4223fcc6-c4dd-43a8-86fa-7661e9fe52ae` is the Done-state regression scorecard run and does **not** contain this redesign notice.
- **Branch:** `main` (primary); ticket work in sibling worktree `abd-cdd-55`
- **Current commit (Turn / handoff window):** `45eebeac` (`finish` — scorecard artifacts). **Not the cause** of the redesign need.
- **Cause:** Earlier / cumulative design debt in CLI agent + session isolation (predates `45eebeac`). Sibling-worktree-for-`session/{name}` behavior and stay-on-main-only-when-`session_branch`-is-default also predate this finish commit; redesign may revisit those boundaries.

## Artifacts to read

- **`agents/.context/`** — canonical redesign context (see Workspace layout above)
- **`agents/.context/bdd-testing-strategy.md`** — vanilla BDD before agent BDD; break the #44 whack-a-mole cycle
- `.context/sessions/agent-based-redesign-of-cli-agent-sub-agent-and-workspace-session-isolation-55/`
- `.context/grill-answers.md` — prior redesign grill

## Request

**Focus:** Agent-based redesign of CLI agent, sub-agent, and workspace session isolation

**Scope:** new code under **`agents/`**; legacy reference: `utilities/cli_agent`, `utilities/sub_agent`, `utilities/workspace`, `utilities/workflow`

Problem: CLI agent is hard to get working — too much responsibility was given to the agent without a proper design. Want a new session that redesigns and rebuilds with CDD discipline.

Planned session approach:
1. One sketch spanning the hierarchy, then generate:
   - story_map (stories) with agent_bdd under each story
   - under each agent_bdd: bdd.behavior (BDDs that probe the code needed for agent BDD)
   - hierarchy: story map -> story -> agent BDD -> BDD
   - clean_engineering.modules then clean_engineering.model
   - all of the above in one sketch cadence
2. Thin-slice functionality in small increments
3. Implement using /bdd first, then /agent_bdd

Related prior context: session create currently forces sibling worktree for session/{name}; staying on main is only when session_branch is default — no open() flag. Redesign may revisit that and broader agent/session boundaries.
