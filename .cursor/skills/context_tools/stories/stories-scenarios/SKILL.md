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
#     {sub-epic-verb-noun}/              # omit when the story file lives under epic/
#       {story_snake_slug}.{tier}.py     # one GWT file per story per tier
#
# # Machinery (copy once per tests/ tree — full source inlined below)
# story_test: tests/story_test.py
#
# # Naming rules
# - Epic / SubEpic folders → kebab-case verb-noun (Sign Up → sign-up)
# - Story test file        → {story_snake_slug}.{tier}.py at epic or sub-epic — NO {story}/ folder
# - Tier                   → file extension segment (.e2e.py, .front-end.py, .back-end.py)
# - Forbidden              → {story}/ folders, *_story.*, *_test_helper.* splits
# ```
#
# Pattern: story_test.py extends Mamba with given / when / then — boot in before_all / after_all.

from __future__ import annotations

from domain.{bounded_context}.runtime import {AppPascal}E2e, config
from domain.{bounded_context}.{aggregate_snake} import {AggregatePascal}
from story_test import after_all, background, before_all, scenario, story


story("{Story Verb-Noun}", _story)


def _story() -> None:
    {app_camel}: {AppPascal} | None = None
    {aggregate_camel}: {AggregatePascal} | None = None

    def boot() -> None:
        nonlocal {app_camel}
        {app_camel} = {AppPascal}E2e.initialize(config)

    before_all(boot)

    def teardown() -> None:
        if {app_camel}:
            {app_camel}.close()

    after_all(teardown)

    def build_background(given) -> None:
        def background_given() -> None:
            {app_camel}.{background_operation}()

        given("{background given step}", background_given)

        def surface_check(given, when, then) -> None:
            def primary_when() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def observable_outcome() -> None:
                pass  # Assert {observable surface outcome}

            when("{primary when step}", primary_when)
            then("{observable surface outcome}", observable_outcome)

        scenario("{surface check — e.g. rules visible}", surface_check)

        def validation_branch(given, when, then) -> None:
            def primary_when() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def follow_on_when() -> None:
                {aggregate_camel}.{field} = {invalid_value}
                {aggregate_camel}.validate()

            def validation_message() -> None:
                pass  # Assert {validation message on domain object}

            when("{primary when step}", primary_when)
            when("{follow-on when step}", follow_on_when)
            then("{validation message on domain object}", validation_message)

        scenario("{validation branch while typing}", validation_branch)

        def validation_clears(given, when, then) -> None:
            def primary_when() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def prior_invalid_state() -> None:
                {aggregate_camel}.{field} = {invalid_value}
                {aggregate_camel}.validate()

            def corrective_action() -> None:
                {aggregate_camel}.{field} = {valid_value}
                {aggregate_camel}.validate()

            def error_cleared() -> None:
                pass  # Assert {error cleared on domain object}

            when("{primary when step}", primary_when)
            when("{prior invalid state}", prior_invalid_state)
            when("{corrective action}", corrective_action)
            then("{error cleared on domain object}", error_cleared)

        scenario("{validation clears when input conforms}", validation_clears)

        def main_flow(given, when, then) -> None:
            def primary_when() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def submit_operation() -> None:
                {aggregate_camel}.{field} = {valid_aggregate_value}
                {aggregate_camel}.{operation}()

            def post_condition() -> None:
                pass  # Assert {post-condition on loaded aggregate}

            when("{primary when step}", primary_when)
            when("{submit operation on domain object}", submit_operation)
            then("{post-condition on loaded aggregate}", post_condition)

        scenario("{main-flow outcome}", main_flow)

    background(build_background)


## story_test.py

# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Given / When / Then on Mamba. Copy to tests/story_test.py once per tests/ tree.
#
# ```
# file: tests/story_test.py
# ```
#
# Extends Mamba: story → description, background given → shared setup, scenario when → before, then → it.

from __future__ import annotations

import inspect
import re
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Callable

StepFn = Callable[[], None]


class ScenarioSteps:
    def __init__(self) -> None:
        self._givens: list[StepFn] = []
        self._whens: list[StepFn] = []
        self._thens: list[tuple[str, StepFn]] = []

    def given(self, _text: str, fn: StepFn) -> None:
        self._givens.append(fn)

    def when(self, _text: str, fn: StepFn) -> None:
        self._whens.append(fn)

    def then(self, text: str, fn: StepFn) -> None:
        self._thens.append((text, fn))


class GivenRegistrar:
    def __init__(self, givens: list[StepFn]) -> None:
        self._givens = givens

    def __call__(self, _text: str, fn: StepFn) -> None:
        self._givens.append(fn)


@dataclass
class _ScenarioDef:
    name: str
    givens: tuple[StepFn, ...]
    whens: tuple[StepFn, ...]
    thens: tuple[tuple[str, StepFn], ...]


@dataclass
class _StoryBuilder:
    name: str
    module_name: str
    before_all_hooks: list[StepFn] = field(default_factory=list)
    after_all_hooks: list[StepFn] = field(default_factory=list)
    background_givens: list[StepFn] = field(default_factory=list)
    scenarios: list[_ScenarioDef] = field(default_factory=list)


