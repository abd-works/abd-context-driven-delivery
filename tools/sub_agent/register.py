"""Sub-agent ToolsetExtensions registration is off.

``primitives.installer.extensions`` is gone. Sub-agent discovery no longer
hooks a parallel member walk. Leave this module import-safe so packages that
still import ``register`` do not fail.
"""
from __future__ import annotations

_registered = False


def register() -> None:
    """No-op — ToolsetExtensions registration is disconnected."""
    global _registered
    _registered = True
    return
