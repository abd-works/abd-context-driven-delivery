"""Given / When / Then helpers (Mamba/RSpec). Copy to tests/story_test.py."""

from __future__ import annotations

from typing import Callable

from mamba import before, context, description, it

BackgroundGiven = Callable[[], None]
StepFn = Callable[[], None]

_active_background: list[BackgroundGiven] = []


def story(name: str, body: Callable[[], None]) -> None:
    with description(name):
        body()


def background(
    body: Callable[[dict[str, Callable[[str, StepFn], None]]], None],
) -> None:
    givens: list[BackgroundGiven] = []

    def given(_text: str, fn: StepFn) -> None:
        givens.append(fn)

    body({"given": given})
    global _active_background
    _active_background = givens


def scenario(name: str, body: Callable[[dict[str, Callable[..., object]]], None]) -> None:
    givens: list[StepFn] = []
    whens: list[StepFn] = []
    thens: list[tuple[str, StepFn]] = []

    class WhenChain:
        def and_(self, _text: str, fn: StepFn) -> WhenChain:
            whens.append(fn)
            return self

    class ThenChain:
        def and_(self, text: str, fn: StepFn) -> ThenChain:
            thens.append((text, fn))
            return self

    when_chain = WhenChain()
    then_chain = ThenChain()

    def given(_text: str, fn: StepFn) -> None:
        givens.append(fn)

    def when(_text: str, fn: StepFn) -> WhenChain:
        whens.append(fn)
        return when_chain

    def then(text: str, fn: StepFn) -> ThenChain:
        thens.append((text, fn))
        return then_chain

    with context(name):
        body({"given": given, "when": when, "then": then})

        @before.all
        def _run_background_given_and_when() -> None:
            for fn in _active_background + givens + whens:
                fn()

        for index, (text, fn) in enumerate(thens):
            label = f"Then {text}" if index == 0 else text

            def _example(step: StepFn = fn) -> None:
                step()

            with it(label):
                _example()
