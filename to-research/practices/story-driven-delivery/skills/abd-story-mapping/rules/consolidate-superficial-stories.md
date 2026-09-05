# Rule: Consolidate Superficial Stories

**Scanner:** Manual review (policy; pairs with *Review and Expand Stories* — see below)


Consolidate stories that differ **only superficially** (same logic, different data values or enumeration). Combine into **one parameterized story** where it applies.

**Relationship to other rules:** This rule removes **data-value duplication** (same behavior, different inputs). *Review and Expand Stories* splits by **component behavior**. Apply **consolidation first**, then expansion if you still need component-level depth.

## DO

- Merge stories that share the same validation logic but differ only by the value validated (e.g. six address fields → one **`Validate Address Field (street, city, …)`** story).
- Merge stories that share the same calculation but differ only by attribute (e.g. multiple “calculate X tax” → **`Calculate Tax Withholdings`**).
- Merge the same operation across entity types when only the type differs (e.g. create customer / vendor / partner → **`Create Business Entity (types…)`**).

## DON'T

- Enumerate every permutation when logic is identical and only data changes — use one parameterized story (e.g. one **`Validate Input Format`** for email, phone, postal code).
- Split by data value when business rules are the same (e.g. separate add-book / add-electronics / add-clothing → **`Add Product`**).
- One story per status when the **workflow pattern** is the same — prefer one **`Update Order Status`** story with allowed values.
- Consolidate without leaving a trail. Parenthetical hints like `(type A, type B, type C)` inside story text are insufficient for downstream work — the AC author needs to know which variants have different validation, parameters, or outcomes.

  **Example (fail):** The story map contains only:

  ```
  (S) HR --> Onboard New Hire (full-time, contractor, intern)
  ```

  The parenthetical hint is all that remains. But full-time requires benefits enrollment + I-9 verification, contractor requires W-9 + SOW linkage + rate-card approval, and intern requires university-agreement check + duration-limited access provisioning. No Consolidation Notes document these differences — the AC author has no idea what to specify per variant.

## Consolidation Notes requirement

When consolidating stories, add a **`## Consolidation Notes (for AC phase)`** section at the end of the story map listing: (a) each consolidation, (b) which source mechanics it groups, (c) what the AC phase must specify per variant.

**Example (pass):** The story map ends with:

```
## Consolidation Notes (for AC phase)

### Onboard New Hire (full-time, contractor, intern)
Groups three onboarding workflows into one parameterized story.
AC must specify per variant:
- Full-time: benefits enrollment (health, dental, 401k), I-9 verification
- Contractor: W-9 filing, SOW linkage, rate-card approval
- Intern: university-agreement check, duration-limited access provisioning

### Apply Discount (loyalty, volume, seasonal, promo-code)
Groups four discount types that share the same "apply percentage reduction to line total" pattern.
AC must specify per variant:
- Loyalty: tier-based percentage, requires active membership
- Volume: threshold quantity triggers, stacking rules with other discounts
- Seasonal: date-range validity, auto-expire at period end
- Promo-code: single-use vs multi-use, redemption-limit enforcement
```
