---
fidelity: [discovery, exploration, specification, engineering]
artifact: [story-map, ac, scenario, test]
scanner: parallel-structure
kind: quality

---

# Rule: Parallel Structure Across Connected Domains

When the product has sibling domain areas that perform the same operations
(e.g. Wire, ACH, Check payments), their stories, AC, scenarios, and tests must
maintain parallel structure. Diverge only where behavior genuinely differs.

## DO

- Give sibling domains the same sub-epic structure and story shapes
- Use the same Given/When/Then skeleton for sibling scenarios — vary only the domain concept
- Parameterise with {Concept} and example tables instead of copy-pasting with hard-coded names
- Add extra scenarios only for real differences (e.g. intermediary bank required for Wire only)

## DON'T

- Give one domain a six-step specification and a sibling a three-step sketch for the same operation
- Duplicate steps with hard-coded names instead of shared structure + {Concept} tables
- Group by technology layer (one "validate all payments" epic mixing domains)

## At each fidelity

**Discovery — story map:**
```
(E) Make Wire Payment          (E) Make ACH Payment
    (S) Submit Wire Payment        (S) Submit ACH Payment
    (S) Validate Wire Payment      (S) Validate ACH Payment
    (S) Confirm Wire Settlement    (S) Confirm ACH Settlement
```

**Exploration — AC:**
Wire and ACH stories have the same AC depth and When/Then pattern.
Wire adds one extra AC for intermediary bank — that is the only divergence.

**Specification — scenarios:**
```
# Wire — parallel structure
Given {WirePayment} has {Recipient}
When {WirePayment} is submitted
Then {WirePayment} is routed to the wire rail

# ACH — same skeleton, different concept
Given {ACHPayment} has {Recipient}
When {ACHPayment} is submitted
Then {ACHPayment} is routed to the ACH rail
```

**Engineering — test classes:**
`TestSubmitWirePayment` and `TestSubmitACHPayment` have the same test method set.
Divergent behavior gets an extra test method only in the class that needs it.
