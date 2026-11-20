"""UX generator - multi-fidelity IA, mockups, specs, and production frontend (front_end_code)."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from harness.guidance.guidance import SketchLens
from harness.guidance.practice_formats import PracticeFormats, RenderRequest
from harness.markdown.format import Format

from cdd_guidance.practices.ux.model.graph_reading import UxReading
from cdd_guidance.practices.ux.model.ux_node import UxNode


class NoJavascriptPractice(ValueError):
    """ensure_javascript was asked for JavaScript from a practice that does not write the JavaScript a mockup imports."""


class UxOutsideSession(ValueError):
    """ensure_javascript was asked of a Ux that works in no session, so it has no Stories or Clean Engineering of its
    own to render the JavaScript through."""


class ViewNotRendered(ValueError):
    """A render was asked to read or write a front-end view. A view is production code a person or an agent writes by
    hand at the front-end code fidelity; no UX format reads one into the UX map or writes one from it."""

    def __init__(self, format: Format) -> None:
        super().__init__(f"UX front-end views are written by hand in {format}, not rendered: no render reads or writes one.")
        self.format = format


class UxFormats(PracticeFormats):
    """The formats UX reads and writes: the UX map's, each through its adapter, and the view formats its front-end code
    fidelity writes by hand (typescript, javascript), which the practice works in but no render converts."""

    @property
    def view_formats(self) -> frozenset[Format]:
        """The formats a UX fidelity writes that no adapter reads: its front-end views."""
        written = {Format(name) for fidelity in self._practice.fidelities for name in fidelity.outputs}
        return frozenset(written - super().supported)

    @property
    def supported(self) -> frozenset[Format]:
        """The formats UX works in: those its adapters read and write, and its view formats."""
        return super().supported | self.view_formats

    def render(self, request: RenderRequest) -> dict:
        """What request renders to; a render to or from a view format is refused as *ViewNotRendered*, before a view's
        text is read as a mockup page or a format list is searched for it."""
        views = self.view_formats
        asked = next((format for format in (request.format, request.source_format) if format in views), None)
        if asked is not None:
            raise ViewNotRendered(asked)
        return super().render(request)


@agent_toolset
class Ux(PracticeGuidance):
    """# Instructions"""

    sketch_lens = SketchLens(("ux:", "user experience:"))
    reading_type = UxReading
    formats_type = UxFormats
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

    first_fidelity = "ia"

    default_workspace_folder = "ux"
    format_adapters = {
        "drawio": ("cdd_guidance.practices.ux.model.drawio.nodes", "DrawioUxMap"),
        "html": ("cdd_guidance.practices.ux.model.html.nodes", "HtmlUxMap"),
        "markdown": ("cdd_guidance.practices.ux.model.markdown.nodes", "MarkdownUxMap"),
        "json": ("cdd_guidance.practices.ux.model.json.nodes", "JsonUxMap"),
        "claude_design": ("cdd_guidance.practices.ux.model.claude_design.nodes", "ClaudeDesignUxMap"),
    }

    @agent_tool
    def ensure_javascript(self, practice: str, source_format: str, content: str) -> dict:
        """Ensure Stories or Clean Engineering JS exists - transform via that practice if needed.
        practice: 'stories' | 'clean_engineering', the practice's catalogue key: story steps come from Stories, the
        object model from Clean Engineering. content: the practice's text in source_format. Returns {format: javascript, content: ...}."""
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


UxNode.practice_class = Ux
