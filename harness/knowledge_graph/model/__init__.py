"""CodeQL infrastructure. Practice graph loaders live under legacy/model."""

from .codeql import CodeQL, CodeQLRunError, Rows

__all__ = [
    "CodeQL",
    "CodeQLRunError",
    "Rows",
]
