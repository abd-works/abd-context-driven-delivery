"""Import toolsets that declare ``@hook`` handlers — re-export from ``dispatch``."""

from hooks.dispatch import load

__all__ = ["load"]
