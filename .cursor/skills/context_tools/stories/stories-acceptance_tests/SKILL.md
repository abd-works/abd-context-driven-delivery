---
name: stories-acceptance_tests
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-acceptance_tests

Use stories guidance at `acceptance_tests` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@stories-scenarios
@stories-story_map
@stories-scaffold

# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution.

Interactions fit into a hierarchy: a `StoryMap` of `Epic` → nestable `SubEpic` → `Story`. Each story is `Scenario`s with discrete steps; backgrounds and scenarios carry examples.

| Fidelity | Default Format | Produce |
|---|---|---|
| **story_map** | markdown | Story map + thin-slice |
| **scenarios** | typescript | Main-flow scenarios per story (single or multiple); optional variations; `examples/` + `givens.ts`. Pass `format markdown` when the strategy asks for a markdown view. |
| **acceptance_tests** | typescript | `tests/{epic}/{sub-epic}/{story}.{tier}.ts` — one GWT file per story per seam (`front-end`, `back-end`, or another system name). No story folder. Fixtures: `examples/` + `givens.ts`. CE runs alongside for wrap classes. |

**Templates** live under `templates/` per format. **Scanners** read the canonical model only — never language syntax.

---

## Shared rules

- **`vocabulary-traces-to-domain-source`** — Trace terms to domain language / model when present.
- **`artifacts-mirror-story-hierarchy`** — Mirror Epic → SubEpic → Story on disk as folders for epic and sub-epic, and as `{story}.{tier}.ts` files (no per-story directory).
- **`read-all-source-context-in-full`** — Before locking hierarchy **and before any grill/iterate question about a seam**, prove-read **every relevant referenced context** for that decision: owning `*-segment.md`, `module-context.md`, session sketches / grill-answers / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Index / mid-epic stub columns are structure hints only — **not** story inventory. Grep or primer-only skims do not count; cite concrete terms from the files read in the question turn. Also re-read these rules. Do not thin from titles or memory!
- **`do-not-invent-requirements`** — Only model behaviours present in source context or an explicit ask. Never invent:
  - status concepts, maintenance signals, warning badges, or config columns (e.g. `Status (ok/stale)`) the source does not require — unconfigured / not-yet-current = **no row** + the existing fallback, never a new invented state to render;
  - a second, competing command / invoke surface beside one the user already specified (e.g. a raw YAML `toolset`/`fidelity`/`action` "Invoke" block given equal billing next to an already-locked `/{skill} <action> {fidelity}` line). Keep the specified surface primary; any secondary format is a subsidiary link at most — never inlined, never a co-equal page element.

---

## acceptance_tests

**Default format:** typescript

**Goal:** Turn locked scenarios into runnable acceptance coverage; CE runs alongside to produce matching wrap classes under `domain/`.

**Tooling & Idioms:** Refer to [`context_tools/language-tools.md`](/context_tools/language-tools.md) for language-specific tool recommendations and idiomatic patterns for tests.

**Produce:** `tests/{epic}/{sub-epic}/{story}.{tier}.ts` — one GWT file per story per seam. `{tier}` is `front-end`, `back-end`, or any other system name you are proving. No `{story}/` folder and no `*_story` / `*_test_helper` split. Fixtures live in `examples/` and `givens.ts` at the lowest shared epic / sub-epic / story folder.

### Rules

- **`behavioral-observable-outcomes`** — same rule as **scenarios**: assertions stay in domain-observable terms, never internals.
- **`explore-full-interaction-surface`** — same rule as **scenarios**: acceptance_tests must cover the explored interaction surface, not just translate the first main-flow scenario into Playwright. Trace react-hook-form rules, shared validation components, and stubbed failure modes during the sandbox walk-through; add a `scenario()` per distinct behavior.
- **`gwt-steps-trace-to-domain-operations`** — same rule as **scenarios**: each step in the test traces to a named domain operation or property. A hop to the next step is a named operation on the arriving aggregate, not a route or `waitForCompletion()`.
- **`reconcile-live-immediately`** — same rule as **scenarios**: live disagreement updates the sketch before the test is locked.
- **`explain-deep-link-arrival`** — same rule as **scenarios**.
- **`given-only-what-the-system-checks`** — same rule as **scenarios**.
- **`when-holds-the-operation`** — same rule as **scenarios**.
- **`then-and-chaining`** — same rule as **scenarios**.
- **`extract-assertion-helper`** — same rule as **scenarios**.
- **`infrastructure-in-lifecycle-hooks`** — same rule as **scenarios**.
- **`load-with-identity-in-hand`** — same rule as **scenarios**.
- **`seed-prior-story-as-given`** — same rule as **scenarios**.
- **`reuse-owning-aggregate-stubs`** — same rule as **scenarios**.

---

## Templates

### python

## scenario-template.py

# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Scenario template — refer to context_tools/language-tools.md for tooling.
#
# ```
# epic:      {epic-verb-noun}
# sub_epic:  {sub-epic-verb-noun}
# story:     {story-verb-noun}
# file:      tests/{epic-verb-noun}/{sub-epic-verb-noun}/{story_verb_noun}.{tier}.py
# tier:      front-end | back-end | external-system
# fixtures:  tests/{epic-verb-noun}/examples/  tests/{epic-verb-noun}/{sub-epic-verb-noun}/givens.py
# ```
#
# Pattern: mirror sign-up-create-account.e2e.ts — Mamba describe/context/it (RSpec-style);
# domain ops in When; observable expects in Then/And; infrastructure in before.all;
# shared state on StoryScenario subclass.

from __future__ import annotations

from expects import equal, expect
from mamba import before, context, description, it

from domain.{bounded_context}.{app_snake} import {AppPascal}
from story_test import StoryScenario


class {StoryPascal}Story(StoryScenario[{AppPascal}]):
    """Shared boot, background, and typed handles for this story's scenarios."""

    {aggregate_camel}: {AggregatePascal}

    @classmethod
    def boot(cls) -> {AppPascal}:
        """Infrastructure only (browser, config, wiring). Never domain assertions here."""
        return {AppPascal}.initialize()  # config from examples/

    def background(self) -> None:
        """Background — shared Given state every scenario inherits. Domain state only."""
        self.{aggregate_camel} = self.app.{aggregate_camel}()


with description("{Story Verb-Noun}") as self:
    with before.all:
        self.ctx = {StoryPascal}Story()
        self.ctx.app = {StoryPascal}Story.boot()
        self.ctx.background()

    with context("{main-flow outcome}"):
        with before.each:
            def _given_and_when() -> None:
                # Given {given step text}
                ...
                # When {when step text} — domain operation, e.g. self.ctx.app.authentication().register(...)
                ...

            _given_and_when()

        with it("Then {then step text}"):
            expect(self.ctx.{aggregate_camel}.{observable}()).to(equal(/* expected */))

        with it("{additional outcome}"):
            expect(self.ctx.{aggregate_camel}.{observable2}()).to(equal(/* expected */))

    with context("{alternate outcome — e.g. validation branch}"):
        with before.each:
            def _given_and_when() -> None:
                # Given {alternate given}
                ...
                # When {alternate when}
                ...

            _given_and_when()

        with it("Then {alternate then}"):
            expect(/* observable */).to(equal(/* expected */))

See examples in `context_tools/stories/examples/` if needed.