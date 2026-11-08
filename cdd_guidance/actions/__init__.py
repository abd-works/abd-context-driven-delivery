"""The actions CDD ships. Importing this package registers their toolsets with the framework's action catalogue, so the
framework works with the actions without naming them.

Each folder here whose name does not start with ``_`` holds its toolset in the module of the folder's name, as the class
of that name in Pascal case (``grill_context/grill_context.py`` holds ``GrillContext``). A new action folder joins the
catalogue by being there, so no other list has to learn about it."""

import importlib
from pathlib import Path

from harness.annotations.name import Name
from harness.guidance.action_catalogue import ActionCatalogue


def _action_toolsets() -> list[type]:
    """Each action folder's toolset class, in folder order."""
    folders = sorted(
        folder for folder in Path(__file__).resolve().parent.iterdir()
        if folder.is_dir() and folder.name[0] not in "_." and (folder / f"{folder.name}.py").is_file()
    )
    return [
        getattr(importlib.import_module(f"{__name__}.{folder.name}.{folder.name}"), Name(folder.name).title_pascal)
        for folder in folders
    ]


ActionCatalogue.register(*_action_toolsets())
