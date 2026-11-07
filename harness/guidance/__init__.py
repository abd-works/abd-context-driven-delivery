"""Harness guidance — ``from harness.guidance import ...``."""
from .rule import AppliesTo, Rule, RulesCollection

def __getattr__(name: str):
    from . import guidance as _guidance

    try:
        return getattr(_guidance, name)
    except AttributeError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
