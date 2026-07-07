---
fidelity: [engineering]
artifact: [story-tests]
---

# Generate — Story Tests

## Before writing code

1. **Declare structure first** — file / class / method hierarchy from story tree. See `concepts/story-tests.md` and rules on test organization.
2. **Confirm language and framework** — ask if unstated. Defaults: pytest (Python), `node:test` (JS/TS), JUnit 5 (Java).
3. Pick the matching template under `templates/<format>/` (e.g. `templates/py/`, `templates/ts/`, `templates/java/`).
4. **Mirror the story map** — all code files follow `{epic-slug}/{sub-epic-slug}/{story-slug}/{story-slug}-{tier}.test.ts` folder hierarchy. Never write flat. Example: `move-money/compose-transfer/draft-transfer-details/draft-transfer-details-domain.test.ts`.

## Build order

One file per area, one class per story. Each scenario is its own `describe` / test method. **Every step string must be written out literally in the test body** — `await tier.given['exact step text']()`, `await tier.when[...]()`, `await tier.then[...]()`. No `runScenario`, no `run_scenario`, no `for` loops over `.given` / `.when` / `.then` arrays. A reader must see exactly which steps run and in what order without tracing into any helper. GWT step implementations live in the tier class; the test body wires them by the exact step string key. Shared helpers → `tests/<epic>/<epic>_helper.py` when reused.

## Helper imports — named destructured only

When a test file imports shared helper functions, **always use named destructured imports** — never a namespace import:

```typescript
// Correct — named destructured imports
import {
  seedSourceAccount,
  seedDestinationAccount,
  postTransferDetailsHttp,
  resetComposeTransferState,
} from '../compose-transfer-helpers'

// Then call directly — no prefix
seedSourceAccount('CHK-001')
```

**Never** use `import * as H` or `import * as helpers` — namespace imports obscure which functions are used and break tree-shaking. Call the functions directly by their imported name.

## Diagnose flip

After **2 consecutive failed fix attempts** on the same test — stop. Read the diagnose reference and run the full diagnose discipline before touching production code again. Do not proceed to the next story until resolved.

## Input traps

Assumptions, ambiguities, and missing context that commonly produce bad acceptance tests. Check each trap against available input before generating — flag gaps honestly; do not write tests that paper over them.

- **Behavior coverage confidence** — which behaviors are we actually proving work — and are we confident we know all the paths, or are there flows nobody has walked through yet?
- **Boundary assumptions** — what happens at the boundaries — when this behavior depends on another system's response, do we know what responses are realistic vs. what we're assuming?
- **Test doubles vs. reality** — where are we substituting a fake for something real — and does the fake behave like the real thing, or are we testing a fantasy?
- **Data realism** — are the test fixtures using values that could actually appear in production, or are we testing with "foo" and "123" and hoping edge cases don't matter?
- **Failure mode blindness** — do we know what failure looks like for each behavior — timeout, partial success, conflicting concurrent changes — or are we only proving the happy path works?
- **Example data alignment** — does every value in every test trace back to an Examples table in the specification — and where a stub stands in for a real system, is it configured to receive and return those exact values, or is it using invented defaults that hide misalignment?
