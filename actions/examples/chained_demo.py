"""Minimal demo for testing framework chain navigation in isolation.

Uses add_action_wrapper directly — no dependency on @sketch, @grill_with_context,
or any other domain decorator. Two stub wrappers (alpha, beta) chain onto a base
action so chain_navigation injection can be verified without importing other modules.
"""
from __future__ import annotations

from actions.action import ActionRunner, action, add_action_wrapper, require_action
from tools.tool import Toolset, tool, toolset


def _alpha_session(self) -> str:  # type: ignore[misc]
    """Alpha wrapper instructions."""
    return "alpha done"


def _beta_session(self) -> str:  # type: ignore[misc]
    """Beta wrapper instructions."""
    return "beta done"


def alpha(func):  # type: ignore[misc]
    require_action(func, "alpha")
    add_action_wrapper(func, name="alpha", chained_action=_alpha_session)
    return func


def beta(func):  # type: ignore[misc]
    require_action(func, "beta")
    add_action_wrapper(func, name="beta", chained_action=_beta_session)
    return func


@toolset
class ChainedDemo:
    """Two-wrapper chain: alpha -> beta -> generate."""

    @tool
    def do_work(self) -> str:
        """Perform a unit of work."""
        return "work done"

    @alpha
    @beta
    @action
    def generate(self) -> str:
        """Base action body."""
        self.do_work()
        return "generate done"

    @action
    def standalone(self) -> str:
        """Plain action with no wrappers."""
        self.do_work()
        return "standalone done"


@toolset
class SingleWrapperDemo:
    """One-wrapper chain: alpha -> generate only (no beta)."""

    @tool
    def do_work(self) -> str:
        """Perform a unit of work."""
        return "work done"

    @alpha
    @action
    def generate(self) -> str:
        """Base action body."""
        self.do_work()
        return "generate done"


def _static_session(self) -> str:  # type: ignore[misc]
    """Static wrapper instructions."""
    return "static done"


def static_wrapper(func):  # type: ignore[misc]
    require_action(func, "static_wrapper")
    add_action_wrapper(
        func,
        name="static_wrapper",
        chained_action=_static_session,
        static_kwargs={"key": "value", "num": 42},
    )
    return func


class SuperDelegationBase(Toolset):
    """Base toolset whose generate action is inherited via super()."""

    @tool
    def do_work(self) -> str:
        """Perform a unit of work."""
        return "work done"

    @action
    def generate(self) -> str:
        """Base generate instructions."""
        self.do_work()
        return "generate done"


SuperDelegationBase._is_toolset = True  # type: ignore[attr-defined]
ActionRunner.instance().validate_toolset(SuperDelegationBase)


class SuperDelegationChild(SuperDelegationBase):
    """Child that delegates to super().generate() and adds a wrapper on top."""

    @alpha
    @action
    def generate(self) -> str:
        """Child generate instructions."""
        super().generate()
        return "child generate done"


SuperDelegationChild._is_toolset = True  # type: ignore[attr-defined]
ActionRunner.instance().validate_toolset(SuperDelegationChild)


class AutoSuperChild(SuperDelegationBase):
    """Child with empty body — ActionExpander auto-delegates to parent generate."""

    @alpha
    @action
    def generate(self) -> str: ...


AutoSuperChild._is_toolset = True  # type: ignore[attr-defined]
ActionRunner.instance().validate_toolset(AutoSuperChild)


class AutoSuperWithReturn(SuperDelegationBase):
    """Empty steps but custom return — parent tools/prose, child result template."""

    @action
    def generate(self) -> str:
        ...
        return "child result only"


AutoSuperWithReturn._is_toolset = True  # type: ignore[attr-defined]
ActionRunner.instance().validate_toolset(AutoSuperWithReturn)


@toolset
class StaticKwargsDemo:
    """Wrapper with static_kwargs — verifies manifest chain dict serialization."""

    @static_wrapper
    @action
    def generate(self) -> str:
        """Base action body."""
        return "done"
