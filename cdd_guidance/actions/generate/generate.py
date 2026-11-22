"""Generate — run generate on each listed guidance."""

from __future__ import annotations

import re
from pathlib import Path

from harness.guidance.guidance import FidelityGuidance, Guidance, PracticeGuidance
from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.guidance.action_catalogue import STEP, TAKES_FORMATS, on_stage
from harness.agent_tools import agent_instructions, agent_toolset, instructions, tools
from harness.installation.files import skill
from harness.markdown.format import Format
from harness.mcp.mcp_annotations import mcp
from cdd_guidance.actions.render.render import Render
from cdd_guidance.actions.render.rendered_file import WHITEBOARD
from cdd_guidance.actions.validate.validate import Validate

# A path that names no one folder: a template to fill, or a wildcard.
_NOT_ONE_FOLDER = re.compile(r"[{*?]")


@agent_toolset
class Generate(GuidanceAction):
    """Generate artifacts for the listed guidance."""

    @on_stage(1, STEP, TAKES_FORMATS)
    @mcp
    @skill
    @agent_instructions
    def generate(self, guidance: GuidanceArg) -> str:
        """Write artifacts for each listed guidance at its current fidelity. The shared rules and that fidelity's rules are part of these instructions. After the artifact is written, call validate with the same guidance and paths set to the files you wrote."""
        self._work_on(guidance)
        process = self._process_first()
        instructions(process)
        rules = self.work.rules_to_follow
        instructions(rules)
        overlay_rules = self.brief.overlay_rules()
        instructions(overlay_rules)
        tools(self._render().render)
        earlier = self._earlier_renders()
        instructions(earlier)
        self.run(self._generate_item, action="generate")
        places = self._where_outputs_go()
        instructions(places)
        if self._writes_whiteboard():
            tools(self._render().publish_board)
            tools(self._render().record_board)
        patterns = self.graph.applied_patterns.record_content(self._output_folders()) if self._session is not None else ""
        instructions(patterns)
        "After the artifact is written, call validate with this same guidance and paths set to the files you wrote: validate refreshes the session's graph with exactly those files, so the graph rules run on them as they are now."
        tools(self._validate().validate)
        return ""

    def _process_first(self) -> str:
        """The order of work the listed fidelities' supplements give, each once, ahead of every rule: a long reply is read
        from the top, and the process says what to do first."""
        processes = dict.fromkeys(fidelity.process for fidelity in self._listed_fidelities if fidelity.process)
        return "\n\n".join(processes)

    @property
    def _listed_fidelities(self) -> list[FidelityGuidance]:
        """The fidelity this generate works at on each listed practice; a practice with none is left out."""
        worked = [self.work.fidelity_of(item) for item in self.listed() if isinstance(item, PracticeGuidance)]
        return [fidelity for fidelity in worked if fidelity is not None]

    def _validate(self) -> Validate:
        """Validate as a tool, so its rules are injected again when it is called."""
        return self._tool_inside(Validate)

    def _render(self) -> Render:
        """Render action, available while generating code from another format."""
        return self._inside(Render)

    def _earlier_renders(self) -> str:
        """What to render before generating: a listed fidelity reads the fidelity before it, so when that earlier
        fidelity declares the format this one is generated in and has no file in it yet, but has a file in another
        format, it is rendered into this format first, from a format it has a file in."""
        renders = [self._earlier_render(item) for item in self.listed() if isinstance(item, PracticeGuidance)]
        return "\n\n".join(render for render in renders if render)

    def _earlier_render(self, practice: PracticeGuidance) -> str:
        current = self.work.fidelity_of(practice)
        wanted = (current.format if current is not None else practice.format).name
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

    def _fidelity_before(self, practice: PracticeGuidance, current: FidelityGuidance) -> FidelityGuidance | None:
        """The practice's fidelity in the stage before current's; none for its first fidelity."""
        fidelities = list(practice.fidelities.entries.values())
        position = next((index for index, fidelity in enumerate(fidelities) if fidelity is current), 0)
        return fidelities[position - 1] if position > 0 else None

    def _existing_files(self, fidelity: FidelityGuidance) -> dict[str, list[str]]:
        """The files fidelity has in this session, by the format it declares them in, each a path from the project."""
        return {label: [entry.path for entry in entries if entry.exists] for label, entries in fidelity.session_output.written.files().items()}


    def _generate_item(self, worked: Guidance | str) -> str:
        """What generating one listed guidance asks for: the text itself, or the instructions of the fidelity this
        generate works at (worked) and what its practice says about writing the artifact. The recipe reads the text
        returned."""
        if isinstance(worked, str):
            return worked
        # The supplements' process opens the reply once, so each fidelity gives only its own words here.
        text = worked.own_instructions if isinstance(worked, FidelityGuidance) else worked.instructions
        return "\n\n".join(part.strip() for part in (text, worked.generate_output()) if part and part.strip())

    def _where_outputs_go(self) -> str:
        outputs = [fidelity.session_output.written.output_paths() for fidelity in self._listed_fidelities]
        places = [f"{label}: {', '.join(paths)}" for listed in outputs for label, paths in listed.items()]
        if not places:
            return ""
        return f"Save each format you write at its path, filling any {{name}} from the work: {'; '.join(places)}"

    def _output_folders(self) -> list[Path]:
        """The folder of each file a listed fidelity writes, once each; the pattern overlays record their patterns at
        the root of each. A templated path's folder, or one a wildcard names, such as harness/**/.context, is no one
        folder, so it is left to the agent."""
        paths = [path for fidelity in self._listed_fidelities for listed in fidelity.session_output.written.output_paths().values() for path in listed]
        return list(dict.fromkeys(self.session.paths.path_named(path).parent for path in paths if not _NOT_ONE_FOLDER.search(path)))

    def _writes_whiteboard(self) -> bool:
        """Whether a listed fidelity writes a whiteboard, which goes on its board in Claude once written."""
        return any(Format(label).name == WHITEBOARD for fidelity in self._listed_fidelities for label in fidelity.session_output.written.output_paths())

    @agent_instructions
    def generate_fixes_from_validate(self) -> str:
        """The fixes step that follows a validate, which an action such as Satisfy names after asking for validate."""
        "Apply the fixes the latest validate report names before considering generate done, in every format of the fidelity: its documents, its diagrams, and its code, so they still mirror each other."
        return ""