_builder_ctx: ContextVar[_StoryBuilder | None] = ContextVar("_story_builder", default=None)
_background_ctx: ContextVar[list[_ScenarioDef] | None] = ContextVar("_background_scenarios", default=None)


def _slug(value: str) -> str:
    slug = re.sub(r"[^0-9a-z]+", "_", value.strip().lower()).strip("_")
    return slug or "story"


def story(name: str, body: Callable[[], None]) -> None:
    """Register one story — Mamba description group."""
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        raise RuntimeError("story() must be called at module scope")
    module_globals = frame.f_back.f_globals
    module_name = str(module_globals.get("__name__", "__main__"))
    builder = _StoryBuilder(name=name, module_name=module_name)
    token = _builder_ctx.set(builder)
    try:
        body()
    finally:
        _builder_ctx.reset(token)
    _install_mamba(builder, module_globals)


def before_all(fn: StepFn) -> StepFn:
    builder = _builder_ctx.get()
    if builder is None:
        raise RuntimeError("before_all() must be called inside story()")
    builder.before_all_hooks.append(fn)
    return fn


def after_all(fn: StepFn) -> StepFn:
    builder = _builder_ctx.get()
    if builder is None:
        raise RuntimeError("after_all() must be called inside story()")
    builder.after_all_hooks.append(fn)
    return fn


def background(build: Callable[[GivenRegistrar], None]) -> None:
    builder = _builder_ctx.get()
    if builder is None:
        raise RuntimeError("background() must be called inside story()")

    registrar = GivenRegistrar([])
    scenarios: list[_ScenarioDef] = []
    bg_token = _background_ctx.set(scenarios)
    try:
        build(registrar)
    finally:
        _background_ctx.reset(bg_token)

    builder.background_givens.extend(registrar._givens)
    builder.scenarios.extend(scenarios)


def scenario(name: str, build: Callable[..., None]) -> None:
    scenarios = _background_ctx.get()
    if scenarios is None:
        raise RuntimeError("scenario() must be called inside background()")

    steps = ScenarioSteps()
    params = inspect.signature(build).parameters
    kwargs: dict[str, object] = {}
    if "given" in params:
        kwargs["given"] = steps.given
    if "when" in params:
        kwargs["when"] = steps.when
    if "then" in params:
        kwargs["then"] = steps.then
    build(**kwargs)
    scenarios.append(
        _ScenarioDef(
            name=name,
            givens=tuple(steps._givens),
            whens=tuple(steps._whens),
            thens=tuple(steps._thens),
        )
    )


def _example_name(prefix: str, label: str) -> str:
    return f"{prefix} {label}"


def _make_example(label: str, prefix: str, body: StepFn) -> Callable[[object], None]:
    name = _example_name(prefix, label)

    def _test(_ctx: object) -> None:
        body()

    _test.__name__ = name.replace(" ", "_")
    _test._example = True  # type: ignore[attr-defined]
    _test._example_name = name  # type: ignore[attr-defined]
    _test._tags = []  # type: ignore[attr-defined]
    _test._pending = False  # type: ignore[attr-defined]
    return _test


def _make_scenario_class(
    scenario_def: _ScenarioDef,
    background_givens: tuple[StepFn, ...],
) -> type:
    bg = background_givens
    given = scenario_def.givens
    when = scenario_def.whens

    def before_all(_ctx: object) -> None:
        for fn in (*bg, *given, *when):
            fn()

    before_all.__name__ = "before_all"

    attrs: dict[str, object] = {
        "_example_group": True,
        "_example_name": scenario_def.name,
        "_tags": [],
        "_pending": False,
        "_shared": False,
        "before_all": before_all,
    }

    for index, (label, then_fn) in enumerate(scenario_def.thens):
        prefix = "it Then" if index == 0 else "it"
        test = _make_example(label, prefix, then_fn)
        attrs[test.__name__] = test

    return type(f"Scenario_{_slug(scenario_def.name)}", (), attrs)


def _install_mamba(builder: _StoryBuilder, module_globals: dict[str, object]) -> None:
    story_slug = _slug(builder.name)
    bg = tuple(builder.background_givens)

    story_attrs: dict[str, object] = {
        "_example_group": True,
        "_example_name": builder.name,
        "_tags": [],
        "_pending": False,
        "_shared": False,
    }

    if builder.before_all_hooks:

        def story_before_all(_ctx: object) -> None:
            for hook in builder.before_all_hooks:
                hook()

        story_before_all.__name__ = "before_all"
        story_attrs["before_all"] = story_before_all

    if builder.after_all_hooks:

        def story_after_all(_ctx: object) -> None:
            for hook in builder.after_all_hooks:
                hook()

        story_after_all.__name__ = "after_all"
        story_attrs["after_all"] = story_after_all

    for scenario_def in builder.scenarios:
        nested = _make_scenario_class(scenario_def, bg)
        story_attrs[nested.__name__] = nested

    story_class = type(f"Story_{story_slug}", (), story_attrs)
    module_globals[story_class.__name__] = story_class

See examples in `context_tools/stories/examples/` if needed.