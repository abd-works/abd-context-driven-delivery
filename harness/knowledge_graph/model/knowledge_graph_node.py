"""Shared knowledge-graph channel types. Practice subtypes live under each practice model."""

from __future__ import annotations

import re

PRACTICE_STAGES = {
    "Stories": ["Discovery"],
    "CleanEngineering": ["Specification", "Implementation"],
    "Ddd": ["Specification"],
    "Bdd": ["Specification"],
}

PRACTICE_NODES = {
    "Stories": {
        "Discovery": ["Increment", "Epic", "Story", "Scenario", "Background", "Step", "Example"],
    },
    "CleanEngineering": {
        "Specification": ["OoadClass", "Property", "Relationship", "Operation", "Parameter"],
        "Implementation": ["Module"],
    },
    "Ddd": {
        "Specification": ["BoundedContext", "Aggregate", "Entity", "EntityRoot", "ValueObject"],
    },
    "Bdd": {
        "Specification": ["Description", "Context", "Observation"],
    },
}

NODE_EDGES = {
    "Epic": ["owns"],
    "Story": ["owns", "demonstrates"],
    "OoadClass": ["composition", "aggregation", "associates", "invokes"],
    "Operation": ["invokes", "hasParameter", "returns"],
    "Property": ["hasType"],
}

NODE_RULES = {
    "OoadClass": ["keep-operations-small-focused"],
    "Operation": ["keep-operations-small-focused"],
    "Property": ["hide-inner-details"],
}

_CALL = re.compile(r"((?:[A-Z][A-Za-z0-9]*\.)?[A-Za-z_][A-Za-z0-9]*)\s*\(")
_STEP_CALL = re.compile(r"\.([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_STEP_EXAMPLE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*Examples?)\b")
_STEP_CALL_SKIP = {
    "expect",
    "toBe",
    "toEqual",
    "toHaveCount",
    "toBeVisible",
    "toContain",
    "getByRole",
    "getByLabel",
    "getByText",
    "getByTestId",
    "locator",
    "click",
    "fill",
    "press",
    "hover",
    "check",
    "uncheck",
    "selectOption",
    "filter",
    "map",
    "forEach",
    "then",
    "catch",
    "push",
    "includes",
    "toString",
    "json",
    "keys",
    "values",
    "entries",
    "all",
    "race",
    "resolve",
    "reject",
    "first",
    "nth",
    "last",
    "count",
    "waitFor",
    "toBeTruthy",
    "toBeFalsy",
    "not",
}

_FILTER_PRACTICE = {
    "clean_engineering": "CleanEngineering",
    "stories": "Stories",
    "ddd": "Ddd",
    "bdd": "Bdd",
    "CleanEngineering": "CleanEngineering",
    "Stories": "Stories",
    "Ddd": "Ddd",
    "Bdd": "Bdd",
}

_PRACTICE_ROOTS = [
    (["clean_engineering", "CleanEngineering"], "Clean Engineering"),
    (["stories", "Stories"], "Stories"),
    (["ddd", "Ddd"], "Domain Driven Design"),
    (["bdd", "Bdd"], "BDD"),
]


def included_filter_practices(practices):
    found = []
    for practice in practices:
        name = _FILTER_PRACTICE.get(practice, practice)
        if name not in found:
            found.append(name)
    if "Ddd" in found and "CleanEngineering" not in found:
        found.append("CleanEngineering")
    return found


def practice_root_labels(selected):
    if not selected:
        return [label for _ids, label in _PRACTICE_ROOTS]
    return [
        label
        for ids, label in _PRACTICE_ROOTS
        if any(practice in selected for practice in ids)
    ]


def restored_branches(stored, present):
    known = set(present)
    return [item for item in stored if item in known]


_PRACTICE_IDS = {
    "CleanEngineering": "clean_engineering",
    "Stories": "stories",
    "Ddd": "ddd",
    "Bdd": "bdd",
    "Clean Engineering": "clean_engineering",
    "Domain Driven Design": "ddd",
    "BDD": "bdd",
}

PRACTICE_NODE_TYPES = {
    "clean_engineering": [
        "Module",
        "Package",
        "OoadClass",
        "Property",
        "Relationship",
        "Operation",
        "Parameter",
        "File",
        "CleanEngineeringModel",
    ],
    "stories": [
        "Increment",
        "Epic",
        "SubEpic",
        "Story",
        "Scenario",
        "Background",
        "Step",
        "Example",
        "StoryModel",
    ],
    "ddd": [
        "BoundedContext",
        "Aggregate",
        "Entity",
        "EntityRoot",
        "ValueObject",
        "Repository",
        "DomainEvent",
        "DomainService",
        "Specification",
    ],
    "bdd": ["Description", "Context", "Observation"],
}

