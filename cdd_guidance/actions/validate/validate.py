"""Validate and create_rule — run on each provided context tool."""

from __future__ import annotations

from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset
from harness.installation.destination import noDeploy
from harness.installation.files import skill
from harness.mcp.mcp_server import mcp
from harness.guidance.rule import Rule

from cdd_guidance.actions.validate.checked_graph import CheckedGraph
from cdd_guidance.actions.validate.report_files import ReportFiles

_VALIDATE_MARKDOWN = Path(__file__).with_name("validate.md").read_text(encoding="utf-8")

# How many graph hits a validate line in the session log names; the report holds every one.
_LOGGED_VIOLATIONS = 40


@agent_toolset
class Validate(GuidanceAction):
    """Validate artifacts for provided context tools."""

    def __init__(self, session=None, call=None) -> None:
        super().__init__(session, call)
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
        fidelities = self._fidelities()
        self._graph = CheckedGraph(self.session, fidelities, paths, graph, self.call)
        self._reports = ReportFiles(self.session, fidelities)
        graph_paths = self._graph.check_beside(self._reports)
        if fidelities:
            sections.append(self._judging_instruction())
        if graph_paths:
            sections.append(self._graph_and_ai_rule_report())
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
            return item.checked_rules_text()

        parts = [part for part in self.run(on, action="validate") if part]
        sections.extend(parts)
        report = "\n\n".join(sections)
        self._reports.save(report, self._graph)
        return f"{report}\n\nValidation report for these artifacts: {self._reports.where()}"

    def _fidelities(self) -> list:
        """The fidelity each listed guidance is validated at. A listed practice is the one this action's session holds,
        so its fidelity's reports go to that session; an item with no current fidelity, or no practice a session works
        on, has none."""
        items = [item for item in self.listed() if not isinstance(item, str)]
        worked = [(item, self.fidelity_of(item)) for item in items]
        return [fidelity for item, fidelity in worked if fidelity is not None and self._session_practice(item) is not None]

    def _judging_instruction(self) -> str:
        """What the judge judges for each listed guidance: at a model or code fidelity with a graph, the graph validate
        built; otherwise the checked format's files. Validate checks one format of each fidelity, the one the guidance
        names, else the one its fidelity last used, else the fidelity's default: the formats mirror each other, so
        checking every one reports each finding once per format."""
        graph_judged = self._graph.judged_files(on_graph=True)
        file_judged = self._graph.judged_files(on_graph=False)
        sentences = []
        if graph_judged:
            sentences.append(
                f"Judge the graph validate built from the checked format's files ({graph_judged}), "
                f"saved at {', '.join(str(path) for path in self._graph.files)}: its classes, operations, parameters, "
                "properties, relationships, and dependencies, against each rule. Read a file only to see what a node "
                "stands for; whether a model document matches the code is a separate, secondary check."
            )
        if file_judged:
            sentences.append(
                f"Judge only the checked format's files ({file_judged}). The other formats mirror "
                "them, so judging those too reports every finding twice."
            )
        return "\n\n".join(sentences)

    def _graph_and_ai_rule_report(self) -> str:
        from cdd_guidance.actions.validate.validation_report import ValidationReport

        violations = self._graph.violations()
        self._log_graph_validation(violations)
        guidance = [self.at_fidelity(item) for item in self.listed() if not isinstance(item, str)]
        sources =[str(path.resolve()) for path in self._graph.files]
        return ValidationReport(self.session, guidance).of_graph(violations, sources)

    def _log_graph_validation(self, violations: list) -> None:
        if self._guidance_text is not None or not violations:
            return
        synopsis = [
            f"graph-rule {violation.rule} {violation.location}:{violation.line or ''}"
            for violation in violations[:_LOGGED_VIOLATIONS]
        ]
        if len(violations) > _LOGGED_VIOLATIONS:
            synopsis.append(f"graph-rule … and {len(violations) - _LOGGED_VIOLATIONS} more")
        for worked in self._worked_fidelities():
            self.log.validation(worked, synopsis)
        # This line is the call's validate line; the session board reads the latest one, so no clean line may follow.
        self._logged_session_action = "validate"

    def _log(self, action: str) -> None:
        """A validate line names each listed practice, which logs its own; any other action logs as every action does."""
        if action != "validate":
            super()._log(action)
            return
        self._log_validation_to_session()

    def _log_validation_to_session(self) -> None:
        if self._guidance_text is not None:
            return
        for worked in self._worked_fidelities():
            self.log.validation(worked, [])

    @noDeploy
    @mcp
    @skill
    @agent_instructions
    def create_rule(self, guidance: GuidanceArg, failed: str = "", wanted: str = "") -> str:
        """Add a named rule to each listed guidance from a failed example and the wanted behavior. Then validate the asset with that rule so the same mistake is detected.
        failed: path to the example that broke. Pass the file. Do not paste its body.
        wanted: path to the behavior the rule must require. Pass the file. Do not paste its body."""
        self._work_on(guidance)

        def on(item) -> str:
            if isinstance(item, str):
                return ""
            return "\n\n".join(part.strip() for part in (str(item.examples or ""), item.templates or "") if part.strip())

        self.run(on, action="create_rule")
        return (
            "Write a new named rule into this tool. "
            "Then run collection validate on the asset and detect a failure "
            "that matches the Mistake."
        )
