"""Validate and create_rule — run on each listed guidance."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.guidance.guidance import Guidance
from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.guidance.stages import CHECKS, STEP, on_stage
from harness.agent_tools import agent_instructions, agent_toolset
from harness.agent_tools.tool_call import ToolCall
from harness.annotations.annotation import noDeploy
from harness.installation.files import skill
from harness.mcp.mcp_annotations import mcp
from harness.guidance.rule import Rule

from cdd_guidance.actions.validate.checked_graph import CheckedGraph, NamedToCheck
from cdd_guidance.actions.validate.report_files import ReportFiles
from cdd_guidance.actions.validate.validation_report import ValidationReport

if TYPE_CHECKING:
    from space.session.session import Session

_VALIDATE_MARKDOWN = Path(__file__).with_name("validate.md").read_text(encoding="utf-8")

# How many graph hits a validate line in the session log names; the report holds every one.
_LOGGED_VIOLATIONS = 40


class UnknownRule(ValueError):
    """A validate call named a rule none of its listed guidance checks. The message lists the rules there are."""

    def __init__(self, rule: str, rules: list[str]) -> None:
        super().__init__(f"no rule {rule!r} among the rules the listed guidance checks; the rules are {', '.join(rules)}")
        self.rule = rule
        self.rules = tuple(rules)


@agent_toolset
class Validate(GuidanceAction):
    """Validate artifacts for the listed guidance."""

    def __init__(self, session: Session | None = None, call: ToolCall | None = None) -> None:
        super().__init__(session, call)
        # What this call checks, made by each validate; the cdd server makes a new action for each call.
        self._graph: CheckedGraph | None = None
        self._reports: ReportFiles | None = None
        self._report_of: ValidationReport | None = None
        # The one rule this call names, read once from the listed guidance; none when it walks every rule.
        self._rule: Rule | None = None

    @on_stage(2, STEP, CHECKS)
    @mcp
    @skill
    @agent_instructions
    def validate(
        self,
        guidance: GuidanceArg,
        rule: str | None = None,
        graph: bool | str | list[str] | None = None,
        paths: list[str] | None = None,
    ) -> str:
        """Check artifacts against rules.
        rule: the name of one rule to check, such as verb-noun-format. A name none of the listed guidance checks is refused. Omit it to walk each guidance's rules.
        graph: true for the session's graph (graph.json in the session's own folder, created for the session and loaded
        when it is missing), or path(s) to graph_return_nodes JSON
        or a saved graph.json. When set, append a graph-rule report for each guidance's practice and still run AI validation.
        paths: the files or folders being edited, named from the project's root or absolute (e.g. src/my-paradise/order.ts).
        For graph-backed guidance, the session's graph is refreshed with exactly these files as they are now and its rules
        run on them; the saved graph is not read or rebuilt. A path that is not there, or not under the session's root, is refused.
        With no paths and no graph, the folders holding the fidelity's written output are checked."""
        self._work_on(guidance)
        self._rule = self._rule_named(rule)
        self._check(NamedToCheck(paths, graph, self.call))
        report = self._report(graph_named=bool(graph))
        return self._saved(report)

    def _rule_named(self, name: str | None) -> Rule | None:
        """The rule name names among the rules the listed guidance checks, each at the fidelity this call works at; none
        when the call names none. A name none of them has raises *UnknownRule*, before anything is checked or saved."""
        if not name:
            return None
        guidance = [self.work.at_fidelity(item) for item in self.listed() if isinstance(item, Guidance)]
        rules = [rule for worked in guidance for rule in worked.checked_rules()]
        found = next((rule for rule in rules if rule.slug == name), None)
        if found is None:
            raise UnknownRule(name, list(dict.fromkeys(rule.slug for rule in rules)))
        return found

    def _saved(self, report: str) -> str:
        """Save the report into this call's report files, with the violations of the graph it checked beside them, and
        answer the call with report, the report as the judge reads it, and where it was saved. The saved report points
        at each rule's text instead of copying it, and leaves out how to judge, which the judge has here."""
        self._reports.save(self._report_of.for_saving(), self._graph)
        return f"{report}\n\nValidation report for these artifacts: {self._reports.where()}"

    def _check(self, to_check: NamedToCheck) -> None:
        """Claim this call's report files and build, or read, the graph it checks beside them."""
        fidelities = self._fidelities()
        self._graph = CheckedGraph(self.session, fidelities, to_check)
        self._reports = ReportFiles(self.session, fidelities)
        self._graph.check_beside(self._reports)
        guidance = [self.work.at_fidelity(item) for item in self.listed() if not isinstance(item, str)]
        self._report_of = ValidationReport(guidance, self._graph, self._rule)

    def _report(self, graph_named: bool) -> str:
        """The report: how to validate, what the judge judges, the graph's violations, each listed guidance's rules
        (or the one rule named), and the overlaid patterns' rules."""
        sections = [
            _VALIDATE_MARKDOWN,
            self._judging_instruction(),
            self._graph_section(graph_named),
            *self.run(self._rules_text, action="validate"),
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
            "graph.json in the session's folder, or pass graph as a path to graph_return_nodes JSON."
        )

    def _rules_text(self, worked: Guidance | str) -> str:
        """What the judge checks worked against: the text itself, the one rule named, or the fidelity's rules; none
        when the graph's report already gives them."""
        if isinstance(worked, str):
            return worked
        if self._graph.files:
            return ""
        if self._rule is not None:
            return self._rule.validate() if self._rule in worked.checked_rules() else ""
        return worked.checked_rules_text()

    def _overlay_section(self) -> str:
        """The rules of the patterns the checked content was generated with; none when it names none."""
        overlay_rules = self.brief.overlay_rules(self._graph.edited or self._graph.prefixes)
        if not overlay_rules:
            return ""
        return f"Judge the work against these overlaid patterns' rules too, as you judge the practices' rules.\n\n{overlay_rules}"

    def _fidelities(self) -> list[FidelityGuidance]:
        """The fidelity each listed guidance is validated at. A listed practice is the one this action's session holds,
        so its fidelity's reports go to that session; an item with no current fidelity, or no practice a session works
        on, has none."""
        items = [item for item in self.listed() if not isinstance(item, str)]
        worked = [(item, self.work.fidelity_of(item)) for item in items]
        return [fidelity for item, fidelity in worked if fidelity is not None and self.session_practice(item) is not None]

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
        self._log_graph_validation(self._graph.violations())
        return self._report_of.for_judge()

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
