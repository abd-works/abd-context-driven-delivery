"""Repair kit - record failures to mistakes.log; root-cause repair loop;
close the loop into regression evals and a durable archive.

Real toolset (not a mixin). Hosts get a real instance as a plain attribute
(``self.repairer``), so a cross-instance call like ``self.repairer.repair(...)``
expands inline as instruction text - same pattern as ``self.partitioner``.
"""

from __future__ import annotations

import ast
import uuid
from dataclasses import dataclass, field, replace
from datetime import date
from pathlib import Path
from typing import Any

from primitives.actions.action import action, agentic_toolset
from scanners.scan import Scan
from sub_agent.sub_agent import sub_agent
from tools.tool import tool

_LOG_HEADER = (
    "# mistakes.log - {sprint} sprint\n"
    "# Log omissions/errors here. Each entry:\n"
    "#   when, artifact, rule, wrong (one line), original, improved, status, tool, fidelity\n"
    '# A mistake pointed out = failed to do it right; '
    "log it immediately via log_mistake, then complete it via log_correction.\n\n"
)


@dataclass(frozen=True)
class MistakeEntry:
    """One recorded mistake, open or completed. ``entry_id`` correlates a
    mistake logged via ``log_mistake`` with its later ``log_correction`` -
    several can stay open at once without being conflated. ``tool``/
    ``fidelity`` name whichever context tool and fidelity produced it -
    auto-injected by the calling host, never supplied by the agent."""

    entry_id: str
    artifact: str
    rule: str
    wrong: str
    original: str
    improved: str = ""
    status: str = "open"
    when: str = ""
    tool: str = ""
    fidelity: str = ""

    @staticmethod
    def _block(text: str) -> str:
        return "\n".join(
            f"  {line}"
            for line in text.replace("\r\n", "\n").rstrip("\n").split("\n")
        )

    def render(self) -> str:
        """Render this entry as one ``--- ... ---`` mistakes.log block."""
        return (
            "---\n"
            f"id: {self.entry_id.strip()}\n"
            f"when: {self.when.strip() or date.today().isoformat()}\n"
            f"artifact: {self.artifact.strip()}\n"
            f"rule: {self.rule.strip()}\n"
            f"wrong: {' '.join(self.wrong.strip().splitlines())}\n"
            "original: |\n"
            f"{self._block(self.original)}\n"
            "improved: |\n"
            f"{self._block(self.improved)}\n"
            f"status: {self.status.strip() or 'open'}\n"
            f"tool: {self.tool.strip()}\n"
            f"fidelity: {self.fidelity.strip()}\n"
            "---\n"
        )


