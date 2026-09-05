---
scanner: test_isolation_scanner.py
---

# Rule: Use Thorough E2E Tests

End-to-end tests are **mandatory** for every sub-epic. E2E tests must reuse the base helper class (not be manually written from scratch), verify **logic** (filtering, eligibility, domain rules) not just element presence, and be executed as a final verification step after implementation. E2E tests exercise the same Gherkin scenarios as server and client tests, but through the complete user workflow: browser → React → HTTP → Express → MongoDB → response → rendered UI.

## E2E Spec Files Existing ≠ E2E Tests Passing

**Generating `*_e2e.spec.ts` files is not the same as having passing E2E tests.** This is a critical distinction.

- `npx playwright test --list` succeeds as long as the spec files compile. It does **not** run the tests.
- `npx vitest run` never runs `*_e2e.spec.ts` files — the Vitest `include` pattern explicitly excludes them. Reporting "all tests pass" after `vitest run` says nothing about E2E.
- E2E tests only pass when a real browser navigates to real page routes served by a live frontend.

**E2E tests require both composition roots to exist and be reachable:**

- `packages/app-server/` — Express entry point that mounts domain API routes
- `packages/app-client/` — React/Vite shell that serves page routes (`/products/:sku`, `/store-locator`, `/admin/...`)

Without `app-client`, navigating to any page route returns `Cannot GET /<route>` — because Express API routes (`/api/...`) are not the same as frontend page routes. The browser has nothing to render. **Every E2E test fails.**

Do **not** tell the user they can run `npx playwright test` until both composition roots exist, are wired to the new module, and are declared in `playwright.config.ts` `webServer`. Running Playwright against a missing frontend produces `Cannot GET` on every test — this is a broken state, not a partial one.

**The complete generation order before E2E tests can pass:**
1. Domain packages (`shared/`, `server/`, `client/`) ← domain module template
2. `packages/app-server/` — scaffold if missing, otherwise mount new domain routes
3. `packages/app-client/` — scaffold if missing, otherwise add page routes for the new domain's views
4. `playwright.config.ts` with `webServer` entries for **both** the API server and the React frontend
5. Run `npx playwright test` — only now can tests actually pass

## DO

- Create `*_e2e.spec.ts` for every lowest sub-epic.
- Extend the base helper class for E2E-specific setup (Playwright page, browser context).
- Assert on **domain logic outcomes**: filtered lists exclude ineligible items, tooltips show remaining time, selected recipients persist across navigation.
- Run E2E tests after implementation as final verification.
- Test the same scenarios as server/client tiers, with complete workflow emphasis.
- Include edge cases and domain variants, not just the happy path.
- Ensure both `app-server/` and `app-client/` composition roots exist and expose the new module before attempting to run E2E tests. Scaffold missing roots; otherwise update the existing shells and then start the dev server.
- Navigate to `/` (or the correct root route) — only navigate to a sub-route if a router exists that handles it.
- Scope all locators to the specific card/section under test: `page.locator('.card', { hasText: 'Name' })` to prevent strict mode violations when multiple matching elements exist.
- Assert on locator text content after state changes, not on the original element reference — React re-renders replace DOM nodes.
- Seed all required test data within each test via API calls or UI interactions — never rely on pre-existing data in the database.
- Implement both the UI affordance and the test that exercises it together — neither should be left incomplete.
- Use unique names per test run (e.g. append `Date.now()`) to prevent collisions with leftover data from previous runs.
- **Match E2E interactions to the actual UI controls.** If the UI uses a button + dropdown to move items, the E2E helper must click that button and select from the dropdown — not use `dragTo()` or other interactions the UI doesn't support.
- **Wait for async results after mutations.** After clicking "Save" or "Submit", wait for the resulting view to render (e.g., `await heading.waitFor({ state: 'visible' })`) before proceeding to the next step.
- **Handle view state transitions in helpers.** If a "When" step needs the list view but the app is showing a detail view, navigate back first. Check current view state before acting.

