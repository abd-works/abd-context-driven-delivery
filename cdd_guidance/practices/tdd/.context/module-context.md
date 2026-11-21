# cdd_guidance/practices/tdd
*TDD* is a practice supplement, not a practice of its own: it adds test-driven rules to the implementation fidelity of four practices (Clean Engineering code, Stories acceptance tests, BDD development, DDD tactics), as `tdd.md`'s front matter lists. Every behaviour is proven working for real before it is trusted, then kept proven by a test at the fastest tier that can prove it. *Tdd* (`tdd.py`) is a *PracticeSupplement*; `tiers.py` says which tier a test file belongs in (unit, heavy, end-to-end) and what real resources it reaches; *TddOverlay* (`graph_overlay.py`) records those facts on the Stories and BDD nodes the graph already holds, so the supplement's rules read them. `practices/stories` and `practices/bdd` hold the rules it adds to each of those practices.

- **Purpose:** Hold the test-tier and test-first rules every implementation fidelity follows, once, beside the practices they supplement.
- **Seam (terms):** Tdd, TddOverlay, `tier_of`, `is_code_file`, `real_resources_in`
- **Dependencies (one-way):** `harness/guidance` (*PracticeSupplement*), `harness/graph` (*Graph*, *Node*, *GraphOverlay*), `harness/agent_tools`, `cdd_guidance/practices/stories` and `cdd_guidance/practices/bdd` (the practices whose nodes it decorates)

## Constraint

A test lives in the fastest tier that can prove its behaviour: unit by default, heavy only for real resources, end-to-end only for a real browser or a real agent. The tiers and their budgets are this supplement's rules; `scripts/test.ps1` runs them.
