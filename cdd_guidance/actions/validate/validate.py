"""Validate and CreateRule — run on each provided context tool."""

from __future__ import annotations

from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset, instructions
from harness.installation.destination import noDeploy
from harness.installation.files import Skill
from harness.mcp.mcp_server import Mcp
from harness.guidance import Rule

_VALIDATE_MARKDOWN = Path(__file__).with_name("validate.md").read_text(encoding="utf-8")

@agent_toolset
class Validate(GuidanceAction):
    """Validate artifacts for provided context tools."""

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
        graph: path(s) to graph_return_nodes JSON (violations-only or full nodes).
        When set, append a graph-rule report from that JSON and still run AI validation.
        paths: optional path prefixes (e.g. src/my-paradise) to scope graph violations."""
        instructions(_VALIDATE_MARKDOWN)
        self._bind_guidance(guidance)
        sections: list[str] = [_VALIDATE_MARKDOWN]
        graph_paths = self._resolve_graph_json_paths(graph)
        if graph_paths:
            sections.append(
                self._graph_and_ai_rule_report(graph_paths, path_prefixes=paths)
            )
        elif graph:
            sections.append(
                "No graph JSON file found. Pass graph as a path to graph_return_nodes JSON "
                "(or set session_path/clean-engineering-violations.json when graph is true)."
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
        sections.append("Validation report for artifacts under {session.path}/.")
        return "\n\n".join(sections)

    def _resolve_graph_json_paths(self, graph: bool | str | list[str] | None) -> list[Path]:
        from validate.graph_json_reader import load_graph_json_paths

        paths = load_graph_json_paths(graph)
        if graph is True and not paths:
            session_path = self._session_path()
            if session_path is not None:
                default = session_path / "clean-engineering-violations.json"
                if default.is_file():
                    return [default]
        return paths

    def _session_path(self) -> Path | None:
        from space.session import Session

        session = Session.current()
        if session is None or session.session_path is None:
            return None
        return Path(session.session_path)

    def _validate_workspace(self) -> Path:
        from space.session import Session

        session = Session.current()
        if session is not None and session.workpath is not None:
            return Path(session.workpath).resolve()
        import os

        project = os.environ.get("CDD_PROJECT")
        if project:
            return Path(project).resolve()
        return Path.cwd().resolve()

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
        violations = violations_from_graph_json_files(paths)
        violations = refresh_stale_limit_operation_parameter_messages(violations, workspace)
        violations = filter_violations_by_path_prefix(violations, path_prefixes)
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
        from space.session import Session

        session = Session.current()
        if session is None or session.session_path is None or self._guidance_text is not None:
            return
        if not violations:
            return
        synopsis = [
            f"graph-rule {item.get('rule_slug', '')} {item.get('location', '')}:{item.get('line_number', '')}"
            for item in violations[:40]
        ]
        if len(violations) > 40:
            synopsis.append(f"graph-rule … and {len(violations) - 40} more")
        for item in self.listed():
            session.log_validation(item, synopsis)

    def _log_running_action(self, action: str) -> None:
        if action == "validate":
            self._log_validation_to_session()
            return
        super()._log_running_action(action)

    def _log_validation_to_session(self) -> None:
        from space.session import Session

        session = Session.current()
        if session is None or session.session_path is None or self._guidance_text is not None:
            return
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
