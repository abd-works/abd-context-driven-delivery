---
fidelity: [exploration]
artifact: [story-scenarios]
---

# Generate — Story Scenarios (main flow)

Fill `templates/md/scenario-main-flow.md` to produce one main-flow walk-through per story. Follow every file in `rules/` filtered to this fidelity.

## Scenario format — Scenario Outline is the default

All scenarios at exploration fidelity **must** be `Scenario Outline` with `{variable}` placeholders in every step. Concrete example values (specific IDs, amounts, names, statuses) must **only** appear in the `### Examples` table — never inline in step text.

- **Wrong** (inline values in steps): `*Given* the Treasurer *Alice* selects Source Account *CHK-001*`
- **Right** (placeholder in steps): `*Given* the **Treasurer** {actor} selects **Source Account** {source_account}`

At exploration fidelity the Examples table has **one representative row** (main flow only). Negative paths and edge cases are added at specification fidelity.

Only use the `scenario-inline.md` template (concrete values in step text) when the prompt explicitly requests inline format.

## Input traps

Assumptions, ambiguities, and missing context that commonly produce bad walk-throughs. Check each trap against available input before generating — flag gaps honestly; do not invent criteria to fill them.

- **Hidden actors** — who actually triggers this — is "the user" hiding three different actors with different journeys and different expectations of "done"?
- **One story or a bundle** — does this story describe one observable interaction, or is it actually three behaviors wearing a trenchcoat? If you can't state done in 4-9 criteria, it might be a bundle.
- **Unstated negative paths** — what should explicitly NOT happen? Every happy path has a shadow — rejection, timeout, conflict, unauthorized. Have those been surfaced or assumed away?
- **Domain vocabulary drift** — are the terms in these criteria the same terms the domain experts use, or has the team invented its own words? Synonyms become bugs.
- **Observable vs. internal** — can a stakeholder verify each criterion by looking at the system's behavior, or do some criteria describe internal state that nobody outside the code can see?
