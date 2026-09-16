"""Member marks for markdown and MCP deploy."""
from __future__ import annotations

from typing import Any, Callable, TypeVar

_F = TypeVar("_F", bound=Callable[..., Any])


def _apply_flag(func: Any, flag: str, name: str | None = None) -> Any:
    setattr(func, flag, True)
    if name is not None:
        setattr(func, f"{flag}_name", name)
    return func


def skill(fn: _F | str | None = None, name: str | None = None) -> Any:
    if callable(fn):
        return _apply_flag(fn, "_skill", name)
    if isinstance(fn, str):
        label = fn

        def decorator(func: _F) -> _F:
            return _apply_flag(func, "_skill", label)

        return decorator

    def decorator(func: _F) -> _F:
        return _apply_flag(func, "_skill", name)

    return decorator


def command(fn: _F | str | None = None, name: str | None = None) -> Any:
    if callable(fn):
        return _apply_flag(fn, "_command", name)
    if isinstance(fn, str):
        label = fn

        def decorator(func: _F) -> _F:
            return _apply_flag(func, "_command", label)

        return decorator

    def decorator(func: _F) -> _F:
        return _apply_flag(func, "_command", name)

    return decorator


def rules(fn: _F | None = None) -> Any:
    if callable(fn):
        return _apply_flag(fn, "_rules")

    def decorator(func: _F) -> _F:
        return _apply_flag(func, "_rules")

    return decorator


def mcp(fn: _F | None = None) -> Any:
    if callable(fn):
        return _apply_flag(fn, "_mcp")

    def decorator(func: _F) -> _F:
        return _apply_flag(func, "_mcp")

    return decorator


def hook(fn: _F | None = None, event: str | None = None) -> Any:
    if callable(fn):
        return _apply_flag(fn, "_hook", event)

    def decorator(func: _F) -> _F:
        return _apply_flag(func, "_hook", event)

    return decorator


def agent(fn: _F | str | None = None, name: str | None = None) -> Any:
    if callable(fn):
        return _apply_flag(fn, "_agent", name)
    if isinstance(fn, str):
        label = fn

        def decorator(func: _F) -> _F:
            return _apply_flag(func, "_agent", label)

        return decorator

    def decorator(func: _F) -> _F:
        return _apply_flag(func, "_agent", name)

    return decorator


def agent_guidance(fn: _F | str | None = None, name: str | None = None) -> Any:
    if callable(fn):
        return _apply_flag(fn, "_agent_guidance", name)
    if isinstance(fn, str):
        label = fn

        def decorator(func: _F) -> _F:
            return _apply_flag(func, "_agent_guidance", label)

        return decorator

    def decorator(func: _F) -> _F:
        return _apply_flag(func, "_agent_guidance", name)

    return decorator
