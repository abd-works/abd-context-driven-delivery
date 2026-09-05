# Input traps — abd-story-acceptance-criteria

Assumptions, ambiguities, and missing context that commonly produce bad acceptance criteria. Check each trap against available input before generating — flag gaps honestly; do not invent criteria to fill them.

- **Hidden actors** — who actually triggers this — is "the user" hiding three different actors with different journeys and different expectations of "done"?
- **One story or a bundle** — does this story describe one observable interaction, or is it actually three behaviors wearing a trenchcoat? If you can't state done in 4-9 criteria, it might be a bundle.
- **Unstated negative paths** — what should explicitly NOT happen? Every happy path has a shadow — rejection, timeout, conflict, unauthorized. Have those been surfaced or assumed away?
- **Domain vocabulary drift** — are the terms in these criteria the same terms the domain experts use, or has the team invented its own words? Synonyms become bugs.
- **Observable vs. internal** — can a stakeholder verify each criterion by looking at the system's behavior, or do some criteria describe internal state that nobody outside the code can see?
