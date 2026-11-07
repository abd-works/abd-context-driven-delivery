"""Generate — run generate on each provided context tool."""

from __future__ import annotations

from harness.guidance.guidance import PracticeGuidance
from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset, instructions, tools
from harness.installation.files import skill
from harness.markdown.format import Format
from harness.mcp.mcp_server import mcp
from cdd_guidance.actions.validate.validate import Validate

@agent_toolset
class Generate(GuidanceAction):
    """Generate artifacts for provided context tools."""

    @mcp
    @skill
    @agent_instructions
    def generate(self, guidance: GuidanceArg) -> str:
        """Write artifacts for each listed guidance at its current fidelity. The shared rules and that fidelity's rules are part of these instructions. After the artifact is written, call validate with the same guidance and paths set to the files you wrote."""
        self._work_on(guidance)
        rules = self._rules()
        instructions(rules)
        tools(self._render().render)
        earlier = self._earlier_renders()
        instructions(earlier)
        self.run(self._generate_item, action="generate")
        places = self._where_outputs_go()
        instructions(places)
        "After the artifact is written, call validate with this same guidance and paths set to the files you wrote: validate refreshes the session's graph with exactly those files, so the graph rules run on them as they are now."
        tools(self._validate().validate)
        return ""

    def _rules(self) -> str:
        """Shared rules and the active fidelity's rules, inlined into generate. Read without running Validate, because
        nothing has been written yet to check."""
        return self._inside(Validate).listed_rules()

    def _validate(self) -> Validate:
        """Validate as a tool, so its rules are injected again when it is called."""
        action = self._inside(Validate)
        action.mode = "tool"
        return action

    def _render(self):
        """Render action, available while generating code from another format."""
        from cdd_guidance.actions.render.render import Render

        return self._inside(Render)

    def _earlier_renders(self) -> str:
        """What to render before generating: a listed fidelity reads the fidelity before it, so when that earlier
        fidelity declares the format this one is generated in and has no file in it yet, but has a file in another
        format, it is rendered into this format first, from a format it has a file in."""
        renders = [self._earlier_render(item) for item in self.listed() if isinstance(item, PracticeGuidance)]
        return "\n\n".join(render for render in renders if render)

    def _earlier_render(self, practice: PracticeGuidance) -> str:
        current = self.fidelity_of(practice)
        wanted = Format(current.format if current is not None else practice.format).name
        earlier = self._fidelity_before(practice, current) if current is not None else None
        if earlier is None or not wanted or wanted not in {Format(label).name for label in earlier.outputs}:
            return ""
        made = {Format(label).name: paths for label, paths in self._existing_files(earlier).items() if paths}
        if not made or wanted in made:
            return ""
        source = sorted(made)[0]
        return (
            f"Before generating {current.slug}, render the earlier fidelity {earlier.slug} into {wanted}, because it has "
            f"no {wanted} file to read yet: call render with guidance {earlier.slug}, format {wanted}, source {source}, "
            f"and paths {', '.join(made[source])}. Then follow place_rendered, so {earlier.slug} has its {wanted} file."
        )

    def _fidelity_before(self, practice: PracticeGuidance, current):
        """The practice's fidelity in the stage before current's; none for its first fidelity."""
        fidelities = list(practice.fidelities.entries.values())
        position = next((index for index, fidelity in enumerate(fidelities) if fidelity is current), 0)
        return fidelities[position - 1] if position > 0 else None

    def _existing_files(self, fidelity) -> dict[str, list[str]]:
        """The files fidelity has in this session, by the format it declares them in, each a path from the project."""
        return {label: [entry.path for entry in entries if entry.exists] for label, entries in fidelity.files().items()}

    def _generate_item(self, item) -> None:
        if isinstance(item, str):
            instructions(item)
            self.generate_output()
        else:
            item.instructions
            item.generate_output()
        self.generate_fixes_from_validate()
        self.add_generate_header_to_generated()

    def _where_outputs_go(self) -> str:
        worked = [self.fidelity_of(item) for item in self.listed() if isinstance(item, PracticeGuidance)]
        outputs = [fidelity.output_paths() for fidelity in worked if fidelity is not None]
        places = [f"{label}: {', '.join(paths)}" for listed in outputs for label, paths in listed.items()]
        if not places:
            return ""
        return f"Save each format you write at its path, filling any {{name}} from the work: {'; '.join(places)}"

    @agent_instructions
    def add_generate_header_to_generated(self) -> str:
        """Prepend the following block verbatim as the very first lines of the file you are writing - before any imports, before any code."""
        return (
            '"""\n'
            '"""\n'
        )

    @agent_instructions
    def generate_output(self) -> str:
        """Write this context tool's artifact for the current fidelity. Override on the practice; the default writes nothing."""
        return ""

    @agent_instructions
    def generate_fixes_from_validate(self) -> str:
        """Apply fixes implied by the latest validate report before considering generate done, in every format of the fidelity: its documents, its diagrams, and its code, so they still mirror each other. Override on the practice when generate must close those gaps in the same pass."""
        return ""