class MistakeLog:
    """Append-only ``mistakes.log`` for one sprint folder. Parses its own
    entries back so ``archive`` can name the destination from whichever
    tool/fidelity actually produced them."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def append(self, entry: MistakeEntry) -> Path:
        """Append *entry*; write the header block on first write only."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.is_file():
            sprint = self.path.parent.name or "session"
            self.path.write_text(_LOG_HEADER.format(sprint=sprint), encoding="utf-8")
        existing = self.path.read_text(encoding="utf-8")
        sep = "" if existing.endswith("\n\n") else "\n" if existing.endswith("\n") else "\n\n"
        self.path.write_text(existing + sep + entry.render(), encoding="utf-8")
        return self.path.resolve()

    def complete(self, entry_id: str, improved: str, status: str = "fixed") -> Path:
        """Complete the open entry matching *entry_id* with its correction.
        Rewrites the log in place - never appends a second entry for the
        same mistake. Raises when no entry matches *entry_id*."""
        entries = self.parse()
        if not any(entry.entry_id == entry_id for entry in entries):
            raise ValueError(f"No logged mistake with id {entry_id!r} in {self.path}")
        updated = [
            replace(entry, improved=improved, status=status)
            if entry.entry_id == entry_id
            else entry
            for entry in entries
        ]
        sprint = self.path.parent.name or "session"
        header = _LOG_HEADER.format(sprint=sprint)
        self.path.write_text(
            header + "\n".join(entry.render() for entry in updated), encoding="utf-8"
        )
        return self.path.resolve()

    def parse(self) -> list[MistakeEntry]:
        """Read every ``--- ... ---`` block back into a ``MistakeEntry``."""
        if not self.path.is_file():
            return []
        entries: list[MistakeEntry] = []
        for raw_block in self.path.read_text(encoding="utf-8").split("---\n"):
            block = raw_block.strip("\n")
            if not block or "artifact:" not in block:
                continue
            fields = self._parse_block(block)
            entries.append(
                MistakeEntry(
                    entry_id=fields.get("id", ""),
                    artifact=fields.get("artifact", ""),
                    rule=fields.get("rule", ""),
                    wrong=fields.get("wrong", ""),
                    original=fields.get("original", ""),
                    improved=fields.get("improved", ""),
                    status=fields.get("status", "open"),
                    when=fields.get("when", ""),
                    tool=fields.get("tool", ""),
                    fidelity=fields.get("fidelity", ""),
                )
            )
        return entries

    @staticmethod
    def _parse_block(block: str) -> dict[str, str]:
        """Parse one entry block's ``key: value`` and ``key: |`` lines (pure)."""
        fields: dict[str, str] = {}
        lines = block.split("\n")
        index = 0
        while index < len(lines):
            line = lines[index]
            if not line or line.startswith("  ") or ":" not in line:
                index += 1
                continue
            key, _, rest = line.partition(":")
            key, rest = key.strip(), rest.strip()
            if rest != "|":
                fields[key] = rest
                index += 1
                continue
            index += 1
            collected: list[str] = []
            while index < len(lines) and (not lines[index] or lines[index].startswith("  ")):
                collected.append(lines[index][2:] if lines[index].startswith("  ") else "")
                index += 1
            fields[key] = "\n".join(collected).rstrip("\n")
        return fields

    def distinct_tags(self) -> tuple[str, str]:
        """One ``(tool, fidelity)`` slug pair for archive naming.

        Each half falls back independently to the session name (this log's
        own parent folder, kebab turned to snake) when its own entries
        disagree or are blank - never guesses one recorded value over another.
        """
        entries = self.parse()
        session_slug = (self.path.parent.name or "session").replace("-", "_")
        tools = {entry.tool for entry in entries if entry.tool}
        fidelities = {entry.fidelity for entry in entries if entry.fidelity}
        tool = next(iter(tools)).lower() if len(tools) == 1 else session_slug
        fidelity = next(iter(fidelities)) if len(fidelities) == 1 else session_slug
        return tool, fidelity

    def archive(self, repo_root: str) -> Path:
        """Move (never copy) this log to
        ``{repo_root}/.context/archive/repairs/{tool}-{fidelity}-{date}.log``.
        Writes the destination before deleting the source - never delete-then-write."""
        tool, fidelity = self.distinct_tags()
        slug = tool if tool == fidelity else f"{tool}-{fidelity}"
        destination = (
            Path(repo_root)
            / ".context"
            / "archive"
            / "repairs"
            / f"{slug}-{date.today().isoformat()}.log"
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.path.read_text(encoding="utf-8"), encoding="utf-8")
        self.path.unlink()
        return destination.resolve()


@dataclass
class RegressionExample:
    """One captured ``faultyAsset``/``repairedAsset`` fixture pair under a
    tool's own ``examples/`` tree."""

    folder: Path

    def _paths(self, single_name: str, plural_name: str) -> list[Path]:
        single = self.folder / single_name
        if single.is_file():
            return [single]
        extensioned = sorted(self.folder.glob(f"{single_name}.*"))
        if extensioned:
            return extensioned
        plural = self.folder / plural_name
        if plural.is_dir():
            return sorted(path for path in plural.rglob("*") if path.is_file())
        return []

    @property
    def faulty_paths(self) -> list[Path]:
        return self._paths("faultyAsset", "faultyAssets")

    @property
    def repaired_paths(self) -> list[Path]:
        return self._paths("repairedAsset", "repairedAssets")

    @property
    def rule(self) -> str:
        """The rule slug this example exercises - the folder name by default.

        A folder name does not always equal its scanner's registered rule
        slug: two folders can deliberately share one rule (e.g. one scanner
        with two independent fixture cases). Such a folder carries a
        ``rule.txt`` sidecar naming the real slug instead of relying on a
        name match that cannot hold for both folders at once."""
        override = self.folder / "rule.txt"
        if override.is_file():
            return override.read_text(encoding="utf-8").strip()
        return self.folder.name

    def _is_clean(self, scanner: Scan, paths: list[Path]) -> bool | None:
        """None when there is nothing to scan on this side of the pair.

        ``root`` is pinned to this example's own folder - never ``cwd`` - so a
        graph-wide scanner (``StoryWorkspaceScanner``) loads just this fixture,
        not the whole repo. ``rule`` scopes the verdict to the one rule this
        fixture exercises, so an incomplete fixture snippet is judged only
        against its own rule, not every other registered scanner too."""
        if not paths:
            return None
        # Absolute paths on both sides - some scanners join non-absolute
        # ``files`` onto ``root``, and since these fixture paths already
        # start with the same folder as ``root``, a relative join would
        # double the prefix into a path that does not exist.
        report = ast.literal_eval(
            scanner.scan(
                [str(path.resolve()) for path in paths],
                root=str(self.folder.resolve()),
                rule=self.rule,
            )
        )
        return bool(report.get("ok"))

    def verify(self, scanner: Scan) -> dict[str, Any]:
        """Faulty paths must still violate scan; repaired paths must still be clean."""
        faulty_still_violates = self._is_clean(scanner, self.faulty_paths) is False
        repaired_still_clean = self._is_clean(scanner, self.repaired_paths) is True
        return {
            "name": self.folder.name,
            "passed": faulty_still_violates and repaired_still_clean,
            "faulty_still_violates": faulty_still_violates,
            "repaired_still_clean": repaired_still_clean,
        }


