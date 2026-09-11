# Working rules for Kilo in this repo

- Run the kit CLI (`.\tools.ps1 run -`) as-is: pipe the block the skill hands you, follow `response.instructions`, and do not read kit internals to "verify" requests. Only inspect kit code when something actually goes wrong.
- If a kit CLI run fails, fall back to raw `gh` and finish the task in the same turn.
- When the user names a GitHub target outside the kit flow, default to raw `gh` — one command, done.
- Ticket/board ops (move a column, attach a sub-issue, check one parent link): use raw `gh`, not `python -c` with `Workflow()`. Each Python bootstrap reloads the whole project board through several `gh` subprocesses and routinely takes 30–90s. Prefer `gh issue edit --add-sub-issue`, `gh project item-edit` (Status field), and `gh api` for a single issue. Call `review_ticket_statuses` or `align_child_tickets_to_parent` only when the user asked for alignment or the destination column is unknown.
- Execute on the first pass. Do not scan options, re-derive requests, or preview alternatives. Ask only when an action is destructive or genuinely ambiguous; otherwise continue through errors without stopping.
- Wrong-project guard: ticket work for PML targets workspace `C:\dev\paradise-mobile\pml-domainmodel` (org Paradise-Mobile, project pml-domain-work #4), not abd-works.