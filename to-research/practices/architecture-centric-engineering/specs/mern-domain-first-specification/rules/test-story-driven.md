---
scanner: test_structure_scanner.py
---

# Rule: Test Story-Driven

Tests mirror story scenarios across three tiers: **Server-Side** (Node.js Test Runner + Supertest), **Client-Side** (Vitest + Testing Library), and **E2E** (Playwright). Each tier tests the **same scenarios** with different emphasis. The test folder hierarchy maps directly to the story graph: Epic → Folder, Sub-Epic → Folder, Lowest Sub-Epic → 3 test files (one per tier). Each test file contains one class per Story and one method per Scenario using Given/When/Then helper methods from a shared base helper.

## DO

- Organize test folders by `tests/{epic}/{sub-epic}/`.
- Create exactly 3 test files per lowest sub-epic: `*_server.test.ts`, `*_client.test.tsx`, `*_e2e.spec.ts`.
- Create a `helpers/` folder per sub-epic with base, server, client, and e2e helpers.
- Name test methods to mirror Gherkin scenario titles verbatim.
- Use Given/When/Then helper methods that read like scenario steps.
- Share test data and abstract helpers in the `.base.ts` helper.

```
tests/
├── create-wire-payment/                    # Epic folder
│   └── select-recipient/                   # Sub-Epic folder (lowest level)
│       ├── helpers/
│       │   ├── select-recipient.base.ts    # Shared test data & abstract helpers
│       │   ├── select-recipient.server.ts  # Server-tier helper (Supertest)
│       │   ├── select-recipient.client.ts  # Client-tier helper (Testing Library)
│       │   └── select-recipient.e2e.ts     # E2E-tier helper (Playwright)
│       ├── select-recipient_server.test.ts
│       ├── select-recipient_client.test.tsx
│       └── select-recipient_e2e.spec.ts
```

```typescript
// select-recipient_server.test.ts — CORRECT: Class = Story, Method = Scenario
import { SelectRecipientServerHelper } from './helpers/select-recipient.server';

class TestViewActiveRecipients {
  helper = new SelectRecipientServerHelper();

  async test_user_views_list_of_active_recipients() {
    await this.helper.givenUserLoggedIntoChannelOne();
    await this.helper.givenEnterpriseHasRecipientsWithActiveStatus();
    await this.helper.whenUserInitiatesWirePayment();
    await this.helper.thenOnlyActiveRecipientsDisplayed();
  }
}
```

## DON'T

- Skip any of the three test tiers for a sub-epic.
- Write tests without Given/When/Then helper methods.
- Name test methods with technical HTTP language instead of scenario language.
- Write E2E tests separately without reusing the base helper class.
- Place test files outside the epic/sub-epic folder structure.
- **Mock `fetch` without realistic response shape.** If the API client checks `response.ok`, the mock must include `ok: true`. Incomplete mocks cause silent failures that only surface as "element not found" errors.

```typescript
// WRONG — no helper, no Given/When/Then structure, technical naming
test('GET /api/recipients returns 200', async () => {
  const res = await request(app).get('/api/recipients');
  expect(res.status).toBe(200);
  expect(res.body.recipients.length).toBe(2);
});

// WRONG — tests placed in flat structure, not by epic/sub-epic
tests/
├── recipients.test.ts        # No hierarchy, no tier separation
├── payments.test.ts
└── e2e.spec.ts               # All E2E in one file
```
