---
description: "Plain English for guidance, rules, and rationale in context-tool guidance documents"
alwaysApply: true
---

Write guidance, goals, and rule rationales in normal English — the way a clear technical lead would explain something to a colleague.

**Name the actual thing.** This skill, this practice, the Generate action, the story map, the templates folder, the bounded-context map. Never "kit", "the piece", "the bit", or "the thing that handles X" — shorthand that stands in for a name means you have not yet said what you mean.

**Name the established term and explain it in plain English — both, not one instead of the other.** The term gives the reader something to recognise and look up; the plain sentence tells them what it means. Use them together and each does work the other cannot.

Never invent a technical-sounding phrase in between: "consistency cluster" is not what practitioners say and it is not English, so a reader can neither look it up nor picture it. Avoiding the real term entirely is the other failure — it forces circumlocution that is harder to read than the term. "Take the smallest set of concepts that can hold that rule true in one step" is worse than naming the **aggregate** and its **root** and saying plainly that the root is the only way in.

**Write positive statements of what to do, each carrying its rationale.** Say the action, then why it earns its place — what it buys the reader, or what it prevents. A rule without a reason gets followed mechanically in the cases it fits and abandoned in the ones it does not, because nobody can tell which is which.

**State what is true and let it stand alone.** Guidance describes the situation the reader is in, not the wrong turns taken getting there. Write a prohibition only where a reader would plausibly reach for the wrong thing unprompted — then frame it around their situation.

**Do not use AI garbage phrasing**, especially:
- Spreadsheet or accounting metaphors: "the price of a line", "the cost of a row", "no row", "deleted row", "requirement row"
- Vague inflation: "leverage", "land", "surface area", "hung off", "ripples through", "durable index", "late surprise work"
- Deferred hand-waving: "settles it later", "gets figured out downstream", "handled in implementation" — say what actually happens
- Pseudo-precision that says nothing: "horizon someone commits to", "prove-read" where "read" is enough
- Invented pseudo-technical terms: "consistency cluster" for an aggregate, "language boundary" for a bounded context, "seam-term" where "public name" is enough

**Say what to do and why**, in plain terms:
- Bad: "A node moves here for the price of a line, and later for the price of every scenario hung off it."
- Good: "It is much easier to change the map while stories are still titles than after scenarios, screens, and tests exist."

- Bad: "unconfigured = no row + existing fallback"
- Good: "Only write stories for behaviours the source describes or the user asks for."

- Bad: "whoever writes the code settles it later"
- Good: "the errors stay uncaught until users actually test it"

When adding a rationale to a rule, append one short clause — what goes wrong if you ignore it. Do not double the length of the section.
