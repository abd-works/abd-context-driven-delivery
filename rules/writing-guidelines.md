---
description: "Plain English for guidance, rules, and rationale in context-tool kits"
alwaysApply: true
---

Write guidance, goals, and rule rationales in normal English — the way a clear technical lead would explain something to a colleague.

**Do not use AI garbage phrasing**, especially:
- Spreadsheet or accounting metaphors: "the price of a line", "the cost of a row", "no row", "deleted row", "requirement row"
- Vague inflation: "leverage", "land", "surface area", "hung off", "ripples through", "durable index", "late surprise work"
- Deferred hand-waving: "settles it later", "gets figured out downstream", "handled in implementation" — say what actually happens
- Pseudo-precision that says nothing: "horizon someone commits to", "prove-read" where "read" is enough

**Say what to do and why**, in plain terms:
- Bad: "A node moves here for the price of a line, and later for the price of every scenario hung off it."
- Good: "It is much easier to change the map while stories are still titles than after scenarios, screens, and tests exist."

- Bad: "unconfigured = no row + existing fallback"
- Good: "Only write stories for behaviours the source describes or the user asks for."

- Bad: "whoever writes the code settles it later"
- Good: "the errors stay uncaught until users actually test it"

When adding a rationale to a rule, append one short clause — what goes wrong if you ignore it. Do not double the length of the section.
