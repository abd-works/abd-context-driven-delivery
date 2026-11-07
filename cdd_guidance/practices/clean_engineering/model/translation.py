"""TranslationError: what translate_from raises for a source of another kind."""

from __future__ import annotations


class TranslationError(Exception):
    """Raised when translate_from is called with an incompatible source."""
