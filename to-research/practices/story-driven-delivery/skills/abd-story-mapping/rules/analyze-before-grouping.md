# Rule: Analyze before grouping

**Scanner:** Manual review

Before writing stories for a domain with multiple entity types (instrument types, account types, fulfilment methods, power types, notification channels, shipping methods), read the source description of **each** type and list: (a) what the user configures, (b) what the system validates or resolves, (c) what runtime lifecycle it has. Group stories by that analysis — not by category label, source heading, or shared name.

## DO

- For each entity type under a shared heading, document a brief **configuration / validation / lifecycle** summary before deciding whether to consolidate or split.

  **Example (pass):** Five "shipping methods" appear under one heading. Before writing stories the agent lists: ground (zone-based rate tables), overnight (cutoff-time validation + carrier API booking), LTL freight (freight-class calculation + BOL generation), ocean container (container-type selection + customs declaration), white-glove (scheduling windows + assembly instructions). The map shows five stories:

  ```
  (E) Configure Shipping Methods
      (S) Shipper --> Configure Zone-Based Ground Rates
      (S) Shipper --> Configure Overnight Cutoff and Carrier Booking
      (S) Shipper --> Calculate LTL Freight Class and Generate BOL
      (S) Shipper --> Select Ocean Container Type and File Customs Declaration
      (S) Shipper --> Schedule White-Glove Delivery Window
  ```

- When the analysis reveals identical workflows, consolidate per *Consolidate Superficial Stories*.

  **Example (pass):** Ground and economy-ground share the same zone-rate lookup and carrier selection — one parameterized story:

  ```
  (S) Shipper --> Configure Zone-Based Ground Rates (ground, economy-ground)
  ```

## DO NOT

- Group entities into one story because they share a heading or category name in the source.

  **Example (fail):** Seven integration types appear under "Integrations" in the source. The agent writes one story:

  ```
  (S) Admin --> Configure Integration (choose: CRM/ERP/email/SMS/webhook/SFTP/EDI)
  ```

  But CRM requires OAuth token exchange with field mapping, ERP needs batch-sync scheduling with conflict resolution, email requires SMTP relay configuration with SPF/DKIM setup, SMS requires carrier gateway registration with opt-in compliance, webhook needs endpoint URL with retry policy, SFTP needs key-pair provisioning with directory mapping, and EDI requires trading-partner agreement with document-type registration. The heading groups them; the mechanics don't.

- Skip the analysis step and group by intuition or label similarity.

  **Example (fail):** Five tax-withholding types appear under "Payroll Withholdings." The agent writes:

  ```
  (S) Payroll Admin --> Configure Withholding (choose: federal/state/local/FICA/garnishment)
  ```

  But federal uses progressive bracket tables updated annually, state varies by jurisdiction (some flat, some progressive, some zero), local requires city/county registration with reciprocity checks, FICA has wage-base caps with employer-match calculations, and garnishment requires court-order parsing with priority stacking rules — five different calculation and compliance workflows behind one label.

- Assume a generic "configure + set level" story covers an entity type whose configuration changes other derived attributes.

  **Example (fail):** Four employment types appear under "Employment." The agent writes:

  ```
  (S) HR --> Set Employment Type (full-time, contractor, seasonal, intern)
  ```

  But full-time triggers benefit-eligibility cascades (health, dental, 401k vesting), contractor triggers a different tax-withholding path (1099 vs W-2) and disables PTO accrual, and seasonal has fixed-term end-date logic with auto-termination. The generic story hides three different downstream configuration cascades. After analysis:

  ```
  (E) Onboard by Employment Type
      (S) HR --> Enroll Full-Time Benefits and Verify I-9
      (S) HR --> File Contractor W-9 and Link SOW
      (S) HR --> Set Seasonal End Date and Auto-Termination
      (S) HR --> Verify Intern University Agreement and Provision Time-Limited Access
  ```

**Source:** Engagement corrections log — entries 2, 3, 4, 5.
