"""Given / When / Then on Mamba. Copy to tests/story_test.py."""

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
