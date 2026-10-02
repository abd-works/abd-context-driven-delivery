"""CodeQL infrastructure. Replaced graph types live under legacy/."""

from .codeql import CodeQL, CodeQLRunError, Rows

__all__ = [
    "CodeQL",
    "CodeQLRunError",
    "Rows",
]
