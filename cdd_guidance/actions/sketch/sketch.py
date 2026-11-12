"""Sketch a solution interactively before generating the formal artifact.

Sketch is a standalone action. Any agent or human can call its tools and its sketch instructions directly.
"""
from __future__ import annotations

from pathlib import Path

from cdd_guidance.actions.generate.generate import Generate
from cdd_guidance.actions.grill_context.grill_context import GrillContext
from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset, instructions, tools
from harness.agent_tools.agent_tools import agent_tool
from harness.installation.files import skill
from harness.mcp.mcp_annotations import mcp

_DEFAULT_TEMPLATE = Path(__file__).parent / "templates" / "sketch-template.md"

@agent_toolset
class Sketch(GuidanceAction):
    """Sketch a solution interactively before generating the formal artifact."""

    def __init__(self, agent_dir: str = "", session=None, call=None) -> None:
        super().__init__(session, call)
        self._agent_dir = agent_dir

    def made_for(self, session, call=None) -> Sketch:
        """A sketch made for session and call, which finds its template in this sketch's agent_dir."""
        return type(self)(agent_dir=self._agent_dir, session=session, call=call)

    @property
    def _sketch_name(self) -> str:
        """The session's sketch file name: a session is named for the subject it works on, so its sketch is too."""
        return f"{self.session.name or 'main'}-sketch.md"

    @property
    def sketch_template(self) -> str:
        """The sketch template for this instance's agent_dir (tiered discovery)."""
        return self.find_template()

    def _grill_context(self) -> GrillContext:
        """The grill this sketch runs: made for this sketch's session and working on what it lists."""
        return self._inside(GrillContext)

    def _generate(self) -> Generate:
        """The generate the agreed sketch becomes the formal artifact through, working on what this sketch lists."""
        return self._inside(Generate)

    def _sketch_text(self, item) -> str:
        """What sketching one listed guidance asks for, read from the fidelity this sketch works at on it: its Scaffold
        section, which is the shell's level of detail, and its practice's sketch template, which is the notation; text
        guidance is itself. The rules the sketch answers are held to arrive once, with the generate the sketch ends with.
        The recipe reads the text returned."""
        if isinstance(item, str):
            return item
        parts = (item.scaffold, item.sketch_template)
        return "\n\n".join(part.strip() for part in parts if part and part.strip())

    @mcp
    @agent_tool
    def find_template(self, agent_dir: str = "") -> str:
        """Locate a sketch template using tiered discovery.
        1. Session context - the caller passes an example directly (skip this tool).
        2. Convention - {agent_dir}/templates/*-sketch.* inside the wrapped agent's templates folder.
        3. Default - sketch/templates/sketch-template.md (this toolset's canonical heading-and-indent notation).
        Returns the resolved template contents as a string.
        agent_dir: the wrapped agent's folder, from the project's root or absolute. Omit it for the folder this sketch was made with."""
        agent_dir = agent_dir or self._agent_dir
        templates_dir = self.path_named(agent_dir) / "templates" if agent_dir else None
        found = sorted(templates_dir.glob("*-sketch.*")) if templates_dir is not None and templates_dir.is_dir() else []
        return (found[0] if found else _DEFAULT_TEMPLATE).read_text(encoding="utf-8")

    @mcp
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
        target = self.session.context_folder(module) / self._sketch_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.document_named(content, paths), encoding="utf-8")
        self.wrote([target])
        return str(target)

    @mcp
    @agent_tool
    def list_sketches(self, module: str = "") -> str:
        """List the sketch files in the session root's .context folder, or in a module's under that root.
        Returns newline-separated paths, or ``no sketches`` when the folder is missing or empty.
        module: a module's folder under the session root."""
        context_dir = self.session.context_folder(module)
        if not context_dir.is_dir():
            return "no sketches"
        paths = [str(path) for path in sorted(context_dir.glob("*-sketch.md"))]
        if not paths:
            return "no sketches"
        return "\n".join(paths)

    @mcp
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

    @mcp
    @skill
    @agent_instructions
    def sketch(self, guidance: GuidanceArg) -> str:
        """Confirm views only when the user did not already name them. Write a high-level shell in one integrated sketch file, one section per practice. The shell's level of detail is that fidelity's Scaffold section; the notation is the practice sketch template. Then ask which theme to start. Ask three or four questions from that fidelity's Sketch section, then sketch those answers into the existing sections. Practice Rules apply after those answers, not to the shell. The reply includes these sketch instructions, each practice's sketch template, and each practice's rules."""
        self._work_on(guidance)
        "save_sketch the shell in the same turn it is written. After three or four grill answers, sketch the theme into that same file, save_sketch again, then review_sketch. Do not ask the next theme until that review confirms the sketch."
        "Carry forward every mistake named in review. Correct the sketch. Do not regenerate as if those mistakes never happened."
        "Evaluate the sketch against each listed guidance's rules, which the generate instructions below give, as an AI check — not a graph query."
        self.each(self._sketch_text)
        instructions(self._grill_context().grill_with_context)
        tools(self.find_template)
        tools(self.save_sketch)
        tools(self.review_sketch)
        "When the sketch is agreed, generate each listed guidance from it:"
        instructions(self._generate().generate)
        return "Sketch complete; generate instructions applied."
