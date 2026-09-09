# Examples — BDD fidelities

| File | Contents |
|---|---|
| `examples.md` | Index and what to notice (this file) |
| `examples.ts` | Behavior hierarchy, Jest/TypeScript signatures, development tests, production code, layer-boundary mocking |
| `examples.py` | Mamba/Python signatures, development tests, minimal production code |

## Behavior hierarchy input (prerequisite)

Approved plain-English hierarchy used as input to **behavior** fidelity — see `examples.ts`, **Behavior hierarchy input** section (comment block at top).

---

## Behavior fidelity — signatures

### Jest/TypeScript output (`character.test.ts`)

See `examples.ts` — **Behavior fidelity — signatures** section.

### Mamba/Python output (`character_spec.py`)

See `examples.py` — **Behavior fidelity — signatures** section.

### What to notice

- Behavior hierarchy has 9 `should` lines → signature has 9 `it` blocks. Count matches exactly.
- 4 nesting levels in scaffold → 4 levels in code.
- Every body contains `// BDD: SIGNATURE` (Jest) or `# BDD: SIGNATURE` (Mamba) and nothing else.
- No imports, no assertions, no mocks, no `beforeEach`.
- `it('should …')` matches the behavior hierarchy text verbatim — no paraphrasing.

### Batch processing for large behavior hierarchies

When a behavior hierarchy has more than ~18 describe blocks, process in batches:

1. First batch: top-level concept and its first 2-3 state blocks (~18 describes).
2. Subsequent batches: remaining state blocks and sub-context_tools.
3. Confirm after each batch that the hierarchy count matches the behavior hierarchy for that slice.

---

## Development fidelity — tests + code

### Phase 1: Signature → Test implementation

**Input (signature)** — see `examples.ts`, **Development fidelity — signature input** section.

**Output (test implementation — Jest/TypeScript)** — see `examples.ts`, **Development fidelity — test implementation** section.

### Phase 2: Failing tests → Minimal production code

Tests above are RED — `Character` does not exist.

**Output (minimal production code — TypeScript)** — see `examples.ts`, **Development fidelity — minimal production code** section.

**What to notice:**
- Only properties tests assert on: `stats`, `wounds`. No `createdAt`, `id`, etc.
- Only methods tests call: `applyDamage`. No `heal()`, `die()`, etc.
- `wounds` starts at `0` because the test asserts `expect(character.wounds).toBe(0)`.
- Class used (not function) because `wounds` is mutable state that accumulates across calls.

### Mamba/Python equivalent

See `examples.py` — **Development fidelity** sections (test implementation and minimal production code).

### Layer boundary mocking example (service layer)

When testing a service that depends on a repository — see `examples.ts`, **Layer boundary mocking example** section.

**Mock is at the boundary** (repository) — the service is fully tested; the repository mock is not the thing under test.
