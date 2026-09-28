"""Knowledge graph file change — model fidelity (Python channel).

Stubs only. Same types as knowledge-graph-file-change-sketch.md.
Does not replace harness/session, hook_server, or live graph modules.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


class Session:
    """Holds the in-memory KnowledgeGraph and each PracticeGuidance for one process."""

    # must live in harness/session — never WorkSession, never session_logs
    # never owns CodeQL databases
    # knowledge_graph and practices instantiate on first get; setter replaces; reset clears both

    @property
    def knowledge_graph(self) -> KnowledgeGraph:
        # first get instantiates; later gets return the same object until reset or setter
        ...

    @knowledge_graph.setter
    def knowledge_graph(self, graph: KnowledgeGraph) -> None:
        ...

    @property
    def practices(self) -> dict[str, PracticeGuidance]:
        # first get instantiates one PracticeGuidance per practice
        # never AgentToolSet.load_toolsets
        ...

    @practices.setter
    def practices(self, practices: dict[str, PracticeGuidance]) -> None:
        ...

    def reset(self) -> None:
        # set graph and practices to nothing; next get instantiates again
        ...


class HookServer:
    """Long-lived daemon that holds one Session across Cursor hook runs."""

    # never own the graph or the practices as fields beside Session
    # hook_server.py per Cursor event is the CLI client onto this daemon

    session: Session

    def ensure(self) -> HookServer:
        # same ensure/spawn pattern as the CodeQL query daemon
        ...


class McpServer:
    """MCP process with its own Session — not the hook daemon's Session."""

    session: Session


class KnowledgeGraph:
    """Aggregate of practice graphs. Always reads the working copy — never master."""

    # never a classify.ql
    # never CodeQL.populate as the public seam

    practice_graphs: list[PracticeGraph]
    # always the working copy

    def update_working_copy(self, paths: list[Path]) -> KnowledgeGraph:
        # extract those paths onto the working copy; never rewrite master
        # -> CodeQL.populate
        ...

    def refresh_master(self) -> KnowledgeGraph:
        # rewrite master, populate master, then copy master to working copy
        # never update_working_copy for this job
        # -> CodeQL.populate
        ...

    def reload_working_copy(self) -> KnowledgeGraph:
        # reload the working copy from the tree, populate from it, copy working copy to master
        # never refresh_master for this job
        # -> CodeQL.populate
        ...

    def create_database(self, root: Path) -> KnowledgeGraph:
        # set the path to that repo
        # write master in that repo, copy master to working copy
        # never populate for this job
        ...

    def filter_graph(self, dirty: list[Path], violations: bool) -> KnowledgeGraph:
        # dirty paths ∩ nodes with node.rules.violations
        # keep ancestors; drop passing siblings
        # never a report file as the hook contract
        ...


class PracticeGraph:
    """One practice tree inside the knowledge graph."""

    root: Any
    nodes: dict[str, Any]
    # node.rules.violations is the source of truth


class PracticeGuidance:
    """A practice. rules is a GraphRulesCollection."""

    def rules(self) -> GraphRulesCollection:
        # override Guidance.rules
        ...


class FidelityGuidance:
    """One fidelity of a practice. rules is a GraphRulesCollection."""

    def rules(self) -> GraphRulesCollection:
        # override Guidance.rules
        ...


class Validate:
    """Walks Guidance; never hand-loops the rule catalog."""

    def validate(self, guidance: Any, rule: Rule | None = None) -> str:
        # -> GuidanceAction.run guidance
        # when rule is omitted -> item.rules.validate
        # when rule is passed -> rule.validate once; no collection walk; no slug lookup
        ...


class RulesCollection:
    """Markdown rule bag. Inject stays here — never CodeQL."""

    def inject_rules(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        # @Hook("postToolUse")
        # -> matches path
        # -> additional_context markdown
        ...

    @classmethod
    def from_markdown(cls, text: str) -> RulesCollection:
        ...

    def validate(self) -> str:
        # @collect of Rule.validate — agent instructions, not CodeQL
        ...


class GraphRulesCollection(RulesCollection):
    """Mixed bag: GraphRule where a .ql exists, Rule otherwise. Do not add evaluate."""

    # do not override matches yet for inject — glob channel stays on RulesCollection

    def notice_changed_file(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        # @Hook("stop") — payload has no paths
        # dirty paths vs master
        # -> KnowledgeGraph.update_working_copy
        # -> validate  (CodeQL on the working copy; write node.rules.violations)
        # -> session.knowledge_graph.filter_graph dirty violations
        ...

    def present_violations(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        # @echo
        # @Hook("stop") — after notice_changed_file on the same daemon Session
        # followup_message from those objects + instructions
        # -> PromptEcho.show_ide_toast  (violations + count; no toast when empty)
        ...

    def validate(self) -> str:
        # inherited @collect — GraphRule.validate or Rule.validate per entry
        # -> node.rules.violations
        ...


class CodeQL:
    """Database and query runner. Master and working copy are two folders, one populate."""

    master: Path
    # .codeql/{language}-master — written by refresh_master and reload_working_copy
    # never extract dirty files onto this folder
    # never --expect-discarded-cache on master

    working_copy: Path
    # .codeql/{language}-working-copy — the only database KnowledgeGraph reads
    # copied from master in refresh_master; copied onto master in reload_working_copy
    # never copy master on each edit

    def populate(self, graph: PracticeGraph, database: Path) -> None:
        # one operation; database is master or working copy
        # same fact queries either way
        # never the KnowledgeGraph seam
        # never a parallel classify.ql
        # never AppliesTo.globs
        ...

    def run(self, query: Path) -> Any:
        ...

    def copy_working_copy_to_master(self) -> Path:
        # reload_working_copy: copy the reloaded working copy onto master
        ...

    def ensure_database(self, language: str = "python") -> Path:
        # update_working_copy: working copy + dirty-file extract
        # refresh_master: rewrite master, populate master, copy to working copy
        # reload_working_copy: reload working copy, populate it, copy to master
        # never OverlayManager / OverlayDatabase
        ...


class GraphRule(Rule):
    """A rule with an optional graph query. Same validate verb as Rule. Do not add evaluate."""

    practice: str
    applies_to: set[str]
    # node types from FIDELITY_NODE_SCOPE — already on the Node

    def validate(self) -> str:
        # -> CodeQL.run graphQuery when .ql exists
        # -> Rule.validate when it does not
        # -> node.rules.violations
        ...


class Rule:
    def validate(self) -> str:
        ...


class RuleViolation:
    rule_slug: str
    message: str
    practice: str
    location: str
    line: int
    node_id: str


class PromptEcho:
    def show_ide_toast(self, message: str, roots: Any = None) -> None:
        ...
