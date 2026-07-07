# Story Map — Payment Rails

**Sources / context:** `interviews/payments-lead.md`

---

(E) Make Wire payment
    (E) Submit Wire payment
        (S) Treasurer --> Submit same-day Wire
        (S) Approver --> Approve pending Wire
    (E) Settle Wire payment
        (S) System --> Settle same-day Wire
        (S) Auditor --> Log Wire settlement
(E) Make ACH payment
    (E) Submit ACH payment
        (S) Treasurer --> Submit same-day ACH
        (S) Approver --> Approve pending ACH
    (E) Settle ACH payment
        (S) System --> Settle same-day ACH
        (S) Auditor --> Log ACH settlement

---

## Scope boundary

**In scope:** same-day Wire and ACH
**Out of scope:** international
