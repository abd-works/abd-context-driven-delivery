"""Validate and CreateRule — run on each provided context tool."""

from __future__ import annotations

from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset
from harness.installation.destination import noDeploy
from harness.installation.files import Skill
from harness.mcp.mcp_server import Mcp
from harness.guidance import Rule

_VALIDATE_MARKDOWN = Path(__file__).with_name("validate.md").read_text(encoding="utf-8")
_GRAPH_PRACTICES = frozenset({"clean_engineering", "ddd", "stories", "bdd", "ux"})


class PathsNotFoundError(FileNotFoundError):
    """Raised when validate is named a path that is not there, or not under the session's root, where the graph reads."""

    def __init__(self, unreadable: list[str], project: Path, session_root: Path) -> None:
        named = "; ".join(f"{path}, read from {project}" for path in unreadable)
        super().__init__(f"validate found no file under the session's root {session_root} at {named}. Name paths from the project's root, or absolute.")


@agent_toolset
class Validate(GuidanceAction):
    """Validate artifacts for provided context tools."""

    # The declared files of the formats a validate does not check; their graph hits are left out of its report.
    _unchecked_files: frozenset[str] | set[str] = frozenset()

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
        if checked:
            sections.append(self._one_format_instruction(checked))
        named = [path for path in self._workspace_relative(paths) if path not in self._unchecked_files]
        prefixes = named or self._workspace_relative(self._written_outputs(checked) if graph is None else [])
        graph_paths = self._resolve_graph_json_paths(graph, prefixes)
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

        parts = [part for part in self.run(guidance, on, action="validate") if part]
        sections.extend(parts)
        report = "\n\n".join(sections)
        saved = self._save_reports(report, graph_paths)
        where = ", ".join(str(path) for path in saved) if saved else str(self._session_path())
        return f"{report}\n\nValidation report for these artifacts: {where}"

    def rules_of(self, guidance: GuidanceArg) -> str:
        """The shared rules and the active fidelity's rules of each listed guidance, as text for another action to
        follow. It checks nothing, so it saves no report and writes nothing to the session log, where a validate line
        would tell the session board the work had been checked."""
        self._bind_guidance(guidance)
        return "\n\n".join(part for part in self.each(self._rules_text_of) if part)

    def _rules_text_of(self, item) -> str:
        return item if isinstance(item, str) else self._rules_for(item)

    def _save_reports(self, report: str, checked_graphs: list[Path]) -> list[Path]:
        """Save the report in the session for each listed guidance, so the board can link to it.

        The graph it checked goes beside each report under the same name, so a report's violations stay on
        their nodes for as long as the report is kept."""
        from validate.graph_json_reader import save_checked_graph

        items = [item for item in self.listed() if not isinstance(item, str)]
        if not items:
            return []
        session = self.acting_session()
        fidelities = [fidelity for fidelity in (self._fidelity_in(session, item) for item in items) if fidelity is not None]
        paths = [fidelity.new_report_path() for fidelity in fidelities]
        for path in paths:
            path.write_text(report, encoding="utf-8")
            save_checked_graph(checked_graphs, path.with_suffix(".json"))
        return paths

    def _fidelity_in(self, session, item):
        """The fidelity a guidance item is validated at, as session's own practice holds it, so its reports go to that
        session; none when the item has no current fidelity or is no practice a session works on."""
        current = getattr(getattr(item, "fidelities", None), "current", None)
        practice = session.practices.get(item.key)
        if current is None or practice is None:
            return None
        return practice.fidelities[current.name]

    def _resolve_graph_json_paths(
        self, graph: bool | str | list[str] | None, edited: list[str]
    ) -> list[Path]:
        from validate.graph_json_reader import load_graph_json_paths

        if edited and graph in (None, True) and self._graph_practices():
            return [self._edited_graph_json(edited)]
        paths = load_graph_json_paths(graph)
        if graph is True and not paths:
            default = self._session_path() / "clean-engineering-violations.json"
            if default.is_file():
                return [default]
            saved = self._validate_workspace() / ".context" / "graph.json"
            if saved.is_file():
                return [saved]
        return paths

    def _edited_graph_json(self, edited: list[str]) -> Path:
        """Build the graph from just the edited files and write it beside the session; the saved graph stays as it is.

        Every graph practice loads, because one builds on another (DDD building blocks come from the
        clean engineering classes); the report keeps only the listed guidance's practice.
        """
        from harness.graph.graph import Graph

        workspace = self._validate_workspace()
        graph = Graph()
        graph.load_files(str(workspace), sorted(_GRAPH_PRACTICES), edited)
        return Path(graph.write_json(str(self._session_path() / "edited-graph.json")))

    def _workspace_relative(self, paths: list[str] | None) -> list[str]:
        """Each named path as graph node files record it, relative to the session's root.

        A relative path is read from the project's checkout, where the agent works and every path it sees starts. A
        path that is not there, or not under the session's root, is refused: the graph would be built from nothing,
        and its empty report would read as a clean validate."""
        workspace = self._validate_workspace()
        project = self._project_checkout()
        named = [(item, (project / item).resolve()) for item in paths or []]
        unreadable = [item for item, path in named if not path.exists() or (path != workspace and workspace not in path.parents)]
        if unreadable:
            raise PathsNotFoundError(unreadable, project, workspace)
        return [path.relative_to(workspace).as_posix() for _, path in named]

    def _checked_outputs(self) -> list[tuple[str, dict[str, list[str]]]]:
        """Each listed guidance's fidelity outputs, by format, and the one format validate checks: the format the
        guidance names, else the one the latest generate wrote, else the fidelity's default. A fidelity's formats mirror
        each other, so checking every one reports each finding once per format."""
        session = self.acting_session()
        named = [item.get("format", "") if isinstance(item, dict) else "" for item in self._tool_items or []]
        checked: list[tuple[str, dict[str, list[str]]]] = []
        for item, format in zip(self.listed(), named):
            if isinstance(item, str):
                continue
            chosen = item.format if format else (session.last_generated_format(item) or item.format)
            checked.append((chosen, self._fidelity_outputs(item)))
        return checked

    def _other_format_files(self, checked: list[tuple[str, dict[str, list[str]]]]) -> set[str]:
        """The declared files of every format validate does not check, as graph node files record them."""
        workspace = self._validate_workspace()
        others = [(self._project_checkout() / path).resolve() for chosen, outputs in checked for format, paths in outputs.items() if format != chosen for path in paths if "{" not in path]
        return {path.relative_to(workspace).as_posix() for path in others if workspace in path.parents}

    def _one_format_instruction(self, checked: list[tuple[str, dict[str, list[str]]]]) -> str:
        judged = "; ".join(f"{chosen}: {', '.join(outputs.get(chosen, []))}" for chosen, outputs in checked)
        return f"Judge only the checked format's files ({judged}). The other formats mirror them, so judging those too reports every finding twice."

    def _written_outputs(self, checked: list[tuple[str, dict[str, list[str]]]]) -> list[str]:
        """The folders holding what each listed graph-backed guidance's fidelity declares in its checked format and has
        already written: what a validate that names no paths checks, so its graph is built and saved beside the report.
        The folder, not the file, because a story map's stories keep their scenarios in files beside it."""
        if not self._graph_practices():
            return []
        workspace = self._validate_workspace()
        declared = [path for chosen, outputs in checked for path in outputs.get(chosen, [])]
        found = [(self._project_checkout() / path).resolve() for path in declared if "{" not in path]
        folders = {path.parent if path.is_file() else path for path in found if path.exists()}
        return sorted(str(folder) for folder in folders if folder == workspace or workspace in folder.parents)

    def _fidelity_outputs(self, item) -> dict[str, list[str]]:
        return self.acting_session().fidelity_outputs(item)

    def _graph_practices(self) -> list[str]:
        """Graph practices of the listed guidance (clean-engineering is clean_engineering); none for other guidance."""
        names = [
            str(getattr(item, "slug", "") or "").replace("-", "_")
            for item in self.listed()
            if not isinstance(item, str)
        ]
        return [name for name in names if name in _GRAPH_PRACTICES]

    def _session_path(self) -> Path:
        return Path(self.acting_session().session_path)

    def _validate_workspace(self) -> Path:
        return Path(self.acting_session().workpath).resolve()

    def _project_checkout(self) -> Path:
        session = self.acting_session()
        return Path(session.repo_path or session.workpath).resolve()

    def _graph_json_report(
        self,
        paths: list[Path],
        *,
        path_prefixes: list[str] | None = None,
    ) -> str:
        from validate.graph_json_reader import (
            filter_violations_by_path_prefix,
            refresh_stale_limit_operation_parameter_messages,
            violations_from_graph_json_files,
        )
        from validate.validation_report import build_graph_json_report

        workspace = self._validate_workspace()
        violations = violations_from_graph_json_files(paths)
        violations = refresh_stale_limit_operation_parameter_messages(violations, workspace)
        violations = filter_violations_by_path_prefix(violations, path_prefixes)
        violations = [violation for violation in violations if violation.get("location") not in self._unchecked_files]
        self._log_graph_validation(violations)
        return build_graph_json_report(
            violations,
            workspace_directory=self._validate_workspace(),
            title="Graph rule validation",
            graph_sources=[str(path.resolve()) for path in paths],
            link_from_directory=self._session_path(),
        )

    def _graph_and_ai_rule_report(
        self,
        paths: list[Path],
        *,
        path_prefixes: list[str] | None = None,
    ) -> str:
        from validate.graph_json_reader import (
            filter_violations_by_path_prefix,
            refresh_stale_limit_operation_parameter_messages,
            violations_from_graph_json_files,
        )
        from validate.validation_report import build_graph_and_ai_rule_report

        workspace = self._validate_workspace()
        violations = violations_from_graph_json_files(paths, self._graph_practices() or None)
        violations = refresh_stale_limit_operation_parameter_messages(violations, workspace)
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
        return build_graph_and_ai_rule_report(
            violations,
            rules,
            workspace_directory=workspace,
            title="Graph rule validation",
            graph_sources=[str(path.resolve()) for path in paths],
            link_from_directory=self._session_path(),
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
        session = self.acting_session()
        synopsis = [
            f"graph-rule {item.get('rule_slug', '')} {item.get('location', '')}:{item.get('line_number', '')}"
            for item in violations[:40]
        ]
        if len(violations) > 40:
            synopsis.append(f"graph-rule … and {len(violations) - 40} more")
        for item in self.listed():
            session.log_validation(item, synopsis)
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
        session = self.acting_session()
        for item in self.listed():
            session.log_validation(item, [])

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
        def on(item) -> None:
            if isinstance(item, str):
                return
            item.contexts
            item.examples
            item.templates

        self.run(guidance, on, action="createRule")
        return (
            "Write a new named rule into this tool. "
            "Then run collection validate on the asset and detect a failure "
            "that matches the Mistake."
        )
