"""DDD's formats: the bounded-context map, which reads and writes the Clean Engineering class models its code holds."""

from __future__ import annotations

from typing import Any

from harness.guidance.practice_formats import PracticeFormats

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap


class DddFormats(PracticeFormats):
    """The formats DDD reads and writes. Its code formats are Clean Engineering class models, which the map writes
    itself into as their own classes; its document formats render the bounded-context map, which reads a class model
    back. A text the map reads as a plain class model is read by the Clean Engineering practice DDD extends
    (``PracticeFormats.parse``)."""

    def model_for(self, target: Any, model: Any) -> Any:
        """The code formats are Clean Engineering class models, which the map writes itself into as their own classes,
        so they render themselves; the DDD formats render the bounded-context map, which reads a class model back."""
        if isinstance(model, BoundedContextMap):
            if isinstance(target, CleanEngineeringModel) and not isinstance(target, BoundedContextMap):
                model.write_classes(target)
                return target
            return model
        if isinstance(target, BoundedContextMap) and isinstance(model, CleanEngineeringModel):
            return MarkdownBoundedContextMap().read_class_model(model)
        return model
