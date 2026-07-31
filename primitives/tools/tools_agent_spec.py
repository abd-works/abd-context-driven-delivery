# @agent-spec-manifest python -m tools agent-spec tools/tools_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: tools/.sessions/general-lee.json
"""BDD agent spec for tools-behavior.md - agent discovers manifest and invokes tools."""

from pathlib import Path

from expects import be_true, equal, expect
from mamba import after, before, context, description, it

from agent_bdd import agent

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SESSIONS = Path(__file__).resolve().parent / ".sessions"


with description("a class"):
    with context("with a toolset applied"):
        with context("with agent"):
            with before.all:
                self._agent = agent(_REPO_ROOT, _SESSIONS / "general-lee.json")
                self.session = self._agent.__enter__()
                self.session.instruct("Read tools/examples/car.py from the workspace.")
                self.ai_response = self.session.instruct_run(
                    "Create a car based on the general lee from the Dukes of Hazzard."
                )

            with after.all:
                self._agent.__exit__(None, None, None)

            with it("should parse the fenced CLI yaml into ai-response"):
                expect(self.ai_response.ok).to(be_true)
                expect(len(self.ai_response.resources) > 0).to(be_true)

            with it("should set ai-response.make containing Dodge"):
                expect("Dodge" in str(self.ai_response.resources.get("make", ""))).to(be_true)

            with it("should set ai-response.model containing Charger"):
                expect("Charger" in str(self.ai_response.resources.get("model", ""))).to(be_true)

            with it("should set ai-response.year to 1969"):
                expect(self.ai_response.resources.get("year")).to(equal(1969))

            with it("should judge ai-response.personality as a rebellious country boy"):
                verdict = self.session.ai_judge(
                    str(self.ai_response.resources.get("personality", "")),
                    "The car should be a rebellious, high-spirited, and loyal country boy.",
                )
                expect(verdict.passed()).to(be_true)
