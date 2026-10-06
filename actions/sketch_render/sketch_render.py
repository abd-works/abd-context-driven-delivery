"""Sketch then render — on sketch approval, render via a background sub-agent."""
from __future__ import annotations

import json
from pathlib import Path

from grill_context.grill_context import GrillContext
from harness.agent_tools import agent_instructions, agent_toolset, instructions, subAgent
from harness.agent_tools.agent_tools import agent_tool
from harness.guidance_actions import GuidanceArg, GuidanceAction
from installation.files import Skill
from harness.mcp.mcp_server import Mcp

STAGE_DEFAULT_FORMATS: dict[str, list[str]] = {
    "discovery": ["drawio", "markdown"],
    "specification": ["typescript", "markdown"],
}

# Sketch → formal artifact: only combinations that have a sketch parse channel and a real target.
# UX markdown is ux-context notes, not IA. DDD markdown expects bounded-context-map shape, not sketch dump.
SKETCH_RENDER_FORMATS: dict[str, dict[str, list[str]]] = {
    "discovery": {
        "practices.stories.stories:Stories": ["drawio", "markdown"],
        "practices.ddd.ddd:Ddd": ["drawio", "markdown"],
        "practices.ux.ux:Ux": ["drawio"],
    },
    "specification": {
        "practices.stories.stories:Stories": ["typescript", "markdown"],
    },
}


@agent_toolset
class SketchRender(GuidanceAction):
    """Sketch interactively; render the approved sketch in a background sub-agent."""

    def __init__(self, path: str = ".", session: str = "") -> None:
        super().__init__(path=path, session=session)
        self.path = path

    def _sketch(self):
        from sketch.sketch import Sketch

        return Sketch(path=self.path, session=self._session_name)

    def _grill_context(self) -> GrillContext:
        return GrillContext()

    def stage_default_formats(self, stage: str) -> list[str]:
        """Default render formats for a fidelity stage."""
        return list(STAGE_DEFAULT_FORMATS.get(stage, STAGE_DEFAULT_FORMATS["discovery"]))

    def _current_stage(self, item) -> str:
        if isinstance(item, str):
            return "discovery"
        current = getattr(getattr(item, "fidelities", None), "current", None)
        return getattr(current, "stage", None) or "discovery"

    def _registration_key(self, item) -> str:
        return getattr(item, "registration_name", "") or ""

    def _sketch_render_formats(self, item, stage: str) -> list[str]:
        by_stage = SKETCH_RENDER_FORMATS.get(stage, {})
        keyed = by_stage.get(self._registration_key(item))
        if keyed:
            return list(keyed)
        supported = getattr(item, "supported_formats", frozenset())
        if "sketch" not in supported:
            return []
        return [
            fmt
            for fmt in self.stage_default_formats(stage)
            if not supported or fmt in supported
        ]

    def _available_formats(self, item) -> frozenset[str]:
        if isinstance(item, str):
            return frozenset(self._sketch_render_formats(item, "discovery"))
        return frozenset(self._sketch_render_formats(item, self._current_stage(item)))

    def _default_formats_for_listed(self) -> list[str]:
        chosen: list[str] = []
        for item in self.listed():
            if isinstance(item, str):
                continue
            for fmt in self._sketch_render_formats(item, self._current_stage(item)):
                if fmt not in chosen:
                    chosen.append(fmt)
        return chosen or list(STAGE_DEFAULT_FORMATS["discovery"])

    def _guidance_ref(self, item) -> dict[str, str]:
        fidelity = item.fidelities.current
        return {
            "toolset": item.registration_name,
            "fidelity": fidelity.name,
        }

    @Mcp
    @agent_tool
    def build_render_calls(
        self,
        formats: list[str],
        sketch_path: str,
    ) -> str:
        """Build explicit render.render MCP calls for each listed Guidance and format.
        Pass the approved sketch path and the chosen formats. Returns JSON the sub-agent runs verbatim."""
        content = Path(sketch_path).read_text(encoding="utf-8")
        calls: list[dict[str, object]] = []
        for item in self.listed():
            if isinstance(item, str):
                continue
            ref = self._guidance_ref(item)
            allowed = self._sketch_render_formats(item, self._current_stage(item))
            for fmt in formats:
                if fmt not in allowed:
                    continue
                calls.append(
                    {
                        "tool": "render.render",
                        "arguments": {
                            "guidance": ref,
                            "format": fmt,
                            "content": content,
                            "source": "sketch",
                        },
                    }
                )
        return json.dumps(calls, indent=2)

    def _render(self):
        from render.render import Render

        return Render()

    @agent_instructions
    def confirm_render_formats(self) -> str:
        """After review_sketch confirms the sketch, AskQuestion whether to render now.
        Required pairs by stage: discovery → drawio and markdown (both); specification → typescript and markdown (both).
        Pass both formats to build_render_calls unless a listed Guidance lacks that channel in supported_formats.
        Do not ask the user to pick a single format unless they explicitly want to override the pair."""
        defaults = ", ".join(self._default_formats_for_listed())
        return (
            "AskQuestion whether to render the approved sketch now. "
            f"Required formats for this stage: {defaults} — pass both to build_render_calls. "
            "Skip a format only when a listed Guidance does not support it."
        )

    @subAgent
    @agent_instructions
    def render_approved_sketch(self, render_calls: str) -> str:
        """Render the approved sketch in a background sub-agent.
        Run every entry in render_calls — each is render.render with guidance, format, content, and source=sketch.
        After all render calls, follow render.place_rendered on the written files."""
        "{{render_calls}}"
        self._render().place_rendered()
        return "Render approved sketch in background."

    @Mcp
    @Skill
    @agent_instructions
    def sketch_render(self, guidance: GuidanceArg) -> str:
        """Sketch interactively like sketch; on review_sketch approval confirm formats, build render calls, and render via sub-agent.
        Pass one or more guidance tools — practice or fidelity slugs, or module:Class refs."""
        self.begin(guidance, action="sketch_render")
        for item in self.listed():
            instructions(item.rules.markdown_block)
            instructions(item.sketch_template)
        self._grill_context().grill_with_context()
        self._sketch().find_template()
        self._sketch().save_sketch()
        self._sketch().review_sketch()
        self.confirm_render_formats()
        self.build_render_calls()
        self.render_approved_sketch()
        self.end()
        return "Sketch complete; render launched in background."
