# Brief — Treasury Same-Day Transfers

## Business context

A commercial bank offers a treasury cash-management product used by corporate customers. Corporate **Treasurers** initiate high-value transfers between their own accounts and to third parties. Same-day settlement is the priority feature: transfers submitted before the daily cutoff (15:00 ET) must settle same day; transfers after cut-off roll to next business day.

## Actors

- **Treasurer** — corporate employee authorised to initiate and approve transfers
- **Approver** — second Treasurer required for transfers over the dual-control threshold
- **Fraud Analyst** — internal reviewer that adjudicates flagged transfers

## In-scope capabilities (this release)

- Compose a transfer (source account, destination, amount, memo)
- Submit and approve transfers (single approval below threshold, dual above)
- View pending, approved, settled, and rejected transfers
- Cancel a pending transfer before it routes
- Route transfers into the daily settlement window (same-day vs next-day)
- Handle fraud-flag and human review outcomes (release / block)

## Out of scope this release

- Cross-currency conversion
- Foreign wires (SWIFT)
- Recurring / scheduled transfers
- Bulk file upload
- Chargebacks / disputes after settlement

## Constraints

- Same-day cutoff: 15:00 ET
- Dual-control threshold: 250,000 USD
- Daily per-customer limit: 5,000,000 USD
