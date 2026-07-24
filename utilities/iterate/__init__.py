"""iterate — chainable action decorator + Iterator toolset.

Public exports:
    iterate    — @iterate decorator (marks an @action as iterate-wrapped)
    Iterator   — standalone iterate toolset (iterate_session pulls grill)
"""
from iterate.iterate import Iterator
from iterate._decorator import iterate  # imported LAST so `from iterate import iterate` binds to the decorator

__all__ = ["iterate", "Iterator"]
