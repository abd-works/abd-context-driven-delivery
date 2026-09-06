# Specification by Example — `<Module Name>`

**Sources / context:** `<source files used>`

**Domain outline:** `docs/domain/domain-model.md` (default) · `docs/domain/domain-specification.md` (if present)

For each **story**, specify **scenarios** as concrete examples using *Given* / *When* / *Then* (and *And* / *But*). Default notation is **Scenario Outline** with normalised **Examples** tables — one table per domain concept, `{placeholder}` tokens in steps. Plain **Scenario** is the exception, only for single-path stories with no data variation.

## Story: `<Verb–Noun Title>`  

**Story type:** user | system | technical

**Sources / context:** _(pointer to AC file and domain model outline — e.g. `domain-model.md` § Campaign)_

### Domain terms  

List the **domain terms** this story's scenarios rely on: words or short phrases for key **things**, **state**, **actions**, and **rules or constraints** in *your* problem space. Use *italics* for each term entry (*Title Case* for multi-word concepts); add a short dash or colon and a plain-language gloss so readers share one vocabulary before they read the steps.

---

## Story: `<Verb–Noun Title>`

**Story type:** user | system | technical  

### Domain terms

List the **domain terms** this story's scenarios rely on: words or short phrases for key **things**, **state**, **actions**, and **rules or constraints** in *your* problem space. Use *italics* for each term entry (*Title Case* for multi-word concepts); add a short dash or colon and a plain-language gloss so readers share one vocabulary before they read the steps.

Every term listed here **must already exist** in a domain source artifact — **Domain Model** (`domain-model.md`) or **Domain Language** (`domain-language.md`) are the most likely sources at this stage; **Domain Specification** (`domain-specification.md`) when available. If a term is missing from all domain sources, stop and resolve it there first before writing it into a scenario.

Keep the list **lean** (only terms that appear in steps or name Example tables below).

---

### Examples

#### `<Domain ConceptA>`:

| scenario      | `<field_1>` | `<field_2>` |
|---------------|-------------|-------------|
| `<Scenario A>` | `<value>`  | `<value>`   |
| `<Scenario B>` | `<value>`  | `<value>`   |

#### `<Domain ConceptB>`:

| scenario      | `<concept_a_fk>` | `<field_1>` | `<field_2>` |
|---------------|-------------------|-------------|-------------|
| `<Scenario A>` | `<fk_value>`     | `<value>`   | `<value>`   |
| `<Scenario B>` | `<fk_value>`     | `<value>`   | `<value>`   |

---

### Background

*Given* a **`<ConceptA>`** {field_1} with **`<ConceptA>`** {field_2}  
  *And* a **`<ConceptB>`** {field_1} linked to **`<ConceptA>`** {concept_a_fk}  

---

### Behaviors

#### Scenario 1: `<outcome-oriented name>`

#### Steps

*When* **`<action>`** using **`<ConceptA>`** {field_1}  
*Then* **`<outcome>`** is {field_2}  

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Scenario 1 | `<source>` | `<location>` |

---

## Example (plain scenario)

## Story: Apply For a Payment Product Agreement

**Story type:** user

### Domain Terms

- *Customer* — account holder applying for the agreement
- *DDA Account* — demand deposit account; must be valid and eligible
- *Payment Product Agreement* — contract under review after submission
- *Owner* — named responsible party on the agreement
- *Contact Details* — email or phone used to notify the **Owner**

---

## Behaviors

### Scenario 1: Agreement submitted with valid DDA Account and Owner

*Given* a **Customer** *Jane Doe* exists  
  *And* that **Customer** *Jane Doe* has a valid **DDA Account** *DDA-001*  
*When* the **Customer** *Jane Doe* applies for a **Payment Product Agreement**  
    using **DDA Account** *DDA-001*  
    with **Owner** *John Doe*  
      that has **Contact Details** *john@acme.com*  
*Then* the **Payment Product Agreement** is submitted for review  
  *And* the **Owner** *John Doe* is notified at *john@acme.com*  

