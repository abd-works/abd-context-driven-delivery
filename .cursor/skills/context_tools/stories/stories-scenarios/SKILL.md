---
name: stories-scenarios
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-scenarios

Use stories guidance at `scenarios` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
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

## scenarios

**Default format:** typescript

**Goal:** Main-flow scenarios per story (single or multiple) with optional variations.

**Produce:** Same `{story}.{tier}.ts` tree as acceptance_tests. Pass `format markdown` only when the strategy command names it.

### Rules

- **`behavioral-observable-outcomes`** — Name and Then in domain-observable terms; never internals.
- **`explore-full-interaction-surface`** — Scenarios are not complete when only the main-flow GWT from the sketch is written. Before locking scenarios (and again before acceptance_tests), walk the real UI and model **every distinct user-visible behavior**: inline rule checklists and how they change while typing, field-level validation errors clearing as input conforms, cross-field rules (confirm password, paste mismatch), submit-button gating, and server-side error surfaces. A story that only codifies the happy path when the screen has rich client-side validation is a **defect** — branch into additional scenarios (or scenario outlines with examples) per mechanical variation, not one paragraph that mentions "validation" in passing.
- **`gwt-steps-trace-to-domain-operations`** — Every Given / When / Then maps to a named domain operation or property. If a step cannot be traced, that is a modelling gap — add the operation or property; do not gloss over it. A hop to the next step is a named operation on the arriving aggregate (`prospect.verifyIdentity()`), not a route, `waitForCompletion()`, or driving the next concern through the previous aggregate.
- **`reconcile-live-immediately`** — The running app wins. When a walk-through disagrees with the sketch, fix the sketch in that increment before locking the test.
- **`explain-deep-link-arrival`** — A scenario that navigates to a parameterized route (`/sign-up/:planId`) must say how a user actually arrives: in-app navigation, marketing/external deep-link, or a wizard step with no URL change. Do not write `When they navigate to X` as if it were a button.
- **`given-only-what-the-system-checks`** — Given states conditions the **running system actually uses** for the behaviour under test. Do not Given a field the code never reads for that decision (`metadata.verified` when routing actually keys off `customer.billing.id`).
- **`when-holds-the-operation`** — When holds the domain operation being exercised. An empty When with a comment, or the operation called inside Then, is a defect. Then only asserts on what When already produced — no I/O in Then.
- **`then-and-chaining`** — The first outcome uses `then()`; every later outcome on the same interaction chains `.and()`. Repeated `then()` calls break the Gherkin narrative. Markdown `And` stays `And`.
- **`extract-assertion-helper`** — The same assertion shape more than twice becomes a named helper that takes a data bag. Call sites pass only the concrete values.
- **`infrastructure-in-lifecycle-hooks`** — Browser boot, app wiring, and `initialize` live in `beforeAll` / `afterAll`. `given(` is domain state only.
- **`load-with-identity-in-hand`** — `load` takes the identity already in hand. Do not assume a browser session. Load once at the highest Given that needs the aggregate and reuse the variable. A cart has no identity outside its prospect — reach it through the owner, not `cartRepository().current()`.
- **`seed-prior-story-as-given`** — A later story's Given is seeded from prior-story fixtures (`givens.ts` / `examples/`), not a replay of that story's When.
- **`reuse-owning-aggregate-stubs`** — For a non-core aggregate, take stubs from **that aggregate's folder / source repository** (`domain/{bounded-context}/{aggregate}/stubs/{system}/`). Do not invent a test-local stub. Do not stub the seam you are proving.

---

## Templates

### markdown

## components/evidence-table.md

---
fidelity: [exploration, specification]
artifact: [story-scenarios]
format: md
section: footer
---

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Scenario 1 | `<source>` | `<location>` |


## components/story-header.md

---
fidelity: [exploration, specification]
artifact: [story-scenarios]
format: md
section: header
---
## Story: `<Verb–Noun Title>`

**Story type:** user | system | technical

**Sources / context:** `<pointer to domain source, AC, or conversation>`

### Domain terms

- ++`<ConceptA>`++ — `<plain-language gloss>`
- ++`<ConceptB>`++ — `<plain-language gloss>`

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).


## scenario-inline.md

---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

## Behaviors

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).

### Scenario 1: `<outcome-oriented scenario name>`

*Given* a ++`<ConceptA>`++ *`<value>`*  
  *And* that ++`<ConceptA>`++ *`<value>`* has a ++`<ConceptB>`++ *`<value>`*  
