# Input traps — abd-thin-slicing

Assumptions, ambiguities, and missing context that commonly produce bad thin-slicing plans. Check each trap against available input before generating — flag gaps honestly; do not batch stories to hide uncertainty.

- **Spine vs optional** — which stories must be delivered together to show an end-to-end path, and which can follow later without blocking value?
- **Vertical not horizontal** — are you slicing by user-visible capability, or by technical layer — and would a stakeholder recognise your increment names?
- **Value assumption** — what makes you believe this increment is the smallest useful thing, rather than a comfortable batch?
- **Dependency trap** — which cross-epic dependencies are you hiding inside an increment instead of making them visible?
- **Ordering rationale** — why does increment N come before increment N+1 — is it risk, learning, or just the order you thought of them?
