---
scanner: example_data_alignment_scanner.py
---

# Rule: Example Data Alignment

Every value used in a test must trace back to the **Examples table** in the specification, or to a **stub constant** derived from the same source. Tests must never invent data.

When a test interacts with a stub or test double, the stub must be configured to **receive and return the exact values named in the examples** — not a default or placeholder that happens not to break the test.

---

## What this rule governs

1. **Test inputs** — values passed to `given_*` / `when_*` helpers must come from spec examples or a shared fixture/constants file, not be typed inline.
2. **Stub configuration** — wherever a stub, mock, or test double stands in for a real dependency, it must be configured to accept the example input and return the example output.
3. **Assertions** — `then_*` helpers must assert the exact value named in the spec (e.g. `"Month-to-Month Plans"`, `3` plan cards, `"Invalid code. Please try again."`), not a weaker partial match invented to make the test green.

---

## DO

- Centralise all example values in a shared fixtures / constants file (e.g. `tests/fixtures.ts`, `tests/conftest.py`).
- Import those constants into every spec file — never duplicate the raw value inline.
- When configuring a stub, use the same constant: the stub receives the spec's input and returns the spec's output.
- Match the scenario number when naming constants: `ALEX_CHEN` for Scenario 1, `NEW_SUBSCRIBER` for Scenario 2.

```typescript
// fixtures.ts — single source derived from specification-by-example.md
export const ALEX_CHEN = {
  email:    'alex.chen@paradise.bm',   // Spec Scenario 1 — active subscriber
  password: STUB_PASSWORD,
}
export const PROMO = {
  valid:   'PROMO10',   // Spec Scenario 2 — voucher applies discount
  invalid: 'INVALID',   // Spec Scenario 3 — voucher rejected
}

// sign-in.spec.ts — imports constant, does not repeat the string
import { ALEX_CHEN } from '../fixtures'

test('valid credentials navigate to home dashboard', async ({ page }) => {
  await given_sign_in_page(page)
  await when_subscriber_enters_credentials(page, ALEX_CHEN.email, ALEX_CHEN.password)
  await then_navigated_to_home(page)
})

// Stub configured to match the spec value, not an invented default
// stubs/handlers/cognito.ts — Cognito stub accepts STUB_EMAIL from customer.ts
// (same file that fixtures.ts imports STUB_EMAIL from)
```

```python
# conftest.py — spec example values
ALEX_CHEN_EMAIL = 'alex.chen@paradise.bm'
PROMO_VALID     = 'PROMO10'

# test_sign_in.py — imports, does not repeat
from conftest import ALEX_CHEN_EMAIL

def test_valid_credentials_navigate_to_home(sign_in_page):
    when_subscriber_enters_credentials(sign_in_page, ALEX_CHEN_EMAIL, STUB_PASSWORD)
    then_navigated_to_home(sign_in_page)
```

---

## DON'T

- Inline raw strings that are also in the spec (`'test@example.com'`, `'foo'`, `'123'`, `'Password1!'`).
- Leave stubs returning invented defaults while the spec defines specific return values.
- Assert a weaker condition than the spec states (e.g. asserting `count >= 1` when the spec says exactly `3`).
- Duplicate the same string literal in two test files — extract to fixtures.

```typescript
// WRONG — invented data not from spec, stub not aligned
test('valid credentials navigate home', async ({ page }) => {
  await when_subscriber_enters_credentials(page, 'test@example.com', 'Password1!')
  //                                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  //                                              not in any Examples table
  await then_navigated_to_home(page)
})

// WRONG — stub returns a default shape the spec didn't describe
http.post('/api/login', () =>
  HttpResponse.json({ ok: true })   // spec says tokens + customerId, not generic ok:true
)

// WRONG — assertion weaker than spec
await expect(page.getByRole('button', { name: 'Sign up now' })).toBeVisible()
// spec says exactly 3 plan cards — should assert count === 3
```

---

## Fixtures file convention

| Language | Fixtures location | Import style |
|---|---|---|
| TypeScript / JS | `tests/fixtures.ts` | `import { ALEX_CHEN } from '../fixtures'` |
| Python | `tests/conftest.py` or `tests/fixtures.py` | `from fixtures import ALEX_CHEN_EMAIL` |
| Java | `src/test/.../Fixtures.java` | `Fixtures.ALEX_CHEN_EMAIL` |

The fixtures file **must** be the single source of truth. Any value that appears in an Examples table or in a stub's seed data file belongs in fixtures. Test files import; they do not define.

---

## Stub alignment checklist

When a test uses a stub, verify all three points before considering the test complete:

- [ ] **Input** — the stub is configured to accept the value named in the spec example (not a wildcard that accepts anything).
- [ ] **Output** — the stub returns the exact shape and values described in the spec's Then column.
- [ ] **Constant reuse** — both the stub configuration and the test assertion reference the same imported constant, not two separately typed copies of the same string.

If the stub cannot be made to match (e.g. the stub's existing shape is wrong), add a `test.skip` with a note explaining what the stub needs to return, referencing the exact spec scenario.
