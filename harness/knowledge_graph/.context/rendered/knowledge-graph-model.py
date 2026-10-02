from __future__ import annotations


# === KnowledgeGraph ===



class CodeQL:
    root: object
    database: object

    def __init__(self, root, database) -> None: ...

    def populate(self, ) -> None: ...

class StoryModel:
    pass

class CleanEngineeringModel:
    pass

class DomainDrivenDesignModel:
    pass

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

    def saveKnowledgeGraph(self, ) -> None: ...

    def loadKnowledgeGraph(self, path) -> None: ...

    def refreshMaster(self, ) -> None: ...

    def reloadWorkingCopy(self, ) -> None: ...

    def updateWorkingCopy(self, paths) -> None: ...

class KnowledgeGraphNodeType:
    name: object
    practice: object
    stage: object
    edgeTypes: object

    def __init__(self, name, practice, stage, edgeTypes) -> None: ...

class KnowledgeGraphEdgeType:
    name: object
    fromType: object
    toType: object
    inverse: object
    cardinality: object

    def __init__(self, name, fromType, toType, inverse, cardinality) -> None: ...

class KnowledgeGraphNode:
    name: object
    sequentialOrder: object
    nodeType: object
    source: object
    nodeId: object
    edges: object
    panel: object
    rules: object

    def __init__(self, ) -> None: ...

    def navigateTo(self, edge) -> None: ...

class KnowledgeGraphSource:
    text: object
    file: object
    startLine: object
    endLine: object
    language: object

    def __init__(self, text, file, startLine, endLine, language) -> None: ...

    def source(self, ) -> None: ...

class KnowledgeGraphCallSource(KnowledgeGraphSource):
    """KnowledgeGraphSource"""

    calls: object
    folds: object
    loadCalls: object
    insertCalls: object
    loadFolds: object

    def __init__(self, calls, folds, loadCalls, insertCalls, loadFolds) -> None: ...

    def source(self, ) -> None: ...

class KnowledgeGraphCall:
    line: object
    sequentialOrder: object
    operation: object

    def __init__(self, line, sequentialOrder, operation) -> None: ...

class KnowledgeGraphSourceFold:
    start: object
    end: object
    kind: object

    def __init__(self, start, end, kind) -> None: ...

class KnowledgeGraphPanel:
    source: object
    language: object
    open: object
    theme: object
    mount: object

    def __init__(self, source, language, open, theme, mount) -> None: ...

class KnowledgeGraphEdge:
    edgeType: object
    from: object
    to: object

    def __init__(self, edgeType, from, to) -> None: ...

class KnowledgeGraphStoryModel(StoryModel, KnowledgeGraphNode):
    """StoryModel : KnowledgeGraphNode"""

    epicType: object
    incrementType: object

    def __init__(self, source) -> None: ...

    def save(self, saves, a, complete, knowledge, graph) -> None: ...

    def load(self, path) -> None: ...

