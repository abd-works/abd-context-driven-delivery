# Rule: Apply quality trade-offs for a minimal spine

The **first** thin slices deliberately trade away polish so the **spine** stays small and **end-to-end**. Document what is manual, stubbed, hard-coded, or unvalidated in early increments; add automation, dynamic data, validation, and richer UX in **later** increments with **clear names** (e.g. “Manual …” → “Automated …”).

## DO

- Start with **manual** ops, **stubbed** integrations, or **hard-coded** data when that keeps a **full journey** testable sooner.
- Use **bare-bones** forms or flows in increment 1; add validation and UX depth later.
- Name increments so **quality level** is obvious—not “Phase 1 / Phase 2” or “Basic / Advanced” without saying *what* got better.

```text
Increment 1: Manual order confirmation — clerk records payment in spreadsheet; customer sees email from template.
Increment 2: Automated payment — same journey; gateway charges card; clerk step removed.
```

## DON'T

- Put **full** automation, dynamic pricing, validation, error handling, and polished UX all in the **first** increment “because we’re agile.”
- Organize increments as **horizontal layers** (all of “order entry,” then all of “payment”)—that delays end-to-end learning.
- Leave trade-offs **unspoken**—reviewers should see why the slice is thin.
