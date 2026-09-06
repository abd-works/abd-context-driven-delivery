# New System vs Existing System (shared)

Cross-cutting discipline for story-driven-delivery skills (story mapping, acceptance criteria, specification by example, acceptance tests). Skills link here instead of repeating it.

## Determine the mode before producing anything

Every SDD skill must know whether it is working against a **new system** or an **existing system**. The mode determines the source of truth and the direction of correction.

| | New system (spec-first) | Existing system (reverse-engineering) |
|---|---|---|
| **Source of truth** | The spec (stories, AC, scenarios) | The implementation (code, extracted context, screenshots) |
| **Direction of correction** | Code must match spec | Spec must match code |
| **How to verify** | Run the test → it should fail until code is written | Read the extraction → the assertion must match what already renders |
| **When spec and code disagree** | Code is wrong — fix the code | Spec is wrong — fix the spec |

## How to detect the mode

**Existing system** — any of these signals:
- Extracted context exists (`docs/extracted-context/`, ARIA snapshots, screenshots)
- The application is already deployed and running
- You are writing tests for features that are already built
- A discovery or scout phase has already captured page structure

**New system** — none of the above exist. Stories, AC, and scenarios are being written before the code.

## Implications per skill

### Story mapping (`abd-story-mapping`)

- **Existing system:** Map what the system already does. Do not add stories for behaviour that doesn't exist unless explicitly scoped as new work. Name epics and stories using the vocabulary the running system already uses (labels, page titles, button names from the extraction).
- **New system:** Map intended behaviour. Stories describe what will be built.

### Acceptance criteria (`abd-story-acceptance-criteria`)

- **Existing system:** AC must describe what the system currently does — not what you wish it did. Read the ARIA snapshot and component code to determine the actual behaviour (e.g. does the UI clamp, reject, disable, or ignore?). When the AC document says "rejects with error" but the UI actually clamps the value, correct the AC.
- **New system:** AC describes intended behaviour. The implementation will be built to match.

### Specification by example (`abd-story-specification`)

- **Existing system:** Scenario values must be valid against the current schema/contract. Read `@project/contracts` (or equivalent) for regex patterns, min/max, and allowed characters before choosing concrete values. If a scenario uses `E2E-BATCH-` as a prefix but the schema only allows `[A-Za-z0-9]+`, the scenario is wrong.
- **New system:** Scenarios define the contract. The schema will be built to accept them.

### Acceptance tests (`abd-story-acceptance-test`)

- **Existing system:** Before writing `then_*` assertions, verify observable behaviour against the extraction (ARIA snapshots, screenshots, controller decorators). Write tests that pass against the running system. When a test fails, the test is likely wrong — not the system.
- **New system:** Tests are written to fail first (RED). The system is then built to make them pass (GREEN). A failing test means the code isn't written yet.

## Evidence sources for existing systems (check in this order)

1. **ARIA snapshots** (`docs/extracted-context/.../aria.yaml`) — exact roles, names, states, placeholders as rendered
2. **Screenshots** (`docs/extracted-context/.../screenshot.png`) — visual rendering for ambiguous cases
3. **Extraction overview** (`docs/extracted-context/.../extraction-overview.md`) — page inventory with URLs and domain/UX focus
4. **Contract schemas** (`packages/contracts/` or equivalent) — regex patterns, min/max, allowed values
5. **Component source code** — for validation logic, clamping, conditional rendering
6. **Controller decorators** — for `@HttpCode()`, response shape, status codes

## When spec and implementation disagree

In an **existing system**, the implementation wins. When you discover a disagreement:

1. **Fix the upstream artifact** — correct the AC, scenario, or story map to match reality.
2. **Document the correction** — add a DO/DO NOT to the strategy (if one exists) with the wrong assumption and the correct behaviour.
3. **Do not silently adjust only the test** — if the test is the only thing that changes, the spec remains wrong and the next person will repeat the mistake.
