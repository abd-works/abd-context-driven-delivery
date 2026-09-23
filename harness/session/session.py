"""Session — in-memory knowledge graph and practice guidance for one process."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.guidance.guidance import PracticeGuidance
    from harness.knowledge_graph.model.knowledge_graph import KnowledgeGraph


class Session:
    """Holds the in-memory KnowledgeGraph and each PracticeGuidance for one process."""

    def __init__(self) -> None:
        self._knowledge_graph = None
        self._practices = None

    @property
    def knowledge_graph(self):
        if self._knowledge_graph is None:
            from harness.knowledge_graph.model.knowledge_graph import KnowledgeGraph

            self._knowledge_graph = KnowledgeGraph()
        return self._knowledge_graph

    @knowledge_graph.setter
    def knowledge_graph(self, graph) -> None:
        self._knowledge_graph = graph

    @property
    def practices(self) -> dict[str, PracticeGuidance]:
        if self._practices is None:
            self._practices = self._instantiate_practices()
        return self._practices

    @practices.setter
    def practices(self, practices) -> None:
        self._practices = practices

    def reset(self) -> None:
        self._knowledge_graph = None
        self._practices = None

    def _instantiate_practices(self) -> dict[str, PracticeGuidance]:
        from practices.bdd.bdd import Bdd
        from practices.clean_engineering.clean_engineering import CleanEngineering
        from practices.ddd.ddd import Ddd
        from practices.stories.stories import Stories
        from practices.ux.ux import Ux

        return {
            "stories": Stories(),
            "clean_engineering": CleanEngineering(),
            "ddd": Ddd(),
            "bdd": Bdd(),
            "ux": Ux(),
        }
