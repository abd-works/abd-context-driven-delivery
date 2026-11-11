"""The stack patterns CDD ships. Importing this package registers them with the graph's pattern overlays, so a graph
applies a pattern by its name without the framework naming it.

Each subfolder whose module of the same name defines a pattern class (one whose ``pattern`` is the folder's name)
registers itself, so a pattern folder added here is offered with no other change; a folder such as
``domain_driven_stack``, which only holds what patterns share, defines none and is left out."""

import importlib
from pathlib import Path

from harness.graph.pattern_overlays import PatternOverlays

import cdd_guidance.practices  # noqa: F401 - the patterns build on the practices, so those are registered with them


def _patterns_in_this_folder() -> list[type]:
    """The pattern class each subfolder's module of the same name defines, in folder name order. Folders are read from
    disk rather than through pkgutil, which skips a pattern folder that has no ``__init__.py``."""
    patterns: list[type] = []
    for folder in sorted(Path(__file__).parent.iterdir()):
        if not (folder / f"{folder.name}.py").is_file():
            continue
        module = importlib.import_module(f"{__name__}.{folder.name}.{folder.name}")
        patterns += [value for value in vars(module).values() if isinstance(value, type) and value.__module__ == module.__name__ and getattr(value, "pattern", "") == folder.name]
    return patterns


PatternOverlays.register(*_patterns_in_this_folder())
