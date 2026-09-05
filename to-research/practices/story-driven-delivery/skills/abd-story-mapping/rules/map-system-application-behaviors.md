# Rule: Map system and application behaviors

**Scanner:** Manual review

Map system behaviors that actors (human or system) depend on: state persistence and versioning, session lifecycle (start/end with state carry-forward), event logging and audit trail, data synchronization, role-based overrides, and template management for repeatable workflows. These are product behaviors, not implementation details — they belong on the story map when any actor (user **or** system) observes or depends on them.

This rule applies to **every** product — not only interactive or user-facing applications. System-to-system integrations, batch pipelines, and back-office platforms all have persistence, lifecycle, logging, and sync behaviors that are observable by the systems and operators that depend on them.

## DO

- After mapping domain workflows, add an epic or sub-epic for **application lifecycle behaviors**: persistence and versioning of domain data, event logging and audit trail, session or process start/end with state carry-forward, data sync between components or connected systems, and role-based or privilege-based overrides.

  **Example (pass):** A telemedicine platform maps clinical workflows, then adds application lifecycle stories:

  ```
  (E) Manage Visit Lifecycle
      (SE) Persist Visit Data
          (S) System --> Store Visit Recording with HIPAA Retention Policy
          (S) System --> Version Clinical Notes per Edit
      (SE) Log Clinical Decisions
          (S) System --> Log Clinical Decision to Audit Trail
      (SE) End Visit
          (S) System --> End Visit and Carry Forward Diagnoses to Patient Chart
          (S) System --> Push Real-Time Vitals to Provider Dashboard
  ```

- When actors repeat a workflow with variations, map **template management** behaviors: clone from existing, save as reusable template, load from template, customize clone independently of original.

  **Example (pass):** A restaurant platform maps menu creation, then adds reuse stories:

  ```
  (SE) Manage Menu Templates
      (S) Manager --> Clone Menu for New Season
      (S) Manager --> Save Menu as Reusable Template
      (S) Manager --> Load Menu from Template
      (S) Manager --> Customize Cloned Item Without Affecting Original
  ```

- For system-to-system products, map behaviors that downstream systems depend on: guaranteed delivery, retry/dead-letter handling, schema versioning, health signalling, and contract enforcement.

  **Example (pass):** A payment-gateway integration maps transaction processing, then adds integration-contract stories:

  ```
  (E) Manage Gateway Integration
      (S) System --> Publish Settlement Event to Downstream Ledger
      (S) System --> Route Failed Message to Dead-Letter Queue
      (S) System --> Version API Contract for Consumer Compatibility
      (S) System --> Report Gateway Health Status
  ```

## DO NOT

- Treat persistence, logging, sync, or session management as "implementation details" that belong only in engineering. If any actor — human or system — will observe versioned data, event history, live updates, or process state, these are product behaviors.

  **Example (fail):** A loan-origination platform maps business workflows only:

  ```
  (E) Originate Loan
      (SE) Evaluate Application
          (S) Underwriter --> Review Applicant Credit Report
          (S) System --> Calculate Debt-to-Income Ratio
          ...
  ```

  No stories for application-state versioning, underwriting-decision audit logging, application closing with document carry-forward to servicing, real-time status sync to borrower portal, or supervisor override of automated decline. The map covers business rules but not the system behaviors that host them.

- Omit system-to-system behaviors because "no human sees them." If a downstream system depends on the behavior, it belongs on the map.

  **Example (fail):** An order-fulfilment pipeline maps only the forward path:

  ```
  (E) Fulfil Order
      (S) System --> Validate Order
      (S) System --> Charge Payment
      (S) System --> Ship Order
  ```

  Missing: `(S) System --> Publish Order Event to Warehouse System`, `(S) System --> Retry Failed Warehouse Acknowledgement`, `(S) System --> Reconcile Shipping Confirmation` — three behaviors the warehouse system depends on.

**Source:** Engagement corrections log — entries 10, 11.