```typescript
// select-recipient_e2e.spec.ts — CORRECT: reuses helper, verifies logic
import { test, expect } from '@playwright/test';
import { SelectRecipientE2EHelper } from './helpers/select-recipient.e2e';

test.describe('View Active Recipients', () => {
  const helper = new SelectRecipientE2EHelper();

  test.beforeEach(async ({ page }) => {
    await helper.setup(page);
  });

  test('user views list of active recipients when initiating wire payment', async () => {
    await helper.givenEnterpriseHasRecipientsWithActiveStatus();
    await helper.whenUserInitiatesWirePayment();
    await helper.thenOnlyActiveRecipientsDisplayed();
    await helper.thenPendingRecipientsAreExcluded();  // verifies logic, not just count
  });

  test('user cannot select pending recipient (MX country variance)', async () => {
    await helper.givenCountryIsMX();
    await helper.givenRecipientCreated15MinutesAgo();
    await helper.whenUserViewsRecipientList();
    await helper.thenRecipientIsNotSelectable();
    await helper.thenTooltipShowsRemainingTime('15 minutes');  // verifies domain logic
  });
});
```

## DON'T

- Skip E2E tests for any sub-epic.
- Write E2E tests that only check element presence without verifying logic.
- Write E2E tests from scratch without reusing the helper class.
- Forget to run E2E tests after implementation.
- Test only the happy path — include edge cases and domain variants.
- Tell the user they can run `npx playwright test` before the required composition roots exist and expose the new module — E2E tests require a live server.
- Claim E2E tests are passing or complete because `*_e2e.spec.ts` files compile, or because `npx playwright test --list` succeeds, or because `npx vitest run` passes. **None of these run E2E tests against a real browser.** E2E tests pass only when Playwright navigates a real browser to real page routes served by a live `app-client` frontend.
- Generate duplicate composition roots for an existing project when compatible `app-server/` and `app-client/` shells already exist.
- Navigate to non-existent routes — if the app has no router, navigate to `/`, not `/todo-lists`.
- Use unscoped locators when multiple elements may match — always scope assertions to a specific card/section using `page.locator('.card', { hasText: 'Specific Name' })`.
- **Use `getByText()` without scoping when the text appears in both a parent container and a child element.** A parent `<div>` containing multiple column names will also match `getByText('Released')`. Scope to the specific element class: `page.locator('.column-tag', { hasText: 'Released' })`.
- Assert on stale element references after state changes — React re-renders replace DOM nodes; assert on the new state via locator text content instead.
- Assume pre-seeded data exists — E2E tests must create their own data via API calls or the UI.
- Leave placeholder or skeleton tests for UI that doesn't exist yet — every E2E scenario must be fully implemented end-to-end: the UI affordance and the test that exercises it must both be complete before moving on. Write them in any order (test-first or component-first), but never leave one without the other.
- Use hardcoded names that may collide with leftover data — use unique names (e.g. append `Date.now()`) so tests are isolated from stale data in the persistent datastore.
- **Use `dragTo()` or other Playwright interactions that don't match the actual UI.** If the component uses click-based interactions (buttons, dropdowns), test with clicks — not drag-and-drop.
- **Proceed to the next step immediately after a mutation without waiting for the result.** Always wait for the expected view/element to appear after a create/update action.
- **Use blanket `deleteMany({})` or "reset all" endpoints in test cleanup.** Only delete the specific resources created during that test run.

```typescript
// WRONG — only checks elements exist, doesn't verify filtering logic
test('recipients page loads', async ({ page }) => {
  await page.goto('/recipients');
  await expect(page.locator('.recipient-card')).toBeVisible();  // WRONG: no logic verified
  // Does NOT check that Pending recipients are excluded
  // Does NOT verify country-specific behavior
});

// WRONG — manually written without helper, duplicates setup logic
test('select recipient', async ({ page }) => {
  await page.goto('/recipients');
  await page.click('[data-testid="recipient-1"]');  // WRONG: hardcoded, no helper
  await expect(page.locator('.selected')).toHaveCount(1);
});
```

## Test Isolation — NEVER Reset All Data

> **CRITICAL:** Tests must ONLY delete the specific data they created. Never delete all data, never reset the database, never use blanket `deleteMany({})`. This is enforced by `test_isolation_scanner.py`.

E2E tests **must** be independent — each test must pass regardless of run order or previous runs. When using a persistent datastore (MongoDB), accumulated data from prior test runs causes strict mode violations and false assertions.

### Forbidden patterns (scanner will flag these):
- `deleteMany({})` — empty filter deletes ALL documents
- `.drop()` / `dropCollection()` / `dropDatabase()` — destroys entire collections/databases
- `POST /api/test/reset` or any `/reset` endpoint — blanket wipe
- `beforeEach`/`afterAll` hooks that call any of the above

