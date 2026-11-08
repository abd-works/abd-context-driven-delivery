"""The folder a class is defined in, which every reader of the markdown, templates, and examples beside a class asks."""

from __future__ import annotations

import inspect
from pathlib import Path

# The attribute a class holds its own folder in, once it is first asked for.
_HELD_AS = "_class_folder"


def class_folder(owner: type) -> Path:
    """The folder owner is defined in, which holds its markdown, templates, and examples: a toolset's install folder, a
    practice's key and documents, an action's guide, and the markdown beside any class all start here. Where a class is
    defined never changes while the process runs, so the class holds its folder once it is first asked for; a class
    with no source file, such as one made in a shell or a built-in type, sits in the current folder."""
    held = owner.__dict__.get(_HELD_AS)
    if held is not None:
        return held
    try:
        held = Path(inspect.getfile(owner)).resolve().parent
    except (TypeError, OSError):
        return Path(".")
    setattr(owner, _HELD_AS, held)
    return held