*When* the ++`<ConceptA>`++ *`<value>`* `<triggering action>`  
    using ++`<ConceptB>`++ *`<value>`*  
*Then* the ++`<observed concept>`++ is `<observable outcome>`  
  *And* the ++`<related concept>`++ is `<additional outcome>`  
  *But* no ++`<concept>`++ is `<what does not happen>`

### Scenario 2: `<alternate outcome-oriented scenario name>`

*Given* `<alternate setup state>`  
*When* `<alternate triggering action>`  
*Then* `<alternate observable outcome>`  
  *And* `<additional outcome>`


## scenario-main-flow.md

---
fidelity: [exploration]
artifact: [story-scenarios]
format: md
section: body
---

### Domain terms

- ++`<Concept>`++ — `<plain-language gloss>`

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).

## Behaviors

### Scenario Outline: `<main-flow outcome name>`

*Given* a ++`<Concept>`++ from `helper.given<Concept…>({ mode: "fake" })`  
  *And* that ++`<Concept>`++ {`<concept_field>`}  
*When* the **`<Actor>`** `<triggering action>`  
*Then* `<observable outcome on the public interface of I{Concept}>`  
  *And* `<additional observable outcome>`

### Examples

| scenario   | `<concept_field>` | `<result_field>` |
|------------|-------------------|------------------|
| ++Scenario 1++ | `<value>`         | `<value>`        |

> Examples table documents the representative row. Code loads the same values from ExampleFactory (AI fills stubs).


## scenario-outline.md

---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

### Domain terms

- ++`<ConceptA>`++ — `<plain-language gloss>`
- ++`<ConceptB>`++ — `<plain-language gloss>`

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).

### Evidence

| Source | Note |
|--------|------|
| `<pointer>` | `<why it matters>` |

### Background

*Given* a ++`<ConceptX>`++ from `helper.given<ConceptX…>({ mode: "fake" })`  
  *And* that ++`<ConceptX>`++ exposes `<public property / operation>`  

---

### Behaviors

#### Scenario Outline: `<outcome-oriented name>`

*Given* a ++`<ConceptA>`++ with {`<field_1>`}  
  *And* the ++`<ConceptB>`++ for that ++`<ConceptA>`++ is {`<field_2>`}  
*When* the **`<Actor>`** `<action>`  
*Then* the ++`<result concept>`++ `<outcome>` is visible on the public interface  
  *And* a ++`<related concept>`++ shows {`<field_3>`}

### Examples

| scenario   | `<field_1>` | `<field_2>` | `<field_3>` |
|------------|-------------|-------------|-------------|
| ++Scenario 1++ | `<value>`   | `<value>`   | `<value>`   |
| ++Scenario 2++ | `<value>`   | `<value>`   | `<value>`   |

> Markdown keeps examples tables for documentation. Code wires values via `{Type}ExampleFactory` (AI fills helper/story method bodies). Do not copy inventable `examples: [{ … }]` literals into code story files.

#### Scenario: `<variation — delta from main flow>`

*Given* … (only the delta from the main flow)  
*When* …  
*Then* …

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
#     examples/                          # epic-shared ExampleFactory values (when shared)
#     givens.py                          # epic-shared background Given helpers
#     whens.py                           # epic-shared When helpers (when shared)
#     {sub-epic-verb-noun}/              # omit this level when the story file lives under epic/
#       examples/{topic}_examples.py     # lowest shared folder for this story's fixtures
#       givens.py                        # background Given helpers for this sub-epic/story
#       whens.py                         # When helpers for this sub-epic/story
#       {story_snake_slug}.{tier}.py     # story file — one GWT file per story per tier
#
# # Shared helper (copy once per tests/ tree — full source inlined below)
# story_test: tests/story_test.py
#
# # Naming rules
# - Epic / SubEpic folders → kebab-case verb-noun (Sign Up → sign-up)
# - Story test file        → {story_snake_slug}.{tier}.py at epic or sub-epic — NO {story}/ folder
# - Tier                   → file extension segment (.e2e.py, .front-end.py, .back-end.py)
# - Examples module        → examples/{topic}_examples.py (concrete values, not inline in GWT)
# - Epic helper (py only)  → {epic_snake}_helper.py — sole snake_case naming exception
# - Forbidden              → {story}/ folders, *_story.*, *_test_helper.* splits
# ```
#
# Pattern: mirror sign-up-create-account.e2e.ts — @story / @background / @scenario (pytest via story_test).

from __future__ import annotations

from expects import be_none, equal, expect

