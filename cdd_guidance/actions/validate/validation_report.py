"""The markdown validation report one validate call writes: graph rule hits and the AI rules, one section per rule."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harness.graph.violation import Violation
from harness.guidance.rule import Rule


class ValidationReport:
    """The validation report of one session on the guidance a validate call lists, each at the fidelity it is validated
    at. It shows each rule that guidance
    checks, and for a graph hit of a rule it does not check, that rule as the guidance has it. It names files by their
    path from the session's root and links each hit to its file by absolute path and line, so a link opens the file from
    wherever the report is read."""

    def __init__(self, session: Any, guidance: list[Any]) -> None:
        self._session = session
        self._guidance = guidance
        self._root = session.work_root.resolve()

    def of_graph(self, violations: list[Violation], graph_sources: list[str] | None = None, held_beside: list[str] | None = None) -> str:
        """Graph hits and AI judgment prompts in one section per rule (description under each heading). A graph that held
        other files beside the checked ones names their folders: a rule over a whole practice compared the checked files
        with them, so another validate of the same files can find other hits when the session's graph holds others."""
        grouped = Violation.by_rule(violations)
        rules = [rule for item in self._guidance for rule in item.checked_rules()]
        lines = [
            "# Graph rule validation",
            "",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Project:** {self._session.work_root.name}",
            "**Action:** validate (graph JSON + AI rules)",
            "",
        ]
        if graph_sources:
            lines.extend(["**Graph sources:**", *(f"- `{source}`" for source in graph_sources), ""])
        if held_beside:
            lines.extend(["**The session's graph also held, and practice-wide rules compared against:**", *(f"- `{folder}`" for folder in held_beside), ""])
        lines.extend(["## Summary", ""])
        if not violations:
            lines.append("**No graph rule violations.** All scanned graph rules passed.")
        else:
            lines.append(f"**Total graph violations:** {len(violations)}")
            lines.append(f"**Rules with graph hits:** {len(grouped)}")
        lines.extend([f"**AI rules in scope:** {len(rules)}", ""])
        lines.extend(self._rule_sections(grouped, rules))
        return "\n".join(lines)

    def _rule_sections(self, grouped: dict[str, list[Violation]], rules: list[Rule]) -> list[str]:
        lines = [
            "## Rules",
            "",
            "Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.",
            "",
        ]
        for rule in rules:
            lines.extend(self._rule_section(rule.slug, rule, grouped.get(rule.slug)))
        checked = {rule.slug for rule in rules}
        every = {rule.slug: rule for item in self._guidance for rule in item.every_rule()}
        for slug in sorted(grouped.keys() - checked):
            lines.extend(self._rule_section(slug, every.get(slug), grouped[slug]))
        return lines

    def _rule_section(self, slug: str, rule: Rule | None, graph_hits: list[Violation] | None) -> list[str]:
        lines = [f"### `{slug}`", ""]
        body = (rule.body or "").strip() if rule is not None else ""
        if body:
            lines.extend([body, ""])
        if graph_hits:
            lines.extend([f"**Graph violations:** {len(graph_hits)}", ""])
            for violation in sorted(graph_hits, key=lambda violation: (violation.location, violation.line or 0)):
                lines.extend(self._violation_lines(violation))
            lines.append("")
        lines.extend([f"Evaluate the current context against this rule ({slug}):", ""])
        return lines

    def _violation_lines(self, violation: Violation) -> list[str]:
        """One graph rule's violation as report lines, linked to its file and line."""
        severity = violation.severity
        icon = "[X]" if severity == "error" else "[!]" if severity == "warning" else "[i]"
        parts = str(violation.described or "No message").split("\n")
        lines = [f"- {icon} **{severity.upper()}** **[graph rule]** - {self._file_link(violation)}: {parts[0]}"]
        for part in parts[1:]:
            if part.strip().startswith("```"):
                lines.append(f"    {part}")
            elif part.strip() == "":
                lines.append("")
            else:
                lines.append(f"  {part}")
        return lines

    def _file_link(self, violation: Violation) -> str:
        """The violation's file, named from the session's root and linked by absolute path with its line, which a
        markdown preview opens."""
        location = str(violation.location)
        if not location or location == "unknown":
            return f"`{location}`"
        try:
            path = Path(location)
            resolved = (path if path.is_absolute() else self._root / path).resolve()
            line = f"#L{violation.line}" if violation.line is not None else ""
            return f"[{self._shown(resolved)}]({resolved}{line})"
        except (OSError, ValueError):
            return f"`{Path(location.replace(chr(92), '/')).name}`"

    def _shown(self, path: Path) -> str:
        try:
            return path.relative_to(self._root).as_posix()
        except ValueError:
            return path.name
