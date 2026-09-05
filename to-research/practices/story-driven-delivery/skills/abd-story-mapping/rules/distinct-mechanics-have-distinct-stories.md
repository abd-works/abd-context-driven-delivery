# Rule: Distinct mechanics have distinct stories

**Scanner:** Manual review

When the source material describes multiple entity types (transaction types, account types, fulfilment methods, inspection types, instrument types), the story map groups them by **distinct mechanical pattern** — entities with identical workflows share one parameterized story; entities with different workflows get separate stories. This holds across all lifecycle phases: configuration/setup, runtime/execution, and observation/reporting. Failure is a single catch-all story covering entity types whose processing, parameters, or outcomes differ fundamentally, or the opposite — separate stories for entity types that share the same workflow.

## DO

- Compare entity-type mechanics **before** writing stories: for each type, identify what a user configures, what the system validates, and what outcomes are possible. Group by workflow pattern, not by name.

  **Example (pass):** A payments domain has 8 instrument types. The story map shows `(S) Operator --> Initiate Wire Transfer` (correspondent-bank routing), `(S) Operator --> Submit Card Payment` (auth-capture-settle), `(S) Operator --> Submit ACH Batch` (batch windows + return codes) — three stories because three distinct clearing mechanics. Cheque, BPAY, and direct debit share the same batch-and-clear workflow as ACH, so they are handled by the same story with a type parameter, not duplicated.

- Perform the comparison across **all lifecycle phases** so the user never has to say "go deeper."

  **Example (pass):** A retail domain maps fulfilment stories for configuration (subscription has recurring billing setup; drop-ship has vendor onboarding), runtime (subscription has pause/resume; drop-ship has vendor handoff; digital has licence key generation), and reporting (subscription has churn metrics; drop-ship has vendor SLA). Three phases, distinct stories per distinct mechanic in each.

- Entities with different **lifecycles** (permanent vs sustained vs reactive) need separate stories even when they share a category.

  **Example (pass):** A healthcare system has four "patient protections" under one heading. The map separates them by lifecycle:

  ```
  (E) Enforce Patient Protections
      (S) System --> Request Insurance Pre-Authorization before Procedure
      (S) System --> Fire Allergy Alert on Medication Order
      (S) Nurse --> Reassess Infection-Control Isolation Daily
      (S) System --> File Adverse-Event Report to Regulator
  ```

  Pre-authorization is proactive (before procedure), allergy is passive (fires automatically), isolation is sustained (daily reassessment, can be overridden), adverse-event is reactive (post-incident). Four trigger types → four stories.

- When the source lists **5+ sub-types** under one heading, enumerate each sub-type's parameters before deciding whether to consolidate. If more than half have different parameter sets, default to separate stories.

  **Example (pass):** Five "notification channels" appear under one heading. After enumeration the map shows:

  ```
  (E) Configure Notification Channels
      (S) Admin --> Configure Email Provider and Template Builder
      (S) Admin --> Configure SMS Carrier Gateway and Opt-In Compliance
      (S) Admin --> Register Push Notification Device Tokens and Certificates
      (S) Admin --> Define In-App Targeting Rules and Read Receipts
      (S) Admin --> Set Webhook Endpoint URL and Retry Policy
  ```

- When a story describes a **state change** that creates a new actor context (trapped, locked, held, escalated), check whether the source describes a separate resolution mechanic for **exiting** that state. If the exit has a different actor, different action type, or different check, it is a distinct story.

  **Example (pass):** A support-ticket system maps escalation and the exits from that state:

  ```
  (SE) Escalate and Resolve Tickets
      (S) Agent --> Escalate Ticket to Tier 2
      (S) Tier 2 Agent --> Reject Escalation with Reason
      (S) Tier 2 Agent --> Accept Escalation and Reassign
  ```

  Reject and Accept are separate stories — different actor (Tier 2, not Tier 1), different checks (rejection criteria vs reassignment workflow).

- When the source describes a **pipeline** (request → validate → process → respond), map **filtering or short-circuit steps** that fire before the main processing step. Passive filters that prevent processing entirely are distinct stories, not implicit.

  **Example (pass):** An order-fulfilment system maps forward processing plus two pipeline filters:

  ```
  (SE) Process Order
      (S) System --> Screen Order Against Embargo and Sanctions List
      (S) System --> Evaluate Fraud Score Against Threshold
      (S) System --> Validate Order Items
      (S) System --> Charge Payment
      (S) System --> Ship Order
  ```

  Embargo screening and fraud scoring are pre-processing filters with different data sources — not implicit parts of `Validate Order`.