from domain.{bounded_context}.runtime import {AppPascal}E2e, config
from domain.{bounded_context}.{aggregate_snake} import (
    {AggregatePascal},
    {ERROR_CONSTANT}_MESSAGE,
)
from examples.{story_verb_noun}_examples import (
    invalid_{field}_example,
    valid_{aggregate}_example,
    valid_{field}_example,
)
from givens import {background_given_fn}
from story_test import ScenarioSteps, after_all, background, before_all, scenario, story
from whens import {primary_when_fn}


@story("{Story Verb-Noun}")
def {story_snake_slug}_story() -> None:
    {app_camel}: {AppPascal} | None = None
    {aggregate_camel}: {AggregatePascal} | None = None

    @before_all
    def boot() -> None:
        nonlocal {app_camel}
        {app_camel} = {AppPascal}E2e.initialize(config)

    @after_all
    def shutdown() -> None:
        nonlocal {app_camel}
        if {app_camel} is not None:
            {app_camel}.close()

    def _primary_when() -> None:
        nonlocal {aggregate_camel}
        {aggregate_camel} = {primary_when_fn}({app_camel})

    def _invalid_input() -> None:
        assert {aggregate_camel} is not None
        {aggregate_camel}.{field} = invalid_{field}_example
        {aggregate_camel}.validate()

    def _valid_input() -> None:
        assert {aggregate_camel} is not None
        {aggregate_camel}.{field} = valid_{field}_example
        {aggregate_camel}.validate()

    def _submit() -> None:
        assert {aggregate_camel} is not None
        {aggregate_camel}.{field} = valid_{aggregate}_example.{field}
        {aggregate_camel}.{operation}()

    def _expect_error() -> None:
        assert {aggregate_camel} is not None
        expect({aggregate_camel}.errors.{field}).to(equal({ERROR_CONSTANT}_MESSAGE))

    def _expect_state() -> None:
        assert {app_camel} is not None and {aggregate_camel} is not None
        {entity_camel} = {app_camel}.{repository}().load({aggregate_camel})
        expect({entity_camel}.is_at_{state}("{StateName}")).to(equal(True))

    @background
    def shared_background(given) -> None:
        given("{background given step}", lambda: {background_given_fn}({app_camel}))

        @scenario("{validation branch while typing}")
        def validation_branch(steps: ScenarioSteps) -> None:
            steps.when("{primary when step}", _primary_when).and_(
                "{follow-on when step}",
                _invalid_input,
            )
            steps.then("{validation message on domain object}", _expect_error)

        @scenario("{validation clears when input conforms}")
        def validation_clears(steps: ScenarioSteps) -> None:
            steps.when("{primary when step}", _primary_when).and_(
                "{prior invalid state}",
                _invalid_input,
            )
            steps.when("{corrective action}", _valid_input)
            steps.then("{error cleared on domain object}", lambda: expect(
                {aggregate_camel}.errors.{field}
            ).to(be_none))

        @scenario("{main-flow outcome}")
        def main_flow(steps: ScenarioSteps) -> None:
            steps.when("{primary when step}", _primary_when)
            steps.when("{submit operation on domain object}", _submit)
            steps.then("{post-condition on loaded aggregate}", _expect_state)


## story_test.py

# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Given / When / Then helpers (pytest). Copy to tests/story_test.py once per tests/ tree.
#
# ```
# file: tests/story_test.py
# ```

from __future__ import annotations

import re
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Callable

import pytest

StepFn = Callable[[], None]


class WhenChain:
    def __init__(self, whens: list[StepFn]) -> None:
        self._whens = whens

    def and_(self, _text: str, fn: StepFn) -> WhenChain:
        self._whens.append(fn)
        return self


class ThenChain:
    def __init__(self, thens: list[tuple[str, StepFn]]) -> None:
        self._thens = thens

    def and_(self, text: str, fn: StepFn) -> ThenChain:
        self._thens.append((text, fn))
        return self


class ScenarioSteps:
    """Step registrar for @scenario bodies — mirrors TS scenario(({ when, then }) => …)."""

    def __init__(self) -> None:
        self._givens: list[StepFn] = []
        self._whens: list[StepFn] = []
        self._thens: list[tuple[str, StepFn]] = []

    def given(self, _text: str, fn: StepFn) -> None:
        self._givens.append(fn)

    def when(self, _text: str, fn: StepFn) -> WhenChain:
        self._whens.append(fn)
        return WhenChain(self._whens)

    def then(self, text: str, fn: StepFn) -> ThenChain:
        self._thens.append((text, fn))
        return ThenChain(self._thens)


