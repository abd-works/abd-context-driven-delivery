"""Co-located markdown extract — thin seam over AssetLocator."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, TypeVar

from primitives.assets import Asset, AssetLocator

_F = TypeVar("_F", bound=Callable[..., Any])


def module_dir_for(host: Any) -> Path:
    context_guidance = getattr(host, "context_guidance", None)
    if context_guidance is not None:
        path = getattr(context_guidance, "module_dir", None)
        if path is not None:
            return Path(path)
    return Path(getattr(host, "module_dir", Path(".")))


class Markdown:
    def __init__(self, host: Any, label: str) -> None:
        self._host = host
        self._label = label

    @classmethod
    def from_label(cls, host: Any, label: str) -> Markdown:
        return cls(host, label)

    def extract(self) -> str:
        host = self._host
        locator_host = _LocatorHost(host, module_dir_for(host))
        return Asset(AssetLocator(locator_host, self._label).locate()).collect()

    def coerce(self, text: str, return_type: type) -> Any:
        if return_type is str:
            return text
        raise TypeError(f"coerce not implemented for {return_type!r}")


class _LocatorHost:
    """Adapter so AssetLocator resolves under context_guidance.module_dir."""

    def __init__(self, host: Any, module_dir: Path) -> None:
        self._host = host
        self.module_dir = module_dir

    def __getattr__(self, name: str) -> Any:
        return getattr(self._host, name)


def _markdown_property(fn: _F, prop_label: str) -> property:
    def getter(self: Any) -> str:
        return Markdown.from_label(self, prop_label).extract()

    getter.__doc__ = fn.__doc__
    getter.__name__ = fn.__name__
    return property(getter)


def markdown(
    fn: _F | str | None = None, *, label: str | None = None
) -> property | Callable[[_F], property]:
    if callable(fn):
        return _markdown_property(fn, fn.__name__)

    def decorator(inner: _F) -> property:
        prop_label = label or fn or inner.__name__
        return _markdown_property(inner, prop_label)

    return decorator
