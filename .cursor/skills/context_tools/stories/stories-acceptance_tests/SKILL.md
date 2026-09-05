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
# Pattern: story_test.py extends Mamba — same shape as scenario-template.ts + story-test.ts.

from __future__ import annotations

from expects import be_above, be_none, equal, expect

from domain.{bounded_context}.runtime import {AppPascal}E2e, config
from domain.{bounded_context}.{aggregate_snake} import (
    {AggregatePascal},
    {ERROR_CONSTANT}_MESSAGE,
)
from story_test import after_all, background, before_all, scenario, story


story("{Story Verb-Noun}", lambda: _story())


def _story() -> None:
    {app_camel}: list[{AppPascal} | None] = [None]
    {aggregate_camel}: list[{AggregatePascal} | None] = [None]

    before_all(lambda: {app_camel}.__setitem__(0, {AppPascal}E2e.initialize(config)))
    after_all(lambda: {app_camel}[0] and {app_camel}[0].close())

    background(
        lambda given: (
            given(
                "{background given step}",
                lambda: {app_camel}[0].{background_operation}(),
            ),
            scenario(
                "{surface check — e.g. rules visible}",
                lambda when, then: (
                    when(
                        "{primary when step}",
                        lambda: {aggregate_camel}.__setitem__(
                            0, {app_camel}[0].{primary_when_operation}()
                        ),
                    ),
                    then(
                        "{observable surface outcome}",
                        lambda: (
                            setattr({aggregate_camel}[0], "{field}", ""),
                            {aggregate_camel}[0].validate(),
                            expect(len({aggregate_camel}[0].errors.{field})).to(be_above(0)),
                        )[2],
                    ),
                ),
            ),
            scenario(
                "{validation branch while typing}",
                lambda when, then: (
                    when(
                        "{primary when step}",
                        lambda: {aggregate_camel}.__setitem__(
                            0, {app_camel}[0].{primary_when_operation}()
                        ),
                    ).and_(
                        "{follow-on when step}",
                        lambda: (
                            setattr({aggregate_camel}[0], "{field}", {invalid_value}),
                            {aggregate_camel}[0].validate(),
                        )[1],
                    ),
                    then(
                        "{validation message on domain object}",
                        lambda: expect({aggregate_camel}[0].errors.{field}).to(
                            equal({ERROR_CONSTANT}_MESSAGE)
                        ),
                    ),
                ),
            ),
            scenario(
                "{validation clears when input conforms}",
                lambda when, then: (
                    when(
                        "{primary when step}",
                        lambda: {aggregate_camel}.__setitem__(
                            0, {app_camel}[0].{primary_when_operation}()
                        ),
                    ).and_(
                        "{prior invalid state}",
                        lambda: (
                            setattr({aggregate_camel}[0], "{field}", {invalid_value}),
                            {aggregate_camel}[0].validate(),
                        )[1],
                    ),
                    when(
                        "{corrective action}",
                        lambda: (
                            setattr({aggregate_camel}[0], "{field}", {valid_value}),
                            {aggregate_camel}[0].validate(),
                        )[1],
                    ),
                    then(
                        "{error cleared on domain object}",
                        lambda: expect({aggregate_camel}[0].errors.{field}).to(be_none),
                    ),
                ),
            ),
            scenario(
                "{main-flow outcome}",
                lambda when, then: (
                    when(
                        "{primary when step}",
                        lambda: {aggregate_camel}.__setitem__(
                            0, {app_camel}[0].{primary_when_operation}()
                        ),
                    ),
                    when(
                        "{submit operation on domain object}",
                        lambda: (
                            setattr({aggregate_camel}[0], "{field}", {valid_aggregate_value}),
                            {aggregate_camel}[0].{operation}(),
                        )[1],
                    ),
                    then(
                        "{post-condition on loaded aggregate}",
                        lambda: expect(
                            {app_camel}[0]
                            .{repository}()
                            .load({aggregate_camel}[0])
                            .is_at_{state}('{StateName}')
                        ).to(equal(True)),
                    ),
                ),
            ),
        )
        or None,
    )


## story_test.py

# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Given / When / Then helpers (Mamba). Copy to tests/story_test.py once per tests/ tree.
#
# ```
# file: tests/story_test.py
# ```
#
# Same surface as story-test.ts — extends Mamba (story → description, scenario → nested group, then → it).

from __future__ import annotations

import inspect
import re
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Callable

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
    """Register one story — same role as story() in story-test.ts (Mamba description group)."""
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
    if "when" in params:
        kwargs["when"] = steps.when
    if "then" in params:
        kwargs["then"] = steps.then
    if "given" in params:
        kwargs["given"] = steps.given
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