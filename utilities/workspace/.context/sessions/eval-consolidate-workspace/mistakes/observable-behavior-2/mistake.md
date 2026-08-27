# observable-behavior-2

- **entry_id:** 89c985b0
- **artifact:** context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md
- **rule:** observable-behavior
- **wrong:** Repeatedly sketched Workspace/API operations instead of stakeholder-visible behavior under real usage events. Treated openWorkSession, lookupPath, load/save, "resolve its path", "load empty path override list", context-index persistence, and "that is opening for the run" as Bdd subjects/observables — tautologies and implementation steps, not outcomes a user can verify. Missed that pathOverrides matter when a turn reads or writes module artifacts (generate/validate), under that has a turn open — not when semantically "resolving" on open. Used invented or informal terms (bout, context-index as domain) and detached workspace from action-run/turn usage story.

- **status:** fixed
