---
name: no-remaining-signatures
scanner: javascript/no_remaining_signatures_scanner.py
severity: error
---

# No Remaining Signatures

A completed BDD test file must contain no `// BDD: SIGNATURE` markers. A marker left in place means the RED phase is incomplete — the test body was never implemented and the test will never run real assertions.

**DO:** Replace every signature marker with a real Arrange-Act-Assert body before committing.

```typescript
it('should apply the discount to eligible items', () => {
  const order = givenAnOrderWith([eligibleItem(100)]);
  const result = whenVoucherApplied(order, tenPercentVoucher());
  thenDiscountedTotalIs(result, 90);
});
```

**DO NOT:** Leave the signature marker in a file that has any other implementation present.

```typescript
it('should apply the discount to eligible items', () => {
  // BDD: SIGNATURE
});
```

- Example (wrong): `// BDD: SIGNATURE` present alongside implemented tests
- Example (correct): Every `it()` body has real assertions; no markers remain
