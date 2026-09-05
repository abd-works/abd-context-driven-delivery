# Rule: Map sequential spine vs optional paths

The **spine** is the **minimum mandatory sequence** that delivers core value. **Optional** items are alternates (only one auth method needed), **enhancements** (customization after baseline works), and **non–happy-path** depth that can follow once the spine is marketable. Thin slicing **pulls from the spine first**; optional work lands in **later** increments or parallel tracks with clear markers.

## DO

- Sequence **mandatory** steps in order; mark **alternates** (e.g. OAuth vs password) as optional so you do not serialize independent choices.
- Treat **dashboard customization**, **sharing**, **extra reports** as enhancements **after** “user sees default dashboard” works.
- Treat **deep error/retry** paths as optional **relative to** the first marketable happy path—still implement them, but not always in increment 1.

## DON'T

- List **three login methods** as three sequential spine steps when **one** suffices for the slice.
- Elevate **nice-to-haves** to the same **mandatory** rank as “user can complete core task.”
- Forget **markers** (optional, alternate, enhancement) on the map or in metadata—reviewers cannot slice what they cannot distinguish.

```text
Spine: Enter credentials → Authenticate (one method) → View dashboard.
Optional: Social login, layout customization, export to PDF.
```