### Scenario 2: Agreement rejected when DDA Account is invalid

*Given* a **Customer** *Jane Doe* exists  
  *And* that **Customer** *Jane Doe* has **DDA Account** *DDA-999* with status *Invalid*  
*When* the **Customer** *Jane Doe* applies for a **Payment Product Agreement**  
    using **DDA Account** *DDA-999*  
*Then* the **Payment Product Agreement** is *rejected*  
  *And* **Customer** *Jane Doe* is notified that the **DDA Account** is *not eligible*  

---

## Example (scenario outline with normalized tables)

## Story: Submit Payment and Validate Against Account Limit

**Story type:** user

### Domain Terms

- *Account* — enterprise sub-account with an activation status
- *Transactional Limit* — maximum amount rule attached to an **Account**
- *Wire Payment* — payment request submitted by the user
- *Payment Amount* — value entered for the **Wire Payment**
- *Validation Status* — outcome after limit check (*successful* or *rejected*)

---

### Examples

#### Account:

| scenario      | enterprise_name | account_name       | activation_status |
|---------------|-----------------|--------------------|-------------------|
| Scenario 1    | Acme Corp       | Acme Operating     | Active            |
| Scenario 2    | Acme Corp       | Acme Payroll       | Active            |

#### Transactional Limit:

| scenario      | account_name       | limit_name  | max_amount   | currency |
|---------------|--------------------|-------------|--------------|----------|
| Scenario 1    | Acme Operating     | daily_wire  | 500000.00    | USD      |
| Scenario 2    | Acme Payroll       | weekly_wire | 2000000.00   | USD      |

#### Wire Payment:

| scenario      | amount      | currency | formatted_display | validation_status |
|---------------|-------------|----------|-------------------|-------------------|
| Scenario 1    | 10000.00    | USD      | $10,000.00        | successful        |
| Scenario 2    | 500000.01   | USD      | $500,000.01       | rejected          |

---

### Background

*Given* a **User** {user_name} is logged into ChannelOne 2.0  
  *And* that **User** {user_name} is representing **Enterprise** {enterprise_name}  

---

### Behaviors

#### Scenario Outline 1: Submit Payment and Validate Against Account Limit

#### Steps

*Given* an **Account** {account_name} with **Activation Status** {activation_status}  
  *And* the **Transactional Limit** for that **Account** is {max_amount} {currency}  
*When* the **User** enters a **Payment Amount** of {amount} {currency}  
*Then* the **Wire Payment** is marked as {validation_status}  
  *And* a **Report** is sent with formatted display {formatted_display}  

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Scenario 1 | *Order Management Workshop* | Whiteboard "submit flow", 2026-03-15 |
| Scenario 2 | *API Spec* v2 | p. 8, §"Limit exceeded" |

---

<!-- Template reference only — do not copy this section into generated project files. -->

## Instructions

- **Default notation: Scenario Outline.** Every multi-scenario story uses Scenario Outline with Examples tables. Plain Scenario only for single-path stories with no data variation.
- **Step keywords:** *Given*, *When*, *Then*, *And*, *But* — single-star italic, sentence case. Never all-caps or bold.
- **Domain terms in steps:** wrap in `**double stars**` (e.g. **Customer**, **DDA Account**). Values/literals use *single-star italic* (e.g. *Jane Doe*, *DDA-001*).
- **Domain terms list:** use `*italic*` for each entry in the glossary list before the steps; keep the list lean (only terms that appear in steps or name example tables).
- **Plain scenarios:** *Given* = state; *When* = action; *Then* = observable outcome.
- **Scenario outlines:** Use `{column_name}` tokens in steps matching example table headers exactly. Provide multiple rows.
- **Example tables:** One table per domain concept. Link related tables with foreign-key columns. Never denormalize multiple concepts into a single flat table.
- Cover at least one happy path, one failure or rejection, and edge cases where the story implies them.
- **Source evidence:** add a `### Evidence` table at the end of the story (one row per scenario or scenario group). Never inline evidence after individual scenarios.
