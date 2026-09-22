"""PromptEcho — model fidelity (Python channel).

Stubs only. Same types as prompt-echo-model.md. Does not replace
prompt_echo.py, guidance_actions.py, or guidance.py.
"""
from __future__ import annotations

from pathlib import Path


# FILE: prompt_echo.py
class Echo:
    """Destination mark. Sets _echo on an AgentTool callable — AgentOperation or AgentInstructions."""

    flag: str
    # must apply to AgentInstructions as well as AgentOperation
    # begin and instructions are AgentInstructions

    def annotate(self, operation):
        # must set _echo on the callable
        ...


class PromptEcho:
    """preToolUse hook. Toasts when the invoked member, or inherited begin, is marked Echo."""

    @property
    def catalog(self) -> list[tuple[str, str]]:
        # must be longest-token-first
        # always includes fallback action names
        ...

    def on_pre_tool_use(self, hook_payload: HookPayload) -> HookResult:
        # after handle, always show_ide_toast when user_message is present
        # -> PromptEcho.handle
        # -> PromptEcho.show_ide_toast
        ...

    def handle(self, hook_payload: HookPayload, toolsets: list[AgentToolSet] | None = None) -> HookResult:
        # empty tool_name must allow quietly
        # must try detect_echo before detect
        ...

    def detect_echo(self, hook_payload: HookPayload, toolsets: list[AgentToolSet] | None = None) -> tuple[str, str] | None:
        # never treat inherited begin as the echo for instructions
        # never toast open_workspace, end, or begin from inherited begin
        # -> PromptEcho.echo_toolsets
        ...

    def detect(self, hook_payload: HookPayload) -> tuple[str, str] | None:
        # never toast an action from a path haystack
        # always name a guideline when the haystack is a rules path
        ...

    def echo_toolsets(self, repo: Path | None = None) -> list[AgentToolSet]:
        # -> AgentToolSet.load_toolsets
        ...

    def show_ide_toast(self, echo: str, repo: Path | None = None) -> Path:
        # must join same-burst inject lines
        # never overwrite an earlier Guidance in that burst
        ...

    def inject_rules_toast(self, source: str, labels: list[str]) -> str:
        # always prefix the joined names with rules :
        ...

    def toast_notice(self, echo: str) -> dict[str, str]:
        ...

    def install_ide_toast_extension(self) -> Path:
        ...


# FILE: guidance_actions.py
class GuidanceAction:
    """Shared action prelude. begin is the one Echo for every kit."""

    def run(self, guidance, operation, *, action: str = "") -> list:
        # always calls begin
        # -> begin
        ...

    def begin(self, guidance=None, action: str = "") -> str:
        # always the one action Echo mark
        # run always calls begin; Sketch.sketch and GrillContext.grill call begin directly
        ...

    def open_workspace(self, name: str = "", path: str = "") -> str:
        # never the action echo
        ...

    def inject_rules(self, hook_payload: HookPayload) -> HookResult:
        # -> PromptEcho.inject_rules_toast
        # -> PromptEcho.show_ide_toast
        ...


class Generate(GuidanceAction):
    """Kit that runs through GuidanceAction.run."""

    def generate(self, guidance) -> str:
        # -> run
        ...


class Sketch(GuidanceAction):
    """Kit that calls GuidanceAction.begin directly."""

    def sketch(self, guidance) -> str:
        # -> begin
        ...


# FILE: guidance.py
class PracticeGuidance:
    """Practice prompt. Echo on instructions is independent of begin."""

    def instructions(self) -> str:
        # never inherit action echo from begin
        ...


class FidelityGuidance:
    """Fidelity prompt. Echo on instructions is independent of begin."""

    def instructions(self) -> str:
        # never inherit action echo from begin
        ...
