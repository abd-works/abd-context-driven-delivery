"""Build a markdown validation report (agile_bots-style sections)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harness.guidance.rule import Rule

from validate.graph_json_reader import violations_by_rule
from validate.validation_report_formatter import ValidationReportFormatter


class ValidationReport:
    """The validation report of one session: it names files by their path from the session's root and links to them
    from the session's folder, where the report is saved, so a link opens the file from wherever the report is read."""

    def __init__(self, session: Any) -> None:
        self._session = session

    def of_graph_and_ai_rules(
        self,
        violations: list[dict[str, Any]],
        rules: list[Rule],
        *,
        graph_sources: list[str] | None = None,
        rule_bodies: dict[str, str] | None = None,
    ) -> str:
        """Graph hits and AI judgment prompts in one section per rule (description under each heading)."""
        grouped = violations_by_rule(violations)
        total = len(violations)
        lines = [
            "# Graph rule validation",
            "",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Project:** {self._session.root.name}",
            f"**Action:** validate (graph JSON + AI rules)",
            "",
        ]
        if graph_sources:
            lines.append("**Graph sources:**")
            for source in graph_sources:
                lines.append(f"- `{source}`")
            lines.append("")
        lines.extend(["## Summary", ""])
        if total == 0:
            lines.append("**No graph rule violations.** All scanned graph rules passed.")
        else:
            lines.append(f"**Total graph violations:** {total}")
            lines.append(f"**Rules with graph hits:** {len(grouped)}")
        lines.append(f"**AI rules in scope:** {len(rules)}")
        lines.append("")
        lines.extend(_rule_by_rule_sections(grouped, rules, self._formatter, rule_bodies or {}))
        return "\n".join(lines)

    @property
    def _formatter(self) -> ValidationReportFormatter:
        folder = self._session.session_path
        return ValidationReportFormatter(self._session.root, link_from_directory=Path(folder) if folder else None)


def _rule_by_rule_sections(
    grouped: dict[str, list[dict[str, Any]]],
    rules: list[Rule],
    formatter: ValidationReportFormatter,
    rule_bodies: dict[str, str],
) -> list[str]:
    lines = [
        "## Rules",
        "",
        "Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.",
        "",
    ]
    seen: set[str] = set()
    for rule in rules:
        seen.add(rule.slug)
        lines.extend(
            _one_rule_section(rule, grouped.get(rule.slug), formatter, rule_bodies)
        )
    for slug in sorted(grouped.keys() - seen):
        lines.extend(
            _one_rule_section(
                Rule(slug=slug, body=rule_bodies.get(slug, "")),
                grouped[slug],
                formatter,
                rule_bodies,
            )
        )
    return lines


def _one_rule_section(
    rule: Rule,
    graph_hits: list[dict[str, Any]] | None,
    formatter: ValidationReportFormatter,
    rule_bodies: dict[str, str],
) -> list[str]:
    lines = [f"### `{rule.slug}`", ""]
    body = (rule.body or rule_bodies.get(rule.slug, "")).strip()
    if body:
        lines.append(body)
        lines.append("")
    if graph_hits:
        lines.append(f"**Graph violations:** {len(graph_hits)}")
        lines.append("")
        for violation in sorted(
            graph_hits,
            key=lambda v: (str(v.get("location")), v.get("line_number") or 0),
        ):
            lines.extend(formatter.format_violation_line(violation))
        lines.append("")
    lines.append(f"Evaluate the current context against this rule ({rule.slug}):")
    lines.append("")
    return lines