class GivenRegistrar:
    def __init__(self, givens: list[StepFn]) -> None:
        self._givens = givens

    def __call__(self, _text: str, fn: StepFn) -> None:
        self._givens.append(fn)


@dataclass
class _ScenarioDef:
    name: str
    build: Callable[[ScenarioSteps], None]


@dataclass
class _StoryBuilder:
    name: str
    before_all_hooks: list[StepFn] = field(default_factory=list)
    after_all_hooks: list[StepFn] = field(default_factory=list)
    background_givens: list[StepFn] = field(default_factory=list)
    scenarios: list[_ScenarioDef] = field(default_factory=list)


_builder_ctx: ContextVar[_StoryBuilder | None] = ContextVar("_story_builder", default=None)
_background_ctx: ContextVar[list[_ScenarioDef] | None] = ContextVar("_background_scenarios", default=None)


def _slug(value: str) -> str:
    slug = re.sub(r"[^0-9a-z]+", "_", value.strip().lower()).strip("_")
    return slug or "story"


def story(name: str):
    """@story('Story title') — registers pytest examples at import (Vitest-style)."""

    def decorator(body: Callable[[], None]) -> Callable[[], None]:
        builder = _StoryBuilder(name=name)
        token = _builder_ctx.set(builder)
        try:
            body()
        finally:
            _builder_ctx.reset(token)
        _install_pytest(builder, body.__module__)
        return body

    return decorator


def before_all(fn: StepFn) -> StepFn:
    builder = _builder_ctx.get()
    if builder is None:
        raise RuntimeError("@before_all must be used inside @story")
    builder.before_all_hooks.append(fn)
    return fn


def after_all(fn: StepFn) -> StepFn:
    builder = _builder_ctx.get()
    if builder is None:
        raise RuntimeError("@after_all must be used inside @story")
    builder.after_all_hooks.append(fn)
    return fn


def background(fn: Callable[[GivenRegistrar], None]) -> Callable[[GivenRegistrar], None]:
    """@background — nest @scenario definitions inside; pass shared Given steps."""

    builder = _builder_ctx.get()
    if builder is None:
        raise RuntimeError("@background must be used inside @story")

    registrar = GivenRegistrar([])
    scenarios: list[_ScenarioDef] = []
    bg_token = _background_ctx.set(scenarios)
    try:
        fn(registrar)
    finally:
        _background_ctx.reset(bg_token)

    builder.background_givens.extend(registrar._givens)
    builder.scenarios.extend(scenarios)
    return fn


def scenario(name: str):
    """@scenario('Outcome title') — body receives ScenarioSteps."""

    def decorator(build: Callable[[ScenarioSteps], None]) -> Callable[[ScenarioSteps], None]:
        scenarios = _background_ctx.get()
        if scenarios is None:
            raise RuntimeError("@scenario must be used inside @background")
        scenarios.append(_ScenarioDef(name=name, build=build))
        return build

    return decorator


def _install_pytest(builder: _StoryBuilder, module_name: str) -> None:
    import sys

    module = sys.modules.get(module_name)
    if module is None:
        return

    story_slug = _slug(builder.name)
    fixture_name = f"_story_{story_slug}_lifecycle"

    @pytest.fixture(scope="module", name=fixture_name)
    def _lifecycle() -> None:
        for hook in builder.before_all_hooks:
            hook()
        yield
        for hook in builder.after_all_hooks:
            hook()

    setattr(module, fixture_name, _lifecycle)

    for scenario_def in builder.scenarios:
        steps = ScenarioSteps()
        scenario_def.build(steps)
        scenario_slug = _slug(scenario_def.name)

        for then_index, (label, then_fn) in enumerate(steps._thens):
            step_label = f"Then {label}" if then_index == 0 else label
            test_name = f"test_{story_slug}_{scenario_slug}_{then_index}"

            def _make_test(
                then: StepFn,
                bg: tuple[StepFn, ...],
                given: tuple[StepFn, ...],
                when: tuple[StepFn, ...],
                fix: str,
                doc: str,
            ) -> Callable[[], None]:
                @pytest.mark.usefixtures(fix)
                def _test() -> None:
                    for fn in (*bg, *given, *when):
                        fn()
                    then()

                _test.__doc__ = doc
                return _test

            test_fn = _make_test(
                then_fn,
                tuple(builder.background_givens),
                tuple(steps._givens),
                tuple(steps._whens),
                fixture_name,
                f"{scenario_def.name} — {step_label}",
            )
            test_fn.__name__ = test_name
            setattr(module, test_name, test_fn)

See examples in `context_tools/stories/examples/` if needed.