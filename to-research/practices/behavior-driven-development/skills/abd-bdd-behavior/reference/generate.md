# Generate — abd-bdd-behavior

Follow every file in `rules/`; fill templates exactly.

## When to use

- Starting a new feature with non-trivial domain behavior
- Domain language, domain model, or acceptance criteria exist and you want test structure from them
- Stakeholders need to review what the system will do before code is written

**Not this skill when:** behavior is trivial, a valid hierarchy already exists, or you are refactoring with existing tests.

## Read context

- **`../../../reference/bdd-concepts.md`** — shared BDD theory: hierarchy, observable behavior, domain practice alignment.
- **`reference/concepts.md`** — behavior-phase specifics: scaffold format, reading domain artifacts, naming rules.
- **`reference/examples.md`** — worked correct and incorrect behavior hierarchies.

## Before writing

1. **Confirm sub-epics in scope** — list sub-epics from the story map this hierarchy covers.
2. **Read domain artifacts** — extract concepts, states, and transitions from `domain-language.md` and `domain-model.md`; observable behaviors from `acceptance-criteria.md`.
3. **Declare the structure** — state top-level describe blocks and nesting in chat before writing the file.

## Build rules

| Step | What to do |
| --- | --- |
| **Name top-level describes** | One per sub-epic in scope. Use the sub-epic's exact name from the story map. |
| **Name nested describes** | Domain concepts, states, or operation groups from domain artifacts. Use names verbatim. |
| **Write behavior lines** | Each leaf starts with `should`. One observable behavior. No code syntax. |
| **Validate with stakeholder** | Walk the hierarchy with a domain expert before handoff. |
| **Save** | Markdown, 2-space indent per level. No code. No test syntax. |

## Output shape

| Template | Deliverable |
| --- | --- |
| `templates/behavior.md` | Plain-English behavior hierarchy file |

## Quality bar

Every describe block traces to a sub-epic or named domain concept. Every leaf is business-readable plain English. Every describe has at least one `should` leaf. No code syntax anywhere.
