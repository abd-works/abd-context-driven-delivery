# Clean Engineering — Procedural Guidance (code fidelity)

## Two phases, one fidelity

Code fidelity has two distinct phases. Don't skip phase 1.

### Phase 1 — typed contracts

Fill out the structural commitments before implementing:

1. **If an interface was requested** — add `Class(I{Class})` in the same file.
2. **If no interface** — the empty `Class` stub from model is already there; continue on it.
3. **Implement public properties and operations** — real types, real signatures.
4. **Add private properties/operations as empty interfaces** — mark them, don't fill them yet.
5. **Add relationships with kind and cardinality** — composition/aggregation/association with counts.
6. **Pin invariants as comments** — plain English rules that must hold. Not enforcement methods.
7. **Pin interactions as `@interaction` abstract stubs on `Class`** — these will be dropped once implemented.

### Phase 2 — production implementation

Now fill everything:

1. **Fill all remaining empty bodies** — no `...`, no `# TODO` on production ops/props.
2. **Wire Production collaborators** — real persistence, real services, real cross-module dependencies. Not Fake-mode stubs.
3. **Drop `@interaction` methods** — they were scaffolding; now they're implemented.
4. **Keep invariants as comments** — they document constraints the code enforces.
5. **Add exceptions, constants, private helpers as needed.**

## Test shape ladder thinking

This is the procedure for testing at code fidelity. It inverts the natural instinct:

1. **Discover with real conditions first** — no stubs, no mocks. Call exactly as the user would. Real sub-agents, real standup, real backend. Learn the real shape of responses before any mock knows what to return. Write test **signatures only** — don't implement tests yet.
2. **Stub TDD second** — only after step 1. Write two-pass tests with stubs at architecture boundaries only (never the subject under test). Stubs MUST match the observed real shape from step 1.
3. **E2E swap third (on request)** — same signatures, same assertions, swap stubs for real collaborators. Run only when asked.

The key insight: humans stub early for speed; AI stubs to get to green without really testing anything. Both shortcuts produce tests that don't test the real thing. Discover real conditions first.

## Operation size and clarity

- Under 20 lines per operation. Extract named helpers when longer.
- Guard clauses for early returns.
- One level of abstraction at a time — don't mix raw I/O with orchestration logic.
- Named constants for magic numbers and unexplained literals.

## Exception thinking

- Domain exceptions that name the failure, not generic catch-alls.
- Log and re-raise or convert; never bare swallow.
- Comments explain why, not what.
