"""Minimal harness write-vehicle decorators used by action kits."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def _mark(kind: str, name: str | None = None):
    def apply(fn: Callable[..., Any]) -> Callable[..., Any]:
        writes = list(getattr(fn, "_harness_writes", []))
        writes.append((kind, name))
        fn._harness_writes = writes
        return fn

    return apply


def dev_only(cls: type) -> type:
    cls._dev_only = True  # type: ignore[attr-defined]
    return cls


def prompt(fn: Callable[..., Any] | None = None, *, name: str | None = None):
    deco = _mark("prompt", name)
    return deco if fn is None else deco(fn)
