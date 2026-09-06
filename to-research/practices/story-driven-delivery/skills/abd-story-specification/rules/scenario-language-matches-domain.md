# Rule: Scenario language matches the domain

**Given / When / Then** lines should read like the team’s domain model: entities, value objects, and collaborations. Avoid UI implementation detail unless the story is explicitly about a literal label or widget. Pick the concept that **owns** the data in context (e.g. **Epic** in **StoryMap**, not a diagram cell type, unless the step is about rendering that cell).

## DO

- Name entities the way the domain does (“**WirePayment** is created with status pending”).
- Use **When** for domain operations (“**User** selects **Recipient**”), not low-level driver events.
- Use **Then** for domain-visible effects and messages users or integrators care about.

``Given an Enterprise with active Recipients
And a User with wire payment permissions
When the User selects a Recipient
Then the WirePayment is created with status pending
``
## DON'T

- Anchor **Given** in pages, modals, or control names (“recipient list page is loaded”) when state can be said in domain terms.
- Use generic placeholders (“items”, “thing”) when real types exist.
- Misplace concepts: if something lives in **StoryMap**, say **{Epic}** / **{SubEpic}** there; reserve diagram-specific types for steps about the diagram.

``# WRONG — UI-first
When the user clicks the dropdown

# STRONGER — domain
When the User selects a Recipient
``