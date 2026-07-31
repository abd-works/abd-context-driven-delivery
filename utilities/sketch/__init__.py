"""Sketch - chainable action decorator + Sketcher toolset.

Public exports:
    sketch     - @sketch decorator (marks an @action as sketch-wrapped)
    Sketcher   - standalone sketching toolset (tools + sketch_session action)
"""
from sketch.sketch import Sketcher
from sketch._decorator import sketch  # imported LAST so `from sketch import sketch` binds to the decorator, not the submodule

__all__ = ["sketch", "Sketcher"]
