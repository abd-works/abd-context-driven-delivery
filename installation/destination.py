"""Destination mark and Installation write channel — no hook or installer import."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

InstallTracker = Callable[[Path], None]


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
