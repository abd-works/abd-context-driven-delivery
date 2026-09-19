"""PromptEcho @echo — model fidelity (Python channel).

Stubs only. Same types as prompt-echo-model.md. Does not replace
prompt_echo.py, guidance_actions.py, or guidance.py.
"""
from __future__ import annotations


class Echo:
    """Destination mark. Sets _echo on an AgentTool callable — AgentOperation or AgentInstructions."""

    # flag is _echo
    # must apply to AgentInstructions as well as AgentOperation
    # begin and instructions are AgentInstructions

    def apply(self, operation):
        # sets operation._echo
        ...


class PromptEcho:
    """preToolUse hook. Toasts when the invoked member, or inherited begin, is marked Echo."""

    def on_pre_tool_use(self, payload: dict) -> dict:
        # -> handle
        ...

    def handle(self, payload: dict) -> dict:
        # invoked member _echo → toast that member (Action / Practice / Fidelity)
        # else toolset begin _echo → Action → kit name
        # -> show_ide_toast
        ...


class GuidanceAction:
    """Shared action prelude. begin is the one Echo for every kit."""

    def run(self, guidance, operation, *, action: str = "") -> list:
        # -> begin
        ...

    def begin(self, guidance=None, action: str = "") -> str:
        # @echo here — one mark; every kit runs this
        # run always calls begin; Sketch.sketch and GrillContext.grill call begin directly
        ...

    def open_workspace(self, name: str = "", path: str = "") -> str:
        # not the action echo
        ...


class Generate(GuidanceAction):
    def generate(self, guidance) -> str:
        # -> run
        # later @echo on this method still works
        ...


class Sketch(GuidanceAction):
    def sketch(self, guidance) -> str:
        # -> begin
        # later @echo on this method still works
        ...


class PracticeGuidance:
    def instructions(self) -> str:
        # @echo independent of begin
        ...


class FidelityGuidance:
    def instructions(self) -> str:
        # @echo independent of begin
        ...
