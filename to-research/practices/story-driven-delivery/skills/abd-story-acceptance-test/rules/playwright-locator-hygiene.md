---
scanner: playwright_locator_anti_patterns_scanner.py
---

# Rule: Playwright Locator Hygiene

When writing E2E tests with Playwright, use only Playwright-native APIs and wait strategies. Do not import conventions from other testing libraries (Testing Library, jQuery, Cypress) — they silently fail or produce flaky tests.

## DO

- **Wait for a specific UI element** that proves the page is interactive, not a generic load event:

```typescript
export async function givenCampaignListPage(page: Page) {
  await page.goto('/campaigns')
  await page.getByRole('button', { name: 'New Campaign' }).waitFor()
}
```

- **Use `.filter({ hasText })` or scope to the correct parent** when narrowing results:

```typescript
const dialog = page.getByRole('dialog')
const error = dialog.locator('[role=alert], p').filter({ hasText: /already exists/i }).first()
await expect(error).toBeVisible()
```

- **Use `.first()` when multiple matches are acceptable** (e.g. same-named rows from previous runs) and you only need one:

```typescript
await expect(page.getByRole('cell', { name: 'E2E-KEY' }).first()).toBeVisible()
```

- **Read the form schema** (`@project/contracts` or equivalent) before choosing test input values. Regex patterns, min/max constraints, and allowed characters are defined there — not in the UI labels.

## DON'T

- **Never use `waitForLoadState('networkidle')`** — it is timing-dependent, breaks under parallel workers, and does not prove the page is ready for user interaction:

```typescript
// WRONG — flaky under load; doesn't guarantee interactive state
await page.goto('/campaigns')
await page.waitForLoadState('networkidle')

// CORRECT — waits for the element the user would look for
await page.goto('/campaigns')
await page.getByRole('button', { name: 'New Campaign' }).waitFor()
```

- **Never use `:visible` as a CSS selector** — it is not a valid CSS pseudo-class. It is a jQuery/Testing Library concept. Playwright either silently ignores it or matches incorrectly:

```typescript
// WRONG — :visible is not CSS; Playwright handles it unpredictably
await dialog.locator('[role="tabpanel"]:visible').getByLabel('Name').fill('x')

// CORRECT — use the data attribute the component actually renders
await dialog.locator('[data-state="active"][role="tabpanel"]').getByLabel('Name').fill('x')
```

- **Never use `page.getByDisplayValue()`** — that is a Testing Library method, not a Playwright API. It does not exist on `Page`:

```typescript
// WRONG — Testing Library API; throws TypeError at runtime
await page.getByDisplayValue(/vk_/)

// CORRECT — use waitForFunction to inspect input.value
await page.waitForFunction(() =>
  [...document.querySelectorAll('input')].some(i => i.value.startsWith('vk_'))
)
```

- **Never fill fields behind inactive tabs or panels without scoping** — the DOM may contain hidden duplicates:

```typescript
// WRONG — matches both the Single and Bulk tab's Discount Value input
await dialog.getByLabel('Discount Value').fill('10')

// CORRECT — scope to the active panel first
await dialog.locator('[data-state="active"][role="tabpanel"]').getByLabel('Discount Value').fill('10')
```

## Quick reference

| Anti-pattern | Fix |
|---|---|
| `waitForLoadState('networkidle')` | `.waitFor()` on a specific element |
| `:visible` in CSS selector | `[data-state="active"]` or `.filter(...)` |
| `page.getByDisplayValue(...)` | `page.waitForFunction(...)` inspecting `input.value` |
| Unscoped label in tabbed UI | Scope to `[data-state="active"][role="tabpanel"]` |
| Bare `getByRole(...)` on accumulating data | Add `.first()` or clean data in setup |
