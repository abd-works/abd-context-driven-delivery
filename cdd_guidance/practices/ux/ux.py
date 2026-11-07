"""UX generator - multi-fidelity IA, mockups, specs, and production frontend (front_end_code)."""

from __future__ import annotations

from typing import Any

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from harness.guidance.practice_catalogue import PracticeCatalogue


class NoJavascriptPractice(ValueError):
    """ensure_javascript was asked for JavaScript from a practice that does not write the JavaScript a mockup imports."""


@agent_toolset
class Ux(PracticeGuidance):
    """# Instructions"""

    sketch_titles = ("ux:", "user experience:")
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

    # The practices whose JavaScript a mockup imports: story steps from Stories, the object model from Clean Engineering.
    javascript_practices = ("stories", "clean_engineering")

    @agent_tool
    def ensure_javascript(self, practice: str, source_format: str, content: Any) -> dict:
        """Ensure Stories or Clean Engineering JS exists - transform via that practice if needed.
        practice: 'stories' | 'clean_engineering', the practice's catalogue key. The practice works in this practice's
        session and workspace. Returns {format: javascript, content: ...}."""
        if practice not in self.javascript_practices:
            raise NoJavascriptPractice(
                f"Unsupported practice {practice!r}. Choose from: {', '.join(self.javascript_practices)}"
            )
        companion = PracticeCatalogue.create(practice)
        companion.session = self.session
        companion.workspace = self.workspace
        return companion.render("javascript", content, source=source_format)
