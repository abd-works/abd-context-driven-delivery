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

## Tick 1 — v1 decisions locked

1. **Backlog** — no WorkSession; `.context/sessions/backlog/{slug}/`
2. **Ticket** — CDD-N + GitHub-Issue trailer when remote
3. **Finish** — direct merge to main
4. **Handoff** — `handoff.write_handoff` on backlog destination