STORY_NODE_TYPES = set(PRACTICE_NODE_TYPES["stories"])


def tagged_practice(semantic_type, practice):
    if semantic_type in STORY_NODE_TYPES:
        return "stories"
    if semantic_type in PRACTICE_NODE_TYPES["bdd"]:
        return "bdd"
    if semantic_type in PRACTICE_NODE_TYPES["ddd"]:
        return "ddd"
    return practice


def retag_practice(node):
    semantic = node.nodeType.name if getattr(node, "nodeType", None) else ""
    node.practice = tagged_practice(semantic, getattr(node, "practice", "") or "")
    properties = getattr(node, "properties", None) or {}
    folder = ""
    if isinstance(properties, dict):
        folder = str(properties.get("folder", "") or "")
    folder = folder.replace("\\", "/")
    if semantic in {"Module", "Package"} and (folder == "tests" or folder.startswith("tests/")):
        node.practice = "stories"
    return node


def is_story_node(node):
    semantic = node.nodeType.name if getattr(node, "nodeType", None) else ""
    if semantic in STORY_NODE_TYPES:
        return True
    if semantic not in {"Module", "Package"}:
        return False
    children = list(getattr(node, "children", None) or [])
    if not children:
        return False
    if all(is_story_node(child) for child in children):
        return True
    return _holds_only_story(node)


def _holds_only_story(node):
    found = False

    def walk(current):
        nonlocal found
        semantic = current.nodeType.name if getattr(current, "nodeType", None) else ""
        if semantic in STORY_NODE_TYPES:
            found = True
            return True
        if semantic == "File":
            return True
        if semantic in {"Module", "Package"}:
            return all(walk(child) for child in (getattr(current, "children", None) or []))
        return False

    return walk(node) and found


def is_story_node(node):
    semantic = node.nodeType.name if getattr(node, "nodeType", None) else ""
    if semantic in STORY_NODE_TYPES:
        return True
    if semantic not in {"Module", "Package"}:
        return False
    children = getattr(node, "children", None) or []
    if not children:
        return False
    if all(is_story_node(child) for child in children):
        return True
    return _holds_only_story(node)


def _holds_only_story(node):
    found = False

    def walk(current):
        nonlocal found
        semantic = current.nodeType.name if getattr(current, "nodeType", None) else ""
        if semantic in STORY_NODE_TYPES:
            found = True
            return True
        if semantic == "File":
            return True
        if semantic in {"Module", "Package"}:
            return all(walk(child) for child in (getattr(current, "children", None) or []))
        return False

    return walk(node) and found


def included_practice_ids(selected, expand_domain_driven_design=True):
    found = []
    for practice in selected:
        name = _PRACTICE_IDS.get(practice, practice)
        if name not in found:
            found.append(name)
    if expand_domain_driven_design and "ddd" in found and "clean_engineering" not in found:
        found.append("clean_engineering")
    return found


def retained_tree(nodes, selected, expand_domain_driven_design=True):
    practices = included_practice_ids(selected, expand_domain_driven_design)
    stories_selected = "stories" in practices
    allowed = set()
    for practice in practices:
        allowed.update(PRACTICE_NODE_TYPES.get(practice, []))

    def copy_node(node):
        copy = KnowledgeGraphNode()
        copy.name = node.name
        copy.nodeId = getattr(node, "nodeId", "")
        copy.practice = node.practice
        copy.nodeType = node.nodeType
        copy.children = []
        copy.relationships = list(getattr(node, "relationships", []) or [])
        return copy

    def visit(node):
        if is_story_node(node):
            if not stories_selected:
                return []
            copy = copy_node(node)
            nested = []
            for child in getattr(node, "children", None) or []:
                nested.extend(visit(child))
            copy.children = nested
            return [copy]
        children = []
        for child in getattr(node, "children", None) or []:
            children.extend(visit(child))
        semantic = node.nodeType.name if node.nodeType else ""
        practice = _PRACTICE_IDS.get(node.practice, node.practice) if node.practice else ""
        type_fits = semantic in allowed
        practice_fits = not practice or practice in practices
        folder = semantic in {"Module", "Package"} and practice_fits and children
        if (type_fits and practice_fits) or folder:
            copy = copy_node(node)
            copy.children = children
            return [copy]
        return children

    return [kept for node in nodes for kept in visit(node)]


