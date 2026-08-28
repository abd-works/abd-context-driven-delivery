# @toolset-manifest python -m tools manifest sketch.sketch:Sketch
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
"""Sketch a solution interactively before generating the formal artifact.

Sketch is a standalone toolset. Any agent or human can invoke its tools and
sketch_session action directly without decorating anything.
"""
from __future__ import annotations

from pathlib import Path

from grill_context.grill_context import GrillContext
from lifecycle import LifecycleAction
from harness.harness_tool import prompt
from primitives.actions.action import agent_instructions, agentic_toolset
from tools.tool import agent_tool
from workspace import docs_dir


_DEFAULT_TEMPLATE = Path(__file__).parent / "templates" / "sketch-template.md"


@agentic_toolset
class Sketch(LifecycleAction):
    """Sketch a solution interactively before generating the formal artifact."""

    def __init__(self, agent_dir: str = "", path: str = ".", session: str = "") -> None:
        super().__init__(path=path, session=session)
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

    def _generate(self):
        from generate.generate import Generate

        return Generate()

    @agent_tool
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

    @agent_tool
    def save_sketch(
        self,
        destination: str,
        slug: str,
        content: str,
    ) -> str:
        """Persist a sketch to the destination docs dir as {slug}-sketch.md.
        Destination is session.path (or session.docs_dir). Files land in
        {path}/.context/{slug}-sketch.md — never sessions/{name}/ and never
        {path}/.context/{session-name}/. Module sketches: destination =
        {session.path}/{module} → {destination}/.context/. Creates parents
        if missing. Overwrites same path. Returns the resolved sketch path."""
        target = self._sketch_path(destination, slug)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return str(target)

    @agent_tool
    def list_sketches(self, destination: str, slug: str = "") -> str:
        """List sketch files under the destination docs dir.
        If slug is provided, filters to sketches matching that slug prefix.
        Returns newline-separated paths; empty string if the folder is missing or empty."""
        context_dir = docs_dir(destination)
        if not context_dir.is_dir():
            return ""
        pattern = f"{slug}-sketch.md" if slug else "*-sketch.md"
        return "\n".join(str(path) for path in sorted(context_dir.glob(pattern)))

    @prompt
    @agent_instructions
    def sketch(self, tools: list) -> str:
        """Sketch then generate - grill + sketch cadence, then the host generate body."""
        """Sketch interactively - rough artifact through an explicit grill_with_context call. MUST persist via save_sketch on the first interim draft and overwrite on every refinement. Never leave the sketch only in chat. destination defaults to session.path (durable {path}/.context/) — not session.folder. Module sketches: {session.path}/{module}. Question shape (frame + options) comes from grill_with_context - do not restate bare options here."""
        """Step 0 - Grill the sketch plan (concept-grounded questions via grill_with_context)."""
        """Step 1 - Resolve destination: session.path (or session.docs_dir). Module -> {session.path}/{module}. If no session sprint exists yet, confirm path with the user, suggest a kebab slug, open, then use session.path. Do not invent {path}/.context/{session-name}/ or write the sketch into sessions/{name}/."""
        """Step 2 - locate the sketch template via find_template(agent_dir=agent_dir). agent_dir is the concrete host toolset module directory (manifest chain agent_dir / module_dir of the invoked Context). If the caller supplied a template directly in context, use that instead."""
        """Step 3 - draft a rough sketch inspired by the template. Show it in chat, then IMMEDIATELY call save_sketch(destination, slug, content) before continuing the grill. A sketch that exists only in chat is a defect - the file under the destination docs dir is the working record."""
        """Step 4 - After every 2-3 grill answers, regenerate the sketch showing exactly what changed, show it in chat, and IMMEDIATELY call save_sketch again (same path). Use placeholders for unresolved branches. Do not write formal generate artifacts during the sketch loop - that is iterate/generate territory."""
        """Step 5 - Repeat until the sketch is stable, the user is satisfied, or the user switches to iterate/generate. Every new grill question still follows grill's Step 3a-3b; this stage only owns sketch persist/show cadence."""
        self.begin(tools, action="sketch")
        for host in self.context_tools(tools):
            self._grill_context().grill_with_context()
            self.find_template()
            self.save_sketch()
            self._generate().generate(tools=[host])
        self.end()
        return "Sketch complete; generate instructions applied."
