"""UX generator - multi-fidelity IA, mockups, specs, and production frontend (front_end_code)."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from harness.guidance.guidance import SketchLens
from harness.guidance.practice_formats import PracticeFormats, Rendered, RenderRequest, TextOrData
from harness.markdown.format import Format

from cdd_guidance.practices.ux.model.graph_reading import UxReading
from cdd_guidance.practices.ux.model.ux_node import UxNode


class UxOutsideSession(ValueError):
    """ensure_javascript was asked of a Ux that works in no session, so it has no Stories or Clean Engineering of its
    own to render the JavaScript through."""


class ViewNotRendered(ValueError):
    """A render was asked to make a UX map's format from a front-end view, or a view from a UX map's format. A view is
    production code, rendered between typescript and javascript only; no UX format reads one into the UX map or writes
    one from it."""

    def __init__(self, format: Format, source: Format) -> None:
        super().__init__(f"A front-end view is rendered between typescript and javascript only: no render makes {format} from {source}.")
        self.format = format
        self.source = source


class UxFormats(PracticeFormats):
    """The formats UX reads and writes: the UX map's, each through its adapter, and the view formats of its front-end
    code fidelity (typescript, javascript), which render into each other and into no format of the UX map."""

    @property
    def view_formats(self) -> frozenset[Format]:
        """The formats a front-end view is written in: the code formats among UX's."""
        return frozenset(format for format in self.supported if format.is_code)

    def render(self, request: RenderRequest) -> Rendered:
        """What request renders to: a view to the other view format, a UX map to another of its formats. A render
        between a view format and a format of the UX map is refused as *ViewNotRendered*, before a view's text is
        read as a mockup page."""
        views = self.view_formats
        source = request.source_format
        if (request.format in views) != (source in views):
            raise ViewNotRendered(request.format, source)
        return super().render(request)

    def _incoming(self, format: Format, content: TextOrData) -> TextOrData:
        """content as format's adapter reads it: a view is its text as it is, though it start with a brace as a JSON
        document does."""
        return content


@agent_toolset
class Ux(PracticeGuidance):
    """# Instructions"""

    sketch_lens = SketchLens(("ux:", "user experience:"))
    reading_type = UxReading
    formats_type = UxFormats
    SHORT_NAME = "UX"
    COLOUR = "#E84393"

    @property
    def markdown_values(self) -> dict[str, str]:
        """Whether each of its graph rules is checked or judged, for the marker the rule's text carries in its document
        (``{{decided.<rule>}}``): the rule's own ``requires_judge`` says which, so it is typed in no document."""
        from cdd_guidance.practices.ux.rules import RULES
        from harness.graph.practice_rule import decided_values

        return decided_values(RULES)

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

    first_fidelity = "ia"

    default_workspace_folder = "ux"
    format_adapters = {
        "drawio": ("cdd_guidance.practices.ux.model.drawio.nodes", "DrawioUxMap"),
        "whiteboard": ("cdd_guidance.practices.ux.model.whiteboard.nodes", "WhiteboardUxMap"),
        "html": ("cdd_guidance.practices.ux.model.html.nodes", "HtmlUxMap"),
        "markdown": ("cdd_guidance.practices.ux.model.markdown.nodes", "MarkdownUxMap"),
        "json": ("cdd_guidance.practices.ux.model.json.nodes", "JsonUxMap"),
        "claude_design": ("cdd_guidance.practices.ux.model.claude_design.nodes", "ClaudeDesignUxMap"),
        "typescript": ("cdd_guidance.practices.ux.model.view.view_formats", "TypeScriptView"),
        "javascript": ("cdd_guidance.practices.ux.model.view.view_formats", "JavaScriptView"),
    }

    @agent_tool
    def ensure_javascript(self, practice: str, source_format: str, content: str) -> Rendered:
        """Ensure Stories or Clean Engineering JS exists - transform via that practice if needed.
        practice: 'stories' | 'clean_engineering', the practice's catalogue key: story steps come from Stories, the
        object model from Clean Engineering. content: the practice's text in source_format. Returns {format: javascript, content: ...}."""
        return self._javascript_practice(practice).render("javascript", content, source=source_format)

    def _javascript_practice(self, key: str) -> PracticeGuidance:
        """The practice key, which writes the JavaScript a mockup imports: the session's own, with the fidelity and
        format it works at there."""
        if self.session is None:
            raise UxOutsideSession(f"Ux works in no session, so it holds no {key!r} practice to write JavaScript through.")
        return self.session.practices[key].guidance


UxNode.practice_class = Ux
