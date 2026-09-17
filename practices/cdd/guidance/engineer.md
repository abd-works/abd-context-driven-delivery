# CDD — Procedural Guidance (engineer fidelity)

## How to run engineer

Engineer produces working software. Everything from spec is locked; now it runs:

1. **All tests green** — BDD development tests pass. Story acceptance tests pass.
2. **Real backend wired** — no fake-only paths. CE code fidelity with Production collaborators.
3. **Real frontend wired** — not greybox or Story Demo alone. UX at front_end_code fidelity (when applicable).
4. **Domain implementation complete** — DDD tactics fully implemented.

## The "is it done?" test

A vertical is at engineer fidelity when:
- Tests are green against real collaborators (not just stubs)
- The UI is production frontend (not mockup shell)
- The backend is production services (not fake factories)
- The domain model is implemented (not just typed contracts)

If any of these are still stub/mock/fake, you're at spec, not engineer.

## UX at engineer

UX has no engineering fidelity of its own. Production UI follows from Stories + Clean Engineering at engineer, honoring the UX spec from spec fidelity. The IA vocabulary and control decisions carry forward — don't re-decide them.
