# @agent-spec-manifest python -m tools agent-spec utilities/record_decisions/record_decisions_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: utilities/record_decisions/.context/.agent_bdd_sessions/write-cdr.json
"""Agent BDD spec for utilities/record_decisions/record_decisions.py — RecordDecisions toolset.

Verifies that an AI agent can:
  1. call ``read_cdr_format`` and receive the CDR template, and
  2. call ``write_cdr`` to persist a qualifying decision as a numbered .md file under .context/cdr/.
"""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("utilities", "primitives", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, expect
from mamba import after, before, context, description, it

from agent_bdd import agent

_SESSIONS = Path(__file__).resolve().parent / ".context" / ".agent_bdd_sessions"
_TOOLSET = "utilities.record_decisions.record_decisions:RecordDecisions"


with description("a RecordDecisions toolset"):
    with context("when the agent reads the CDR format"):
        with before.all:
            self._ag = agent(_REPO_ROOT, _SESSIONS / "read-cdr-format.json")
            self.session = self._ag.__enter__()
            self.format_response = self.session.instruct_run(
                "Using shell, run exactly: python -m tools run -\n"
                "Pipe this YAML on stdin:\n"
                f"toolset: {_TOOLSET}\n"
                "tool: read_cdr_format\n"
                "Return the complete fenced YAML stdout from the CLI.",
                timeout_seconds=60,
            )

        with after.all:
            self._ag.__exit__(None, None, None)

        with it("should return ok from read_cdr_format"):
            expect(self.format_response.ok).to(be_true)

        with it("should identify read_cdr_format as the invoked tool"):
            from expects import equal
            expect(self.format_response.tool).to(equal("read_cdr_format"))

        with it("should return a non-empty CDR format string"):
            result = str(self.format_response.result or "")
            expect(len(result) > 50).to(be_true)

        with it("should judge that the format describes when to offer a CDR"):
            verdict = self.session.ai_judge(
                str(self.format_response.result or ""),
                "The content must explain when to offer a Context Decision Record "
                "and include a template or format guidance. "
                "Pass if criteria and a structural template are present.",
            )
            expect(verdict.passed()).to(be_true)

    with context("when the agent writes a CDR for a qualifying decision"):
        with before.all:
            self._ag2 = agent(_REPO_ROOT, _SESSIONS / "write-cdr.json")
            self.session2 = self._ag2.__enter__()
            self._tmpdir = tempfile.mkdtemp()
            self.write_response = self.session2.instruct_run(
                "Using shell, run exactly: python -m tools run -\n"
                "Pipe this YAML on stdin:\n"
                f"toolset: {_TOOLSET}\n"
                "tool: write_cdr\n"
                "arguments:\n"
                f"  root: '{self._tmpdir}'\n"
                "  slug: 'use-yaml-for-tool-requests'\n"
                "  content: |\\n"
                "    # Use YAML for tool requests\\n"
                "    \\n"
                "    We chose YAML over JSON for tool request files because it is "
                "human-readable and supports multi-line strings without escaping.\\n"
                "Return the complete fenced YAML stdout from the CLI.",
                timeout_seconds=90,
            )

        with after.all:
            self._ag2.__exit__(None, None, None)

        with it("should return ok from write_cdr"):
            expect(self.write_response.ok).to(be_true)

        with it("should return a result path ending with .md"):
            result = str(self.write_response.result or "")
            expect(result.endswith(".md")).to(be_true)

        with it("should have created the CDR file under .context/cdr/"):
            result_path = Path(str(self.write_response.result or ""))
            expect(result_path.is_file()).to(be_true)
            expect("cdr" in str(result_path)).to(be_true)

        with it("should have numbered the CDR file starting at 0001"):
            result_path = Path(str(self.write_response.result or ""))
            expect(result_path.name.startswith("0001-")).to(be_true)

        with it("should judge that the written CDR is well-structured"):
            result_path = Path(str(self.write_response.result or ""))
            content = result_path.read_text(encoding="utf-8")
            verdict = self.session2.ai_judge(
                content,
                "The CDR must have a markdown heading and at least one sentence "
                "explaining the decision with a stated rationale. "
                "Pass if it looks like a coherent, persisted decision record.",
            )
            expect(verdict.passed()).to(be_true)
