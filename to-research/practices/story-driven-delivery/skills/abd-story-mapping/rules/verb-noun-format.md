---
scanner: verb-noun-format
---

# Rule: Verb–Noun Format

**Scanner:** `scanners/verb-noun-format-scanner.py` — **`VerbNounFormatScanner`**


Use verb–noun format at every level. Document the actor separately (e.g. `story_type`, metadata)—**not** in the name. Prefer **base verb forms** (imperative / infinitive style: `Place Order`, `Select Items`), not gerunds (`Placing Order`) or third-person singular (`Places` / `Selects` as the *wrong* pattern when the rule asks for base form—see examples below).

## DO

- **Format:** `verb` + `noun` [optional qualifiers]. Actor is separate. Use specific objects and context. Focus on what can be *done*, not what things *are*.

| Level | Examples (from rule) |
|--------|----------------------|
| Epic | `Manage Customer Orders`, `Process Online Payments` |
| Sub-Epic | `Place New Order`, `Validate Credit Card Payment` |
| Story (action phrasing) | `Process Order Payment`, `Validate Submitted Payments` — tie to lifecycle: Load → Read → Edit → Render → Synchronize → Search → Save |
| Story (system examples) | `Load Order Data`, `Validate Payment`, `Generate XML` |
| With actor (actor not in name) | `Place Order` (actor: Customer), `Validate Payment` (actor: System), `Update Stock` (actor: Inventory Manager) |
| Base verb form | `Select Items`, `Group Shipments`, `Process Payment` — not `Selects Items`, not `Selecting Items` |

## DON'T

- **Actor in the name:** e.g. not `Customer Places Order` → use `Place Order` and set actor in metadata. Same for `OrderProcessor Validates Payment` → `Validate Payment`; `Cart Adds Product` → `Add Product`.

- **Too generic or noun-only:** e.g. `Process Payment` without context when specificity is needed; `Payment Processing` (noun-only); `Order Management` (capability, not a concrete action); `Selects Items` (wrong verb form for this rule → `Select Items`).

- **Capability / structure phrasing instead of actions:** e.g. `PaymentValidator Contains Validation Logic`, `Cart Hierarchy Foundation`, `Product Represents Item`.

- **Transforming “capability” into action (examples from rule):** `Contains Logic` → e.g. `Generate XML`, `Render Diagram`; `Tracks Count` → `Read Count`, `Update Count`; `Represents X` → `Create X`, `Load X`.
