# Grill me — abd-story-mapping

**Mechanics:** [`common/reference/grill-me-with-practice-skill.md`](../../../../common/reference/grill-me-with-practice-skill.md) — one question at a time; generate-to-learn when enough is shared.

Ask until the map at this fidelity level is unambiguous:

- Who are the real actors — is "the user" one person or several with different goals? Any system actors nobody mentioned yet?
- For each actor: real human role in **this** iteration, or automation that does not exist yet? If everything is manual now, should automated actors be on the map?
- Are these outcomes stakeholders care about, or build tasks dressed as stories?
- For vague story names ("manage", "handle", "provision"): what is the one observable behavior?
- Which specific tool or mechanism performs each generic behavior ("extract", "notify")?
- What triggers behaviors — scheduled jobs, background processes, external systems?
- Read sub-epics in order: can each story start before the next? What prerequisites are missing?
- If there is a delivery epic: do its stories follow the real CDD fidelity flow, or generic "generate → review → submit"?
- Where does this product end and another system begin?
- Do any two sub-epics describe the same behaviour under different names?
- What depth does everyone expect — outline for conversation, or full breakdown for planning?
