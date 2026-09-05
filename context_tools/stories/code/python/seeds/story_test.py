"""Given / When / Then helpers (pytest). Copy to tests/story_test.py."""

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


def scenario(name: str, build: Callable[[ScenarioSteps], None]) -> None:
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