def editor_height(line_count, folds, open_starts, line_height=20, max_height=520):
    open_lines = set(open_starts)
    hidden = 0
    for fold in folds:
        if fold.start in open_lines:
            continue
        covered = any(
            other is not fold
            and other.start <= fold.start
            and other.end >= fold.end
            and other.end > other.start
            and other.start not in open_lines
            for other in folds
        )
        if covered:
            continue
        hidden += max(0, fold.end - fold.start + 1)
    visible = max(1, line_count - hidden)
    return min(max_height, visible * line_height)


def step_members(text):
    operations = []
    examples = []
    for match in _STEP_CALL.finditer(text):
        name = match.group(1)
        if name in _STEP_CALL_SKIP or name in operations:
            continue
        operations.append(name)
    for match in _STEP_EXAMPLE.finditer(text):
        name = match.group(1)
        if name not in examples:
            examples.append(name)
    return {"operations": operations, "examples": examples}


class KnowledgeGraphNodeType:
    def __init__(self, name, practice, stage, edgeTypes=None) -> None:
        self.name = name
        self.practice = practice
        self.stage = stage
        self.edgeTypes = list(edgeTypes or [])


class KnowledgeGraphEdgeType:
    def __init__(self, name, fromType=None, toType=None, inverse=None, cardinality="0..*") -> None:
        self.name = name
        self.fromType = fromType
        self.toType = toType
        self.inverse = inverse
        self.cardinality = cardinality


class KnowledgeGraphNode:
    def __init__(self) -> None:
        self.name = ""
        self.sequentialOrder = 0
        self.nodeType = None
        self.source = None
        self.nodeId = ""
        self.edges = []
        self.panel = None
        self.rules = None

    def navigateTo(self, edge):
        if edge.from_node is self:
            return edge.to
        if edge.to is self:
            return edge.from_node
        return None


class KnowledgeGraphSource:
    def __init__(self, text, file, startLine, endLine, language) -> None:
        self.text = text
        self.file = file
        self.startLine = startLine
        self.endLine = endLine
        self.language = language

    def source(self):
        return self.text


class KnowledgeGraphCallSource(KnowledgeGraphSource):
    def __init__(self, text, file, startLine, endLine, language) -> None:
        KnowledgeGraphSource.__init__(self, text, file, startLine, endLine, language)
        self.calls = []
        self.folds = []

    def source(self):
        KnowledgeGraphSource.source(self)
        self.loadCalls()
        self.insertCalls()
        self.loadFolds()
        return self.text

    def loadCalls(self) -> None:
        self.calls = []
        skip = {"if", "for", "while", "function", "def", "switch", "catch"}
        for line_no, line in enumerate(self.text.splitlines(), 1):
            order = 0
            for match in _CALL.finditer(line):
                name = match.group(1)
                if name.split(".")[-1] in skip:
                    continue
                order += 1
                self.calls.append(KnowledgeGraphCall(line_no, order, name))

    def insertCalls(self) -> None:
        lines = self.text.splitlines()
        for call in self.calls:
            index = call.line - 1
            if 0 <= index < len(lines) and f"call:{call.operation}" not in lines[index]:
                lines[index] = f"{lines[index]} /* call:{call.operation} */"
        self.text = "\n".join(lines)

    def loadFolds(self) -> None:
        self.folds = []
        for call in self.calls:
            kind = "call" if "." in str(call.operation) else "class"
            self.folds.append(KnowledgeGraphSourceFold(call.line, call.line, kind))


class KnowledgeGraphCall:
    def __init__(self, line, sequentialOrder, operation) -> None:
        self.line = line
        self.sequentialOrder = sequentialOrder
        self.operation = operation


class KnowledgeGraphSourceFold:
    def __init__(self, start, end, kind) -> None:
        self.start = start
        self.end = end
        self.kind = kind


class KnowledgeGraphPanel:
    def __init__(self, source=None, language="", open=False, theme=None, mount=None) -> None:
        self.source = source
        self.language = language
        self.open = open
        self.theme = theme
        self.mount = mount


class KnowledgeGraphEdge:
    def __init__(self, edgeType, from_node, to) -> None:
        self.edgeType = edgeType
        self.from_node = from_node
        self.to = to


