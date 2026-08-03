"""api_versioning_decision — shows RecordDecisions persisting a concrete API trade-off."""
from __future__ import annotations

from record_decisions.record_decisions import RecordDecisions

_CDR_CONTENT = """\
# URL-path versioning chosen over header-based versioning

We adopt `/v{N}/` URL prefixes for all public API routes rather than an
`Accept: application/vnd.api+json;version=N` header scheme. URL-path versioning
is visible in browser address bars and proxy logs, making it far easier to route,
cache, and debug without custom tooling. The trade-off is slightly noisier URLs and
the discipline required to retire old prefixes; header versioning is cleaner but
invisible to intermediaries and harder to test manually.
"""


class ApiVersioningDecision:
    """Example: record the API versioning strategy as a Context Decision Record."""

    def record(self, workspace: str) -> str:
        """Persist the API versioning trade-off as a CDR under *workspace*.

        Instantiates RecordDecisions rooted at the workspace, then calls
        write_cdr so the decision is numbered and written to
        {workspace}/.context/cdr/NNNN-url-path-versioning.md immediately.
        """
        recorder = RecordDecisions(path=workspace)
        return recorder.write_cdr(
            root=workspace,
            slug="url-path-versioning",
            content=_CDR_CONTENT,
        )
