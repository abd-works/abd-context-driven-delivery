"""Build a markdown validation report (agile_bots-style sections)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harness.guidance.rule import Rule

from validate.graph_json_reader import violations_by_rule
from validate.validation_report_formatter import ValidationReportFormatter


def build_graph_json_report(
    violations: list[dict[str, Any]],
    *,
    workspace_directory: Path,
    title: str = "Validation Report",
    graph_sources: list[str] | None = None,
    link_from_directory: Path | None = None,
) -> str:
    formatter = ValidationReportFormatter(
        workspace_directory,
        link_from_directory=link_from_directory,
    )
    grouped = violations_by_rule(violations)
    total = len(violations)
    lines = [
        f"# {title}",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"**Project:** {workspace_directory.name}",
        f"**Action:** validate (graph JSON)",
        "",
    ]
    if graph_sources:
        lines.append("**Graph sources:**")
        for source in graph_sources:
            lines.append(f"- `{source}`")
        lines.append("")
    lines.extend(["## Summary", ""])
    if total == 0:
        lines.append("**No graph rule violations.** All scanned rules passed.")
        lines.append("")
        return "\n".join(lines)
    lines.append(f"**Total graph violations:** {total}")
    lines.append(f"**Rules with hits:** {len(grouped)}")
    lines.append("")
    lines.extend(_violations_section(grouped, formatter))
    return "\n".join(lines)


def build_graph_and_ai_rule_report(
    violations: list[dict[str, Any]],
    rules: list[Rule],
    *,
    workspace_directory: Path,
    title: str = "Graph rule validation",
    graph_sources: list[str] | None = None,
    link_from_directory: Path | None = None,
    rule_bodies: dict[str, str] | None = None,
) -> str:
    """Graph hits and AI judgment prompts in one section per rule (description under each heading)."""
    formatter = ValidationReportFormatter(
        workspace_directory,
        link_from_directory=link_from_directory,
    )
    grouped = violations_by_rule(violations)
    total = len(violations)
    lines = [
        f"# {title}",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"**Project:** {workspace_directory.name}",
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
    bodies = rule_bodies or {}
    lines.extend(_rule_by_rule_sections(grouped, rules, formatter, bodies))
    return "\n".join(lines)


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


def _violations_section(
    grouped: dict[str, list[dict[str, Any]]],
    formatter: ValidationReportFormatter,
) -> list[str]:
    lines = ["## Violations Found (graph rules)", "", "Each item was detected by the practice graph scanner (`graph_rule: true`).", ""]
    for rule in sorted(grouped.keys(), key=lambda r: (-len(grouped[r]), r)):
        hits = grouped[rule]
        lines.append(f"### {rule}: {len(hits)} violation(s)")
        lines.append("")
        for violation in sorted(
            hits,
            key=lambda v: (str(v.get("location")), v.get("line_number") or 0),
        ):
            lines.extend(formatter.format_violation_line(violation))
        lines.append("")
    return lines
