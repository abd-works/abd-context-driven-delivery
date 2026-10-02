from __future__ import annotations

from harness.knowledge_graph.model.knowledge_graph_node import (
    KnowledgeGraphCall,
    KnowledgeGraphCallSource,
    KnowledgeGraphEdge,
    KnowledgeGraphEdgeType,
    KnowledgeGraphFilter,
    KnowledgeGraphNode,
    KnowledgeGraphNodeType,
    KnowledgeGraphPanel,
    KnowledgeGraphSource,
    KnowledgeGraphSourceFold,
    NodeFilter,
    NodeRules,
    PracticeFilter,
    PracticeGraph,
    RelationshipFilter,
    RuleFilter,
    RuleHit,
    RuleSetFilter,
    SourceRange,
    StageFilter,
    WebKnowledgeGraphNode,
    WorkspaceFile,
)
from practices.bdd.model.knowledge_graph.nodes import KnowledgeGraphDescription
from practices.clean_engineering.model.knowledge_graph.nodes import KnowledgeGraphCleanEngineeringModel
from practices.ddd.model.knowledge_graph.nodes import KnowledgeGraphDomainDrivenDesignModel
from practices.stories.model.knowledge_graph.nodes import KnowledgeGraphStoryModel


class KnowledgeGraph:
    storyModel: object
    ceModel: object
    domainDrivenDesignModel: object
    description: object
    nodes: object
    kinds: object
    folder: object
    createDatabase: object
    copyMasterToWorkingCopy: object
    copyWorkingCopyToMaster: object
    filter: object
    matching: object
    selected: object
    expanded: object

    def __init__(self, storyModel, ceModel, domainDrivenDesignModel, description) -> None: ...

    def saveKnowledgeGraph(self) -> None: ...

    def loadKnowledgeGraph(self, path) -> None: ...

    def refreshMaster(self) -> None: ...

    def reloadWorkingCopy(self) -> None: ...

    def updateWorkingCopy(self, paths) -> None: ...
