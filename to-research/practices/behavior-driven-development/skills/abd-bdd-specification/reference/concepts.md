# Concepts — abd-bdd-specification

For shared BDD theory (what BDD is, the three phases, observable behavior, domain practice alignment) see `../../../reference/bdd-concepts.md`.

This file covers concepts specific to the signature phase.

---

## What a signature file is

A signature file is the code-structure equivalent of the behavior hierarchy. It translates every describe block and every `should` statement from the plain-English hierarchy into the framework syntax — `describe()` / `it()` blocks — with no logic inside them. Every `it` body contains exactly one marker comment and nothing else.

The signature file is reviewable code. Stakeholders confirm the structure still matches what was agreed. Developers confirm the nesting is correct for the framework. Nobody writes a test assertion yet.

---

## The BDD: SIGNATURE marker

Every `it` body in the signature phase contains exactly:

- Jest/TypeScript: `// BDD: SIGNATURE`
- Mamba/Python: `# BDD: SIGNATURE`

The marker has two jobs:
1. It signals to a reviewer that this test slot has not been implemented yet.
2. It makes unsigned tests scannable — a script can count `// BDD: SIGNATURE` occurrences and report how many remain before a file is considered done.

**Pass:**
```typescript
it('should apply a percentage discount to eligible items', () => {
  // BDD: SIGNATURE
});
```

**Fail — no marker:**
```typescript
it('should apply a percentage discount to eligible items', () => {
});
```

**Fail — has implementation:**
```typescript
it('should apply a percentage discount to eligible items', () => {
  const result = voucher.apply(order);
  expect(result.discount).toBe(0.1);
});
```

---

## Hierarchy preservation

The signature file is a 1:1 translation of the behavior hierarchy. Every level of nesting in the plain-English hierarchy must appear at the same depth in the signature file. Nothing is flattened, nothing is added.

If the hierarchy has four levels of nesting, the signature file has four levels of nesting. If a describe block in the hierarchy has three `should` leaves, the signature file has three `it` blocks under the matching `describe`.

This fidelity matters because the hierarchy was agreed with stakeholders. Changing the structure in the signature file changes what was agreed without surfacing that change for review.

---

## Framework syntax

| Construct | Jest (TypeScript) | Mamba (Python) |
|---|---|---|
| Top-level concept | `describe('Concept', () => {` | `with description('Concept'):` |
| Nested state/context | `describe('that has been created', () => {` | `with context('that has been created'):` |
| Behavior | `it('should have initial stats', () => {` | `with it('should have initial stats'):` |
| Signature marker | `// BDD: SIGNATURE` | `# BDD: SIGNATURE` |
| Body close | `});` | *(indentation only)* |

Do not mix Jest and Mamba syntax in the same file. Confirm the framework before writing the first line.
