# Rule: Source-supported mechanics mapped not listed as deferred gaps

**Scanner:** Manual review

The story map in **`story-map.md`** / **`story-map.txt`** reflects what the **available source material** already explains about workflows, entity types, and system behaviors: those mechanics appear as stories, sub-epics, or brief inline notes—not only as a **Context Gaps** bullet that says "not yet mapped" or equivalent. Failure is a gap or deferred phrase where the source already describes the mechanic in enough detail to break it into behaviors today.

## DO

- After reading the source, map **mechanics the source already describes** into the tree (split or consolidate per other rules) instead of parking them in **Context Gaps** as unfinished analysis.

  **Example (pass):** The source defines wire vs card clearing (routing vs auth-capture-settle). The map has `(S) Operator --> Initiate Wire Transfer` and `(S) Operator --> Submit Card Payment`; **Context Gaps** has no line "Payment clearing mechanics — not yet mapped."

- Use **Context Gaps** only when information is **actually missing** from source and stakeholders (aligned with **Context gaps are genuinely missing information**).

  **Example (pass):** Source covers domestic wires only. Gap: "Cross-border settlement currency — not specified in source; need product decision."

- When the source describes a **distinct action type** that consumes a resource (time, action, turn, API call, dispatch slot) **differently** from the default action, map it as a separate story even if the actor is the same.

  **Example (pass):** A warehouse system's source describes `Direct Robot to Zone` as a supervisor action consuming a limited "dispatch slot." The map includes it alongside picking:

  ```
  (SE) Execute Warehouse Operations
      (S) Picker --> Pick Item from Bin
      (S) Picker --> Pack Order for Shipment
      (S) Supervisor --> Direct Robot to Zone
      (S) System --> Ship Order
  ```

  `Direct Robot to Zone` is a separate story — different actor (Supervisor, not Picker), different resource (dispatch slot, not pick time), different validation (zone-capacity + robot-availability).

- **Verification pass after drafting:** Re-read each source section's action/command list and confirm every named action appears as a story or is explicitly documented as consolidated into another story.

  **Example (pass):** The source's "Order Fulfilment Actions" section lists: Pick, Pack, Ship, Hold, Split, Cancel, Return, Redirect. After drafting, the agent confirms each named action has a story or a consolidation note. `Redirect` was missing — added `(S) Customer --> Redirect In-Transit Shipment to Alternate Address` under Manage Shipments.

## DO NOT

- Record a map-level or inline gap that says an area is "not yet mapped" or "TBD" when the source material already spells out that workflow in enough detail to write stories.

  **Example (fail):** **Context Gaps** includes "Transaction rules per account type — not yet mapped" while the source documents IRA contribution limits, margin maintenance calls, and trust distributions in detail—the stories belong on the map, not as a deferral.

- Treat **Context Gaps** as a staging area for analysis you have not performed on **available** source text.

  **Example (fail):** Ten instrument types appear in the domain spec, but the map has only `(S) Operator --> Process Payment` and a gap listing "Break out instrument-specific flows — later" although the spec already distinguishes wire, card, and ACH mechanics.

- Map only the **named or labeled** actions from the source while ignoring the generic resolution mechanic that underlies them. If the source describes a general-purpose resolution path (e.g., "any skill check," "any API call," "any form submission") that specific named actions are special cases of, the general path needs its own story.

  **Example (fail):** A project-management tool maps only the named review actions:

  ```
  (SE) Review Artifacts
      (S) Reviewer --> Approve Budget
      (S) Reviewer --> Reject Change Request
      (S) Manager --> Escalate Risk
  ```

  But the source also describes a general `Resolve Review` action — any artifact can be submitted for review with a configurable checklist, and the reviewer can approve/reject/request-changes. The general resolution mechanic `(S) Reviewer --> Resolve Review with Checklist` is missing — the named actions are special cases of it.

**Source:** Engagement corrections log — map deferred instead of using available source; entries 12, 13.
