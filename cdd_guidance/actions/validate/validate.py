"""Validate and create_rule — run on each provided context tool."""

from __future__ import annotations

from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset
from harness.installation.destination import noDeploy
from harness.installation.files import skill
from harness.mcp.mcp_server import mcp
from harness.guidance import Rule
from harness.guidance.guidance import PracticeGuidance
from harness.guidance.practice_catalogue import PracticeCatalogue

from cdd_guidance.actions.validate.checked_graph import CheckedGraph, CheckedOutputs
from cdd_guidance.actions.validate.report_files import ReportFiles

_VALIDATE_MARKDOWN = Path(__file__).with_name("validate.md").read_text(encoding="utf-8")

# How many graph hits a validate line in the session log names; the report holds every one.
_LOGGED_VIOLATIONS = 40


@agent_toolset
class Validate(GuidanceAction):
    """Validate artifacts for provided context tools."""

    def __init__(self, session=None) -> None:
        super().__init__(session)
        # What this call checks, made by each validate; the cdd server makes a new action for each call.
        self._graph: CheckedGraph | None = None
        self._reports: ReportFiles | None = None

    @mcp
    @skill
    @agent_instructions
    def validate(
        self,
        guidance: GuidanceArg,
        rule: Rule | None = None,
        graph: bool | str | list[str] | None = None,
        paths: list[str] | None = None,
    ) -> str:
        """Check artifacts against rules.
        rule: one Rule to check. Omit it to walk each guidance's rules.
        graph: true for the saved graph of the session's folder (.context/graph.json, there only after graph.load_working_copy
        has run on that folder), or path(s) to graph_return_nodes JSON
        or a saved graph.json. When set, append a graph-rule report for each guidance's practice and still run AI validation.
        paths: the files or folders being edited, named from the project's root or absolute (e.g. src/my-paradise/order.ts).
        For graph-backed guidance, the session's graph is refreshed with exactly these files as they are now and its rules
        run on them; the saved graph is not read or rebuilt. A path that is not there, or not under the session's root, is refused.
        With no paths and no graph, the folders holding the fidelity's written output are checked."""
        self._work_on(guidance)
        sections: list[str] = [_VALIDATE_MARKDOWN]
        checked = self._checked_outputs()
        self._graph = CheckedGraph(self.session, checked, self._graph_practices())
        prefixes = self._graph.prefixes(paths, graph)
        self._reports = ReportFiles(self.session, self._fidelities())
        graph_paths = self._graph.paths(graph, prefixes, self._reports)
        if checked:
            sections.append(self._judging_instruction(checked, graph_paths))
        if graph_paths:
            sections.append(self._graph_and_ai_rule_report(graph_paths, prefixes))
        elif graph:
            sections.append(
                "No saved graph found. Run graph.load_working_copy on the session's folder, which saves "
                ".context/graph.json there, or pass graph as a path to graph_return_nodes JSON."
            )

        def on(item) -> str:
            if rule is not None:
                return rule.validate()
            if isinstance(item, str):
                return item
            if graph_paths:
                return ""
            return _rules_text(item)

        parts = [part for part in self.run(on, action="validate") if part]
        sections.extend(parts)
        report = "\n\n".join(sections)
        self._reports.save(report, graph_paths)
        return f"{report}\n\nValidation report for these artifacts: {self._reports.where()}"

    def listed_rules(self) -> str:
        """The shared rules and the active fidelity's rules of each listed guidance, as text for another action to
        follow. It checks nothing, so it saves no report and writes nothing to the session log, where a validate line
        would tell the session board the work had been checked."""
        return "\n\n".join(part for part in self.each(self._rules_text_of) if part)

    def _rules_text_of(self, item) -> str:
        return item if isinstance(item, str) else _rules_text(item)

    def _fidelities(self) -> list:
        """The fidelity each listed guidance is validated at. A listed practice is the one this action's session holds,
        so its fidelity's reports go to that session; an item with no current fidelity, or no practice a session works
        on, has none."""
        items = [item for item in self.listed() if not isinstance(item, str)]
        worked = [(item, self.fidelity_of(item)) for item in items]
        return [fidelity for item, fidelity in worked if fidelity is not None and self._session_practice(item) is not None]

    def _checked_outputs(self) -> CheckedOutputs:
        """Each listed guidance with the format this call checks and its fidelity outputs, by format. Validate checks
        one format, the guidance's own: the format the guidance names, else the one its fidelity last used, else the
        fidelity's default. It is read once, here, so the whole call checks that format. A fidelity's formats mirror
        each other, so checking every one reports each finding once per format."""
        return [(item, *self._checked_format_and_outputs(item)) for item in self.listed() if not isinstance(item, str)]

    def _checked_format_and_outputs(self, item) -> tuple[str, dict[str, list[str]]]:
        """The format this call checks item's fidelity in, and where that fidelity writes each format."""
        fidelity = self.fidelity_of(item)
        if fidelity is None or not isinstance(item, PracticeGuidance):
            return item.format, {}
        return fidelity.format, self._fidelity_outputs(fidelity)

    def _fidelity_outputs(self, fidelity) -> dict[str, list[str]]:
        """Where fidelity writes each format in this action's session."""
        return fidelity.output_paths()

    def _judging_instruction(self, checked: CheckedOutputs, graph_paths: list[Path]) -> str:
        """What the judge judges for each listed guidance: at a model or code fidelity with a graph, the graph validate
        built; otherwise the checked format's files."""
        graph_judged = [entry for entry in checked if graph_paths and self._judges_graph(entry[0])]
        file_judged = [entry for entry in checked if not (graph_paths and self._judges_graph(entry[0]))]
        sentences = []
        if graph_judged:
            sentences.append(
                f"Judge the graph validate built from the checked format's files ({self._judged_files(graph_judged)}), "
                f"saved at {', '.join(str(path) for path in graph_paths)}: its classes, operations, parameters, "
                "properties, relationships, and dependencies, against each rule. Read a file only to see what a node "
                "stands for; whether a model document matches the code is a separate, secondary check."
            )
        if file_judged:
            sentences.append(
                f"Judge only the checked format's files ({self._judged_files(file_judged)}). The other formats mirror "
                "them, so judging those too reports every finding twice."
            )
        return "\n\n".join(sentences)

    def _judged_files(self, checked: CheckedOutputs) -> str:
        return "; ".join(f"{format}: {', '.join(outputs.get(format, []))}" for _item, format, outputs in checked)

    def _judges_graph(self, item) -> bool:
        fidelity = self.fidelity_of(item)
        return fidelity is not None and fidelity.is_judged_on_graph

    def _listed_practices(self) -> list:
        """Each listed practice as this action's session holds it, which logs its own validate line; guidance that is no
        practice CDD has is left out."""
        found = [self._session_practice(item) for item in self.listed() if not isinstance(item, str)]
        return [practice for practice in found if practice is not None]

    def _graph_practices(self) -> list[str]:
        """The catalogue key of each listed practice, such as clean_engineering; none for other guidance."""
        practices = [item for item in self.listed() if isinstance(item, PracticeGuidance)]
        return [practice.key for practice in practices if PracticeCatalogue.has(practice.key)]

    def _graph_and_ai_rule_report(self, paths: list[Path], prefixes: list[str]) -> str:
        from cdd_guidance.actions.validate.validation_report import ValidationReport

        violations = self._graph.violations(paths, prefixes)
        self._log_graph_validation(violations)
        guidance = [item for item in self.listed() if not isinstance(item, str)]
        return ValidationReport(self.session).of_graph_and_ai_rules(
            violations,
            [rule for item in guidance for rule in item.checked_rules()],
            graph_sources=[str(path.resolve()) for path in paths],
            rule_bodies={rule.slug: rule.body or "" for item in guidance for rule in item.every_rule()},
        )

    def _log_graph_validation(self, violations: list) -> None:
        if self._guidance_text is not None or not violations:
            return
        synopsis = [
            f"graph-rule {violation.rule} {violation.location}:{violation.line or ''}"
            for violation in violations[:_LOGGED_VIOLATIONS]
        ]
        if len(violations) > _LOGGED_VIOLATIONS:
            synopsis.append(f"graph-rule … and {len(violations) - _LOGGED_VIOLATIONS} more")
        for practice in self._listed_practices():
            practice.log_validation(synopsis)
        # This line is the call's validate line; the session board reads the latest one, so no clean line may follow.
        self._logged_session_action = "validate"

    def _log_running_action(self, action: str) -> None:
        if action != "validate":
            super()._log_running_action(action)
            return
        if self._logged_session_action == action:
            return
        self._logged_session_action = action
        self._log_validation_to_session()

    def _log_validation_to_session(self) -> None:
        if self._guidance_text is not None:
            return
        for practice in self._listed_practices():
            practice.log_validation([])

    @noDeploy
    @mcp
    @skill
    @agent_instructions
    def create_rule(self, guidance: GuidanceArg, failed: str = "", wanted: str = "") -> str:
        """Add a named rule to each listed guidance from a failed example and the wanted behavior. Then validate the asset with that rule so the same mistake is detected.
        failed: path to the example that broke. Pass the file. Do not paste its body.
        wanted: path to the behavior the rule must require. Pass the file. Do not paste its body."""
        self._work_on(guidance)

        def on(item) -> None:
            if isinstance(item, str):
                return
            item.examples
            item.templates

        self.run(on, action="create_rule")
        return (
            "Write a new named rule into this tool. "
            "Then run collection validate on the asset and detect a failure "
            "that matches the Mistake."
        )


def _rules_text(guidance) -> str:
    """The rules a validate of guidance checks, as their markdown, for an agent to judge against."""
    texts = (collection.validate.strip() for collection in guidance.checked_rule_collections())
    return "\n\n".join(text for text in texts if text)
