# Grill answers — workflow-package

## Tick 0 — user intent (2026-08-26)

**Source:** chat prompt — new package under `actions/workflow`, simple v1.

**Commands:**

- `/backlog` — take context (incl. commentary in prompt); create handoff doc focused on
  what is required to move the idea forward; create GitHub ticket; attach handoff to issue.
- `/start` — find ticket; create new work session from it (branch checkout/create, etc.);
  apply additional instructions from prompt/ticket.
- `/finish` — close session; merge session branch to main; checkout main.

**Paths cited:**

- `.context/research/git-knowledge-and-workflow-backbone.md` §8, G-36, G-37
- `context_tools/actions/handoff/` — handoff doc pattern
- `context_tools/actions/workspace/` — WorkSession, session branch, turns

**Slice note:** Behavior sketch locked; `workflow.py` scaffold landed. Next: spec + agent_skills deploy entry.

## Tick 1 — `/backlog` and WorkSession (2026-08-26)

**Question:** Does `/backlog` require an open WorkSession?

**Answer (user):** **No.** Backlog is ticket-only — add to GitHub, no repo artifact changes yet. WorkSession opens on `/start` when work actually begins.

**Locked:** `/backlog` runs without WorkSession; forward-requirements in GitHub issue body + Project Backlog only.

---

## Tick 2 — ticket identity + GitHub Projects (2026-08-26)

**Research (not user assertion):**

- **Issue** = work item; durable id = **`#87`** per repo (`owner/repo#87`).
- **Project** (v2) = board; **Status** is a single-select field (often named Backlog / In Progress / Done — **names are per-project**, not global).
- Creating an issue does **not** auto-add it to a Project — need `gh project item-add` then `gh project item-edit --field Status --value "Backlog"`.
- **Issue state** (open/closed) ≠ **Project Status** — kanban column is Project Status; use `item-edit`, not only `issue close`.

**User alignment (validated):**

| Command | GitHub | Project Status (typical) |
| --- | --- | --- |
| `/backlog` | `gh issue create` + add to Project | **Backlog** |
| `/start` | read issue #87 | **In Progress** + open WorkSession + session branch |
| `/finish` | merge work (PR or direct) | **Done** (+ optional `gh issue close`) |

**Ticket id v1:** **GitHub issue # only** — drop CDD-N / `tickets.jsonl` unless offline needed later.

**Project scope v1:** **One GitHub Project per repository** (config: owner + project number in workflow settings). Per-theme/per-effort projects deferred.

**Issue ↔ session correlation (best):** commit **trailers** on `/start` turn (`GitHub-Issue:`, `Workflow-State:`), session branch `session/{slug-from-issue}`, optional `refs/notes/cdd-workflow` — **not tags**.

---

## Tick 3 — `/finish` merge + issue close (2026-08-26)

**Best approach (research + repo context):**

- **v1: direct merge** session branch → `main` — user confirmed ("for now we can merge").
- **Why:** Small team, no branch protection yet; `/finish` stays one command; matches original sketch.
- **On finish also:** set Project Status **Done** + **`gh issue close #87`** (no PR means no `Fixes #87` auto-close — close explicitly).
- **Git:** merge commit trailers `GitHub-Issue:`, `Workflow-State: done`, `Reviewed-By:` optional.
- **Evolve later:** when branch protection lands → `/finish` opens PR, CI runs, `gh pr merge`; keep direct merge as fallback when allowed.

**Locked:** direct merge v1; Project Done + close issue on finish.

---

## Tick 4 — backlog handoff location (2026-08-26)

**Answer (user):** Handoff content lives in the **GitHub issue body** (all information required to move forward).

**On `/start`:** read issue via `gh issue view` — either **refer to the ticket** (link + #) as context or **copy** relevant sections into the WorkSession folder when that helps the agent; choose per situation (refer when body is enough; copy when session needs local artifacts).

**Locked:** issue body = canonical handoff at backlog; no required local backlog folder for v1.

---
