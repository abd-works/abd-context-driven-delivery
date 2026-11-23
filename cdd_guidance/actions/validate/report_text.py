"""The markdown validation report one validate call writes: graph rule hits and the AI rules, one section per rule."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from harness.graph.violation import Violation
from harness.graph.schema_conformance import FRAMEWORK_RULES
from harness.guidance.guidance import Guidance
from harness.guidance.rule import Rule

if TYPE_CHECKING:
    from cdd_guidance.actions.validate.checked_graph import CheckedGraph
    from space.session.session import Session

# A Windows path's separator, which a location may carry; the report names files with forward slashes.
_BACKSLASH = "\\"
_CANDIDATES_NOTE = (
    "A hit marked `**CANDIDATE**` comes from a rule that requires a judge: its check only lists places to read, so read each "
    "and fail the rule only where the reading finds it broken."
)
_RULES_FOR_JUDGE = ["## Rules", "", f"Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt. {_CANDIDATES_NOTE}", ""]
_RULES_SAVED = [
    "## Rules",
    "",
    "Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended "
    f"after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6). {_CANDIDATES_NOTE}",
    "",
]
# What a hit of a rule that runs over the whole working copy says when it is outside the paths a validate was given.
_OUTSIDE_PATHS = " *(outside the paths this validate was given)*"
# A rule as a practice document lists it: a bullet opening with its slug, in backticks or bold.
_RULE_BULLET = re.compile(r"^\s*[-*]\s+(?:\*\*`?|`)(?P<slug>[^`*]+)`?(?:\*\*)?\s*[—:-]")


class ReportText:
    """The text of the validation report of one session on the guidance a validate call lists, each at the fidelity it is validated
    at, and the graph the call checked (its *CheckedGraph*). It shows each rule that guidance checks, and for a graph hit
    of a rule it does not check, that rule as the guidance has it; for a call that names one rule, that rule alone. It names files by their path from the session's root
    and links each hit to its file by absolute path and line, so a link opens the file from wherever the report is read.

    The judge is given each rule's text with its hits (``for_judge``); the report saved in the session points at where
    each rule's text is kept instead (``for_saving``), since every report would otherwise copy the same rules again."""

    def __init__(self, guidance: list[Guidance], checked: CheckedGraph, only: Rule | None = None) -> None:
        # The session the checked graph was built in, whose root the report names files from.
        self._session: Session = checked.session
        self._guidance = guidance
        self._checked = checked
        # The one rule the call names, which is then the only rule the report shows; none for every rule.
        self._only = only
        self._root = self._session.work_root.resolve()
        self._places = RulePlaces(guidance)

    def for_judge(self) -> str:
        """Graph hits and AI judgment prompts in one section per rule (its text under each heading). A graph that held
        other files beside the checked ones names their folders: a rule over a whole practice compared the checked files
        with them, so another validate of the same files can find other hits when the session's graph holds others."""
        lines = [*self._header_lines(), *self._summary_lines(), *_RULES_FOR_JUDGE]
        for slug, rule, hits in self._sections():
            body = (rule.body or "").strip() if rule is not None else ""
            lines.extend([f"### `{slug}`", "", *([body, ""] if body else []), *self._hit_lines(hits)])
            lines.extend([f"Evaluate the current context against this rule ({slug}):", ""])
        return "\n".join(lines)

    def for_saving(self) -> str:
        """The report as the session keeps it: its header, summary, and one section per rule with where the rule's text
        is kept and its graph hits, for the judge to append its judgment to. The rule texts and how to judge are in the
        guidance, so no saved report copies them."""
        lines = [*self._header_lines(), *self._summary_lines(), *_RULES_SAVED]
        for slug, _, hits in self._sections():
            lines.extend([f"### `{slug}`", "", f"Rule text: {self._places.place_of(slug)}", "", *self._hit_lines(hits)])
        return "\n".join(lines)

    def _sections(self) -> list[tuple[str, Rule | None, list[Violation]]]:
        """Each rule the listed guidance checks, then each other rule the graph hit, with the hits on it."""
        grouped = Violation.by_rule(self._checked.violations())
        rules = self._rules_in_scope()
        if self._only is not None:
            return [(rule.slug, rule, grouped.get(rule.slug, [])) for rule in rules]
        checked = {rule.slug for rule in rules}
        every = {slug: check.rule for slug, check in FRAMEWORK_RULES.items()}
        every.update((rule.slug, rule) for item in self._guidance for rule in item.every_rule)
        sections = [(rule.slug, rule, grouped.get(rule.slug, [])) for rule in rules]
        return sections + [(slug, every.get(slug), grouped[slug]) for slug in sorted(grouped.keys() - checked)]

    def _header_lines(self) -> list[str]:
        """When and for which project the report was written, and the graph files and folders it was built from."""
        lines = [
            "# Graph rule validation",
            "",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Project:** {self._session.work_root.name}",
            "**Action:** validate (graph JSON + AI rules)",
            "",
        ]
        sources = [str(path.resolve()) for path in self._checked.files]
        if sources:
            lines.extend(["**Graph sources:**", *(f"- `{source}`" for source in sources), ""])
        held_beside = self._checked.held_beside
        if held_beside:
            lines.extend(["**The session's graph also held, and practice-wide rules compared against:**", *(f"- `{folder}`" for folder in held_beside), ""])
        return lines

    def _summary_lines(self) -> list[str]:
        """How many graph violations the report holds, across how many rules, how many candidates the rules that require
        a judge listed, which are counted apart since nothing has decided they are wrong, how many it leaves out because a person
        accepted them, and how many rules the AI judges; with no graph checked, that the judgment covers the files
        alone; and each named path the graph read no node from."""
        found = self._checked.violations()
        violations = [violation for violation in found if not violation.is_candidate]
        candidates = [violation for violation in found if violation.is_candidate]
        accepted = self._checked.accepted()
        unread = self._checked.unread
        lines = ["## Summary", "", *self._graph_result_lines(violations, unread)]
        if candidates:
            lines.append(f"**Candidates for the judge to read:** {len(candidates)}. A rule that requires a judge listed each; none is a violation until the judge reads it and fails it.")
        if accepted:
            lines.append(self._accepted_line(accepted))
        if unread:
            lines.append(self._unread_line(unread))
        lines.extend([f"**AI rules in scope:** {len(self._rules_in_scope())}", ""])
        return lines

    def _graph_result_lines(self, violations: list[Violation], unread: list[str]) -> list[str]:
        """What the graph rules found: that no graph was checked, how many violations across how many rules, or that
        every rule passed; nothing when the graph read no node from any named path, which the unread line says."""
        if not self._checked.files:
            return ["**No graph checked.** The judgment covers the checked files."]
        if violations:
            return [f"**Total graph violations:** {len(violations)}", f"**Rules with graph hits:** {len(Violation.by_rule(violations))}"]
        if len(unread) < len(self._checked.edited) or not unread:
            return ["**No graph rule violations.** All scanned graph rules passed."]
        return []

    def _accepted_line(self, accepted: list[Violation]) -> str:
        """That the report leaves out the violations a person accepted, how many, and the file that keeps them, so a
        judge does not report them again and a reader can find and take back an acceptance."""
        kept = self._shown(self._session.accepted_violations.file.resolve())
        return f"**Accepted violations left out:** {len(accepted)}. A person accepted them as they are, in `{kept}`; do not report them again."

    def _unread_line(self, unread: list[str]) -> str:
        """That no graph rule ran on the named paths the graph read no node from, so nobody reads a report with no
        violation as those files passing the graph rules."""
        named = ", ".join(f"`{path}`" for path in unread)
        return f"**No graph rule ran on:** {named}. The graph read no node from them, so only the AI rules judge them."

    def _rules_in_scope(self) -> list[Rule]:
        """The rules the judge judges: the one the call names, else every rule the listed guidance checks."""
        if self._only is not None:
            return [self._only]
        return [rule for item in self._guidance for rule in item.checked_rules()]

    def _hit_lines(self, hits: list[Violation]) -> list[str]:
        """A rule's hits: its violations under their count, then its candidates under theirs."""
        violations = [hit for hit in hits if not hit.is_candidate]
        candidates = [hit for hit in hits if hit.is_candidate]
        return [*self._listed("Graph violations", violations), *self._listed("Candidates for the judge to read", candidates)]

    def _listed(self, heading: str, hits: list[Violation]) -> list[str]:
        if not hits:
            return []
        lines = [f"**{heading}:** {len(hits)}", ""]
        for violation in sorted(hits, key=lambda violation: (violation.location, violation.line or 0)):
            lines.extend(self._violation_lines(violation))
        return [*lines, ""]

    def _violation_lines(self, violation: Violation) -> list[str]:
        """One graph rule's violation as report lines, linked to its file and line; a candidate is marked ``[?]``, and a
        hit of a rule that runs over the whole working copy is marked when it is outside the paths the call was given."""
        severity = violation.severity
        icon = "[?]" if violation.is_candidate else "[X]"
        parts = str(violation.described or "No message").split("\n")
        outside = _OUTSIDE_PATHS if self._is_outside_given_paths(violation) else ""
        lines = [f"- {icon} **{severity.upper()}** **[graph rule]** - {self._file_link(violation)}: {parts[0]}{outside}"]
        for part in parts[1:]:
            if part.strip().startswith("```"):
                lines.append(f"    {part}")
            elif part.strip() == "":
                lines.append("")
            else:
                lines.append(f"  {part}")
        return lines

    def _is_outside_given_paths(self, violation: Violation) -> bool:
        given = self._checked.files_built_from
        return bool(given) and violation.runs_over_all and not violation.is_under(given)

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
            return f"`{Path(location.replace(_BACKSLASH, '/')).name}`"

    def _shown(self, path: Path) -> str:
        try:
            return path.relative_to(self._root).as_posix()
        except ValueError:
            return path.name


