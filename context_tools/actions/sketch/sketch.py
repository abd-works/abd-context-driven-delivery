# @toolset-manifest python -m tools manifest sketch.sketch:Sketcher
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Sketch a solution interactively before generating the formal artifact.

Sketcher is a standalone toolset. Any agent or human can invoke its tools and
sketch_session action directly without decorating anything.
"""
from __future__ import annotations

from pathlib import Path

from grill_context.grill_context import GrillContext
from primitives.actions.action import action
from tools.tool import _ToolsetLoader, tool, toolset
from workspace import docs_dir


def context_tool(item: object) -> object:
    """Resolve a tools item to a context-tool instance (path, mapping, or already loaded)."""
    if isinstance(item, str):
        return _ToolsetLoader.instance().load(item)()
    if isinstance(item, dict):
        loaded = _ToolsetLoader.instance().load(str(item["toolset"]))
        return loaded(**(item.get("context") or {}))
    return item


_DEFAULT_TEMPLATE = Path(__file__).parent / "templates" / "sketch-template.md"


@toolset
class Sketcher:
    """Sketch a solution interactively before generating the formal artifact."""

    def __init__(self, agent_dir: str = "") -> None:
        self._agent_dir = agent_dir

    def _sketch_path(self, destination: str, slug: str) -> Path:
        """Resolve sketch path under the destination docs dir (pure)."""
        return docs_dir(destination) / f"{slug}-sketch.md"

    @property
    def sketch_template(self) -> str:
        """The sketch template for this instance's agent_dir (tiered discovery)."""
        return self.find_template(agent_dir=self._agent_dir)

    def _grill_context(self) -> GrillContext:
        """GrillContext toolset for in-method composition (not a tool)."""
        return GrillContext()

    @tool
    def find_template(self, agent_dir: str = "") -> str:
        """Locate a sketch template using tiered discovery.
        1. Session context - the caller passes an example directly (skip this tool).
        2. Convention - {agent_dir}/templates/*-sketch.* inside the wrapped agent's templates folder.
        3. Default - sketch/templates/sketch-template.md (this toolset's canonical terse-indent notation).
        Returns the resolved template contents as a string."""
        if agent_dir:
            root = Path(agent_dir)
            if root.is_dir():
                templates_dir = root / "templates"
                if templates_dir.is_dir():
                    for path in sorted(templates_dir.glob("*-sketch.*")):
                        return path.read_text(encoding="utf-8")
        return _DEFAULT_TEMPLATE.read_text(encoding="utf-8")

    @tool
    def save_sketch(
        self,
        destination: str,
        slug: str,
        content: str,
    ) -> str:
        """Persist a sketch to the destination docs dir as {slug}-sketch.md.
        Engagement sketches: destination = session.folder
        ({path}/.context/sessions/{name}/) - files are written flat in that sprint.
        Module sketches: destination = {session.path}/{module} - files go under
        {destination}/.context/. Creates parents if missing. Overwrites same path.
        Returns the resolved sketch path."""
        target = self._sketch_path(destination, slug)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return str(target)

    @tool
    def list_sketches(self, destination: str, slug: str = "") -> str:
        """List sketch files under the destination docs dir.
        If slug is provided, filters to sketches matching that slug prefix.
        Returns newline-separated paths; empty string if the folder is missing or empty."""
        context_dir = docs_dir(destination)
        if not context_dir.is_dir():
            return ""
        pattern = f"{slug}-sketch.md" if slug else "*-sketch.md"
        return "\n".join(str(path) for path in sorted(context_dir.glob(pattern)))

    @action
    def sketch(self, tools: list) -> str:
        """Sketch then generate - grill + sketch cadence, then the host generate body."""
        for item in tools:
            host = context_tool(item)
            host.workspace.open()
            host.decisions.record_decisions_session()
            self.sketch_session()
            host.generate()
        return "Sketch complete; generate instructions applied."

    @action
    def sketch_session(self, slug: str, destination: str, agent_dir: str = "") -> str:
        """Sketch {{slug}} interactively - rough artifact through an explicit grill_with_context call. MUST persist via save_sketch on the first interim draft and overwrite on every refinement. Never leave the sketch only in chat. destination defaults to session.folder (sprint) for engagement sketches, or {session.path}/{module} for module sketches. Question shape (frame + options) comes from grill_with_context - do not restate bare options here."""
        """Step 0 - Grill the sketch plan (concept-grounded questions via grill_with_context)."""
        self._grill_context().grill_with_context(slug)
        """Step 1 - Resolve destination: engagement -> session.folder; module -> {session.path}/{module}. If no session sprint exists yet, confirm path with the user, suggest a kebab slug, create_session, then use session.folder. Do not invent a divergent folder."""
        """Step 2 - locate the sketch template via find_template(agent_dir=agent_dir). agent_dir is the concrete host toolset module directory (manifest chain agent_dir / module_dir of the invoked Context). If the caller supplied a template directly in context, use that instead."""
        self.find_template(agent_dir)
        """Step 3 - draft a rough sketch inspired by the template. Show it in chat, then IMMEDIATELY call save_sketch(destination, slug, content) before continuing the grill. A sketch that exists only in chat is a defect - the file under the destination docs dir is the working record."""
        self.save_sketch()
        """Step 4 - After every 2-3 grill answers, regenerate the sketch showing exactly what changed, show it in chat, and IMMEDIATELY call save_sketch again (same path). Use placeholders for unresolved branches. Do not write formal generate artifacts during the sketch loop - that is iterate/generate territory."""
        self.save_sketch()
        """Step 5 - Repeat until the sketch is stable, the user is satisfied, or the user switches to iterate/generate. Every new grill question still follows grill's Step 3a-3b; this stage only owns sketch persist/show cadence."""
        return "Sketch saved for {{slug}} under {{destination}}."
