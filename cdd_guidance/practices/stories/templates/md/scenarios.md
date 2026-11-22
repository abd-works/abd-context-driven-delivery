---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

<!-- Default: Scenario Outline + Examples table. Alternate: inline sibling scenarios below.

     Disk layout (`artifacts-mirror-story-hierarchy` + `kebab-case-paths`):
     {epic}/{sub-epic}/{story}/{story_snake}_story.test.md
     {epic}/{sub-epic}/{story}/{story_snake}_story.test.{lang}
     — kebab-case folders; one scenarios file and one story test per story, same stem.
     Exception: Python epic helper only — {epic_slug}_helper.py at epic root.

     Outcome chaining: first *Then* on a step; further outcomes on the same *When* use *And*
     (not a second *Then*). New *When* when actor or trigger changes. -->

<!-- Head the file with the name the story has on the story map (`scenarios-name-a-story-on-the-map`). -->

## Story: `<Story Verb–Noun>`

### Domain terms

- ++[`<ConceptA>`](<path>/domain-model.md#<concepta-heading-anchor>)++ — `<plain-language gloss>`
- ++[`<ConceptB>`](<path>/domain-model.md#<conceptb-heading-anchor>)++ — `<plain-language gloss>`

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).
> Link each domain term to its heading in the domain model markdown — `domain-model.md` (DDD) or `class-model.md` (Clean Engineering) — when that file exists (`domain-terms-link-to-model`). The anchor is the heading's own: `#### SimCard <<Entity>>` is `#simcard-entity`. With no model file, leave the term unlinked.

### Evidence

| Source | Note |
|--------|------|
| `<pointer>` | `<why it matters>` |

### Edge conditions

<!-- `edge-conditions-walked`: every condition gets one line. Name the Scenario that covers it, or write
     "does not apply, because ...", or write the question for the person where the source and the running
     product are silent. A condition with no line is the failure. -->

| Edge condition | Scenario, "does not apply, because ...", or question for the person |
|----------------|-------------------------------------------------------------------|
| Missing or empty input | `<answer>` |
| Malformed input, or input at or past a limit | `<answer>` |
| Duplicate | `<answer>` |
| Repeated action | `<answer>` |
| Two actors at once | `<answer>` |
| Interrupted action | `<answer>` |
| Dependency absent, unavailable, slow, or wrong | `<answer>` |
| Changed or gone since last seen | `<answer>` |
| Actor not allowed | `<answer>` |

### Background

*Given* a ++`<ConceptX>`++ from `helper.given<ConceptX…>({ mode: "fake" })`  
  *And* that ++`<ConceptX>`++ exposes `<public property / operation>`  

---

## Behaviors

### Default — Scenario Outline

#### Scenario Outline: `<outcome-oriented name>`

*Given* a ++[`<ConceptA>`](<path>/domain-model.md#<concepta-heading-anchor>)++ with {`<field_1>`}  
  *And* the ++[`<ConceptB>`](<path>/domain-model.md#<conceptb-heading-anchor>)++ for that ++`<ConceptA>`++ is {`<field_2>`}  
*When* the **`<Actor>`** `<action>`  

```realization
<entry>.<operation>(<args>)
  -> <collaborator>.<operation>(<args>)
  <- <result>
```

*Then* the ++`<result concept>`++ `<outcome>` is visible on the public interface  
  *And* a ++`<related concept>`++ shows {`<field_3>`}

#### Examples

| scenario   | `<field_1>` | `<field_2>` | `<field_3>` |
|------------|-------------|-------------|-------------|
| ++Scenario 1++ | `<value>`   | [`<ConceptB value>`](<path>/domain-model.md#<conceptb-heading-anchor>)   | `<value>`   |
| ++Scenario 2++ | `<value>`   | `<value>`   | `<value>`   |
| ++Scenario 3++ | `<value>`   | `<value>`   | `<value>`   |

> Markdown keeps examples tables for documentation. Code wires values via `{Type}ExampleFactory` (AI fills helper/story method bodies). Do not copy inventable `examples: [{ … }]` literals into code story files.

#### Scenario: `<variation — delta from the outline>`

*Given* `<only the state that differs from the outline>`  
*When* the **`<Actor>`** `<action>`  
*Then* the ++`<result concept>`++ `<outcome that differs>`

#### Scenario: `<refusal — the action is refused at an edge condition>`

*Given* a ++`<ConceptA>`++ `<in the state the edge condition names — a blank value, a duplicate, a second actor, a missing dependency>`  
*When* the **`<Actor>`** `<action>`  
*Then* the ++`<result concept>`++ is `<refused, with the reason the actor is shown>`  
  *But* no ++`<concept>`++ is `<what the refused action must leave unchanged>`

---

### Alternate — inline scenarios

Use only for  simple scenarios where an examples table adds limited value — express mechanical variation as sibling scenarios instead.

#### Scenario 1: `<outcome-oriented scenario name>`

*Given* a ++`<ConceptA>`++ *`<value>`*  
  *And* that ++`<ConceptA>`++ *`<value>`* has a ++`<ConceptB>`++ *`<value>`*  
*When* the ++`<ConceptA>`++ *`<value>`* `<triggering action>`  
    using ++`<ConceptB>`++ *`<value>`*  
*Then* the ++`<observed concept>`++ is `<observable outcome>`  
  *And* the ++`<related concept>`++ is `<additional outcome>`  
  *But* no ++`<concept>`++ is `<what does not happen>`

#### Scenario 2: `<alternate outcome-oriented scenario name>`

*Given* `<alternate setup state>`  
*When* `<alternate triggering action>`  
*Then* `<alternate observable outcome>`  
  *And* `<additional outcome>`
