# Specification by Example — Core Concepts

**Domain sources first.** Read [`../../../reference/domain-input-priority.md`](../../../reference/domain-input-priority.md) before writing scenarios — produce `domain.json` when required.

## What is specification by example?

**Specification by example** is a practice where we create specifications for stories through **concrete scenarios** demonstrated through **examples**. Spec scenarios include preconditions (**Given**), the triggering action (**When**), and an observable outcome (**Then**).

**Inputs:** Scenarios are often created from **acceptance criteria** (WHEN/THEN statements in a story). When AC exist, start from the main-flow AC, add Given steps until the flow is concrete, then add scenarios for failures, edges, and alternate flows. The same quality rules apply when the only inputs are a story name, bullet notes, or shared understanding.

**Living documentation:** Specifications by example are not throwaway analysis artifacts. They become **executable requirements** — testable without translation — captured in **live documentation** that stays current as the system evolves.

**Multiple perspectives, not solo work.** Ensure context covers business, technical, and testing perspectives; flag a missing perspective as an unknown rather than inventing plausible-sounding scenarios. See [`../../../reference/handling-incomplete-context.md`](../../../reference/handling-incomplete-context.md) for the shared discipline.

**Determine new system vs existing system before writing scenarios.** If specifying an existing system, you MUST read the contract schemas (`packages/contracts/` or equivalent) before choosing concrete values. Check regex patterns, min/max, allowed characters, required fields. A scenario with `prefix: "E2E-BATCH-"` against a schema that only allows `[A-Za-z0-9]+` will silently fail at runtime. See [`../../../reference/new-vs-existing-system.md`](../../../reference/new-vs-existing-system.md) for the shared discipline.

---

## Given, When, Then (and And)

- **Given** — preconditions: data and state that exist before the behavior. Use Background for setup shared by three or more scenarios.
- **When** — an action or event under test. A scenario may have **multiple** When/Then beats when the behaviour is a sequence of interactions. Each new When starts the next beat.
- **Then** — observable outcomes to assert after the preceding When.
- **And** — continues a Given, When, or Then block with another line of the same kind. Start a new **When** when the actor or trigger changes — do not chain unrelated actions with And.

## Formatting convention

In `.md` artifacts, use **bold** for domain concept names and *italics* for their actual values — for example **User** *Jane Doe*, **Enterprise** *Acme Corp*, **Payment Amount** *$1,000.00 USD*.

## Working from acceptance criteria

If the story has AC (WHEN/THEN from abd-story-acceptance-criteria), use the main-flow AC as the spine: convert WHEN to When, THEN/AND to Then/And, then add Given preconditions to make it runnable. Remaining AC become additional scenarios (failures, edges, alternate flows). The mapping is rarely one-to-one, but readers should see the relationship.

## Scenarios vs Scenario Outlines

- **Scenario** (plain) — one path, all values inline. Use for distinct flows: happy path, rejection, edge case.
- **Scenario Outline** (parameterized) — same steps, varying data rows. Values use `{column_name}` tokens bound to an **Examples** block. Use only when variation is real and the steps are genuinely identical.

## Background

Use Background only when three or more scenarios share identical starting state. Given and And only — no When or Then.

## Domain concept grounding

Specification by example works at two levels simultaneously: it specifies *behavior* and it confirms *the domain model*. When domain model content — a domain specification, domain model, or domain language glossary — is available, the scenarios are its behavioral proof. Concept names must match exactly.

When no domain model exists, the scenarios themselves reveal the model. The deliberate way a step names a concept and connects it to another documents the model for the team.

**This is exactly the same job the example tables do in Scenario Outlines.** A table column set of `customer_name | dda_account_number | payment_product_name` grounds the data in the domain relational structure. Tables that show only one concept's fields in isolation lose the relationships that make the domain model legible.

## Specification level

The default level is the **story** — each story gets its own scenarios. But specifications can be written at any level of the story map:

- **Epic or sub-epic level** — a specification that describes the end-to-end flow across its child stories.
- **Story level** (default) — scenarios for one discrete behaviour.
- **Cross-story** — when a scenario naturally spans multiple stories in sequence.

Higher-level specifications help answer: "when these stories are all done, is the feature actually complete?"

---

## Validate scenario values against the schema (existing systems)

When specifying an existing system, every concrete value in a scenario must satisfy the constraints the system already enforces. A scenario with invalid values will produce a test that fails for the wrong reason — typically a silent form validation failure or a cryptic API 4xx.

**Before committing values, check:**

| What to check | Where to find it | What goes wrong if you skip |
|---|---|---|
| Allowed characters (regex) | Contract schemas (`packages/contracts/`, Zod `.regex(...)`) | Scenario uses `E2E-BATCH-` but schema only allows `[A-Za-z0-9]+` → silent form rejection |
| Min/max range | Schema `.min()` / `.max()` | Scenario uses `count: 1000` but schema caps at 500 → API 400 |
| Required fields | Schema shape (no `.optional()`) | Scenario omits discount value → form never submits |
| Enum values | Schema `.enum([...])` or discriminated unions | Scenario uses `type: "flat"` but only `"percentage"` and `"amount"` exist |
| Date constraints | Service validators, campaign date ranges | Scenario uses a date that falls outside the campaign window → API 409 |

**The cost of skipping this is high:** when a form silently fails validation, the symptom is "dialog stays open" or "nothing happens" — no error message, no stack trace, no obvious cause. These are the hardest bugs to diagnose in E2E tests.

**Rule of thumb:** If the scenario involves user input that will be validated (form submission, API call), spend 2 minutes reading the schema for that input before choosing values.

---

## Quick checklist

- **Given** is state-only; **When** is an action or trigger; **Then** asserts outcomes. Multiple **When/Then** beats are fine for multi-step journeys.
- **{Concept}** ↔ tables **both ways**; domain words sit beside each `{Concept}`.
- Happy, edge, and error paths implied by the story, notes, or AC are **visible** in scenarios or outlines.
- Outlines used only when **variation** is real, not ceremonial.
- **Domain emphasis:** in Markdown scenario artifacts, domain-significant terms use *italics* consistently.

---

## Example: epic-level specification

```gherkin
# Epic-level: Manage Customer Orders
Scenario: Customer places and tracks a new order
  Given a Customer with an active account
  When the Customer adds items to the cart and submits the order
  Then the order is confirmed with a tracking number
  When the Customer views the active orders for their account
  Then that order is displayed along with any other active orders
  And the status for that order is displayed as Processing
  When the order is dispatched
  Then the Customer receives a shipment notification
  And the order status changes to Shipped
```
