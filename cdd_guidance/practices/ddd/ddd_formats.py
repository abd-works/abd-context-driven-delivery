"""DDD's formats: the bounded-context map, which reads and writes the Clean Engineering class models its code holds."""

from __future__ import annotations

from harness.guidance.practice_formats import PracticeFormats

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from cdd_guidance.practices.ddd.model.nodes import BoundedContextMap

# A model DDD's formats hold: the bounded-context map of a document format, or the class model of a code format.
DddFormatModel = BoundedContextMap | CleanEngineeringModel
# The levels a class's place names at least: its bounded context, then its aggregate.
_PLACE_LEVELS = 2


class DddFormats(PracticeFormats):
    """The formats DDD reads and writes. Its code formats are Clean Engineering class models, which the map writes
    itself into as their own classes; its document formats render the bounded-context map, which reads a class model
    back. A text the map reads as a plain class model is read by the Clean Engineering practice DDD extends
    (``PracticeFormats.parse``)."""

    def model_for(self, target: DddFormatModel, model: DddFormatModel) -> DddFormatModel:
        """The code formats are Clean Engineering class models, which the map writes itself into as their own classes,
        so they render themselves; the DDD formats render the bounded-context map, which reads a class model back. Code
        whose classes name their places is written into another code format through the map, a module for each
        aggregate."""
        if isinstance(model, BoundedContextMap):
            if isinstance(target, CleanEngineeringModel) and not isinstance(target, BoundedContextMap):
                model.write_classes(target)
                return target
            return model
        if isinstance(target, BoundedContextMap) and isinstance(model, CleanEngineeringModel):
            return MarkdownBoundedContextMap().read_class_model(model)
        if isinstance(model, CleanEngineeringModel) and self._names_every_place(model):
            MarkdownBoundedContextMap().read_class_model(model).write_classes(target)
            return target
        return model

    def _names_every_place(self, model: CleanEngineeringModel) -> bool:
        """Whether model is code whose every class names the bounded context and aggregate it lives in, as the code
        DDD writes does: such code is written into another code format as one module for each aggregate, so each
        aggregate keeps its own file. Code that names no place stays the one module its file is."""
        classes = [oclass for oclass in model.every_class() if not oclass.name.startswith("_")]
        return bool(classes) and all(len(oclass.module_path) >= _PLACE_LEVELS for oclass in classes)