class KnowledgeGraphIncrement(Increment, KnowledgeGraphNode):
    """Increment : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphEpic(Epic, KnowledgeGraphNode):
    """Epic : KnowledgeGraphNode"""

    storyType: object

    def __init__(self, source) -> None: ...

class KnowledgeGraphStory(Story, KnowledgeGraphNode):
    """Story : KnowledgeGraphNode"""

    scenarioType: object

    def __init__(self, source) -> None: ...

class KnowledgeGraphScenario(Scenario, KnowledgeGraphNode):
    """Scenario : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphBackground(Background, KnowledgeGraphNode):
    """Background : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphStep(Step, KnowledgeGraphNode):
    """Step : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphExample(Example, KnowledgeGraphNode):
    """Example : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphCleanEngineeringModel(CleanEngineeringModel, KnowledgeGraphNode):
    """CleanEngineeringModel : KnowledgeGraphNode"""

    moduleType: object
    save: object

    def __init__(self, source) -> None: ...

    def load(self, path) -> None: ...

class KnowledgeGraphModule(Module, KnowledgeGraphNode):
    """Module : KnowledgeGraphNode"""

    classType: object

    def __init__(self, source) -> None: ...

class KnowledgeGraphOoadClass(OoadClass, KnowledgeGraphNode):
    """OoadClass : KnowledgeGraphNode"""

    propertyType: object
    operationType: object
    relationshipType: object

    def __init__(self, source) -> None: ...

class KnowledgeGraphProperty(Property, KnowledgeGraphNode):
    """Property : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphRelationship(Relationship, KnowledgeGraphNode):
    """Relationship : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphOperation(Operation, KnowledgeGraphNode):
    """Operation : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphParameter(Parameter, KnowledgeGraphNode):
    """Parameter : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphDomainDrivenDesignModel(DomainDrivenDesignModel, KnowledgeGraphNode):
    """DomainDrivenDesignModel : KnowledgeGraphNode"""

    boundedContextType: object
    save: object

    def __init__(self, source) -> None: ...

    def load(self, path) -> None: ...

class KnowledgeGraphBoundedContext(BoundedContext, KnowledgeGraphNode):
    """BoundedContext : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphAggregate(Aggregate, KnowledgeGraphNode):
    """Aggregate : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphEntity(Entity, KnowledgeGraphNode):
    """Entity : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphEntityRoot(Entity, KnowledgeGraphNode):
    """Entity : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphValueObject(ValueObject, KnowledgeGraphNode):
    """ValueObject : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphRepository(Repository, KnowledgeGraphNode):
    """Repository : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphDomainEvent(DomainEvent, KnowledgeGraphNode):
    """DomainEvent : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphDomainService(DomainService, KnowledgeGraphNode):
    """DomainService : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphSpecification(Specification, KnowledgeGraphNode):
    """Specification : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphDescription(Description, KnowledgeGraphNode):
    """Description : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphContext(Context, KnowledgeGraphNode):
    """Context : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphObservation(Observation, KnowledgeGraphNode):
    """Observation : KnowledgeGraphNode"""

    def __init__(self, source) -> None: ...

class KnowledgeGraphFilter:
    type: object
    selected: object
    available: object

    def __init__(self, practices) -> None: ...

class PracticeFilter(KnowledgeGraphFilter):
    """KnowledgeGraphFilter"""

    selected: object
    available: object

    def __init__(self, selected, available) -> None: ...

class StageFilter(KnowledgeGraphFilter):
    """KnowledgeGraphFilter"""

    selected: object

    def __init__(self, selected) -> None: ...

    def available(self, practices) -> None: ...

class NodeFilter(KnowledgeGraphFilter):
    """KnowledgeGraphFilter"""

    selected: object

    def __init__(self, selected) -> None: ...

    def available(self, practices, stages) -> None: ...

class RelationshipFilter(KnowledgeGraphFilter):
    """KnowledgeGraphFilter"""

    selected: object

    def __init__(self, selected) -> None: ...

    def available(self, nodes) -> None: ...

class RuleSetFilter(KnowledgeGraphFilter):
    """KnowledgeGraphFilter"""

    selected: object
    available: object

    def __init__(self, selected, available) -> None: ...

class RuleFilter(KnowledgeGraphFilter):
    """KnowledgeGraphFilter"""

    selected: object

    def __init__(self, selected) -> None: ...

    def available(self, nodes) -> None: ...

class WebKnowledgeGraphNode(KnowledgeGraphNode):
    """KnowledgeGraphNode"""

    keyword: object
    origin: object
    properties: object
    isFile: object
    isFolder: object

    def __init__(self, keyword, origin, properties, isFile, isFolder) -> None: ...

class PracticeGraph:
    id: object
    name: object
    nodes: object
    relationships: object

    def __init__(self, id, name, nodes, relationships) -> None: ...

class SourceRange:
    file: object
    startLine: object
    endLine: object
    text: object

    def __init__(self, file, startLine, endLine, text) -> None: ...

class RuleHit:
    ruleSlug: object
    message: object
    body: object
    practice: object
    fidelity: object
    tag: object

    def __init__(self, ruleSlug, message, body, practice, fidelity, tag) -> None: ...

class NodeRules:
    applicable: object
    violations: object
    statuses: object
    details: object
    tally: object

    def __init__(self, applicable, violations, statuses, details, tally) -> None: ...

    def status(self, ruleSlug) -> None: ...

    def hasRule(self, ruleSlug) -> None: ...

class WorkspaceFile:
    relativePath: object
    text: object

    def __init__(self, relativePath, text) -> None: ...
