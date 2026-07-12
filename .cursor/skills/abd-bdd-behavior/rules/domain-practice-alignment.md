---
rule: domain-practice-alignment
severity: warning
---
# Domain Practice Alignment

Every `describe` block in the hierarchy must correspond to either a sub-epic from the story map or a named concept from the domain language or domain model. Names must match exactly — do not abbreviate, paraphrase, or invent synonyms.

**Top-level describes** come from sub-epics in `story-map.md`. Use the sub-epic name verbatim.

**Nested describes** come from concepts in `domain-language.md` or `domain-model.md`. Use concept names verbatim.

**DO:** Use sub-epic and concept names from practice artifacts verbatim.

```
Place New Order              ← sub-epic from story-map.md
  Voucher                    ← concept from domain-language.md
    should apply a percentage discount to eligible items
```

**DO NOT:** Invent category names not present in any domain practice artifact.

```
Order Processing             ← invented grouping not in domain-language.md or story-map.md
  Stuff that happens
    should do the order thing
```

- Example (wrong): `Order Processing` — invented name, not in any domain practice artifact
- Example (correct): `Place New Order` — exact sub-epic from the story map; `Voucher` — exact concept from domain language

If a concept is missing from the domain language or domain model, surface it there first, then reference it here.
