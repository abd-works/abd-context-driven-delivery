---
name: signature-markers
scanner: javascript/signature_markers_scanner.py
severity: error
---

# Rule: Signature Markers

Every `it` body in the signature phase contains exactly one comment: `// BDD: SIGNATURE` (Jest) or `# BDD: SIGNATURE` (Mamba). No other content. The marker makes unsigned tests scannable and prevents partial implementations from passing undetected.

## DO

- Place the signature marker as the sole statement in every `it` body.
- Use the exact marker string for the active framework: `// BDD: SIGNATURE` or `# BDD: SIGNATURE`.

```typescript
it('should have initial stats assigned', () => {
  // BDD: SIGNATURE
});
```

```python
with it('should have initial stats assigned'):
    # BDD: SIGNATURE
```

## DO NOT

- Leave the body empty (invisible — cannot be scanned).
- Add any code, comment, or assertion alongside the marker.
- Use an alternate marker string ("TODO", "pending", "stub", etc.).

```typescript
// Empty body — invisible to signature scanner
it('should have initial stats assigned', () => {
});

// Implementation present — wrong phase
it('should have initial stats assigned', () => {
  // BDD: SIGNATURE
  const character = new Character(); // Leaking implementation
});
```

**Example (pass):**
Every `it` block in the file contains exactly and only `// BDD: SIGNATURE`. Grep for `// BDD: SIGNATURE` returns the same count as grep for `it(`. PASS.

**Example (fail):**
Any `it` block with an empty body, or with code alongside the marker. FAIL.
