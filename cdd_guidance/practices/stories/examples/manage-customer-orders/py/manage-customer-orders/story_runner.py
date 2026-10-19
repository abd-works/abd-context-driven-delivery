"""Generic scenario runner - the ONLY test-framework glue.

Every tier reuses this function; tier files just wire a Story constant, a
scenario key, and a factory that produces the tier's `TierImpl`. The runner:

1. Validates that every step string in the scenario has a matching key in
   `tier.given` / `tier.when` / `tier.then` - missing keys fail with the
   exact string and phase, so the author knows what's unimplemented.
2. Walks `given`, then each interaction's `when` steps, then dispatches one
   pytest test per `then` step (so each observable outcome is its own row).
3. Runs `cleanup` after every scenario, even on failure.

Sync and async step bodies both work - the runner awaits when needed.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Callable, Dict, Type

from story_types import Scenario, StepFn, TierImpl


class ScenarioRunner:
    def _maybe_await(self, result: object) -> None:
        if inspect.isawaitable(result):
            asyncio.get_event_loop().run_until_complete(result)  # type: ignore[arg-type]

    def _dispatch(self, step: str, table: Dict[str, StepFn], phase: str) -> None:
        fn = table.get(step)
        if fn is None:
            raise KeyError(
                f"Tier is missing a {phase!r} implementation for step {step!r}. "
                f"Add it to `tier.{phase}[{step!r}]`."
            )
        self._maybe_await(fn())

    def _label(self, keyword: str, index: int, step: str) -> str:
        return f"{keyword} {step}" if index == 0 else step

    def _slug(self, name: str) -> str:
        out = []
        prev_alnum = False
        for ch in name:
            if ch.isalnum():
                out.append(ch)
                prev_alnum = True
                continue
            if prev_alnum:
                out.append("_")
            prev_alnum = False
        return "".join(out).strip("_") or "scenario"

    def scenario_class(
        self,
        scenario: Scenario,
        make_tier: Callable[[], TierImpl],
    ) -> Type:
        """One pytest class per scenario; one `test_*` method per `then` step."""
        tier_holder: Dict[str, TierImpl] = {}
        runner = self

        def setup_class() -> None:
            tier = make_tier()
            tier_holder["tier"] = tier
            for step in scenario["given"]:
                runner._dispatch(step, tier["given"], "given")
            for interaction in scenario["interactions"]:
                for step in interaction["when"]:
                    runner._dispatch(step, tier["when"], "when")

        def teardown_class() -> None:
            tier = tier_holder.get("tier")
            if tier is not None:
                runner._maybe_await(tier["cleanup"]())

        methods: Dict[str, Callable[..., None]] = {}
        for interaction_index, interaction in enumerate(scenario["interactions"]):
            for then_index, step in enumerate(interaction["then"]):
                method_name = f"test_then_{interaction_index}_{then_index}"
                step_value = step

                def _method(self, _step: str = step_value) -> None:  # noqa: ANN001
                    runner._dispatch(_step, tier_holder["tier"]["then"], "then")

                _method.__doc__ = runner._label("Then", then_index, step_value)
                methods[method_name] = _method

        return type(
            f"Test_{self._slug(scenario['name'])}",
            (object,),
            {
                "setup_class": staticmethod(setup_class),
                "teardown_class": staticmethod(teardown_class),
                **methods,
            },
        )

    def run(self, scenario: Scenario, make_tier: Callable[[], TierImpl]) -> None:
        """Emit one pytest class per scenario; one `test_*` method per `then` step.

        Call from a tier test file at module scope; pytest discovers the emitted
        class automatically.
        """
        cls = self.scenario_class(scenario, make_tier)
        frame = inspect.stack()[1].frame
        caller_globals = frame.f_globals
        caller_globals[cls.__name__] = cls
        cls.__module__ = caller_globals.get("__name__", cls.__module__)
