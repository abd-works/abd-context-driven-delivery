# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for GrillContext toolset."""

import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

from primitives.actions.action import _ActionExpander
from grill_context.grill_context import GrillContext


with description("GrillContext toolset"):
    with context("manifest signature"):
        with it("should expose explore_context_files as a tool"):
            sig = GrillContext.manifest.signature
            expect(sig["explore_context_files"]["kind"]).to(equal("tool"))

        with it("should expose read_context_file as a tool"):
            sig = GrillContext.manifest.signature
            expect(sig["read_context_file"]["kind"]).to(equal("tool"))

        with it("should expose write_grill_answer as a tool"):
            sig = GrillContext.manifest.signature
            expect(sig["write_grill_answer"]["kind"]).to(equal("tool"))

        with it("should expose grill_with_context as an action"):
            sig = GrillContext.manifest.signature
            expect(sig["grill_with_context"]["kind"]).to(equal("action"))

        with it("should wire explore_context_files and read_context_file into grill_with_context"):
            entry = GrillContext.manifest.signature["grill_with_context"]
            expect("explore_context_files" in entry["tools"]).to(be_true)
            expect("read_context_file" in entry["tools"]).to(be_true)

    with context("explore_context_files tool"):
        with before.each:
            self.gc = GrillContext()
            self.tmp = tempfile.TemporaryDirectory()
            self.root = self.tmp.name

        with context("that scans a root with no files"):
            with it("should return an empty JSON array"):
                result = self.gc.explore_context_files(root=self.root)
                expect(json.loads(result)).to(equal([]))

        with context("that scans a root containing a context-named file"):
            with it("should return that file with kind context-named"):
                ctx_file = Path(self.root) / "module-context.md"
                ctx_file.write_text("# context\n", encoding="utf-8")

                result = json.loads(self.gc.explore_context_files(root=self.root))

                expect(len(result)).to(equal(1))
                expect(result[0]["kind"]).to(equal("context-named"))
                expect(result[0]["path"]).to(contain("module-context.md"))

        with context("that scans a root with a .context/ subfolder file"):
            with it("should return that file with kind context-folder"):
                ctx_dir = Path(self.root) / ".context"
                ctx_dir.mkdir()
                (ctx_dir / "session.md").write_text("# session\n", encoding="utf-8")

                result = json.loads(self.gc.explore_context_files(root=self.root))

                expect(len(result)).to(equal(1))
                expect(result[0]["kind"]).to(equal("context-folder"))

        with context("that scans a root with a __pycache__ path"):
            with it("should exclude __pycache__ entries"):
                cache_dir = Path(self.root) / "__pycache__"
                cache_dir.mkdir()
                (cache_dir / "module.cpython-312.pyc").write_text("", encoding="utf-8")

                result = json.loads(self.gc.explore_context_files(root=self.root))

                expect(result).to(equal([]))

        with context("that scans a root with a private-prefixed subdirectory"):
            with it("should exclude files inside underscore-prefixed directories"):
                priv_dir = Path(self.root) / "_private"
                priv_dir.mkdir()
                (priv_dir / "context.md").write_text("# private\n", encoding="utf-8")

                result = json.loads(self.gc.explore_context_files(root=self.root))

                expect(result).to(equal([]))

    with context("read_context_file tool"):
        with before.each:
            self.gc = GrillContext()
            self.tmp = tempfile.TemporaryDirectory()

        with context("that reads a file that exists"):
            with it("should return the file contents as a string"):
                target = Path(self.tmp.name) / "notes.md"
                target.write_text("hello world\n", encoding="utf-8")

                result = self.gc.read_context_file(path=str(target))

                expect(result).to(equal("hello world\n"))

    with context("write_grill_answer tool"):
        with before.each:
            self.gc = GrillContext()
            self.tmp = tempfile.TemporaryDirectory()
            self.root = self.tmp.name

        with context("that writes when no grill-answers.md exists yet"):
            with it("should create grill-answers.md under .context/ in the root"):
                self.gc.write_grill_answer(
                    root=self.root,
                    heading="How actions are discovered",
                    body="Actions are discovered by scanning @action decorators.",
                )
                answers_path = Path(self.root) / ".context" / "grill-answers.md"
                expect(answers_path.exists()).to(be_true)

            with it("should write a fresh header followed by the given entry"):
                self.gc.write_grill_answer(
                    root=self.root,
                    heading="Design rationale",
                    body="The design separates context discovery from question framing.",
                )
                answers_path = Path(self.root) / ".context" / "grill-answers.md"
                content = answers_path.read_text(encoding="utf-8")
                expect(content).to(contain("# Grill Answers"))
                expect(content).to(contain("### Design rationale"))
                expect(content).to(contain("The design separates context discovery"))

            with it("should return the path to grill-answers.md as a string"):
                result = self.gc.write_grill_answer(
                    root=self.root,
                    heading="Initial insight",
                    body="Context files reveal intent.",
                )
                expect(isinstance(result, str)).to(be_true)
                expect(result).to(contain("grill-answers.md"))

        with context("that appends when grill-answers.md already exists"):
            with it("should preserve prior content and add the new entry"):
                self.gc.write_grill_answer(
                    root=self.root,
                    heading="First insight",
                    body="Exploration precedes questions.",
                )
                self.gc.write_grill_answer(
                    root=self.root,
                    heading="Second insight",
                    body="Answers are accumulated incrementally.",
                )
                answers_path = Path(self.root) / ".context" / "grill-answers.md"
                content = answers_path.read_text(encoding="utf-8")
                expect(content).to(contain("### First insight"))
                expect(content).to(contain("### Second insight"))
                expect(content).to(contain("Exploration precedes questions."))
                expect(content).to(contain("Answers are accumulated incrementally."))

    with context("grill_with_context action body"):
        with before.each:
            self.gc = GrillContext()
            self.body = _ActionExpander.instance().parse_body(
                GrillContext.grill_with_context, self.gc
            )

        with it("should wire explore_context_files as a tool step"):
            expect("explore_context_files" in self.body.tool_steps).to(be_true)

        with it("should wire read_context_file as a tool step"):
            expect("read_context_file" in self.body.tool_steps).to(be_true)

        with it("should carry instructions referencing the grilling workflow"):
            joined = "\n".join(self.body.prose_parts)
            expect(joined).to(contain("grill"))
