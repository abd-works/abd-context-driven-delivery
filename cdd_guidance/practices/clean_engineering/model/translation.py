"""ChildCollectionPair and TranslationError: what translate_from matches between two formats' children, and the error
it raises for an incompatible source."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadNode


class TranslationError(Exception):
    """Raised when translate_from is called with an incompatible source."""


@dataclass
class ChildCollectionPair:
    self_children: List["OoadNode"]
    source_children: List["OoadNode"]
    load: Callable[["OoadNode"], "OoadNode"]
