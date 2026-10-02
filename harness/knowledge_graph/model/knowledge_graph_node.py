"""Shared knowledge-graph channel types. Practice subtypes live under each practice model."""

from __future__ import annotations


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

    def __init__(self) -> None: ...

    def navigateTo(self, edge) -> None: ...


class KnowledgeGraphSource:
    text: object
    file: object
    startLine: object
    endLine: object
    language: object

    def __init__(self, text, file, startLine, endLine, language) -> None: ...

    def source(self) -> None: ...


class KnowledgeGraphCallSource(KnowledgeGraphSource):
    calls: object
    folds: object
    loadCalls: object
    insertCalls: object
    loadFolds: object

    def __init__(self, calls, folds, loadCalls, insertCalls, loadFolds) -> None: ...

    def source(self) -> None: ...


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
    from_node: object
    to: object

    def __init__(self, edgeType, from_node, to) -> None: ...


class KnowledgeGraphFilter:
    type: object
    selected: object
    available: object

    def __init__(self, practices) -> None: ...


class PracticeFilter(KnowledgeGraphFilter):
    selected: object
    available: object

    def __init__(self, selected, available) -> None: ...


class StageFilter(KnowledgeGraphFilter):
    selected: object

    def __init__(self, selected) -> None: ...

    def available(self, practices) -> None: ...


class NodeFilter(KnowledgeGraphFilter):
    selected: object

    def __init__(self, selected) -> None: ...

    def available(self, practices, stages) -> None: ...


class RelationshipFilter(KnowledgeGraphFilter):
    selected: object

    def __init__(self, selected) -> None: ...

    def available(self, nodes) -> None: ...


class RuleSetFilter(KnowledgeGraphFilter):
    selected: object
    available: object

    def __init__(self, selected, available) -> None: ...


class RuleFilter(KnowledgeGraphFilter):
    selected: object

    def __init__(self, selected) -> None: ...

    def available(self, nodes) -> None: ...


class WebKnowledgeGraphNode(KnowledgeGraphNode):
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
