# Grill me — abd-architecture-code

**Mechanics:** [`common/reference/grill-me-with-practice-skill.md`](../../../../../common/reference/grill-me-with-practice-skill.md) — one question at a time; generate-to-learn when enough is shared.

Ask until inputs are resolved, spec ⇄ template consistency is confirmed, and layer/tier coverage is concrete:

## Input resolution

- Which mechanism does this story implement? Walk me through the Where-to-Start row that matches it. If the story touches more than one mechanism, which one is primary, and how do the secondary ones get covered?
- Where is the central spec for this project? Show me the path. Where does the Where-to-Start row link to for the mechanism in scope — that link is `<context-file>`?
- Where is the template package for this mechanism — `docs/architecture/templates/<slug>/`? Does `<spec-root>/example/` currently build and pass tests? If it does not, we cannot proceed; the template skill must fix it first.
- Where is the test-helpers package-tier `architecture-context.md`? What test tiers does it name? What is its mapping from story artifact to test file (sub-epic → file, scenario → file, something else)?

## Spec ⇄ template consistency

- Does the placeholder vocabulary in `<spec-root>/template/` match `<context-file>` § Canonical Patterns verbatim? If you spot drift, that is a template-skill bug; we cannot bridge it here.
- Does `<spec-root>/template/` have a participant for every entry in `<context-file>` § File Structure? Same question for `<spec-root>/rules/` against `<context-file>` § Rules.
- Does `<spec-root>/templates/tests/` cover every tier the helpers context file mandates?

## Layer and behaviour

- Where does each layer's responsibility end — what may it know about adjacent layers (from `<context-file>` § File Structure and § Class Specification)?
- Which spec patterns have never been exercised by a real story?
- For each scenario, is the risk in domain logic or framework plumbing?
- What responses from other systems or layers are assumed but unverified?
- Which behaviors are proven at only one test tier?
- Which error, concurrency, or partial-failure flows does the spec imply but the story doesn't name?

## Substitution

- What does the story bind each placeholder in `<spec-root>/parameters.json` to? Walk through the rename map for filenames.
- Does the story's domain name collide with the template's sentinel binding under `<spec-root>/example/`? If yes, pick a different name before generating.