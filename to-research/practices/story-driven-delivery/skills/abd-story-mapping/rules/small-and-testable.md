---
scanner: small-and-testable
---

# Rule: Small and Testable

**Scanner:** `scanners/small-and-testable-scanner.py` — **`SmallAndTestableScanner`**

Stories must be **testable as complete interactions** and deliverable independently. Small enough to test, large enough to matter.

## DO

Each story must:
- Have clear acceptance criteria
- Be testable without parent context
- Represent a complete enough behavior to verify
- Be small enough to test quickly

**STORY vs STEP distinction:**

| Type | Definition | Example |
|------|-----------|---------|
| Story | User/system outcome — testable independently | `User --> save story graph` |
| Step | Implementation detail — part of parent test | `convert format`, `serialize to JSON`, `write file` |

Examples:
- Story: `User --> render diagram` → Steps (not separate stories): `generate XML`, `calculate positions`, `apply styles`

## DON'T

- Create stories too small to test meaningfully
- Turn implementation steps into stories

Implementation operation patterns that are **steps, not stories**:
- `Serialize`, `deserialize`, `convert`, `transform`, `format`
- `Calculate`, `compute`, `generate` (technical artifacts)
- `Apply`, `set`, `configure` (technical settings)
- `Save`, `write`, `store` (without user context)

Examples of wrong stories:
- ~~`Add order button`~~ (can't test without full order flow)
- ~~`Convert Diagram to StoryGraph Format`~~ (implementation step)
- ~~`Serialize Components to JSON`~~ (not testable alone)
- ~~`Calculate Component Positions`~~ (no user outcome)
