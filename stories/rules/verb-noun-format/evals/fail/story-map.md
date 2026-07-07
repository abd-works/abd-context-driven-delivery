# Story Map — Cash Management

**Sources / context:** `interviews/treasurer-workflow.md`

---

(E) Move money
    (E) Submit payment
        (S) Treasurer --> Submitting same-day transfer
        (S) Treasurer --> Submit next-day transfer
        (S) Approver --> Approve pending transfer
    (E) Cancel payment
        (S) Treasurer --> Cancel pending transfer
        (S) Auditor --> Log cancellation event

---

## Scope boundary

**In scope:** same-day and next-day domestic transfers
**Out of scope:** cross-currency
