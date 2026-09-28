"""Destination mark and Installation write channel — no hook or installer import."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

InstallTracker = Callable[[Path], None]


_NO_CATALOG_FLAG = "_no_catalog"
_NO_DEPLOY_FLAG = "_no_deploy"


def noCatalog(target: Any = None) -> Any:
    """Omit this class or operation from the catalog.

    Install and deploy ignore this mark. Use it when the behavior is real
    but not ready to show in the catalog.
    """

    def mark(obj: Any) -> Any:
        setattr(obj, _NO_CATALOG_FLAG, True)
        return obj

    if target is None:
        return mark
    return mark(target)


def noDeploy(target: Any = None) -> Any:
    """Omit this operation from install.

    Skill, command, MCP, and hook marks on the same operation do not write
    files. The catalog can still list it.
    """

    def mark(obj: Any) -> Any:
        setattr(obj, _NO_DEPLOY_FLAG, True)
        return obj

    if target is None:
        return mark
    return mark(target)


def omitted_from_catalog(obj: Any) -> bool:
    """True when ``obj`` or its underlying function carries ``@noCatalog``."""
    if getattr(obj, _NO_CATALOG_FLAG, False):
        return True
    fn = getattr(obj, "__func__", None)
    return bool(fn is not None and getattr(fn, _NO_CATALOG_FLAG, False))


def omitted_from_deploy(obj: Any) -> bool:
    """True when ``obj`` or its underlying function carries ``@noDeploy``."""
    if getattr(obj, _NO_DEPLOY_FLAG, False):
        return True
    fn = getattr(obj, "__func__", None)
    return bool(fn is not None and getattr(fn, _NO_DEPLOY_FLAG, False))


class Destination:
    """Base annotation to define the installation destination of a tool."""

    flag = ""

    def annotate(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        setattr(fn, self.flag, True)
        name = getattr(self, "name", None)
        if name is not None:
            setattr(fn, f"{self.flag}_name", name)
        return fn

    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        return self.annotate(fn)


class Installation:
    """``install(tool)`` writes the channel; subclass ``write``."""

    channel = ""

    def __init__(
        self,
        ide: str,
        path: Path | str,
        toolset_ref: str = "",
        repo: Path | str | None = None,
    ) -> None:
        self.ide = ide
        self.path = Path(path)
        self.toolset_ref = toolset_ref
        self.repo = Path(repo).resolve() if repo is not None else None
        self._install_tracker: InstallTracker | None = None

    def bind_tracker(self, tracker: InstallTracker) -> None:
        self._install_tracker = tracker

    def track_write(self, dest: Path) -> None:
        if self._install_tracker is not None:
            self._install_tracker(dest)

    def folder_for(self, toolset: Any) -> Path:
        """Repo-relative package folder the toolset already knows (practice dir, fidelity leaf)."""
        raw = getattr(toolset, "install_folder", None)
        if raw is None:
            slug = getattr(toolset, "slug", None) or "toolset"
            return Path(str(slug))
        folder = Path(raw)
        repo = self.repo
        if repo is None:
            return folder
        try:
            return folder.resolve().relative_to(repo)
        except ValueError:
            return Path(folder.name)

    def install(self, tool: Any) -> None:
        self.write(tool)

    def write(self, tool: Any) -> None:
        raise NotImplementedError
