# Rule: Story map stays within user-requested scope

**Scanner:** Manual review

The epic and story tree in **`story-map.md`** / **`story-map.txt`** reflects **only** the product scope the user (or product owner) has asked for: alternate journeys, build methods, or channels do not appear as parallel first-class flows unless the user asked for them or confirmed they are in scope. Failure is an extra path, persona flow, or "optional" track presented as part of the map when the user explicitly narrowed scope or chose a single path.

## DO

- When the user states **one** path (e.g. "manual onboarding only", "custom build only"), map **that** path and treat other approaches as out of scope until the user expands scope.

  **Example (pass):** User: "Manual onboarding only for now." The map has sub-epics and stories for staff-led onboarding only; there is no sibling sub-epic "Self-service onboarding" unless the user later adds it.

- When a real choice exists and the user has **not** decided, capture **one** gap naming the decision and options—not two full parallel backlogs.

  **Example (pass):** Gap: "Onboarding: manual vs self-service not decided—no stories for self-service until PO confirms."

## DO NOT

- Add a **second** major flow (e.g. self-service onboarding, quick-build archetype, alternate sales channel) as if it were in-scope when the user already chose or restricted to the other path.

  **Example (fail):** User said "custom build only, no quick start." The map still includes `(E) Quick-Start From Archetype` with stories—that is unrequested scope.

- Present **unrequested** alternatives as normal epics "for completeness" without asking.

  **Example (fail):** User asked for a B2B wholesale portal map; the map adds a full B2C retail epic "because many platforms have both" without product confirmation.

**Source:** Engagement corrections log — scope fabrication and parallel paths without user ask.
