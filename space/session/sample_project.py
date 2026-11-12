"""SampleProject. The one example project the specs share: every practice's content, with many known issues, copied once
per spec run into a folder of its own, with one session whose graph reads it once.

The project is the graph's sample working copy (``harness/graph/_examples/input``: TypeScript domain code with DDD and
Clean Engineering violations, TypeScript shared stories and server specs with their examples) with the extras of
``harness/graph/_examples/project`` laid over it (a markdown story map whose story breaks verb-noun-format, Python code
over the parameter limit, a Python shared story with its examples module, and a screen spec). A spec that only reads
shares ``SampleProject.shared().session``; a spec whose examples write what another would see (session log lines,
edited files) makes a session of its own with ``fresh_session``, on a folder as small as it needs.
"""

from __future__ import annotations

import atexit
import shutil
import tempfile
from functools import cached_property
from pathlib import Path
from typing import ClassVar

from harness.agent_tools.tool_call import ToolCall

_EXAMPLES = Path(__file__).resolve().parents[2] / "harness" / "graph" / "_examples"
SAMPLE = _EXAMPLES / "input"
EXTRAS = _EXAMPLES / "project"


class SampleProject:
    """The sample copied into a folder of its own, a project as a checked-out one is, removed when the run ends."""

    _shared: ClassVar[SampleProject | None] = None

    def __init__(self) -> None:
        self._folder = Path(tempfile.mkdtemp(prefix="cdd-sample-project-"))
        self.root = self._folder / "sample"
        shutil.copytree(SAMPLE, self.root)
        shutil.copytree(EXTRAS, self.root, dirs_exist_ok=True)
        atexit.register(shutil.rmtree, self._folder, True)

    @classmethod
    def shared(cls) -> SampleProject:
        """The one sample project of this run, made the first time a spec asks."""
        if cls._shared is None:
            cls._shared = cls()
        return cls._shared

    @cached_property
    def session(self):
        """The sample's main session, working in the whole sample, its graph holding the whole working copy: read once,
        then shared by every spec that only reads."""
        session = ToolCall(project=self.root).session
        session.workpath = self.root
        session.graph.hold_whole()
        return session

    def clear_reports(self) -> None:
        """Remove the validation reports the shared session holds, so an example counts only the ones it saves."""
        shutil.rmtree(Path(self.session.session_path) / "validation-reports", ignore_errors=True)