### Required pattern — tests clean up ONLY their own data:
1. Each test that creates data **must capture the created resource's ID** (from API response or by querying the GET endpoint after UI creation).
2. Track all created IDs in the test helper (e.g., `createdIds: string[]`).
3. In `afterEach`, delete **only those specific IDs** via `DELETE /api/test/{resource}` with `{ ids: [...] }` body.
4. The server endpoint **must require an `ids` array** and reject requests without one — never expose a "delete all" capability.
5. If no IDs were created during a test, cleanup is a no-op.

### Why this matters:
- Blanket resets destroy data created by other developers, other test suites, or manual QA sessions sharing the same database.
- Parallel test runs (sharded Playwright workers) can delete each other's data mid-test.
- A "clean slate" approach masks bugs that only surface when real data exists alongside test data.

```typescript
// playwright.config.ts — CORRECT: starts both server and client, waits for each
export default defineConfig({
  webServer: [
    {
      command: 'npx tsx watch packages/app-server/index.ts',
      url: 'http://localhost:3001/health',
      reuseExistingServer: true,
    },
    {
      command: 'cd packages/app-client && npx vite',
      url: 'http://localhost:3000',
      reuseExistingServer: true,
    },
  ],
});
```

```typescript
// CORRECT — test creates data, asserts, then deletes only what it created
test('User marks a task as completed', async ({ page, request }) => {
  // Seed via API — capture the created ID
  const createRes = await request.post('/api/todo-lists', {
    data: { name: 'Errands', tasks: [{ title: 'Buy milk' }] },
  });
  const createdList = await createRes.json();

  await page.goto('/');

  // Scoped locator — targets specific card
  const card = page.locator('.todo-list-card', { hasText: 'Errands' });
  await expect(card).toBeVisible();

  // Assert on outcome, not stale reference
  const checkbox = card.locator('input[type="checkbox"]').first();
  await checkbox.click();
  await expect(card.locator('.task-count')).toContainText('1/1 completed');

  // Cleanup — delete only the item this test created
  await request.delete(`/api/todo-lists/${createdList.id}`);
});

// CORRECT — data created via UI, cleanup via query + delete
test('User creates a new todo list', async ({ page, request }) => {
  await page.goto('/');
  await page.fill('input[placeholder="New list name..."]', 'Shopping List');
  await page.click('button:text("Create List")');

  const card = page.locator('.todo-list-card', { hasText: 'Shopping List' });
  await expect(card).toBeVisible();

  // Cleanup — find the created item and delete it
  const listsRes = await request.get('/api/todo-lists');
  const { items } = await listsRes.json();
  const created = items.find((l: any) => l.name === 'Shopping List');
  if (created) await request.delete(`/api/todo-lists/${created.id}`);
});
```

```typescript
// WRONG — blanket reset destroys all data including non-test data
test.beforeEach(async ({ request }) => {
  await request.post('/api/test/reset');  // WRONG: deletes everything
});

// WRONG — no isolation, assumes empty DB, unscoped locators
test('User marks a task as completed', async ({ page }) => {
  await page.goto('/todo-lists');  // WRONG: route may not exist
  await expect(page.locator('.todo-list-card')).toBeVisible();  // WRONG: strict mode if multiple
  const checkbox = page.locator('input[type="checkbox"]:not(:checked)').first();
  await checkbox.click();
  await expect(checkbox).toBeChecked();  // WRONG: stale reference after re-render
});
```

## Composition Root Requirements for E2E

The app-server composition root must include:
- A **valid UUID** for the stub development user (Zod schemas validate `userId` as UUID). Never use plain strings like `'dev-user'`.
- A `DELETE /api/test/{resource}` route for each domain resource that **requires an `ids` array in the request body** and deletes only those specific documents. Example: `DELETE /api/test/boards` with body `{ ids: ["id1", "id2"] }`. The handler must reject requests with missing or empty `ids`.
- **Never expose a blanket reset endpoint** (`POST /api/test/reset`, `DELETE /api/test/reset`, or any route that calls `deleteMany({})`, `.drop()`, or `dropCollection()`). The scanner will flag these.
- **Error handling** in the Express pipeline so unhandled exceptions return 500 instead of crashing the server.
