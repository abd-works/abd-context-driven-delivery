# Rule: Verify Assertions Against Implementation When Reverse-Engineering

When writing E2E tests for an **existing system** (reverse-engineering mode), the application is already built. The code is truth. Assertions must describe what the system **does**, not what the specification **hoped** it would do.

See [`../../../reference/new-vs-existing-system.md`](../../../reference/new-vs-existing-system.md) for the shared discipline across all SDD skills. This rule applies that discipline specifically to E2E test assertions.

## DO

- **Read the extracted ARIA snapshot** (`aria.yaml`) for the page/modal under test BEFORE writing `then_*` assertions. The snapshot shows exact labels, placeholder text, button names, and component states as they actually render.

- **Read the controller's `@HttpCode()` decorator** (or route handler return) before asserting HTTP status codes. NestJS defaults to 200 for non-POST and 201 for POST — but decorators override this.

- **Check form validation behaviour in the component code** before assuming how it rejects invalid input. Does it show an inline error? Disable the button? Clamp the value? Reject on submit? These are implementation decisions already made.

- **Use screenshots from the extraction** when the ARIA snapshot is ambiguous. If you need to know what "unlimited" looks like on screen, the screenshot shows it (e.g. `∞` symbol vs the word "Unlimited").

```typescript
// CORRECT — assertion matches what the extraction showed
// aria.yaml shows placeholder "Unlimited" on the input, but the
// CLEARED state renders ∞ in the detail view (verified via screenshot)
await expect(page.getByText('∞')).toBeVisible()

// CORRECT — checked the controller: @HttpCode(200) on POST /redeem
expect(response.status()).toBe(200)
```

- **When spec and implementation disagree, correct the spec** — add a DO/DO NOT to the strategy or update `specification-by-example.md`. Do not silently adjust the test and leave the spec wrong.

## DON'T

- **Don't write assertions from acceptance criteria alone** when the system already exists:

```typescript
// WRONG — spec said "shows validation error" but UI actually clamps the value at 100
await thenFieldErrorContains(page, 'cannot exceed 100')
// The UI never shows this error — DiscountValueInput caps at Math.min(value, 100)

// CORRECT — verify what the component actually does
await expect(dialog.getByLabel('Discount Value')).toHaveValue('100')
```

- **Don't assume HTTP status codes** — check the decorator:

```typescript
// WRONG — assumed POST = 201, but controller has @HttpCode(200)
expect(response.status()).toBe(201)
```

- **Don't guess UI labels** — read the ARIA snapshot:

```typescript
// WRONG — assumed "Save" button but ARIA shows "Generate" on the Bulk tab
await dialog.getByRole('button', { name: 'Save' }).click()

// CORRECT — ARIA snapshot for 05b shows tab "Bulk" with button "Generate"
await dialog.getByRole('button', { name: /^(Save|Generate)$/ }).click()
```

## Evidence sources (check in this order)

1. **`docs/extracted-context/from-application/pages/<step>/aria.yaml`** — ARIA tree snapshot showing exact roles, names, states, placeholders
2. **`docs/extracted-context/from-application/pages/<step>/screenshot.png`** — Visual rendering for ambiguous cases
3. **`docs/extracted-context/from-application/extraction-overview.md`** — Page inventory with URLs and domain/UX focus
4. **Component source code** (`apps/web/src/features/...`) — For validation logic, clamping, conditional rendering
5. **Controller decorators** (`apps/api/src/.../controller.ts`) — For `@HttpCode()`, `@Post()`, response shape
6. **Contract schemas** (`packages/contracts/src/...`) — For regex patterns, min/max, allowed values

## When to apply

Ask yourself: **does this system already exist?** If `docs/extracted-context/` has ARIA snapshots and screenshots for the page you're testing, you are in reverse-engineering mode. The extraction is your source of truth for observable behaviour — not the acceptance criteria.

If the extraction is missing or incomplete for a specific page, run a quick Playwright exploration (`page.goto(url)` → `page.accessibility.snapshot()` or `page.screenshot()`) before writing assertions.
