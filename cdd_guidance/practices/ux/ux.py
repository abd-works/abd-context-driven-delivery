"""UX generator - multi-fidelity IA, mockups, specs, and production frontend (front_end_code)."""

from __future__ import annotations

from typing import Any

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.guidance.guidance import PracticeGuidance

from cdd_guidance.practices.ux.model.ux_node import UxNode


class NoJavascriptPractice(ValueError):
    """ensure_javascript was asked for JavaScript from a practice that does not write the JavaScript a mockup imports."""


class UxOutsideSession(ValueError):
    """ensure_javascript was asked of a Ux that works in no session, so it has no Stories or Clean Engineering of its
    own to render the JavaScript through."""


@agent_toolset
class Ux(PracticeGuidance):
    """# Instructions"""

    sketch_titles = ("ux:", "user experience:")
    model_classes = (UxNode,)
    SHORT_NAME = "UX"
    COLOUR = "#E84393"

    # How the catalog shows this practice; the generator discovers it like the installer does.
    catalog_card = {
        "name": "User Experience",
        "label": "user-experience",
        "family": "aad-fam-uxd",
        "perspective": "uxd",
        "order": 30,
        "blurb": "Defining user impact from journey and information architecture to screen navigation.",
        "spec_blurb": "Interface mockups that work according to story specs and design templates",
    }

    def __init__(
        self,
        fidelity: str = "ia",
        format: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            fidelity=fidelity,
            default_workspace_folder="ux",
            formats={
                "drawio": ("cdd_guidance.practices.ux.model.drawio.nodes", "DrawioUxMap"),
                "html": ("cdd_guidance.practices.ux.model.html.nodes", "HtmlUxMap"),
                "markdown": ("cdd_guidance.practices.ux.model.markdown.nodes", "MarkdownUxMap"),
                "json": ("cdd_guidance.practices.ux.model.json.nodes", "JsonUxMap"),
                "claude_design": ("cdd_guidance.practices.ux.model.claude_design.nodes", "ClaudeDesignUxMap"),
            },
        )

    # In the knowledge graph: UX checks its screen rules on the UX maps put on a graph and offers the explorer the node
    # types a UX map is made of. A working-copy load reads no UX files yet.
    node_types = (
        "UxMap",
        "Screen",
        "Region",
        "Control",
        "StoryDemoControl",
        "Interaction",
        "Transition",
        "ContentType",
        "NavComponent",
        "UxContext",
    )

    @agent_tool
    def ensure_javascript(self, practice: str, source_format: str, content: Any) -> dict:
        """Ensure Stories or Clean Engineering JS exists - transform via that practice if needed.
        practice: 'stories' | 'clean_engineering', the practice's catalogue key: story steps come from Stories, the
        object model from Clean Engineering. Returns {format: javascript, content: ...}."""
        return self.javascript_practice(practice).render("javascript", content, source=source_format)

    def javascript_practice(self, key: str) -> PracticeGuidance:
        """The practice key, which writes the JavaScript a mockup imports: the session's own, with the fidelity and
        format it works at there."""
        if self.session is None:
            raise UxOutsideSession(f"Ux works in no session, so it holds no {key!r} practice to write JavaScript through.")
        practice = self.session.practices[key].guidance
        if "javascript" not in practice.formats:
            raise NoJavascriptPractice(f"Practice {key!r} writes no JavaScript; Stories and Clean Engineering do.")
        return practice
