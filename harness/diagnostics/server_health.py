"""The running parts of CDD that a person needs to see are up: each registered app, and the latest test runs."""
from __future__ import annotations

from pathlib import Path

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.apps.app import APPS, App
from harness.release.test_runs import TestCadence, TestRun, TestRunRecord, default_record_folder, main_checkout
from harness.e2e_review.e2e_review import E2eReview, E2eRunReview, ScheduledReview
from harness.installation.data_class import data_field, language_adapter
from harness.mcp.mcp_annotations import mcp


@language_adapter(language="typescript")
@agent_toolset
class ServerHealth:
    """Report the parts of CDD that run outside this MCP host, so a person can see what is up without opening a terminal."""

    # The server health band reads this after every cdd call and every prompt, so its tool stays out of the session log.
    # This tool answers only while the MCP host is up, so the band itself works out that the host is lost.

    def __init__(self, repo_root: Path | str, cadence: TestCadence | None = None, e2e_review: E2eReview | None = None) -> None:
        self._repo_root = Path(repo_root).resolve()
        self._cadence = cadence if cadence is not None else TestCadence(TestRunRecord(default_record_folder(), main_checkout(self._repo_root)))
        # The scheduled e2e run's screens are reviewed in the main checkout it runs in.
        self._e2e_review = e2e_review if e2e_review is not None else E2eReview(self._cadence.checkout or self._repo_root, ScheduledReview.RELEASE)

    @classmethod
    @tool_subject
    def load(cls, *, project: Path | str) -> ServerHealth:
        """The health of project, the folder the call names."""
        return cls(project)

    @mcp
    @agent_tool
    @noSessionLog
    def report(self) -> ServerHealth:
        """Return each registered app with its status and the port it answers on, and the latest heavy and e2e runs.
        Reading it is the cadence's clock: a tier overdue on main starts in the background."""
        self._cadence.start_due()
        return self

    @property
    @data_field
    def apps(self) -> list[App]:
        """Every app a module registered, each read as it is now."""
        return APPS.registered

    @property
    @data_field
    def test_runs(self) -> list[TestRun]:
        """The latest run of each test tier the cdd server runs on a cadence, heavy and e2e, that has run."""
        return self._cadence.latest_runs

    @property
    @data_field
    def e2e_review(self) -> E2eRunReview | None:
        """The latest scheduled e2e run's screen review: its changed, unjudged and missed steps, and its report; none
        before a scheduled e2e run has captured its screens."""
        return self._e2e_review.latest()
