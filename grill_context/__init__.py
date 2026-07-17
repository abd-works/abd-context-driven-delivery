"""grill_context — chainable action decorator + GrillContext toolset.

Public exports:
    grill_with_context   — @grill_with_context decorator (marks an @action as grill-wrapped)
    GrillContext         — standalone grilling toolset (tools + grill_with_context action)

The decorator and the toolset action deliberately share the name
``grill_with_context`` because they are two faces of the same behavior: the
toolset is the standalone entrypoint; the decorator opts an existing action
into the same grill loop before it runs.
"""
from grill_context.grill_context import GrillContext
from grill_context._decorator import grill_with_context  # imported LAST so `from grill_context import grill_with_context` binds to the decorator, not the submodule

__all__ = ["grill_with_context", "GrillContext"]
