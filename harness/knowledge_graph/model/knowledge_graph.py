from __future__ import annotations

from pathlib import Path

from harness.knowledge_graph.model.codeql import CodeQL
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
    filter: object
    matching: object
    selected: object
    expanded: object

    def __init__(self, storyModel=None, ceModel=None, domainDrivenDesignModel=None, description=None) -> None:
        self.storyModel = KnowledgeGraphStoryModel(storyModel)
        self.ceModel = KnowledgeGraphCleanEngineeringModel(ceModel)
        self.domainDrivenDesignModel = KnowledgeGraphDomainDrivenDesignModel(
            domainDrivenDesignModel
        )
        self.description = KnowledgeGraphDescription(description)
        self.nodes = []
        self.kinds = []
        self.folder = None
        self.filter = []
        self.matching = []
        self.selected = None
        self.expanded = []
        self._codeql = None

    def saveKnowledgeGraph(self) -> None:
        folder = Path(self.folder)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "story-map.kg").write_text(self.storyModel.save() or "", encoding="utf-8")
        (folder / "class-model.kg").write_text(self.ceModel.save() or "", encoding="utf-8")
        (folder / "bounded-context-map.kg").write_text(
            self.domainDrivenDesignModel.save() or "", encoding="utf-8"
        )
        (folder / "description.kg").write_text(self.description.save() or "", encoding="utf-8")
        self._collect_nodes()

    def loadKnowledgeGraph(self, path) -> None:
        self.folder = path
        folder = Path(path)
        self.storyModel = KnowledgeGraphStoryModel().load(folder)
        self.ceModel = KnowledgeGraphCleanEngineeringModel().load(folder)
        self.domainDrivenDesignModel = KnowledgeGraphDomainDrivenDesignModel().load(folder)
        self.description = KnowledgeGraphDescription().load(folder)
        self._collect_nodes()

    def createDatabase(self) -> None:
        ql = CodeQL(Path(self.folder))
        language = ql.detect_language()
        ql.rewrite_master(language)
        ql.copy_master_to_working_copy()
        self._codeql = ql

    def copyMasterToWorkingCopy(self) -> None:
        ql = self._ql()
        if Path(ql.master).exists():
            ql.copy_master_to_working_copy()

    def copyWorkingCopyToMaster(self) -> None:
        ql = self._ql()
        if Path(ql.working_copy).exists():
            ql.copy_working_copy_to_master()

    def refreshMaster(self) -> None:
        self.copyWorkingCopyToMaster()
        self.saveKnowledgeGraph()
        self.loadKnowledgeGraph(self.folder)

    def reloadWorkingCopy(self) -> None:
        self.saveKnowledgeGraph()
        self.copyWorkingCopyToMaster()
        self.loadKnowledgeGraph(self.folder)

    def updateWorkingCopy(self, paths) -> None:
        self._ql().extract_working_copy([Path(item) for item in paths])
        self.saveKnowledgeGraph()
        self.loadKnowledgeGraph(self.folder)

    def choose(self, node) -> None:
        self.selected = node

    def open(self, node) -> None:
        if node not in self.expanded:
            self.expanded.append(node)

    def close(self, node) -> None:
        self.expanded = [item for item in self.expanded if item is not node]

    def _ql(self) -> CodeQL:
        if self._codeql is None:
            self._codeql = CodeQL(Path(self.folder))
            self._codeql._database_language = self._codeql.detect_language()
        return self._codeql

    def _collect_nodes(self) -> None:
        self.nodes = []
        for epic in getattr(self.storyModel, "epics", []):
            node = KnowledgeGraphNode()
            node.name = epic.name
            node.nodeId = epic.name
            self.nodes.append(node)
        for module in getattr(self.ceModel, "modules", []):
            node = KnowledgeGraphNode()
            node.name = module.name
            node.nodeId = module.name
            self.nodes.append(node)
        self.matching = list(self.nodes)
