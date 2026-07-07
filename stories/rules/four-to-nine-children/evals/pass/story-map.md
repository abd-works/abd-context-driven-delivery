# Story Map — Cash Management

**Sources / context:** `interviews/treasurer-workflow.md`

---

(E) Move money
    (E) Submit payment
        (S) Treasurer --> Submit same-day transfer
        (S) Treasurer --> Submit next-day transfer
        (S) Approver --> Approve pending transfer
        (S) Treasurer --> Cancel pending transfer
    (E) Route payment
        (S) System --> Route to same-day rail
        (S) System --> Route to next-day rail
        (S) System --> Reject over-limit transfer
        (S) System --> Notify treasurer of route
    (E) Settle payment
        (S) System --> Settle same-day transfer
        (S) System --> Settle next-day transfer
        (S) System --> Retry failed settlement
        (S) Auditor --> Log settlement event
    (E) Reconcile payment
        (S) System --> Match settled transfer
        (S) System --> Flag unmatched transfer
        (S) Auditor --> Approve reconciled batch
        (S) Auditor --> Log reconciliation event

---

## Scope boundary

**In scope:** same-day and next-day domestic transfers
**Out of scope:** cross-currency, ACH batching
