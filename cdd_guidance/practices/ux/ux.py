"""UX generator - multi-fidelity IA, mockups, specs, and production frontend (front_end_code)."""

from __future__ import annotations

import itertools
import os
from pathlib import Path, PurePosixPath

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.design_canvas.versions import DESIGN_CANVAS_FOLDER
from harness.guidance.guidance import PracticeGuidance
from harness.guidance.guidance import SketchLens
from harness.guidance.practice_formats import PracticeFormats, Rendered, RenderContent, RenderRequest, TextOrData
from harness.guidance.worked_session import NamedPaths
from harness.markdown.format import Format

from cdd_guidance.practices.ux.model.graph_reading import UxReading
from cdd_guidance.practices.ux.model.ux_map import UxMap
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


class UxFolderSearch:
    """The folders under root, nearest first, looked through for the one holding a project's UX map (``ux.json``) or
    its design canvas (``design-canvas/``). Hidden folders and installed packages are passed over, and the search stops
    a few folders down and after a few hundred folders, so a large project, or a root that is no project at all, such
    as a temporary folder, is not read through on every question about UX's folder."""

    MARKERS = ("ux.json", DESIGN_CANVAS_FOLDER)
    PASSED_OVER = frozenset({"node_modules", "__pycache__", "venv", "dist", "build"})
    DEPTH = 3
    FOLDERS_LOOKED_AT = 300

    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def nearest(self) -> Path | None:
        """The nearest folder holding a marker; the conventional ``ux`` folder is looked at first. None when no folder
        within the search holds one."""
        conventional = self.root / Ux.default_workspace_folder
        if self._holds_marker(conventional):
            return conventional
        level, looked_at = [self.root], 0
        for _ in range(self.DEPTH + 1):
            level = level[:self.FOLDERS_LOOKED_AT - looked_at]
            found = next((folder for folder in level if self._holds_marker(folder)), None)
            looked_at += len(level)
            if found is not None or looked_at >= self.FOLDERS_LOOKED_AT:
                return found
            level = [child for folder in level for child in self._subfolders(folder)]
        return None

    def _holds_marker(self, folder: Path) -> bool:
        return any((folder / marker).exists() for marker in self.MARKERS)

    def _subfolders(self, folder: Path) -> list[Path]:
        """The folders in folder the search goes into, by name; at most as many entries are read as the search looks
        at folders, so one folder holding thousands is not read through."""
        try:
            with os.scandir(folder) as entries:
                read = list(itertools.islice(entries, self.FOLDERS_LOOKED_AT))
        except PermissionError:
            # A folder the user may not list, such as a Windows junction in a home folder, holds no UX map to find.
            return []
        return [Path(entry.path) for entry in sorted(read, key=lambda entry: entry.name)
                if entry.is_dir() and not entry.name.startswith(".") and entry.name not in self.PASSED_OVER]


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

    def read(self, paths: NamedPaths, request: RenderRequest) -> RenderContent:
        """What request converts from the files at paths: what the map's format reads beside the first of them when it
        is written as several files, such as a Claude Design canvas's prototype pages beside its canvas.json; else
        their text."""
        source = self.adapter(request.source_format) if request.source_format in self else None
        beside = source.content_beside(self._first_path(paths)) if isinstance(source, UxMap) and paths else None
        return super().read(paths, request) if beside is None else beside

    def _first_path(self, paths: NamedPaths) -> Path:
        """The first of paths, read from the project of the session the practice works in."""
        first = paths if isinstance(paths, str) else paths[0]
        session = self._practice.session
        return session.paths.path_named(first) if session is not None else Path(first)

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
    # The folder default_folder found under each root the session worked in, held on this instance once searched.
    _default_folders: dict[Path, str] | None = None
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

    @property
    def default_folder(self) -> str:
        """The folder UX writes into while nobody chose a root for it: the folder under the session's root that holds
        the project's UX map (``ux.json``) or its design canvas (``design-canvas/``), the nearest first, else ``ux``.
        A project that keeps its UX work elsewhere is then read where it is, rather than in an empty ``ux`` folder.
        Searched once for each root the session works in, since the session asks for its practices' folders often."""
        if self.session is None:
            return self.default_workspace_folder
        root = self.session.work_root
        if not root.is_relative_to(self.session.checkout.root.resolve()):
            # A workpath outside the project, such as a home folder, holds no project's UX work to search for.
            return self.default_workspace_folder
        if self._default_folders is None:
            self._default_folders = {}
        if root not in self._default_folders:
            found = UxFolderSearch(root).nearest()
            self._default_folders[root] = self.default_workspace_folder if found is None else Path(found).relative_to(root).as_posix()
        return self._default_folders[root]

    def placed_under(self, declared: PurePosixPath, root: Path) -> Path | None:
        """Where a path a UX fidelity declares lands under root. A design canvas (``design-canvas/...``) lands in the
        UX practice's own root, the folder the session names for it (``ux`` by default), where
        ``CanvasVersions.in_practice_root`` keeps its versions, rather than in the session's root."""
        if declared.parts[:1] == (DESIGN_CANVAS_FOLDER,) and self._session_output is not None:
            return Path(self._session_output.folder) / declared
        return super().placed_under(declared, root)

    @agent_tool
    def ensure_javascript(self, practice: str, source_format: str, content: str) -> Rendered:
        """Ensure Stories or Clean Engineering JS exists - transform via that practice if needed.
        practice: 'stories' | 'clean_engineering', the practice's catalogue key: story steps come from Stories, the
        object model from Clean Engineering. content: the practice's text in source_format. Returns {format: javascript, content: ...}."""
        return self._javascript_practice(practice).render("javascript", content, source=source_format)

    @agent_tool
    def render_story_canvas(self) -> str:
        """Render the project's story canvas in the claude_design format: the story map below the Stories practice's
        root, the UX map (ux.json) in the UX practice's root, the fixtures bundle the session's stack pattern builds,
        the screens already in the working version, the story map and the story explorer, then the walk of the screens
        (walk.md). Stops, rendering nothing, when the fixtures cannot be built. Returns where it rendered and what the
        walk found missing."""
        from cdd_guidance.practices.ux.model.claude_design.project_story_canvas import ProjectStoryCanvas

        if self.session is None:
            raise UxOutsideSession("Ux works in no session, so it knows no project roots to render the story canvas from.")
        root = self.session.checkout.root
        canvas = ProjectStoryCanvas(project_root=root, ux_root=Path(self._session_output.folder),
                                    stories_root=Path(self.session.practices["stories"].folder),
                                    fixtures=self._canvas_fixtures(root))
        return canvas.render().summary()

    def _canvas_fixtures(self, workspace: Path) -> object:
        """The fixtures builder of the first pattern the session overlays that builds canvas fixtures, else one that
        stops the render and says so."""
        from cdd_guidance.practices.ux.model.claude_design.project_story_canvas import NoCanvasFixtures
        from harness.graph.pattern_overlays import PatternOverlays

        overlays = list(self.session.overlays)
        for pattern in PatternOverlays(overlays).patterns:
            builds = getattr(pattern, "canvas_fixtures", None)
            if builds is not None:
                return builds(workspace)
        return NoCanvasFixtures(overlays)

    def _javascript_practice(self, key: str) -> PracticeGuidance:
        """The practice key, which writes the JavaScript a mockup imports: the session's own, with the fidelity and
        format it works at there."""
        if self.session is None:
            raise UxOutsideSession(f"Ux works in no session, so it holds no {key!r} practice to write JavaScript through.")
        return self.session.practices[key].guidance


UxNode.practice_class = Ux
