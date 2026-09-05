---
name: hierarchy-preservation
---

# Rule: Hierarchy Preservation

The signature file is a 1:1 translation of the scaffold. Every describe entry and every behavior entry in `*-hierarchy.txt` must appear in the signature file at the matching nesting depth. Nothing is added; nothing is removed; nesting depth is identical.

## DO

- Count the nesting levels in the scaffold and confirm the same count in the generated file.
- Translate every plain-English describe line to a `describe()` (or `with description`/`with context`) block.
- Translate every "should …" line to an `it()` block.
- When the scaffold has 4 levels, the signature has 4 levels.

```
Scaffold:                              Signature:
Character                              describe('Character', () => {
  that has been created                  describe('that has been created', () => {
    should have initial stats              it('should have initial stats', () => {
    should have zero wounds                  // BDD: SIGNATURE
                                           });
                                           it('should have zero wounds', () => {
                                             // BDD: SIGNATURE
                                           });
                                         });
                                       });
```

## DO NOT

- Collapse scaffold levels: "that has been created" disappears and behaviors move up.
- Skip scaffold entries because they seem duplicated or obvious.
- Add describe blocks, helpers, or `beforeEach` blocks not present in the scaffold.

**Example (pass):**
Scaffold has 3 nesting levels and 12 `it` entries. Signature has 3 nesting levels and 12 `it` blocks, each with `// BDD: SIGNATURE`. PASS.

**Example (fail):**
Scaffold has 12 `it` entries, signature has 10. Two entries were judged "redundant" and omitted. FAIL — the scaffold is the authority.
