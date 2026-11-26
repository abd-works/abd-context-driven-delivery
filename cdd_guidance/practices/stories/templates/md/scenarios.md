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
     (not a second *Then*). New *When* when actor or trigger changes.

     Realizations: one ```realization block after each Given group (a Background's included) and each When group.
     Statements, not prose: name each object once (`cart = new Cart(customerProfile)`) and use the name after;
     constructors with the parameters the code's constructor takes; repositories called only by the flow, each a
     statement of its own (`CartRepository.update(cart)`), never under a domain operation; `<- ` only for a value the
     next statements use; `// <the Given line's words>` before each Given line's statements; the repository or
     aggregate operation a seed reaches, never a test helper. A Given that sets up nothing has no block. -->

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

### Background

*Given* a ++`<ConceptX>`++ `<in the state every scenario starts from>`  
  *And* that ++`<ConceptX>`++ holds a ++`<ConceptY>`++ `<in its state>`

```realization
// a <ConceptX> <in the state every scenario starts from>
<conceptX> = new <ConceptX>(<constructor parameters>)
<ConceptX>Repository.create(<conceptX>)
// that <ConceptX> holds a <ConceptY> <in its state>
<conceptY> = <conceptX>.<addConceptY>(<parameters>)
<ConceptX>Repository.update(<conceptX>)
```

---

## Behaviors

### Default — Scenario Outline

#### Scenario Outline: `<outcome-oriented name>`

*Given* a ++[`<ConceptA>`](<path>/domain-model.md#<concepta-heading-anchor>)++ with {`<field_1>`}  
  *And* the ++[`<ConceptB>`](<path>/domain-model.md#<conceptb-heading-anchor>)++ for that ++`<ConceptA>`++ is {`<field_2>`}

```realization
// a <ConceptA> with {<field_1>}
<conceptA> = new <ConceptA>({<field_1>})
<ConceptA>Repository.create(<conceptA>)
// the <ConceptB> for that <ConceptA> is {<field_2>}
<conceptB> = new <ConceptB>(<conceptA>.<conceptAId>, {<field_2>})
<ConceptB>Repository.create(<conceptB>)
```

*When* the **`<Actor>`** `<action>`

```realization
<conceptA> = <ConceptA>Repository.load(<conceptAId>)
<conceptB> = <ConceptB>Repository.load(<conceptBId>)
<result> = <conceptA>.<operation>(<conceptB>)
  -> <conceptB>.<operation>(<args>)
<ConceptA>Repository.update(<conceptA>)
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

#### Scenario: `<refusal — the action is refused in an edge or error case>`

*Given* a ++`<ConceptA>`++ `<in the state of the edge or error case — a blank value, a duplicate, a second actor, a missing dependency>`  
*When* the **`<Actor>`** `<action>`  
*Then* the ++`<result concept>`++ is `<refused, with the reason the actor is shown>`  
  *But* no ++`<concept>`++ is `<what the refused action must leave unchanged>`

---

### Alternate — inline scenarios

Use only for  simple scenarios where an examples table adds limited value — express mechanical variation as sibling scenarios instead.

#### Scenario 1: `<outcome-oriented scenario name>`

*Given* a ++`<ConceptA>`++ *`<value>`*  
  *And* that ++`<ConceptA>`++ *`<value>`* has a ++`<ConceptB>`++ *`<value>`*  
*When* the **`<Actor>`** `<triggering action>` on the ++`<ConceptA>`++ *`<value>`*  
    using ++`<ConceptB>`++ *`<value>`*  
*Then* the ++`<observed concept>`++ is `<observable outcome>`  
  *And* the ++`<related concept>`++ is `<additional outcome>`  
  *But* no ++`<concept>`++ is `<what does not happen>`

#### Scenario 2: `<alternate outcome-oriented scenario name>`

*Given* `<alternate setup state>`  
*When* the **`<Actor>`** `<alternate triggering action>`  
*Then* `<alternate observable outcome>`  
  *And* `<additional outcome>`
