# Input traps — abd-architecture-code

Assumptions, ambiguities, and missing context that commonly produce wrong code. Check each trap against available input before generating — flag gaps honestly; do not guess spec layout, do not silently bridge gaps between the design (`<context-file>`) and the embodiment (`<spec-root>` template package).

## Input resolution traps

- **Mechanism in scope is unclear** — the story implements behaviour that touches multiple mechanisms (e.g. Partner Integrations *and* Caching). Pick the wrong one and `<context-file>` and `<spec-root>` resolve to the wrong recipe; the generated code follows a pattern that does not belong to the story's primary concern. Route via the central spec's Where-to-Start and confirm with the user when ambiguous.
- **Template package missing** — the spec is present and complete but `docs/architecture/templates/<slug>/` does not exist. Do not improvise a scaffold from prose; route back to `abd-architecture-template` to produce the runnable reference module first.
- **Template package `example/` does not build** — the package exists but its sentinel example fails to compile or its tests fail to pass. The template itself is broken; do not propagate the breakage into per-feature code. Route back to `abd-architecture-template` to fix the package, then resume.
- **Helpers context file missing** — the project has no test-helpers package-tier `architecture-context.md`. Tier names, helper layout, and layer order have no source of truth and the test inventory cannot be derived. Route back to `abd-architecture-specification` to author the helpers context file.

## Spec ⇄ template drift traps

- **Vocabulary drift between `<context-file>` and `<spec-root>`** — `<context-file>` § Canonical Patterns uses `{System}`; `<spec-root>/template/` uses `{Partner}` or `{Service}`. The two should agree verbatim (enforced by `abd-architecture-template`'s `template-uses-spec-placeholders` rule). Drift means one side is stale. Do not pick a winner — route back to `abd-architecture-template` to refresh the package against the current spec.
- **Participant added to spec but missing from template** — `<context-file>` § File Structure names five participants; `<spec-root>/template/` has four. The fifth was added to the spec after the template was generated. Generating code from the template will miss the participant.
- **Rule added to spec but missing from `<spec-root>/rules/`** — `<context-file>` § Rules has eight bullets; `<spec-root>/rules/` has seven files. The eighth bullet has never been lifted. Generated code may violate the unlifted rule because no validation file enforces it.
- **`templates/tests/` does not match the helpers context file** — the helpers context file mandates four tiers; `<spec-root>/templates/tests/` only scaffolds three. The fourth tier has no parameterized template. Per-feature tests for that tier cannot be generated cleanly.

## Layer and tier traps

- **Layer boundaries** — where does one layer's responsibility end and the next begin? If you can't name what each layer is allowed to know about the layers around it (from `<context-file>` § File Structure or § Class Specification), the code will blur those boundaries under pressure.
- **Spec vs. reality** — which parts of `<context-file>` and `<spec-root>` have never been exercised by a real story? Those are the patterns most likely to need rework once production code hits them.
- **Domain behavior vs. framework plumbing** — for each scenario you're about to implement, is the interesting behavior in the domain logic or in the framework wiring? If the test is mostly asserting plumbing, what domain risk is it leaving uncovered?
- **Boundary assumptions** — when this code calls another system or layer, what responses are you assuming you'll get? Which of those assumptions have you verified, and which are you hoping are right?
- **Test tier coverage gaps** — which behaviors are only proven at one tier? If the domain test passes but the integration test doesn't exist yet, what could still be wrong that you wouldn't catch?
- **Scenario completeness** — are there flows through this story that nobody has written a scenario for — error paths, concurrent access, partial failures — that `<context-file>` implies but the story doesn't explicitly name?

## Substitution traps

- **`parameters.json` placeholders missing for the story** — `<spec-root>/parameters.json` declares `{Domain}` and `{Feature}`; the story needs to substitute three values (domain + feature + sub-feature variant). The third has no declared placeholder. Either the template is under-parameterized (route back to template skill) or the story is using the wrong template package.
- **Rename map gap** — `<spec-root>/template/{Domain}Service.ts` exists but `parameters.json` `renameMap` has no entry for it. Generated filename would keep the `{Domain}` token literally. Verify before generation.
- **Sentinel collision with story domain** — the story implements a `PartnerA` integration; `<spec-root>/example/PartnerA/` already exists as the template's sentinel binding. Generating into `PartnerA` would overwrite the example. Pick a real story-driven name and confirm it does not collide with any sentinel.