@dataclass
class RegressionReport:
    """Regression run across one tool's own ``examples_root`` - never repo-wide."""

    examples_root: Path
    results: list[dict[str, Any]] = field(default_factory=list)

    def verify_examples(self, scanner: Scan) -> "RegressionReport":
        root = Path(self.examples_root)
        folders = sorted(path for path in root.iterdir() if path.is_dir()) if root.is_dir() else []
        self.results = [RegressionExample(folder).verify(scanner) for folder in folders]
        return self

    def summary(self) -> str:
        total = len(self.results)
        if total == 0:
            return f"No regression examples found under {self.examples_root}."
        failed = [result for result in self.results if not result["passed"]]
        if not failed:
            return f"Regression clean: {total}/{total} example(s) still hold."
        names = ", ".join(result["name"] for result in failed)
        return f"Regression FAILED for {len(failed)}/{total} example(s): {names}."


@agentic_toolset
class Repair:
    """Records mistake entries, runs the root-cause repair loop, checks
    regression across a tool's own examples, and archives a closed log."""

    def __init__(self, workspace, scanner: Scan | None = None) -> None:
        self.workspace = workspace
        self.scanner = scanner or Scan()

    @tool
    def log_mistake(
        self,
        artifact: str,
        rule: str,
        wrong: str,
        original: str,
        when: str = "",
        tool: str = "",
        fidelity: str = "",
    ) -> str:
        """Log a mistake the moment it is spotted - before any fix exists.
        Returns the entry_id; pass it to log_correction once the fix lands,
        so several mistakes can stay open at once without being conflated.
        ``tool``/``fidelity`` name whichever context tool and fidelity
        produced this entry - hosts auto-inject both; do not ask the
        calling agent for them."""
        entry = MistakeEntry(
            entry_id=uuid.uuid4().hex[:8],
            artifact=artifact,
            rule=rule,
            wrong=wrong,
            original=original,
            when=when,
            tool=tool,
            fidelity=fidelity,
        )
        MistakeLog(self.workspace.folder / "mistakes.log").append(entry)
        return entry.entry_id

    @tool
    def log_correction(self, entry_id: str, improved: str, status: str = "fixed") -> str:
        """Complete a previously logged mistake once its fix lands.
        entry_id is whatever log_mistake returned - never open a new entry
        for the same mistake."""
        path = MistakeLog(self.workspace.folder / "mistakes.log").complete(
            entry_id, improved, status
        )
        return str(path)

    @sub_agent
    @action
    def repair(self, asset: str, violation: str) -> str:
        """repair"""
        return "Repair {{asset}} under {session.path}/ until validate passes."

    @sub_agent
    @tool
    def verify_regression(self, examples_root: str) -> str:
        """Re-scan every faultyAsset/repairedAsset pair directly under
        examples_root (one tool's own examples/ tree - never repo-wide).
        Every faultyAsset(s) file must still violate scan; every
        repairedAsset(s) file must still be clean. Returns the pass/fail summary."""
        report = RegressionReport(Path(examples_root)).verify_examples(self.scanner)
        return report.summary()

    @sub_agent
    @tool
    def archive_mistakes(self, repo_root: str) -> str:
        """Move (never copy) {session.folder}/mistakes.log to
        {repo_root}/.context/archive/repairs/{tool}-{fidelity}-{date}.log,
        tagged from every entry's recorded tool/fidelity - falling back to
        the session name when entries disagree."""
        destination = MistakeLog(self.workspace.folder / "mistakes.log").archive(repo_root)
        return str(destination)

    @action
    def improve(self) -> str:
        """improve"""
        self.log_mistake(artifact="", rule="", wrong="", original="")
        self.log_correction(entry_id="", improved="")
        self.mode = "tool"
        self.repair(asset="", violation="")
        return "Read the roadmap above before this session forgets it."
