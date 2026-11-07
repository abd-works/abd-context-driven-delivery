"""Sketch a solution interactively before generating the formal artifact.

Sketch is a standalone toolset. Any agent or human can invoke its tools and
sketch_session action directly without decorating anything.
"""
from __future__ import annotations

from pathlib import Path

from cdd_guidance.actions.grill_context.grill_context import GrillContext
from harness.guidance_actions import GuidanceArg, GuidanceAction, load_document
from harness.agent_tools import agent_instructions, agent_toolset, instructions, tools
from harness.agent_tools.agent_tools import agent_tool
from harness.installation.files import Skill
from harness.mcp.mcp_server import Mcp

_DEFAULT_TEMPLATE = Path(__file__).parent / "templates" / "sketch-template.md"

@agent_toolset
class Sketch(GuidanceAction):
    """Sketch a solution interactively before generating the formal artifact."""

    def __init__(self, agent_dir: str = "", session=None) -> None:
        super().__init__(session)
        self._agent_dir = agent_dir

    def made_for(self, session) -> Sketch:
        """A sketch made for session that finds its template in this sketch's agent_dir."""
        return type(self)(agent_dir=self._agent_dir, session=session)

    def _context_folder(self, module: str) -> Path:
        """The .context folder sketches go in: the session root's, or a module's under that root."""
        folder = self.session.root / module if module else self.session.root
        return folder if folder.name == ".context" else folder / ".context"

    @property
    def _sketch_name(self) -> str:
        """The session's sketch file name: a session is named for the subject it works on, so its sketch is too."""
        return f"{self.session.name or 'main'}-sketch.md"

    @property
    def sketch_template(self) -> str:
        """The sketch template for this instance's agent_dir (tiered discovery)."""
        return self.find_template(agent_dir=self._agent_dir)

    def _grill_context(self) -> GrillContext:
        """The grill this sketch runs: made for this sketch's session and working on what it lists."""
        return self._inside(GrillContext)

    @Mcp
    @agent_tool
    def find_template(self, agent_dir: str = "") -> str:
        """Locate a sketch template using tiered discovery.
        1. Session context - the caller passes an example directly (skip this tool).
        2. Convention - {agent_dir}/templates/*-sketch.* inside the wrapped agent's templates folder.
        3. Default - sketch/templates/sketch-template.md (this toolset's canonical heading-and-indent notation).
        Returns the resolved template contents as a string."""
        templates_dir = Path(agent_dir) / "templates" if agent_dir else None
        found = sorted(templates_dir.glob("*-sketch.*")) if templates_dir is not None and templates_dir.is_dir() else []
        return (found[0] if found else _DEFAULT_TEMPLATE).read_text(encoding="utf-8")

    @Mcp
    @agent_tool
    def save_sketch(
        self,
        content: str = "",
        paths: list[str] | str | None = None,
        module: str = "",
    ) -> str:
        """Save the session's sketch as {session root}/.context/{session name}-sketch.md, replacing the one there, and
        return its path. One file holds every practice's section, so a session has one sketch.
        paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the sketch body in content.
        content: in-process text. Leave this empty on an MCP call.
        module: a module's folder under the session root, for a sketch of that module alone; it goes in that module's .context folder."""
        target = self._context_folder(module) / self._sketch_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(load_document(content, paths), encoding="utf-8")
        return str(target)

    @Mcp
    @agent_tool
    def list_sketches(self, module: str = "") -> str:
        """List the sketch files in the session root's .context folder, or in a module's under that root.
        Returns newline-separated paths, or ``no sketches`` when the folder is missing or empty.
        module: a module's folder under the session root."""
        context_dir = self._context_folder(module)
        if not context_dir.is_dir():
            return "no sketches"
        paths = [str(path) for path in sorted(context_dir.glob("*-sketch.md"))]
        if not paths:
            return "no sketches"
        return "\n".join(paths)

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
        """Confirm views only when the user did not already name them. Write a high-level shell in one integrated sketch file, one section per practice. The shell's level of detail is that fidelity's Scaffold section; the notation is the practice sketch template. Then ask which theme to start. Ask three or four questions from that fidelity's Sketch section, then sketch those answers into the existing sections. Practice Rules apply after those answers, not to the shell. The reply includes these sketch instructions, each practice's sketch template, and each practice's rules."""
        self.begin(guidance, action="sketch")
        "save_sketch the shell in the same turn it is written. After three or four grill answers, sketch the theme into that same file, save_sketch again, then review_sketch. Do not ask the next theme until that review confirms the sketch."
        "Carry forward every mistake named in review. Correct the sketch. Do not regenerate as if those mistakes never happened."
        for item in self.listed():
            instructions(item.rules.markdown_block)
            instructions(item.sketch_template)
        self._grill_context().grill_with_context()
        tools(self.find_template)
        tools(self.save_sketch)
        tools(self.review_sketch)
        self._grill_context().generate_each()
        return "Sketch complete; generate instructions applied."
