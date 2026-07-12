---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

### Examples

#### `<ConceptA>`:

| scenario   | `<field_1>` | `<field_2>` |
|------------|-------------|-------------|
| Scenario 1 | `<value>`   | `<value>`   |
| Scenario 2 | `<value>`   | `<value>`   |

#### `<ConceptB>`:

| scenario   | `<concept_a_fk>` | `<field_1>` | `<field_2>` |
|------------|-------------------|-------------|-------------|
| Scenario 1 | `<fk_value>`     | `<value>`   | `<value>`   |
| Scenario 2 | `<fk_value>`     | `<value>`   | `<value>`   |

---

### Background

*Given* a **`<ConceptX>`** {`<field>`} `<state description>`  
  *And* that **`<ConceptX>`** {`<field>`} `<additional state>`  

---

### Behaviors

#### Scenario Outline 1: `<outcome-oriented name>`

#### Steps

*Given* a **`<ConceptA>`** {`<field_1>`} with **`<field_2>`** {`<field_2>`}  
  *And* the **`<ConceptB>`** for that **`<ConceptA>`** is {`<field_1>`} {`<field_2>`}  
*When* the **`<Actor>`** `<action>` with a **`<Concept>`** of {`<field>`} {`<field>`}  
*Then* the **`<result concept>`** is `<outcome>` as {`<field>`}  
  *And* a **`<related concept>`** shows {`<field>`}  
