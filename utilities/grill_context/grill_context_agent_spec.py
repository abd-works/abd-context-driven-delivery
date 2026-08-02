# @agent-spec-manifest python -m tools agent-spec utilities/grill_context/grill_context_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: utilities/grill_context/.agent_bdd_sessions/grill-write.json
"""Agent BDD spec for utilities/grill_context/grill_context.py — GrillContext toolset.

Verifies that an AI agent can:
  1. call ``explore_context_files`` on a directory and receive a valid JSON array of context files, and
  2. call ``write_grill_answer`` to persist an insight, producing a well-formed grill-answers.md entry.
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

_SESSIONS = Path(__file__).resolve().parent / ".agent_bdd_sessions"
_TOOLSET = "utilities.grill_context.grill_context:GrillContext"
# This module's own .context/ folder is a stable source of context files to explore.
_GRILL_CONTEXT_DIR = str(Path(__file__).resolve().parent)


with description("a GrillContext toolset"):
    with context("when the agent explores context files"):
        with before.all:
            self._ag = agent(_REPO_ROOT, _SESSIONS / "grill-write.json")
            self.session = self._ag.__enter__()
            self.explore_response = self.session.instruct_run(
                "Using shell, run exactly: python -m tools run -\n"
                "Pipe this YAML on stdin:\n"
                f"toolset: {_TOOLSET}\n"
                "tool: explore_context_files\n"
                "arguments:\n"
                f"  root: '{_GRILL_CONTEXT_DIR}'\n"
                "Return the complete fenced YAML stdout from the CLI.",
                timeout_seconds=90,
            )

        with after.all:
            self._ag.__exit__(None, None, None)

        with it("should return ok from explore_context_files"):
            expect(self.explore_response.ok).to(be_true)

        with it("should identify explore_context_files as the invoked tool"):
            from expects import equal
            expect(self.explore_response.tool).to(equal("explore_context_files"))

        with it("should return a non-empty result listing context files"):
            result = str(self.explore_response.result or "")
            # The grill_context directory contains a .context/ subfolder
            expect(len(result) > 2).to(be_true)

        with it("should judge that the result looks like a JSON array of context file objects"):
            verdict = self.session.ai_judge(
                str(self.explore_response.result or ""),
                "The result must look like a JSON array where each element has a 'path' "
                "and a 'kind' field ('context-named' or 'context-folder'). "
                "Pass if the structure is present and at least one entry is visible.",
            )
            expect(verdict.passed()).to(be_true)

    with context("when the agent writes a grill answer"):
        with before.all:
            self._ag2 = agent(_REPO_ROOT, _SESSIONS / "grill-answer-write.json")
            self.session2 = self._ag2.__enter__()
            self._tmpdir = tempfile.mkdtemp()
            self.write_response = self.session2.instruct_run(
                "Using shell, run exactly: python -m tools run -\n"
                "Pipe this YAML on stdin:\n"
                f"toolset: {_TOOLSET}\n"
                "tool: write_grill_answer\n"
                "arguments:\n"
                f"  root: '{self._tmpdir}'\n"
                "  heading: 'How explore_context_files discovers files'\n"
                "  body: 'It scans recursively for files whose name contains context "
                "or that live inside a .context/ subfolder, skipping __pycache__ and "
                "private underscore-prefixed paths.'\n"
                "Return the complete fenced YAML stdout from the CLI.",
                timeout_seconds=90,
            )

        with after.all:
            self._ag2.__exit__(None, None, None)

        with it("should return ok from write_grill_answer"):
            expect(self.write_response.ok).to(be_true)

        with it("should return a result path containing grill-answers.md"):
            result = str(self.write_response.result or "")
            expect("grill-answers.md" in result).to(be_true)

        with it("should have created the grill-answers.md file on disk"):
            answers_path = Path(self._tmpdir) / ".context" / "grill-answers.md"
            expect(answers_path.is_file()).to(be_true)

        with it("should have written the heading and body into the file"):
            answers_path = Path(self._tmpdir) / ".context" / "grill-answers.md"
            content = answers_path.read_text(encoding="utf-8")
            expect("How explore_context_files discovers files" in content).to(be_true)
            expect("scans recursively" in content).to(be_true)

        with it("should judge that the written insight is grounded and specific"):
            answers_path = Path(self._tmpdir) / ".context" / "grill-answers.md"
            content = answers_path.read_text(encoding="utf-8")
            verdict = self.session2.ai_judge(
                content,
                "The grill-answers file must contain a ### heading followed by a "
                "body that makes a specific, grounded claim about how the tool works. "
                "It should mention paths, skipping, or recursion in concrete terms. "
                "Pass if the entry is substantive and not a vague placeholder.",
            )
            expect(verdict.passed()).to(be_true)
