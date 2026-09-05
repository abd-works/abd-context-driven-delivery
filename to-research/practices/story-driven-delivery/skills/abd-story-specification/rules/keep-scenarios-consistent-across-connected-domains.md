# Rule: Keep scenarios consistent across connected domains

At small scale, one scenario can cover closely related behaviors. As domains grow, prefer **parallel** scenario shapes for parallel concepts (same step count and pattern, different **{Concept}**), diverging only where behavior genuinely differs. That keeps comparisons fair and reviews fast.

## DO

- Reuse the same **Given / When / Then** skeleton for sibling concepts (e.g. **{WirePayment}** vs **{ACHPayment}**) when the business flow matches.
- Add **extra** scenarios only for real differences (e.g. intermediary bank required for wire only).
- Parameterize with **{Concept}** and tables instead of copy-pasting eight steps with only the product name changed.

``# Wire
Given {WirePayment} has {Recipient}
When {WirePayment} is submitted
Then {WirePayment} is routed to the wire rail

# ACH — parallel structure
Given {ACHPayment} has {Recipient}
When {ACHPayment} is submitted
Then {ACHPayment} is routed to the ACH rail
``
## DON'T

- Give one rail a six-step specification and a sibling rail a three-step soup for the “same” operation without justification.
- Fork scenarios by duplicating hard-coded values instead of shared structure + **{Concept}** tables.
