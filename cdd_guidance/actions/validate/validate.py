"""Validate and CreateRule — run on each provided context tool."""

from __future__ import annotations

import tempfile
from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset
from harness.installation.destination import noDeploy
from harness.installation.files import Skill
from harness.mcp.mcp_server import Mcp
from harness.guidance import Rule
from harness.guidance.guidance import PracticeGuidance
from harness.guidance.practice_catalogue import PracticeCatalogue

_VALIDATE_MARKDOWN = Path(__file__).with_name("validate.md").read_text(encoding="utf-8")

# At these fidelities the rules are about the object model the code holds: one object model, classes with one job,
# state held on the object, typed relationships, one-way dependencies. Validate builds that model as a graph, so the
# judge checks the graph; whether a model document matches the code is a separate check.
_GRAPH_JUDGED_FIDELITIES = frozenset({"model", "code"})


class PathsNotFoundError(FileNotFoundError):
    """Raised when validate is named a path that is not there, or not under the session's root, where the graph reads."""

    def __init__(self, unreadable: list[str], project: Path, session_root: Path) -> None:
        named = "; ".join(f"{path}, read from {project}" for path in unreadable)
        super().__init__(f"validate found no file under the session's root {session_root} at {named}. Name paths from the project's root, or absolute.")


@agent_toolset
class Validate(GuidanceAction):
    """Validate artifacts for provided context tools."""

    # One action serves every MCP call at once, so what a call works on is kept per call, the way the base keeps the
    # guidance it bound.
    @property
    def _unchecked_files(self) -> set[str]:
        """The declared files of the formats this call does not check; their graph hits are left out of its report."""
        return getattr(self._running, "unchecked_files", set())

    @_unchecked_files.setter
    def _unchecked_files(self, files: set[str]) -> None:
        self._running.unchecked_files = files

    @property
    def _reports(self) -> list[Path]:
        """The report files this call claimed, one for each listed guidance's fidelity."""
        return getattr(self._running, "reports", [])

    @_reports.setter
    def _reports(self, reports: list[Path]) -> None:
        self._running.reports = reports

    @Mcp
    @Skill
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
        graph: true for the workspace's saved graph (.context/graph.json), or path(s) to graph_return_nodes JSON
        or a saved graph.json. When set, append a graph-rule report for each guidance's practice and still run AI validation.
        paths: the files or folders being edited, named from the project's root or absolute (e.g. src/my-paradise/order.ts).
        For graph-backed guidance, the graph is built from just these files as they are now and its rules run on them;
        the saved graph is not read or rebuilt. A path that is not there, or not under the session's root, is refused.
        With no paths and no graph, the folders holding the fidelity's written output are checked."""
        self._bind_guidance(guidance)
        sections: list[str] = [_VALIDATE_MARKDOWN]
        checked = self._checked_outputs()
        self._unchecked_files = self._other_format_files(checked)
        named = [path for path in self._workspace_relative(paths) if path not in self._unchecked_files]
        prefixes = named or self._workspace_relative(self._written_outputs(checked) if graph is None else [])
        self._reports = self._new_reports()
        graph_paths = self._resolve_graph_json_paths(graph, prefixes)
        if checked:
            sections.append(self._judging_instruction(checked, graph_paths))
        if graph_paths:
            sections.append(
                self._graph_and_ai_rule_report(graph_paths, path_prefixes=prefixes)
            )
        elif graph:
            sections.append(
                "No graph JSON file found. Load the graph (graph_load_working_copy) so the workspace has "
                ".context/graph.json, or pass graph as a path to graph_return_nodes JSON."
            )

        def on(item) -> str:
            if rule is not None:
                return rule.validate()
            if isinstance(item, str):
                return item
            if graph_paths:
                return ""
            return self._rules_for(item)

        parts = [part for part in self.run(on, action="validate") if part]
        sections.extend(parts)
        report = "\n\n".join(sections)
        self._save_reports(report, graph_paths)
        where = ", ".join(str(path) for path in self._reports) if self._reports else str(self._session_path())
        return f"{report}\n\nValidation report for these artifacts: {where}"

    def listed_rules(self) -> str:
        """The shared rules and the active fidelity's rules of each listed guidance, as text for another action to
        follow. It checks nothing, so it saves no report and writes nothing to the session log, where a validate line
        would tell the session board the work had been checked."""
        return "\n\n".join(part for part in self.each(self._rules_text_of) if part)

    def _rules_text_of(self, item) -> str:
        return item if isinstance(item, str) else self._rules_for(item)

    def _new_reports(self) -> list[Path]:
        """A new report file in the session for each listed guidance's fidelity, claimed before the graph is built so
        the graph this call checks can be written beside its report."""
        items = [item for item in self.listed() if not isinstance(item, str)]
        fidelities = [fidelity for fidelity in (self._fidelity_of(item) for item in items) if fidelity is not None]
        return [self._claimed(fidelity.new_report_path()) for fidelity in fidelities]

    def _claimed(self, dated: Path) -> Path:
        """Create the report file under a name no other call holds. A report's name is dated to the second, so a call
        in the same second as another takes the next number (``…T034343_2.md``); the date stays where the board reads
        it, and the names still sort by time."""
        path, number = dated, 1
        while not self._created(path):
            number += 1
            path = dated.with_name(f"{dated.stem}_{number}{dated.suffix}")
        return path

    def _created(self, path: Path) -> bool:
        """Create path as an empty file; false when another call already holds that name."""
        try:
            path.touch(exist_ok=False)
        except FileExistsError:
            return False
        return True

    def _save_reports(self, report: str, checked_graphs: list[Path]) -> None:
        """Save the report into each file this call claimed, so the board can link to it.

        The graph it checked goes beside each report under the same name, so a report's violations stay on
        their nodes for as long as the report is kept."""
        from cdd_guidance.actions.validate.graph_json_reader import save_checked_graph

        for path in self._reports:
            path.write_text(report, encoding="utf-8")
            beside = path.with_suffix(".json")
            if beside not in checked_graphs:
                save_checked_graph(checked_graphs, beside)

    def _fidelity_of(self, item):
        """The fidelity a guidance item is validated at. A listed practice is the one this action's session holds, so
        its fidelity's reports go to that session; none when the item has no current fidelity or is no practice a
        session works on."""
        current = getattr(getattr(item, "fidelities", None), "current", None)
        return current if current is not None and self._session_practice(item) is not None else None

    def _resolve_graph_json_paths(
        self, graph: bool | str | list[str] | None, edited: list[str]
    ) -> list[Path]:
        from cdd_guidance.actions.validate.graph_json_reader import load_graph_json_paths

        if edited and graph in (None, True) and self._graph_practices():
            return [self._edited_graph_json(edited)]
        paths = load_graph_json_paths(graph)
        if graph is True and not paths:
            default = self._session_path() / "clean-engineering-violations.json"
            if default.is_file():
                return [default]
            saved = self.session.root / ".context" / "graph.json"
            if saved.is_file():
                return [saved]
        return paths

    def _edited_graph_json(self, edited: list[str]) -> Path:
        """Build the graph from just the edited files and write it beside this call's report; the saved graph stays as
        it is. Each call writes its own file, so calls running at once never read each other's graph.

        Every graph practice loads, because one builds on another (DDD building blocks come from the
        clean engineering classes); the report keeps only the listed guidance's practice.
        """
        from harness.graph.graph import Graph

        destination = self._reports[0].with_suffix(".json") if self._reports else self._new_session_graph_file()
        graph = Graph()
        graph.load_files(str(self.session.root), list(PracticeCatalogue.keys()), edited)
        graph.write_json(str(destination))
        return destination

    def _new_session_graph_file(self) -> Path:
        """A graph file of this call's own in the session, for a validate that saves no report."""
        folder = self._session_path()
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=folder, prefix="edited-graph-", suffix=".json", delete=False) as file:
            return Path(file.name)

    def _workspace_relative(self, paths: list[str] | None) -> list[str]:
        """Each named path as graph node files record it, relative to the session's root.

        A relative path is read from the project's checkout, where the agent works and every path it sees starts. A
        path that is not there, or not under the session's root, is refused: the graph would be built from nothing,
        and its empty report would read as a clean validate."""
        workspace = self.session.root
        project = self.session.repo_from_session()
        named = [(item, (project / item).resolve()) for item in paths or []]
        unreadable = [item for item, path in named if not path.exists() or (path != workspace and workspace not in path.parents)]
        if unreadable:
            raise PathsNotFoundError(unreadable, project, workspace)
        return [path.relative_to(workspace).as_posix() for _, path in named]

    def _checked_outputs(self) -> list[tuple[object, dict[str, list[str]]]]:
        """Each listed guidance with its fidelity outputs, by format. Validate checks one format, the guidance's own:
        the format the guidance names, else the one the latest generate wrote, else the fidelity's default. A
        fidelity's formats mirror each other, so checking every one reports each finding once per format."""
        return [(item, self._fidelity_outputs(item)) for item in self.listed() if not isinstance(item, str)]

    def _other_format_files(self, checked: list[tuple[object, dict[str, list[str]]]]) -> set[str]:
        """The declared files of every format validate does not check, as graph node files record them."""
        workspace = self.session.root
        others = [(self.session.repo_from_session() / path).resolve() for item, outputs in checked for format, paths in outputs.items() if format != item.format for path in paths if "{" not in path]
        return {path.relative_to(workspace).as_posix() for path in others if workspace in path.parents}

    def _judging_instruction(self, checked: list[tuple[object, dict[str, list[str]]]], graph_paths: list[Path]) -> str:
        """What the judge judges for each listed guidance: at a model or code fidelity with a graph, the graph validate
        built; otherwise the checked format's files."""
        graph_judged = [(item, outputs) for item, outputs in checked if graph_paths and self._judges_graph(item)]
        file_judged = [(item, outputs) for item, outputs in checked if not (graph_paths and self._judges_graph(item))]
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

    def _judged_files(self, checked: list[tuple[object, dict[str, list[str]]]]) -> str:
        return "; ".join(f"{item.format}: {', '.join(outputs.get(item.format, []))}" for item, outputs in checked)

    def _judges_graph(self, item) -> bool:
        current = getattr(getattr(item, "fidelities", None), "current", None)
        return getattr(current, "name", None) in _GRAPH_JUDGED_FIDELITIES

    def _written_outputs(self, checked: list[tuple[object, dict[str, list[str]]]]) -> list[str]:
        """The folders holding what each listed graph-backed guidance's fidelity declares in its checked format and has
        already written: what a validate that names no paths checks, so its graph is built and saved beside the report.
        The folder, not the file, because a story map's stories keep their scenarios in files beside it."""
        if not self._graph_practices():
            return []
        workspace = self.session.root
        declared = [path for item, outputs in checked for path in outputs.get(item.format, [])]
        found = [(self.session.repo_from_session() / path).resolve() for path in declared if "{" not in path]
        folders = {path.parent if path.is_file() else path for path in found if path.exists()}
        return sorted(str(folder) for folder in folders if folder == workspace or workspace in folder.parents)

    def _fidelity_outputs(self, item) -> dict[str, list[str]]:
        return item.output_paths() if isinstance(item, PracticeGuidance) else {}

    def _listed_practices(self) -> list:
        """Each listed practice as this action's session holds it, which logs its own validate line; guidance that is no
        practice CDD has is left out."""
        found = [self._session_practice(item) for item in self.listed() if not isinstance(item, str)]
        return [practice for practice in found if practice is not None]

    def _graph_practices(self) -> list[str]:
        """The catalogue key of each listed practice, such as clean_engineering; none for other guidance."""
        practices = [item for item in self.listed() if isinstance(item, PracticeGuidance)]
        return [practice.key for practice in practices if PracticeCatalogue.has(practice.key)]

    def _session_path(self) -> Path:
        return Path(self.session.session_path)

    def _graph_and_ai_rule_report(
        self,
        paths: list[Path],
        *,
        path_prefixes: list[str] | None = None,
    ) -> str:
        from cdd_guidance.actions.validate.graph_json_reader import (
            filter_violations_by_path_prefix,
            refresh_stale_limit_operation_parameter_messages,
            violations_from_graph_json_files,
        )
        from cdd_guidance.actions.validate.validation_report import ValidationReport

        violations = violations_from_graph_json_files(paths, self._graph_practices() or None)
        violations = refresh_stale_limit_operation_parameter_messages(violations, self.session.root)
        violations = filter_violations_by_path_prefix(violations, path_prefixes)
        violations = [violation for violation in violations if violation.get("location") not in self._unchecked_files]
        self._log_graph_validation(violations)
        rules: list = []
        rule_bodies: dict[str, str] = {}
        for item in self.listed():
            if isinstance(item, str):
                continue
            rules.extend(self._iter_validate_rules(item))
            rule_bodies.update(self._rule_bodies_from_guidance(item))
        return ValidationReport(self.session).of_graph_and_ai_rules(
            violations,
            rules,
            graph_sources=[str(path.resolve()) for path in paths],
            rule_bodies=rule_bodies,
        )

    def _iter_validate_rules(self, item) -> list:
        from harness.guidance.rule import Rule

        ordered: list[Rule] = []
        seen: set[int] = set()
        for collection in (getattr(item, "rules", None), *self._fidelity_rule_collections(item)):
            if collection is None or id(collection) in seen:
                continue
            seen.add(id(collection))
            for child in collection:
                if isinstance(child, Rule):
                    ordered.append(child)
        return ordered

    def _rule_bodies_from_guidance(self, item) -> dict[str, str]:
        from harness.guidance.rule import Rule

        bodies: dict[str, str] = {}
        seen: set[int] = set()
        collections: list = [getattr(item, "rules", None)]
        fidelities = getattr(item, "fidelities", None)
        if fidelities is not None:
            for child in fidelities:
                collections.append(getattr(child, "rules", None))
        for collection in collections:
            if collection is None or id(collection) in seen:
                continue
            seen.add(id(collection))
            text = getattr(collection, "markdown", "") or ""
            for line in text.splitlines():
                if not line.strip().startswith(("-", "*")):
                    continue
                parsed = Rule.from_bullet(line)
                if parsed.slug:
                    bodies[parsed.slug] = parsed.body
        return bodies

    def _log_graph_validation(self, violations: list) -> None:
        if self._guidance_text is not None or not violations:
            return
        synopsis = [
            f"graph-rule {item.get('rule_slug', '')} {item.get('location', '')}:{item.get('line_number', '')}"
            for item in violations[:40]
        ]
        if len(violations) > 40:
            synopsis.append(f"graph-rule … and {len(violations) - 40} more")
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

    def _rules_for(self, item) -> str:
        """Shared rules plus the active fidelity's rules. Every fidelity when none is active."""
        sections: list[str] = []
        seen: set[int] = set()
        for collection in (getattr(item, "rules", None), *self._fidelity_rule_collections(item)):
            if collection is None or id(collection) in seen:
                continue
            seen.add(id(collection))
            text = self._validate_text(collection)
            if text:
                sections.append(text)
        return "\n\n".join(sections)

    def _fidelity_rule_collections(self, item) -> list:
        fidelities = getattr(item, "fidelities", None)
        if fidelities is None:
            return []
        current = getattr(fidelities, "current", None)
        if current is not None:
            rules = getattr(current, "rules", None)
            return [rules] if rules is not None else []
        return [
            rules
            for child in fidelities
            if (rules := getattr(child, "rules", None)) is not None
        ]

    def _validate_text(self, collection) -> str:
        for accessor in ("validate", "markdown_block", "markdown"):
            text = getattr(collection, accessor, None)
            if text is None:
                continue
            if callable(text):
                text = text()
            if isinstance(text, str) and text.strip():
                return text.strip()
        return ""

    @noDeploy
    @Mcp
    @Skill
    @agent_instructions
    def createRule(self, guidance: GuidanceArg, failed: str = "", wanted: str = "") -> str:
        """Add a named rule to each listed guidance from a failed example and the wanted behavior. Then validate the asset with that rule so the same mistake is detected.
        failed: path to the example that broke. Pass the file. Do not paste its body.
        wanted: path to the behavior the rule must require. Pass the file. Do not paste its body."""
        self._bind_guidance(guidance)

        def on(item) -> None:
            if isinstance(item, str):
                return
            item.examples
            item.templates

        self.run(on, action="createRule")
        return (
            "Write a new named rule into this tool. "
            "Then run collection validate on the asset and detect a failure "
            "that matches the Mistake."
        )
