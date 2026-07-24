"""Session bout model and session-scoped logging for @log-marked tools/actions."""

from sessions.session import ISession, Session, docs_dir
from sessions.session_log import (
    ISessionLog,
    SessionLog,
    inherit_annotations,
    inherit_annotations_from_bases,
    is_logged,
    log,
    member_is_logged,
    summarize_mapping,
)

__all__ = [
    "ISession",
    "ISessionLog",
    "Session",
    "SessionLog",
    "docs_dir",
    "inherit_annotations",
    "inherit_annotations_from_bases",
    "is_logged",
    "log",
    "member_is_logged",
    "summarize_mapping",
]
