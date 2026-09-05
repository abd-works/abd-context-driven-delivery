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
# Pattern: story_test machinery only — lifecycle, background(), scenario(), inline step bodies.

from __future__ import annotations

from expects import be_above, be_none, equal, expect

from domain.{bounded_context}.runtime import {AppPascal}E2e, config
from domain.{bounded_context}.{aggregate_snake} import (
    {AggregatePascal},
    {ERROR_CONSTANT}_MESSAGE,
)
from story_test import after_all, background, before_all, scenario, story


def _{story_snake_slug}_story() -> None:
    {app_camel}: {AppPascal} | None = None
    {aggregate_camel}: {AggregatePascal} | None = None

    def boot() -> None:
        nonlocal {app_camel}
        {app_camel} = {AppPascal}E2e.initialize(config)

    def shutdown() -> None:
        nonlocal {app_camel}
        if {app_camel} is not None:
            {app_camel}.close()

    before_all(boot)
    after_all(shutdown)

    def shared(given) -> None:
        given(
            "{background given step}",
            lambda: {app_camel}.{background_operation}(),
        )

        def surface_check(steps) -> None:
            def when_primary() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def surface_then() -> None:
                assert {aggregate_camel} is not None
                {aggregate_camel}.{field} = ""
                {aggregate_camel}.validate()
                expect(len({aggregate_camel}.errors.{field})).to(be_above(0))

            steps.when("{primary when step}", when_primary)
            steps.then("{observable surface outcome}", surface_then)

        scenario("{surface check — e.g. rules visible}", surface_check)

        def validation_branch(steps) -> None:
            def when_primary() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def when_invalid() -> None:
                {aggregate_camel}.{field} = {invalid_value}
                {aggregate_camel}.validate()

            steps.when("{primary when step}", when_primary).and_(
                "{follow-on when step}",
                when_invalid,
            )
            steps.then(
                "{validation message on domain object}",
                lambda: expect({aggregate_camel}.errors.{field}).to(
                    equal({ERROR_CONSTANT}_MESSAGE)
                ),
            )

        scenario("{validation branch while typing}", validation_branch)

        def validation_clears(steps) -> None:
            def when_primary() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def when_invalid() -> None:
                {aggregate_camel}.{field} = {invalid_value}
                {aggregate_camel}.validate()

            def when_valid() -> None:
                {aggregate_camel}.{field} = {valid_value}
                {aggregate_camel}.validate()

            steps.when("{primary when step}", when_primary).and_(
                "{prior invalid state}",
                when_invalid,
            )
            steps.when("{corrective action}", when_valid)
            steps.then(
                "{error cleared on domain object}",
                lambda: expect({aggregate_camel}.errors.{field}).to(be_none),
            )

        scenario("{validation clears when input conforms}", validation_clears)

        def main_flow(steps) -> None:
            def when_primary() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def when_submit() -> None:
                {aggregate_camel}.{field} = {valid_aggregate_value}
                {aggregate_camel}.{operation}()

            steps.when("{primary when step}", when_primary)
            steps.when("{submit operation on domain object}", when_submit)
            steps.then(
                "{post-condition on loaded aggregate}",
                lambda: expect(
                    {app_camel}.{repository}().load({aggregate_camel}).is_at_{state}(
                        "{StateName}"
                    )
                ).to(equal(True)),
            )

        scenario("{main-flow outcome}", main_flow)

    background(shared)


story("{Story Verb-Noun}", _{story_snake_slug}_story)


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
#
# Same surface as story-test.ts: story(), before_all(), after_all(), background(), scenario().

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
    """Passed to scenario() — mirrors TS ({ when, then }) => …."""

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
    """Register one story — same role as story() in story-test.ts."""
    import inspect

    module_name = inspect.getmodule(body).__name__ if inspect.getmodule(body) else "__main__"
    builder = _StoryBuilder(name=name, module_name=module_name)
    token = _builder_ctx.set(builder)
    try:
        body()
    finally:
        _builder_ctx.reset(token)
    _install_pytest(builder)


def before_all(fn: StepFn) -> StepFn:
    """Call inside story() — same role as beforeAll() in Vitest."""
    builder = _builder_ctx.get()
    if builder is None:
        raise RuntimeError("before_all() must be called inside story()")
    builder.before_all_hooks.append(fn)
    return fn


def after_all(fn: StepFn) -> StepFn:
    """Call inside story() — same role as afterAll() in Vitest."""
    builder = _builder_ctx.get()
    if builder is None:
        raise RuntimeError("after_all() must be called inside story()")
    builder.after_all_hooks.append(fn)
    return fn


def background(build: Callable[[GivenRegistrar], None]) -> None:
    """Call inside story() — register shared Given steps and nested scenario() calls."""
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


def scenario(name: str, build: Callable[[ScenarioSteps], None]) -> None:
    """Call inside background() — same role as scenario() in story-test.ts."""
    scenarios = _background_ctx.get()
    if scenarios is None:
        raise RuntimeError("scenario() must be called inside background()")
    scenarios.append(_ScenarioDef(name=name, build=build))


def _install_pytest(builder: _StoryBuilder) -> None:
    import sys

    module = sys.modules.get(builder.module_name)
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