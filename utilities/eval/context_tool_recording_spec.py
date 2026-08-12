"""
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
"""
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD - a session that a context tool records through eval.

Sources / context:
utilities/eval/.context/sessions/eval/eval-bdd-sketch.md
utilities/eval/.context/sessions/eval/eval-ce-sketch.md
utilities/eval/.context/module-context.md
context_tools/base/base_context_tool.py
"""
import shutil
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from context_tools.stories.stories import Stories
from workspace.session_log import SessionLog


with description("a session"):
    with context("that a context tool records through eval"):
        with before.each:
            self.tmp = Path(tempfile.mkdtemp())
            self.context_tool = Stories(
                fidelity="story_map", path=str(self.tmp), session="eval-context-tool"
            )
            SessionLog.set_instance(None)
            SessionLog.instance().bind(self.context_tool.workspace)
            self._shutil = shutil

        with it("should expose eval beside workspace"):
            expect(self.context_tool.eval is not None).to(equal(True))
            expect(self.context_tool.eval.path).to(equal(str(self.tmp)))
            expect(getattr(self.context_tool.workspace, "eval", None)).to(
                equal(self.context_tool.eval)
            )
            self._shutil.rmtree(str(self.tmp), ignore_errors=True)

        with context("that a first-order logged tool is invoked on the context tool"):
            with before.each:
                SessionLog.instance().append(
                    kind="tool",
                    toolset="context_tools.stories.stories:Stories",
                    name="scan",
                    summary="paths=[]",
                    ok=True,
                )

            with it("should attach a ToolCall to the open Turn"):
                open_turn = self.context_tool.eval.open_turn
                expect(open_turn is not None).to(equal(True))
                expect(len(open_turn.tool_calls)).to(equal(1))
                expect(open_turn.tool_calls[0].name).to(equal("scan"))
                self._shutil.rmtree(str(self.tmp), ignore_errors=True)

            with it("should not close the Turn yet"):
                expect(len(self.context_tool.eval.turns)).to(equal(0))
                expect(self.context_tool.eval.open_turn is not None).to(equal(True))
                self._shutil.rmtree(str(self.tmp), ignore_errors=True)

        with context("that a mistake is logged on the context tool"):
            with before.each:
                self.entry_id = self.context_tool.log_mistake(
                    artifact="a.md",
                    rule="r1",
                    wrong="bad",
                    original="old",
                )

            with it("should record a Mistake on the open Turn through eval"):
                open_turn = self.context_tool.eval.open_turn
                expect(open_turn is not None).to(equal(True))
                expect(len(open_turn.mistakes)).to(equal(1))
                expect(open_turn.mistakes[0].entry_id).to(equal(self.entry_id))
                expect(open_turn.mistakes[0].correction.status).to(equal("open"))
                self._shutil.rmtree(str(self.tmp), ignore_errors=True)

        with context("that a correction is logged on the context tool"):
            with before.each:
                self.entry_id = self.context_tool.log_mistake(
                    artifact="a.md",
                    rule="r1",
                    wrong="bad",
                    original="old",
                )
                self.context_tool.log_correction(entry_id=self.entry_id, improved="good")

            with it("should set Correction.improved and status=fixed on that Mistake"):
                mist = self.context_tool.eval.open_turn.mistakes[0]
                expect(mist.correction.improved).to(equal("good"))
                expect(mist.correction.status).to(equal("fixed"))
                self._shutil.rmtree(str(self.tmp), ignore_errors=True)
