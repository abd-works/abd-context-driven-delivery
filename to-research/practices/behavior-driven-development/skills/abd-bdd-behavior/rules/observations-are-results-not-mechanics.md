---
rule: observations-are-results-not-mechanics
severity: error
---
# Observations Are Results, Not Mechanics

Every `it should …` leaf describes an **observable result** — a fact about the state of the subject or its collaborators after the containing state has been reached. It never describes the internal steps that produced that state — the method calls, the super calls, the private helpers, the intermediate wiring.

The reader of a behavior spec should be able to swap the entire implementation of the system (different super chain, different factory names, different private methods, different call order) without changing a single observation. If a leaf breaks when the internals are rearranged but the results are the same, the leaf is describing mechanics, not results.

## How to tell mechanics from results

A leaf is a mechanic if it mentions any of these:

- A specific method name that is not part of the domain vocabulary (`super.updateSelf`, `findMatch`, `createChildXxx`, `translateFrom`) — the reader has to look at the code to understand what is being asserted
- The **order** in which internal steps happened (`first via …`, `before creating any new child`) — order of internal steps is implementation
- The **fact of a call** rather than its effect (`should have called …`, `should have invoked …`, `should have delegated to …`)
- A private helper, factory, or intermediate data structure whose existence is an implementation choice
- Absence of an event that no observer would notice (`should never be replaced` without a follow-up observation that verifies identity)

A leaf is a result if it describes:

- The **value** of a field on the subject (`it should carry the same name`, `it should hold 3 SubEpics`)
- The **contents** of a collection on the subject (`it should list the Epics in sequential order`)
- A **relationship** to a collaborator that is part of the domain (`the held LanguageAst should be the same instance that was held before the call`)
- A **rejection** of an operation (`it should reject the translation`)
- A **payload** produced by the subject (`the UpdateReport should record the rename`)

## Rewrite recipes

| Wrong (mechanic) | Right (result) |
|---|---|
| `it should have copied the domain fields from source first via super.updateSelf` | `it should carry the same domain fields as the source` |
| `it should have set position and size from the placementRules for its type` | `its position and size should match the placementRules for its type` |
| `it should have called its own createChildXxx factory to produce the new child` | `the new child on the target > it should be of the correct semantic type for its position` |
| `it should have called translateFrom on the new child to fill its fields` | `the new child on the target > it should carry every field from the source child` |
| `it should match self-children to source-children by name and sequential order via findMatch before creating any new child` | `the target children matched to a source child by name and sequential order > it should keep its identity through reconciliation` |
| `it should process child collection pairs in the order declared by childCollections` | `every declared child collection on the target > it should appear in the order declared by childCollections` |
| `the held LanguageAst > it should never be replaced` | `that has had updateSelf called a second time > the held LanguageAst > it should be the same instance that was held before the second call` |

The pattern: whenever you catch yourself writing an observation about "what the code did", ask what the reader could observe from outside. Rewrite the observation to describe that observable thing directly, and — if needed — restructure the containing describes so the standing subject is the thing being observed.

## The swap-the-implementation test

Imagine a second implementation of the same behavior that:

- Uses a completely different internal method chain
- Renames every private helper
- Restructures the super class
- Uses a totally different data structure to hold intermediate state

If any observation in your spec would need to change to still pass against that second implementation, that observation is describing mechanics, not results. Rewrite it as a fact the reader could verify by looking only at inputs, outputs, and the state of the subject and its named collaborators.

## Domain vocabulary is allowed, code vocabulary is not

Observations may name domain concepts that the reader would recognise from the domain glossary (`the UpdateReport`, `the NodeSnapshot`, `the reconstructed Story Map`, `the target`, `the source`, `sequential order`, `StoryType`). Those are part of the shared vocabulary and are stable across implementations.

Observations may not name code-level concepts that only exist because of the current implementation (`super.updateSelf`, `placementRules`, `createChildXxx`, `findMatch`, `childCollections`) unless they appear in a describe as a state condition being set up — never as the thing observed.

The line: if the concept is in the ubiquitous language, it is fair game in an observation. If it is only in the code, it is only fair game as a setup condition.

## Examples

- Example (wrong): `it should have called its own createChildXxx factory to produce the new child` — names a factory method and asserts the fact of a call
- Example (correct): `the new child on the target > it should be of the correct semantic type for its position` — observes the resulting child's type, which the reader can verify without looking at the factory
- Example (wrong): `it should have copied the domain fields from source first via super.updateSelf` — names a super method and asserts call order
- Example (correct): `it should carry the same domain fields as the source` — observes the resulting field values
- Example (wrong): `the held LanguageAst > it should never be replaced` — asserts absence of an event
- Example (correct): `that has had updateSelf called a second time > the held LanguageAst > it should be the same instance that was held before the second call` — sets up the state where a replacement would be observable, then observes identity
