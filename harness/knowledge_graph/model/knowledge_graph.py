"""KnowledgeGraph — aggregate of practice graphs; always the working copy."""

from __future__ import annotations

from pathlib import Path
from typing import List

from .practice_graph import PracticeGraph


class KnowledgeGraph:
    """Always reads the working copy — never master."""

    def __init__(
        self,
        practice_graphs: List[PracticeGraph] | None = None,
        root: Path | None = None,
    ) -> None:
        self._practice_graphs = list(practice_graphs or [])
        self._root = Path(root) if root is not None else None

    @property
    def root(self) -> Path:
        if self._root is not None:
            return self._root
        if self._practice_graphs:
            return self._practice_graphs[0].root
        return Path.cwd()

    @property
    def practice_graphs(self) -> List[PracticeGraph]:
        return list(self._practice_graphs)

    def refresh_master(self) -> KnowledgeGraph:
        from .codeql import CodeQL
        from .practice_graph import PracticeGraph

        codeql = CodeQL(self.root)
        master = codeql.rewrite_master()
        graph = PracticeGraph(self.root)
        codeql.populate(graph, database=master, results_path=master / "practice-graph.json")
        codeql.copy_master_to_working_copy()
        self._practice_graphs = [graph]
        return self

    def update_working_copy(self, paths: list[Path]) -> KnowledgeGraph:
        from .codeql import CodeQL
        from .practice_graph import PracticeGraph

        codeql = CodeQL(self.root)
        working = codeql.extract_working_copy(list(paths))
        graph = PracticeGraph(self.root)
        codeql.populate(
            graph,
            database=working,
            results_path=working / "practice-graph.json",
        )
        from .loader import attach_story_tests

        attach_story_tests(graph, list(paths))
        self._practice_graphs = [graph]
        return self

    def validate(self, rule=None) -> KnowledgeGraph:
        from .codeql import CodeQL
        from .practice_graph import RuleSlugs

        slugs = RuleSlugs([rule.slug]) if rule is not None else None
        working = CodeQL(self.root).working_copy
        instructions: list[str] = []
        for graph in self._practice_graphs:
            graph.evaluate_rules(slugs=slugs, database=working)
            instructions.extend(self._markdown_instructions(graph, rule))
        self.markdown_instructions = "\n".join(instructions)
        return self

    def _markdown_instructions(self, graph, rule) -> list[str]:
        texts: list[str] = []
        for item in graph.rule_registry.rules:
            if rule is not None and item.slug != rule.slug:
                continue
            if getattr(item, "graphQuery", None) is not None:
                continue
            texts.append(item.validate())
        return texts
