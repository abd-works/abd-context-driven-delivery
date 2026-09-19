"""Draw.io channel + miniature render kit for Clean Engineering.

The UML/modules diagram channel loads here. The ``Drawio`` kit (render → scan
→ repair) stays in ``drawio.py`` and is imported only when that kit is used.
"""

from practices.clean_engineering.class_model.drawio.drawio_class_model import (
    DrawIOCleanEngineeringModel,
)

__all__ = ["Drawio", "DrawIOCleanEngineeringModel"]


def __getattr__(name: str):
    if name == "Drawio":
        from practices.clean_engineering.class_model.drawio.drawio import Drawio

        return Drawio
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
