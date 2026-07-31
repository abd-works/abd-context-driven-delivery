"""record_decisions - chainable action decorator + RecordDecisions toolset.

Public exports:
    record_decisions   - @record_decisions decorator (marks an @action as CDR-wrapped)
    RecordDecisions    - standalone CDR toolset (tools + record_decisions_session action)

The decorator and the toolset action share the same concern: offer Context Decision
Records sparingly and persist them under ``.context/cdr/``. See CDR-FORMAT.md.
"""
from record_decisions.record_decisions import RecordDecisions
from record_decisions._decorator import record_decisions  # imported LAST so `from record_decisions import record_decisions` binds to the decorator

__all__ = ["record_decisions", "RecordDecisions"]
