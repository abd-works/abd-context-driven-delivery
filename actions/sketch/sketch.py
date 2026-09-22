"""Sketch a solution interactively before generating the formal artifact.

Sketch is a standalone toolset. Any agent or human can invoke its tools and
sketch_session action directly without decorating anything.
"""
from __future__ import annotations

from pathlib import Path

from grill_context.grill_context import GrillContext
from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset
from harness.agent_tools.agent_tools import agent_tool
from installation.files import Skill
from harness.mcp.mcp_server import Mcp

_DEFAULT_TEMPLATE = Path(__file__).parent / "templates" / "sketch-template.md"

@agent_toolset
class Sketch(GuidanceAction):
    """Sketch a solution interactively before generating the formal artifact."""

    def __init__(self, agent_dir: str = "", path: str = ".", session: str = "") -> None:
        super().__init__(path=path, session=session)
        self._agent_dir = agent_dir

    def _sketch_path(self, destination: str, slug: str) -> Path:
        """Resolve sketch path under the destination docs dir (pure)."""
        return Path(destination) / ".context" / f"{slug}-sketch.md"

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

    @Mcp
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

    @Mcp
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

    @Mcp
    @agent_tool
    def list_sketches(self, destination: str, slug: str = "") -> str:
        """List sketch files under the destination docs dir.
        If slug is provided, filters to sketches matching that slug prefix.
        Returns newline-separated paths; empty string if the folder is missing or empty."""
        context_dir = Path(destination) / ".context"
        if not context_dir.is_dir():
            return ""
        pattern = f"{slug}-sketch.md" if slug else "*-sketch.md"
        return "\n".join(str(path) for path in sorted(context_dir.glob(pattern)))

    @Mcp
    @agent_tool
    def review_sketch(self) -> str:
        """Hard gate after every save_sketch — pause for human review before any next grill question.
        1. Pause so the person can look at the persisted sketch (show path + what changed).
        2. AskQuestion: was this sketch correct? (Yes / No — it has mistakes / Other).
        3. If not correct: AskQuestion what mistakes it made (bad assumptions, poor performance, poor hygiene, or anything else named); correct those mistakes in the artifact; save_sketch again; re-enter this gate.
        4. Only after the person confirms the sketch is correct may you ask the next grill question.
        5. Carry forward: every named mistake must shape the next sketch regeneration — correct the model; do not regenerate as if those mistakes never happened.
        Skipping this pause, asking the next question before confirmed-correct, or regenerating while ignoring named mistakes is a defect.
        Grill must validate the sketch's thinking here — not run as a disconnected interview."""
        return "sketch-review"

    @Mcp
    @Skill
    @agent_instructions
    def sketch(self, guidance: GuidanceArg) -> str:
        """Grill the plan with grill: ask short framed questions and wait for answers. After each small batch of answers, sketch only what those answers unlocked, save it, and get user feedback before asking more. Work in short cycles until the sketch is agreed. Then generate the formal artifact from that sketch — do not generate the full product during the sketch loop. Pass a string to sketch that text once."""
        self.begin(guidance, action="sketch")
        self._grill_context().grill_with_context()
        self.find_template()
        self.save_sketch()
        self.review_sketch()
        self.each(lambda item: self._generate().generate(item if isinstance(item, str) else [item]))
        self.end()
        return "Sketch complete; generate instructions applied."
