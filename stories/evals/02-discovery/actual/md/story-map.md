# Story Map — Treasury Same-Day Transfers

**Sources / context:** context/brief.md

---

(E) Move money
    (E) Compose transfer
        (S) Treasurer --> Draft transfer details
        (S) Treasurer --> Attach memo to transfer
        (S) Treasurer --> Validate destination account
        (S) Treasurer --> Review composed transfer
    (E) Approve transfer
        (S) Treasurer --> Submit transfer for approval
        (S) Approver --> Approve single-control transfer
        (S) Approver --> Approve dual-control transfer
        (S) Treasurer --> Cancel pending transfer
    (E) Route transfer
        (S) Treasurer --> Route transfer before cutoff
        (S) Treasurer --> Route transfer after cutoff
        (S) Fraud Analyst --> Release flagged transfer
        (S) Fraud Analyst --> Block flagged transfer
    (E) Track transfer
        (S) Treasurer --> View pending transfers
        (S) Treasurer --> View settled transfers
        (S) Treasurer --> View rejected transfers
        (S) Treasurer --> View blocked transfers

---

## Scope boundary

**In scope:** same-day USD transfers, dual-control approvals, fraud review outcomes
**Out of scope:** cross-currency, SWIFT wires, recurring transfers, bulk upload, chargebacks
