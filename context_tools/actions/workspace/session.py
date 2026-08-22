"""SessionPaths helpers and lazy ``WorkSession`` re-export.

``WorkSession`` is loaded lazily so ``from workspace import log`` does not pull
``@action`` / ``@tool`` during the primitives bootstrap cycle.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["WorkSession", "SessionPaths", "docs_dir"]


class SessionPaths:
    """Path helpers for resolving where process docs live relative to a destination."""

    @staticmethod
    def docs_dir(destination: str | Path) -> Path:
        """Resolve where process docs live for a destination.

        - Sprint folder (``.../.context/sessions/{name}``) -> write flat into that folder
        - Working area or module root -> ``{destination}/.context/``
        """
        dest = Path(destination)
        if dest.name and dest.parent.name == "sessions":
            return dest
        return dest / ".context"


docs_dir = SessionPaths.docs_dir


def __getattr__(name: str):
    if name == "WorkSession":
        from workspace.workspace import WorkSession

        return WorkSession
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