class KnowledgeGraphFilter:
    def __init__(self, practices=None) -> None:
        practices = list(practices or [])
        self.type = "Practice"
        self.selected = practices
        self.available = practices
        self.stageFilter = StageFilter([])
        self.nodeFilter = NodeFilter([])
        self.relationshipFilter = RelationshipFilter([])
        self.ruleSetFilter = RuleSetFilter([], ["base", "project"])
        self.ruleFilter = RuleFilter([])
        self.stageFilter.available(practices)
        stages = self.stageFilter.selected or self.stageFilter.choices
        self.nodeFilter.available(practices, stages)
        self.relationshipFilter.available(self.nodeFilter.selected or self.nodeFilter.choices)
        self.ruleSetFilter.available = ["base", "project"]
        self.ruleFilter.available(self.nodeFilter.selected or self.nodeFilter.choices)


class PracticeFilter(KnowledgeGraphFilter):
    def __init__(self, selected=None, available=None) -> None:
        self.type = "Practice"
        self.selected = list(selected or [])
        self.available = list(available or [])


class StageFilter:
    def __init__(self, selected=None) -> None:
        self.type = "Stage"
        self.selected = list(selected or [])
        self.choices = []

    def available(self, practices) -> None:
        found = []
        for practice in included_filter_practices(practices):
            for stage in PRACTICE_STAGES.get(practice, []):
                if stage not in found:
                    found.append(stage)
        self.choices = found
        if not self.selected:
            self.selected = list(found)


class NodeFilter:
    def __init__(self, selected=None) -> None:
        self.type = "Node"
        self.selected = list(selected or [])
        self.choices = []

    def available(self, practices, stages) -> None:
        found = []
        for practice in included_filter_practices(practices):
            by_stage = PRACTICE_NODES.get(practice, {})
            for stage in stages:
                for name in by_stage.get(stage, []):
                    if name not in found:
                        found.append(name)
        self.choices = found
        if not self.selected:
            self.selected = list(found)


class RelationshipFilter:
    def __init__(self, selected=None) -> None:
        self.type = "Relationship"
        self.selected = list(selected or [])
        self.choices = []

    def available(self, nodes) -> None:
        found = []
        for node in nodes:
            name = node.name if hasattr(node, "name") else str(node)
            for edge in NODE_EDGES.get(name, []):
                if edge not in found:
                    found.append(edge)
        self.choices = found
        if not self.selected:
            self.selected = list(found)


class RuleSetFilter:
    def __init__(self, selected=None, available=None) -> None:
        self.type = "RuleSet"
        self.selected = list(selected or [])
        self.available = list(available or ["base", "project"])


class RuleFilter:
    def __init__(self, selected=None) -> None:
        self.type = "Rule"
        self.selected = list(selected or [])
        self.choices = []

    def available(self, nodes) -> None:
        found = []
        for node in nodes:
            name = node.name if hasattr(node, "name") else str(node)
            for rule in NODE_RULES.get(name, []):
                if rule not in found:
                    found.append(rule)
        self.choices = found
        if not self.selected:
            self.selected = list(found)


class WebKnowledgeGraphNode(KnowledgeGraphNode):
    def __init__(self, keyword="", origin=None, properties=None, isFile=False, isFolder=False) -> None:
        KnowledgeGraphNode.__init__(self)
        self.keyword = keyword
        self.origin = origin
        self.properties = properties or {}
        self.isFile = isFile
        self.isFolder = isFolder


class PracticeGraph:
    def __init__(self, id, name, nodes=None, relationships=None) -> None:
        self.id = id
        self.name = name
        self.nodes = list(nodes or [])
        self.relationships = list(relationships or [])


class SourceRange:
    def __init__(self, file, startLine, endLine, text="") -> None:
        self.file = file
        self.startLine = startLine
        self.endLine = endLine
        self.text = text


class RuleHit:
    def __init__(self, ruleSlug, message="", body="", practice="", fidelity="", tag="base") -> None:
        self.ruleSlug = ruleSlug
        self.message = message
        self.body = body
        self.practice = practice
        self.fidelity = fidelity
        self.tag = tag


class NodeRules:
    def __init__(self, applicable=None, violations=None, statuses=None, details=None, tally=None) -> None:
        self.applicable = list(applicable or [])
        self.violations = list(violations or [])
        self.statuses = statuses or {}
        self.details = details
        self.tally = tally

    def status(self, ruleSlug):
        return self.statuses.get(ruleSlug)

    def hasRule(self, ruleSlug) -> bool:
        return ruleSlug in self.applicable or any(hit.ruleSlug == ruleSlug for hit in self.violations)


class WorkspaceFile:
    def __init__(self, relativePath, text) -> None:
        self.relativePath = relativePath
        self.text = text
