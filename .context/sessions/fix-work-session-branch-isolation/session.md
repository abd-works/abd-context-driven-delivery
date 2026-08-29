# Session: fix-work-session-branch-isolation

## Start

- **date:** 2026-08-29
- **path:** C:\dev\abd-cdd-fix-work-session-branch
- **goal:** (unset)
- **fidelities:** (unset)
- **contexts:** (unset)

## Analysis

*(2026-08-29 — analysis job for FIRST isolation backlog item; ticket #41)*

Full analysis written to ticket notes:
`.context/sessions/defect-fix-job-1-creates-work-session-as-default-before-start-ticket-wrong-branch-worktree-41/issue-body.md` under ## Analysis.

Summary: partial #41 fix skipped `default` sole-session fallback but premature bind + missing post-start-ticket workspace rebind remain; must hold for CliAgent, SubAgent, and no-agent at work-session/start-ticket layer.

## Diagnosis

*(2026-08-29)* Category **BOTH**. Premature `_ensure_work_session` before start-ticket + missing post-start workspace rebind; prompt/template cannot undo attach order. Full write-up in ticket `issue-body.md` under ## Diagnosis.

## Failing tests (2026-08-29)

Category BOTH → mechanical BDD first, then agentic.

### Mechanical (cli_agent_spec.py) — confirmed red
1. `should not bind a durable folder-slug session while HEAD is still main` — fails: binds `cli-pre-start-slug-*`.
2. `should rebind workspace root to the ticket worktree for later jobs` — fails: no `rebind_to_worktree`.

### Agentic (cli_agent_session_isolation_agent_spec.py)
Requires defect-fix + module contexts to mandate session/worktree isolation + rebind for CliAgent, SubAgent, **and no-agent**. `no-agent` not yet in those docs → red until prompt/docs updated with the code fix.

## Fix (2026-08-29)

- Deferred durable CliAgent bind on main: `_pending_work_session` (`cli-agent-pending`) instead of folder-slug; `_session` stays unbound until rebind.
- Added `rebind_to_worktree(path, session=)` for post-start-ticket retarget.
- Updated defect-fix job 1 + cli_agent/workspace module-context for CliAgent, SubAgent, and no-agent isolation/rebind.
- Isolation mechanical specs green; judge PASS on fix job.
