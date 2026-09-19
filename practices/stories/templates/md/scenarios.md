---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

<!-- Default: Scenario Outline + Examples table. Alternate: inline sibling scenarios below.

     Disk layout (`artifacts-mirror-story-hierarchy` + `kebab-case-paths`):
     tests/{epic-verb-noun}/{sub-epic-verb-noun}/{story-kebab-slug}.py|md
     — kebab-case folders and file stems; one file per story; no {story}/ folder.
     Exception: Python epic helper only — {epic_slug}_helper.py at epic root.

     Outcome chaining: first *Then* on a step; further outcomes on the same *When* use *And*
     (not a second *Then*). New *When* when actor or trigger changes. -->

### Domain terms

- ++`<ConceptA>`++ — `<plain-language gloss>`
- ++`<ConceptB>`++ — `<plain-language gloss>`

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).

### Evidence

| Source | Note |
|--------|------|
| `<pointer>` | `<why it matters>` |

### Background

*Given* a ++`<ConceptX>`++ from `helper.given<ConceptX…>({ mode: "fake" })`  
  *And* that ++`<ConceptX>`++ exposes `<public property / operation>`  

---

## Behaviors

### Default — Scenario Outline

#### Scenario Outline: `<outcome-oriented name>`

*Given* a ++`<ConceptA>`++ with {`<field_1>`}  
  *And* the ++`<ConceptB>`++ for that ++`<ConceptA>`++ is {`<field_2>`}  
*When* the **`<Actor>`** `<action>`  
*Then* the ++`<result concept>`++ `<outcome>` is visible on the public interface  
  *And* a ++`<related concept>`++ shows {`<field_3>`}

#### Examples

| scenario   | `<field_1>` | `<field_2>` | `<field_3>` |
|------------|-------------|-------------|-------------|
| ++Scenario 1++ | `<value>`   | `<value>`   | `<value>`   |
| ++Scenario 2++ | `<value>`   | `<value>`   | `<value>`   |

> Markdown keeps examples tables for documentation. Code wires values via `{Type}ExampleFactory` (AI fills helper/story method bodies). Do not copy inventable `examples: [{ … }]` literals into code story files.

#### Scenario: `<variation — delta from the outline>`

*Given* … (only the delta from the outline)  
*When* …  
*Then* …

---

### Alternate — inline scenarios

Use when an examples table adds no value — express mechanical variation as sibling scenarios instead.

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
