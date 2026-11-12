"""Validate and create_rule — run on each provided context tool."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.guidance.guidance import Guidance
from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset
from harness.agent_tools.tool_call import ToolCall
from harness.installation.destination import noDeploy
from harness.installation.files import skill
from harness.mcp.mcp_server import mcp
from harness.guidance.rule import Rule

from cdd_guidance.actions.validate.checked_graph import CheckedGraph, NamedToCheck
from cdd_guidance.actions.validate.report_files import ReportFiles

if TYPE_CHECKING:
    from space.session.session import Session

_VALIDATE_MARKDOWN = Path(__file__).with_name("validate.md").read_text(encoding="utf-8")

# How many graph hits a validate line in the session log names; the report holds every one.
_LOGGED_VIOLATIONS = 40


@agent_toolset
class Validate(GuidanceAction):
    """Validate artifacts for provided context tools."""

    def __init__(self, session: Session | None = None, call: ToolCall | None = None) -> None:
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
        self._check(NamedToCheck(paths, graph, self.call))
        report = self._report(rule, graph_named=bool(graph))
        self._reports.save(report, self._graph)
        return f"{report}\n\nValidation report for these artifacts: {self._reports.where()}"

    def _check(self, to_check: NamedToCheck) -> None:
        """Claim this call's report files and build, or read, the graph it checks beside them."""
        fidelities = self._fidelities()
        self._graph = CheckedGraph(self.session, fidelities, to_check)
        self._reports = ReportFiles(self.session, fidelities)
        self._graph.check_beside(self._reports)

    def _report(self, rule: Rule | None, graph_named: bool) -> str:
        """The report: how to validate, what the judge judges, the graph's violations, each listed guidance's rules
        (or the one rule named), and the overlaid patterns' rules."""
        sections = [
            _VALIDATE_MARKDOWN,
            self._judging_instruction(),
            self._graph_section(graph_named),
            *self.run(lambda worked: self._rules_text(worked, rule), action="validate"),
            self._overlay_section(),
        ]
        return "\n\n".join(section for section in sections if section)

    def _graph_section(self, graph_named: bool) -> str:
        """The graph rules' report when this call checks a graph; when it named one and none was found, how to make one."""
        if self._graph.files:
            return self._graph_and_ai_rule_report()
        if not graph_named:
            return ""
        return (
            "No saved graph found. Run graph.load_working_copy on the session's folder, which saves "
            ".context/graph.json there, or pass graph as a path to graph_return_nodes JSON."
        )

    def _rules_text(self, worked: Guidance | str, rule: Rule | None) -> str:
        """What the judge checks worked against: the one rule named, the text itself, or the fidelity's rules; none
        when the graph's report already gives them."""
        if rule is not None:
            return rule.validate()
        if isinstance(worked, str):
            return worked
        if self._graph.files:
            return ""
        return worked.checked_rules_text()

    def _overlay_section(self) -> str:
        """The rules of the patterns the checked content was generated with; none when it names none."""
        overlay_rules = self._overlay_rules(self._graph.edited or self._graph.prefixes)
        if not overlay_rules:
            return ""
        return f"Judge the work against these overlaid patterns' rules too, as you judge the practices' rules.\n\n{overlay_rules}"

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
        sentences = [
            self._graph_judging(self._graph.judged_files(on_graph=True)),
            self._files_judging(self._graph.judged_files(on_graph=False)),
        ]
        return "\n\n".join(sentence for sentence in sentences if sentence)

    def _graph_judging(self, judged: str) -> str:
        """How to judge the fidelities judged on the graph, whose checked files are judged; none when there are none."""
        if not judged:
            return ""
        return (
            f"Judge the graph validate built from the checked format's files ({judged}), "
            f"saved at {', '.join(str(path) for path in self._graph.files)}: its classes, operations, parameters, "
            "properties, relationships, and dependencies, against each rule. Read a file only to see what a node "
            "stands for; whether a model document matches the code is a separate, secondary check."
        )

    def _files_judging(self, judged: str) -> str:
        """How to judge the fidelities judged on their files, the judged ones; none when there are none."""
        if not judged:
            return ""
        return (
            f"Judge only the checked format's files ({judged}). The other formats mirror "
            "them, so judging those too reports every finding twice."
        )

    def _graph_and_ai_rule_report(self) -> str:
        from cdd_guidance.actions.validate.validation_report import ValidationReport

        violations = self._graph.violations()
        self._log_graph_validation(violations)
        guidance = [self.at_fidelity(item) for item in self.listed() if not isinstance(item, str)]
        sources =[str(path.resolve()) for path in self._graph.files]
        return ValidationReport(self.session, guidance).of_graph(violations, sources, self._graph.held_beside)

    def _log_graph_validation(self, violations: list) -> None:
        if self.work.text is not None or not violations:
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
        if self.work.text is not None:
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
