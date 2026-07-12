# Story Map — Treasury Same-Day Transfers

**Sources / context:** context/brief.md

---

(E) Move money
    * approx 22-27 total stories
    (E) Compose transfer
        (S) Treasurer --> Draft transfer details
        * approx 2-3 more stories (various transfer detail entry and validation)
    (E) Approve transfer
        * approx 4-6 more stories (review, approve, reject, etc)
    (E) Route transfer
        (S) Treasurer --> Route transfer before cutoff
        (S) Treasurer --> Route transfer after cutoff
        * approx 2-3 more stories (eg fraud routing)
    (E) Track transfer
        * approx 2-3 more stories (view transfer statuses, pending, settled, rejected, etc)

---

## Scope boundary

**In scope:** same-day USD transfers, dual-control approvals, fraud review outcomes
**Out of scope:** cross-currency, SWIFT wires, recurring transfers, bulk upload, chargebacks