- When an entity type has both a **configuration phase** and a **runtime phase**, check whether it appears in the runtime context even if it was initially categorized under configuration. An entity classified as "setup-only" may have distinct runtime resolution.

  **Example (pass):** A banking system maps account configuration and runtime separately:

  ```
  (E) Open Accounts
      (S) Customer --> Open Savings Account
      (S) Customer --> Open Checking Account
      (S) Customer --> Open Money Market Account

  (E) Process Account Transactions
      (S) System --> Enforce Money Market Monthly Transaction Limit
      (S) System --> Assess Money Market Excess-Transaction Penalty
      (S) System --> Execute Checking Overdraft-Protection Transfer from Savings
  ```

  Money Market and Checking have runtime stories that differ from generic deposit/withdrawal — found by checking whether "setup-only" entities appear at runtime.

- When the domain includes entities that **may or may not** have runtime behaviors, document the analysis in a **Passive vs Active Runtime Analysis** subsection of Consolidation Notes. For each entity type, state whether it is (a) static/configuration-only (no runtime story needed), (b) passively enforced at runtime (system filter — needs a runtime story), or (c) actively triggered at runtime (user action — needs a runtime story).

  **Example (pass):** An insurance platform's Consolidation Notes include:

  ```
  ## Passive vs Active Runtime Analysis
  - Deductible Amount → static (applied as number in claims calc; no runtime story)
  - Coverage Exclusion → passive filter (system checks every claim against list before processing)
    → runtime story: (S) System --> Check Claim Against Coverage Exclusions
  - Rider Benefit → active trigger (policyholder files separate rider claim)
    → runtime story: (S) Policyholder --> File Rider Benefit Claim
  - Premium Discount → static (applied at renewal calculation; no runtime story)
  ```

## Pitfall

Don't map only the **initiating side** of an interaction. After mapping all "forward" stories in a phase, re-scan the source for **reverse, compensating, defensive, supportive, and observational** actions in the same context — they often have distinct resolution mechanics.

**Example (fail):** An e-commerce platform maps only the forward purchase path:

```
(SE) Checkout
    (S) Customer --> Place Order
    (S) System --> Process Payment
    (S) System --> Reserve Inventory
```

But the source also describes `Issue Refund` (different gateway call), `Cancel Reservation` (releases held inventory, fires restock webhook), and `Apply Store Credit` (different tender type with balance-check logic). Three reverse/compensating actions missed.

**Example (fail):** A claims system maps only the forward claim-processing actions:

```
(SE) Process Insurance Claim
    (S) Adjuster --> Assess Property Damage
    (S) Adjuster --> Evaluate Medical Expenses
    (S) Adjuster --> Calculate Liability Payout
    (S) System --> Issue Settlement Payment
```

But the source in the same section describes: Subrogation Recovery (system initiates recovery from at-fault party's insurer, different negotiation workflow), Salvage Disposition (adjuster arranges sale of damaged property, auction mechanics), Fraud Referral (system flags anomalies, routes to special investigations unit with hold on payment), Reopened Claim (claimant submits new evidence, triggers re-adjudication with different authority thresholds). Four non-forward claim actions with distinct resolution paths were missed because the agent only analyzed the settlement side.

## DO NOT

- Write one generic story for a domain with 10+ entity types without comparing their mechanics.

  **Example (fail):** `(S) Operator --> Process Payment` as the only story for wire, ACH, card, cheque, BPAY, direct debit, real-time, and crypto — when wire requires correspondent-bank routing and card requires auth-capture-settle, the single story hides fundamentally different workflows.

- Assume entity names imply distinct stories when the mechanics are identical.

  **Example (fail):** Separate stories `(S) Operator --> Submit ACH Payment` and `(S) Operator --> Submit Direct Debit Payment` when both use the same batch-and-clear workflow with the same parameters, validations, and outcomes — duplicating without mechanical justification.

- Cover only one lifecycle phase (e.g., configuration) while leaving runtime or reporting as a gap.

  **Example (fail):** A wealth management map has stories for opening 12 account types but the `Context Gaps` section says "Transaction rules per account type — not yet mapped" when the source material describes IRA contribution limits, margin maintenance calls, and trust beneficiary distributions in detail.

**Source:** Engagement corrections log — root cause C; entries 3, 5, 6, 7, 8, 9, 15.