class RulePlaces:
    """Where each rule the listed guidance can report is written: the line of its bullet in the document of the
    practice that holds it, read once from each practice's document."""

    def __init__(self, guidance: list[Guidance]) -> None:
        self._guidance = guidance
        self._lines: dict[str, tuple[Path, int]] | None = None

    def place_of(self, slug: str) -> str:
        """A link to the line slug's rule is written on; a note that it is written in no practice document, for a rule
        only the graph checks."""
        place = self._found().get(slug)
        if place is None:
            return "a graph rule, written in no practice document"
        document, line = place
        return f"[{document.parent.name}/{document.name}:{line}]({document}#L{line})"

    def _found(self) -> dict[str, tuple[Path, int]]:
        if self._lines is None:
            self._lines = {}
            for document in self._documents():
                self._read(document)
        return self._lines

    def _read(self, document: Path) -> None:
        for number, line in enumerate(document.read_text(encoding="utf-8").splitlines(), 1):
            bullet = _RULE_BULLET.match(line)
            if bullet:
                self._lines.setdefault(bullet["slug"].strip(), (document, number))

    def _documents(self) -> list[Path]:
        """The documents of the practices whose rules the listed guidance checks, each once, its own practice's first."""
        owners = [collection.owner_practice for item in self._guidance for collection in item.checked_rule_collections]
        documents = [owner.domain_markdown_path for owner in owners if owner is not None]
        return [document for document in dict.fromkeys(documents) if document.is_file()]
