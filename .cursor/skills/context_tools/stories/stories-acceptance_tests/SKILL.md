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
| **story_map** | markdown | Story map |
| **scenarios** | python | Main-flow scenarios per story — `{story}.{tier}.py` GWT files. Pass `format markdown` only when the strategy asks for a markdown view. |
| **acceptance_tests** | python | Same `{story}.{tier}.py` tree as scenarios. CE runs alongside for wrap classes. |

**Templates** live under `templates/` per format. **Scanners** read the canonical model only — never language syntax.

---

## Shared rules

- **`vocabulary-traces-to-domain-source`** — Trace terms to domain language / model when present.
- **`artifacts-mirror-story-hierarchy`** — Mirror Epic → SubEpic → Story on disk as folders for epic and sub-epic, and as `{story}.{tier}.py` files (no per-story directory).
- **`read-all-source-context-in-full`** — Before locking hierarchy **and before any grill/iterate question about a seam**, prove-read **every relevant referenced context** for that decision: owning `*-segment.md`, `module-context.md`, session sketches / grill-answers / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Index / mid-epic stub columns are structure hints only — **not** story inventory. Grep or primer-only skims do not count; cite concrete terms from the files read in the question turn. Also re-read these rules. Do not thin from titles or memory!
- **`do-not-invent-requirements`** — Only model behaviours present in source context or an explicit ask. Never invent:
  - status concepts, maintenance signals, warning badges, or config columns (e.g. `Status (ok/stale)`) the source does not require — unconfigured / not-yet-current = **no row** + the existing fallback, never a new invented state to render;
  - a second, competing command / invoke surface beside one the user already specified (e.g. a raw YAML `toolset`/`fidelity`/`action` "Invoke" block given equal billing next to an already-locked `/{skill} <action> {fidelity}` line). Keep the specified surface primary; any secondary format is a subsidiary link at most — never inlined, never a co-equal page element.

---

## acceptance_tests

**Default format:** python

**Goal:** Turn locked scenarios into runnable acceptance coverage; CE runs alongside to produce matching wrap classes under `domain/`.

**Tooling & Idioms:** Refer to [`context_tools/language-tools.md`](/context_tools/language-tools.md) for language-specific tool recommendations and idiomatic patterns for tests.

**Produce:** `tests/{epic}/{sub-epic}/{story}.{tier}.py` — one GWT file per story per seam. `{tier}` is `front-end`, `back-end`, or any other system name you are proving. No `{story}/` folder and no `*_story` / `*_test_helper` split.

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
# # Params — fill before writing code
# epic:       {epic-verb-noun}           # kebab folder under tests/
# sub_epic:   {sub-epic-verb-noun}       # kebab folder under epic/ (omit level if story hangs off epic)
# story:      {story-verb-noun}          # Verb Noun title from the story map
# story_file: {story_snake_slug}         # snake file slug, e.g. sign_up_create_account
# tier:       e2e | front-end | back-end | {system}
#
# # Artifact layout (artifacts-mirror-story-hierarchy)
# tests/
#   {epic-verb-noun}/
#     {sub-epic-verb-noun}/              # omit when the story file lives under epic/
#       {story_snake_slug}.{tier}.py     # one GWT file per story per tier
#
# # Machinery — copy once per tests/ tree if missing (do not inline in skills):
#   context_tools/stories/templates/py/story_test.py → tests/story_test.py
# story_test: tests/story_test.py
#
# # Naming rules
# - Epic / SubEpic folders → kebab-case verb-noun (Sign Up → sign-up)
# - Story test file        → {story_snake_slug}.{tier}.py at epic or sub-epic — NO {story}/ folder
# - Tier                   → file extension segment (.e2e.py, .front-end.py, .back-end.py)
# - Forbidden              → {story}/ folders, *_story.*, *_test_helper.* splits
# ```
#
# Pattern: GWT structure only — replace pass with real code under each with.

from __future__ import annotations

from mamba import after, before

from story_test import and_, background, given, scenario, story, then, when


with story("{Story Verb-Noun}"):
    with before.all:
        pass  # boot — test code goes here

    with after.all:
        pass  # teardown — test code goes here

    with background.each:
        with given("{background given step}"):
            pass  # test code goes here

        with scenario("{surface check — e.g. rules visible}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with then("{observable surface outcome}"):
                pass  # test code goes here

        with scenario("{validation branch while typing}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with and_("{follow-on when step}"):
                pass  # test code goes here

            with then("{validation message on domain object}"):
                pass  # test code goes here

        with scenario("{validation clears when input conforms}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with and_("{prior invalid state}"):
                pass  # test code goes here

            with when("{corrective action}"):
                pass  # test code goes here

            with then("{error cleared on domain object}"):
                pass  # test code goes here

        with scenario("{main-flow outcome}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with when("{submit operation on domain object}"):
                pass  # test code goes here

            with then("{post-condition on loaded aggregate}"):
                pass  # test code goes here

See examples in `context_tools/stories/examples/` if needed.