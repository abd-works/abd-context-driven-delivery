import { useEffect, useState } from 'react';
import {
  fieldTypeNames,
  isClassKind,
  isSimpleProperty,
  memberCallLabels,
  methodSignature,
  returnTypeNames,
  signatureTypeNames,
  SKIP_TYPES,
  stepTitle,
  type ListedRelationshipKind,
  type ListedTreeNode,
} from './knowledge-graph/knowledge-graph';

export function kindLabel(kind: string, isFile: boolean): string {
  if (isFile && kind === 'Module') {
    return 'File';
  }
  if (kind === 'OoadClass') {
    return 'Class';
  }
  if (kind === 'SubEpic') {
    return 'Sub-epic';
  }
  if (kind === 'BoundedContext') {
    return 'Bounded context';
  }
  if (kind === 'EntityRoot') {
    return 'Entity root';
  }
  if (kind === 'ValueObject') {
    return 'Value object';
  }
  if (kind === 'DomainEvent') {
    return 'Domain event';
  }
  if (kind === 'DomainService') {
    return 'Domain service';
  }
  return kind || 'Node';
}

const KNOWN_MARKS = new Set([
  'PracticeGraph',
  'File',
  'Module',
  'Package',
  'Class',
  'Operation',
  'Rule',
  'Rules',
  'Properties',
  'Relationships',
  'Relationship',
  'Book',
  'Gear',
  'Entity diagram',
  'Form',
  'Checklist',
  'Practice',
  'Epic',
  'Sub-epic',
  'Story',
  'Background',
  'Scenario',
  'Step',
  'Example',
  'Bounded context',
  'Aggregate',
  'Entity',
  'Entity root',
  'Value object',
  'Repository',
  'Domain event',
  'Domain service',
  'Specification',
  'Description',
  'Context',
  'Observation',
]);

function KindMark({ kind, isFile }: { kind: string; isFile: boolean }) {
  const label = kindLabel(kind, isFile);
  return (
    <svg
      className="kind-mark"
      viewBox="0 0 16 16"
      width="16"
      height="16"
      data-kind={label}
      aria-label={label}
      role="img"
    >
      <title>{label}</title>
      {label === 'PracticeGraph' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <circle cx="8" cy="3.5" r="1.75" />
          <circle cx="3.5" cy="12" r="1.75" />
          <circle cx="12.5" cy="12" r="1.75" />
          <path d="M8 5.3v2.2L4.8 10.6M8 7.5l3.2 3.1" />
        </g>
      )}
      {label === 'File' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <path d="M5 2.5h4.2L12 5.3V13.5H5z" />
          <path d="M9.2 2.5V5.3H12" />
        </g>
      )}
      {label === 'Module' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <path d="M2.5 13V5.5h4.2l1.3 1.5H13.5V13z" />
        </g>
      )}
      {label === 'Class' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <rect x="3" y="3" width="10" height="10" rx="0.5" />
          <path d="M3 6.5h10" />
        </g>
      )}
      {label === 'Operation' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M5 4.5 2.5 8 5 11.5M11 4.5 13.5 8 11 11.5" />
        </g>
      )}
      {label === 'Rules' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <path d="M3.5 2.5h8v10L7.5 10.5 3.5 12.5z" />
        </g>
      )}
      {label === 'Rule' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <path d="M4 2.5h8v11.5L8 11.5 4 14z" />
        </g>
      )}
      {label === 'Properties' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <rect x="3" y="3.5" width="10" height="9" rx="1" />
          <path d="M5.5 6.5h5M5.5 9.5h3.5" />
        </g>
      )}
      {label === 'Relationships' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
        >
          <circle cx="4" cy="8" r="2" />
          <circle cx="12" cy="8" r="2" />
          <path d="M6 8h4" />
        </g>
      )}
      {label === 'Relationship' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
        >
          <path d="M3 8h10M11 5.5 13.5 8 11 10.5" />
        </g>
      )}
      {label === 'Book' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M3.2 3.2h6.2A2.2 2.2 0 0 1 11.6 5.4V13H5.2A2 2 0 0 0 3.2 15z" />
          <path d="M3.2 3.2V15" />
        </g>
      )}
      {label === 'Gear' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
          <circle cx="8" cy="8" r="2.1" />
          <path d="M8 2.4v1.8M8 11.8v1.8M2.4 8h1.8M11.8 8h1.8M4.1 4.1l1.3 1.3M10.6 10.6l1.3 1.3M11.9 4.1 10.6 5.4M5.4 10.6 4.1 11.9" />
        </g>
      )}
      {label === 'Entity diagram' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.2">
          <rect x="1.4" y="1.6" width="4.2" height="3" />
          <rect x="10.4" y="1.6" width="4.2" height="3" />
          <rect x="5.9" y="11.2" width="4.2" height="3" />
          <path d="M5.6 3.1h4.8M8 4.6v6.6" />
        </g>
      )}
      {label === 'Form' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="2.4" width="10" height="11.2" rx="1" />
          <path d="M5.2 6h5.6M5.2 8.6h5.6M5.2 11.2h3" />
        </g>
      )}
      {label === 'Checklist' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="2.4" width="10" height="11.2" rx="1" />
          <path d="M5 6.2 6 7.2 7.8 5.2M5 10.6 6 11.6 7.8 9.6M9.2 6.4h2.2M9.2 10.8h2.2" />
        </g>
      )}
      {label === 'Package' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
          strokeDasharray="2 2"
        >
          <path d="M2.5 13V5.5h4.2l1.3 1.5H13.5V13z" />
        </g>
      )}
      {label === 'Practice' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M8 2.5 13.2 5.5v5L8 13.5 2.8 10.5v-5z" />
        </g>
      )}
      {label === 'Epic' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M4 2.5v11" />
          <path d="M4 3.5h8L10.5 6 12 8.5H4" />
        </g>
      )}
      {label === 'Sub-epic' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M5.5 4v9" />
          <path d="M5.5 4.5h6.5L10.5 6.5 12 8.5H5.5" />
        </g>
      )}
      {label === 'Story' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <rect x="3" y="2.5" width="10" height="11" rx="1" />
          <path d="M5.5 6h5M5.5 8.5h5M5.5 11h3" />
        </g>
      )}
      {label === 'Background' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <rect x="5" y="2.5" width="8" height="8" />
          <path d="M3 5.5h8V13.5H3z" />
        </g>
      )}
      {label === 'Scenario' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
          <circle cx="4" cy="12" r="1.6" />
          <circle cx="12" cy="4" r="1.6" />
          <path d="M5.3 10.8 10.7 5.2" />
        </g>
      )}
      {label === 'Step' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round">
          <path d="M3 12.5h3.5V9h3.5V5.5H13" />
        </g>
      )}
      {label === 'Example' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M6.2 3.2C4.8 3.2 4 4.2 4 5.4v1.4L2.6 8 4 9.2v1.4c0 1.2.8 2.2 2.2 2.2" />
          <path d="M9.8 3.2c1.4 0 2.2 1 2.2 2.2v1.4L13.4 8 12 9.2v1.4c0 1.2-.8 2.2-2.2 2.2" />
        </g>
      )}
      {label === 'Bounded context' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeDasharray="2 1.4">
          <rect x="2.5" y="3" width="11" height="10" rx="2" />
        </g>
      )}
      {label === 'Aggregate' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="2.5" y="2.5" width="5" height="5" />
          <rect x="8.5" y="2.5" width="5" height="5" />
          <rect x="5.5" y="8.5" width="5" height="5" />
        </g>
      )}
      {label === 'Entity' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="3" y="3" width="10" height="10" rx="0.5" />
          <circle cx="8" cy="8" r="1.3" fill="currentColor" stroke="none" />
        </g>
      )}
      {label === 'Entity root' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="3" y="3" width="10" height="10" rx="0.5" />
          <path d="M3 6.5h10" />
          <rect x="3.4" y="3.4" width="9.2" height="2.8" fill="currentColor" stroke="none" />
        </g>
      )}
      {label === 'Value object' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="3.5" y="3.5" width="9" height="9" rx="2" />
        </g>
      )}
      {label === 'Repository' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M3 5.5c0-1.2 2.2-2 5-2s5 .8 5 2v5c0 1.2-2.2 2-5 2s-5-.8-5-2z" />
          <path d="M3 5.5c0 1.2 2.2 2 5 2s5-.8 5-2" />
        </g>
      )}
      {label === 'Domain event' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M8 2.5 13 13H3z" />
        </g>
      )}
      {label === 'Domain service' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="8" cy="8" r="4.5" />
          <circle cx="8" cy="8" r="1.4" fill="currentColor" stroke="none" />
        </g>
      )}
      {label === 'Specification' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M4 2.5h6l2 2V13.5H4z" />
          <path d="M6 8h4M6 10.5h3" />
        </g>
      )}
      {label === 'Description' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M3 3.5h10v6.5H8.2L6 12.5V10H3z" />
        </g>
      )}
      {label === 'Context' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="2.5" y="2.5" width="11" height="11" rx="2" />
          <rect x="5.2" y="5.2" width="5.6" height="5.6" rx="1" />
        </g>
      )}
      {label === 'Observation' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="8" cy="8" r="5" />
          <path d="M5.4 8.2 7.2 10l3.4-4" />
        </g>
      )}
      {!KNOWN_MARKS.has(label) && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="8" cy="8" r="4.5" />
        </g>
      )}
    </svg>
  );
}

function listedRules(node: ListedTreeNode) {
  return (node.rules ?? []).filter((rule) => rule.status === 'violating');
}

function listedProperties(node: ListedTreeNode) {
  return Object.entries(node.properties ?? {}).filter(
    ([name, value]) => name !== 'folder' && value,
  );
}

function listedRelationships(node: ListedTreeNode, practices: string[] | null) {
  const groups = node.relationships ?? [];
  return groups
    .map((group) => {
      if (
        group.kind === 'owns' ||
        group.kind === 'belongsTo' ||
        group.kind === 'demonstratedThrough'
      ) {
        return { ...group, targets: [] };
      }
      let targets = group.targets.filter((target) => target.semantic_type !== 'Example');
      if (practices) {
        targets = targets.filter((target) => practices.includes(target.practice));
      }
      if (group.kind === 'demonstrates' && node.semantic_type !== 'Example') {
        targets = [];
      }
      if (group.kind === 'demonstrates') {
        targets = targets.filter((target) => target.semantic_type === 'OoadClass');
      }
      return { ...group, targets };
    })
    .filter((group) => group.targets.length > 0);
}

function practiceSectionMark(practice: string): string {
  if (practice === 'examples') {
    return 'Example';
  }
  if (practice === 'internal') {
    return 'Relationships';
  }
  if (practice === 'stories') {
    return 'Book';
  }
  if (practice === 'clean_engineering') {
    return 'Gear';
  }
  if (practice === 'ddd') {
    return 'Entity diagram';
  }
  if (practice === 'ux') {
    return 'Form';
  }
  if (practice === 'bdd') {
    return 'Checklist';
  }
  return 'Relationships';
}

type RelatedNode = Partial<ListedTreeNode> & {
  node_id: string;
  practice: string;
};

function listedTreeNode(node: RelatedNode): ListedTreeNode {
  return {
    node_id: node.node_id,
    name: node.name ?? node.node_id,
    path: node.path ?? node.name ?? node.node_id,
    practice: node.practice ?? '',
    semantic_type: node.semantic_type ?? '',
    is_file: node.is_file ?? false,
    properties: node.properties ?? {},
    rule_statuses: node.rule_statuses ?? {},
    rules: node.rules ?? [],
    relationships: node.relationships ?? [],
    source: node.source ?? null,
    origin: node.origin ?? null,
    failed: node.failed ?? 0,
    total: node.total ?? 0,
    children: node.children ?? [],
  };
}

function invokeLabel(
  kind: string,
  target: { node_id: string; name: string },
  nodesById: Map<string, ListedTreeNode>,
): string {
  if (kind !== 'invokes') {
    return target.name;
  }
  const owner = classOwning(nodesById, target.node_id);
  return owner ? `${target.name} on ${owner}` : target.name;
}

const TYPE_CONTAINERS = new Set(['Module', 'Aggregate', 'BoundedContext']);

function containerOf(
  nodeId: string,
  parentOf: Map<string, string>,
  nodesById: Map<string, ListedTreeNode>,
): string | null {
  let current = parentOf.get(nodeId);
  while (current) {
    const node = nodesById.get(current);
    if (!node) {
      return null;
    }
    if (TYPE_CONTAINERS.has(node.semantic_type)) {
      return node.node_id;
    }
    current = parentOf.get(current);
  }
  return null;
}

function classNodeOwning(
  nodesById: Map<string, ListedTreeNode>,
  memberId: string,
  parentOf?: Map<string, string>,
): ListedTreeNode | null {
  const parentId = parentOf?.get(memberId);
  const parent = parentId ? nodesById.get(parentId) : undefined;
  if (parent && isClassKind(parent.semantic_type)) {
    return parent;
  }
  for (const node of nodesById.values()) {
    if (!isClassKind(node.semantic_type)) {
      continue;
    }
    if (node.children.some((child) => child.node_id === memberId)) {
      return node;
    }
  }
  return null;
}

function isPublicOperation(node: ListedTreeNode): boolean {
  if (node.name === 'constructor' || node.name.startsWith('_')) {
    return false;
  }
  const line = (node.source?.text ?? node.origin?.text ?? '').split('\n')[0] ?? '';
  return !/\b(?:private|protected)\b/.test(line);
}

function matchingClass(
  name: string,
  container: string | null,
  nodesById: Map<string, ListedTreeNode>,
  parentOf: Map<string, string>,
  sameModuleOnly: boolean,
): ListedTreeNode | undefined {
  const matches = [...nodesById.values()].filter(
    (candidate) => isClassKind(candidate.semantic_type) && candidate.name === name,
  );
  const local = container
    ? matches.find((candidate) => containerOf(candidate.node_id, parentOf, nodesById) === container)
    : undefined;
  if (local) {
    return local;
  }
  if (sameModuleOnly) {
    return undefined;
  }
  return matches[0];
}

function classOwning(nodesById: Map<string, ListedTreeNode>, operationId: string): string {
  return classNodeOwning(nodesById, operationId)?.name ?? '';
}

function invokeTypeNodes(
  target: { node_id: string; name: string },
  nodesById: Map<string, ListedTreeNode>,
  parentOf: Map<string, string>,
  sameModuleOnly = false,
): ListedTreeNode[] {
  const operation = nodesById.get(target.node_id);
  if (!operation || (sameModuleOnly && !isPublicOperation(operation))) {
    return [];
  }
  const owner = classNodeOwning(nodesById, operation.node_id, parentOf);
  const text = methodSignature(
    operation.name,
    operation.source?.text ?? '',
    owner?.source?.text ?? '',
  );
  const names = new Set(sameModuleOnly ? returnTypeNames(text) : signatureTypeNames(text));
  if (!sameModuleOnly) {
    for (const child of operation.children) {
      if (child.semantic_type !== 'Parameter') {
        continue;
      }
      for (const group of child.relationships) {
        if (group.kind !== 'hasType') {
          continue;
        }
        for (const related of group.targets) {
          names.add(related.name);
        }
      }
    }
  }
  for (const group of operation.relationships) {
    if (group.kind !== 'returns' && (sameModuleOnly || group.kind !== 'hasType')) {
      continue;
    }
    for (const related of group.targets) {
      names.add(related.name);
    }
  }
  const container = owner ? containerOf(owner.node_id, parentOf, nodesById) : null;
  const found: ListedTreeNode[] = [];
  const seen = new Set<string>([operation.node_id]);
  if (owner) {
    seen.add(owner.node_id);
  }
  for (const name of names) {
    if (SKIP_TYPES.has(name) || name === owner?.name) {
      continue;
    }
    const match = matchingClass(name, container, nodesById, parentOf, sameModuleOnly);
    if (!match || seen.has(match.node_id)) {
      continue;
    }
    seen.add(match.node_id);
    found.push(match);
  }
  return found;
}

function propertyTypeNodes(
  property: ListedTreeNode,
  nodesById: Map<string, ListedTreeNode>,
  parentOf: Map<string, string>,
  sameModuleOnly = false,
): ListedTreeNode[] {
  const names = new Set(fieldTypeNames(property.source?.text ?? ''));
  for (const group of property.relationships) {
    if (group.kind !== 'hasType') {
      continue;
    }
    for (const related of group.targets) {
      names.add(related.name);
    }
  }
  const owner = classNodeOwning(nodesById, property.node_id, parentOf);
  const container = owner ? containerOf(owner.node_id, parentOf, nodesById) : null;
  const found: ListedTreeNode[] = [];
  const seen = new Set<string>([property.node_id]);
  if (owner) {
    seen.add(owner.node_id);
  }
  for (const name of names) {
    if (SKIP_TYPES.has(name) || name === owner?.name) {
      continue;
    }
    const match = matchingClass(name, container, nodesById, parentOf, sameModuleOnly);
    if (!match || seen.has(match.node_id)) {
      continue;
    }
    seen.add(match.node_id);
    found.push(match);
  }
  return found;
}

function composedByFolderRoot(node: ListedTreeNode): Set<string> {
  const composed = new Set<string>();
  if (node.semantic_type !== 'Module' && node.semantic_type !== 'Package') {
    return composed;
  }
  const folder = (node.properties.folder || node.name).split(/[\\/.]/).filter(Boolean).pop()?.toLowerCase() ?? '';
  const root = node.children.find(
    (child) => isClassKind(child.semantic_type) && child.name.toLowerCase() === folder,
  );
  if (!root) {
    return composed;
  }
  for (const group of root.relationships) {
    if (group.kind !== 'composition') {
      continue;
    }
    for (const target of group.targets) {
      if (target.node_id !== root.node_id) {
        composed.add(target.node_id);
      }
    }
  }
  return composed;
}

function calledMembers(
  node: ListedTreeNode,
  nodesById: Map<string, ListedTreeNode>,
): ListedTreeNode[] {
  if (node.semantic_type !== 'Operation' && node.semantic_type !== 'Property') {
    return [];
  }
  const labels = memberCallLabels(node.source?.text ?? '');
  const found: ListedTreeNode[] = [];
  const seen = new Set<string>();
  for (const group of node.relationships ?? []) {
    if (group.kind !== 'invokes') {
      continue;
    }
    for (const target of group.targets) {
      if (target.semantic_type !== 'Operation' && target.semantic_type !== 'Property') {
        continue;
      }
      const full = nodesById.get(target.node_id);
      if (!full || seen.has(full.node_id)) {
        continue;
      }
      const label = labels.get(full.name);
      if (!label) {
        continue;
      }
      if (
        node.semantic_type === 'Operation' &&
        full.semantic_type === 'Property' &&
        isSimpleProperty(full.source?.text ?? '')
      ) {
        continue;
      }
      seen.add(full.node_id);
      found.push({ ...full, name: label });
    }
  }
  return found;
}

function linkedTypeNodes(
  node: ListedTreeNode,
  nodesById: Map<string, ListedTreeNode>,
  parentOf: Map<string, string>,
): ListedTreeNode[] {
  if (node.semantic_type === 'Operation') {
    return invokeTypeNodes({ node_id: node.node_id, name: node.name }, nodesById, parentOf);
  }
  if (node.semantic_type === 'Property') {
    return propertyTypeNodes(node, nodesById, parentOf);
  }
  return [];
}

function asMemberNode(
  target: ListedRelationshipKind['targets'][number],
  nodesById: Map<string, ListedTreeNode>,
): ListedTreeNode | null {
  if (target.semantic_type !== 'Operation' && target.semantic_type !== 'Property') {
    return null;
  }
  const full = nodesById.get(target.node_id);
  if (full) {
    return full;
  }
  return {
    node_id: target.node_id,
    name: target.name,
    path: target.name,
    practice: target.practice,
    semantic_type: target.semantic_type,
    is_file: false,
    properties: {},
    rule_statuses: {},
    rules: [],
    relationships: [],
    source: null,
    origin: null,
    failed: 0,
    total: 0,
    children: [],
  };
}

function flatRelationships(relationships: ListedRelationshipKind[]) {
  const rows: Array<{ kind: string; target: ListedRelationshipKind['targets'][number] }> = [];
  const seen = new Set<string>();
  for (const group of relationships) {
    for (const target of group.targets) {
      if (target.semantic_type === 'Example') {
        continue;
      }
      const key = `${group.kind}:${target.node_id}`;
      if (seen.has(key)) {
        continue;
      }
      seen.add(key);
      rows.push({ kind: group.kind, target });
    }
  }
  return rows;
}

function PropertiesGroup({
  nodeId,
  properties,
  depth,
  expanded,
  onToggle,
}: {
  nodeId: string;
  properties: Array<[string, string]>;
  depth: number;
  expanded: Set<string>;
  onToggle: (id: string) => void;
}) {
  const propertiesId = `${nodeId}::properties`;
  const isOpen = expanded.has(propertiesId);
  return (
    <li data-depth={depth} data-testid="tree-properties">
      <div className="tree-row">
        <button
          type="button"
          className="tree-twist"
          data-testid="tree-expand-properties"
          aria-expanded={isOpen}
          aria-label={`${isOpen ? 'Collapse' : 'Expand'} properties`}
          onClick={() => onToggle(propertiesId)}
        >
          {isOpen ? '▼' : '▶'}
        </button>
        <button type="button" title="Properties" onClick={() => onToggle(propertiesId)}>
          <KindMark kind="Properties" isFile={false} />
          <span className="tree-name">properties</span>
        </button>
      </div>
      {isOpen && (
        <ul>
          {properties.map(([name, value]) => (
            <li key={name} data-depth={depth + 1}>
              <div className="tree-row">
                <span className="tree-twist-spacer" />
                <span className="tree-name" title="Property">
                  {name} : {value}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </li>
  );
}

function RulesGroup({
  nodeId,
  rules,
  depth,
  selectedId,
  selectedRule,
  expanded,
  onToggle,
  onSelect,
}: {
  nodeId: string;
  rules: ReturnType<typeof listedRules>;
  depth: number;
  selectedId: string | null;
  selectedRule: string | null;
  expanded: Set<string>;
  onToggle: (id: string) => void;
  onSelect: (id: string, ruleSlug?: string) => void;
}) {
  const rulesId = `${nodeId}::rules`;
  const isOpen = expanded.has(rulesId);
  return (
    <li data-depth={depth} data-testid="tree-rules">
      <div className="tree-row">
        <button
          type="button"
          className="tree-twist"
          data-testid="tree-expand-rules"
          aria-expanded={isOpen}
          aria-label={`${isOpen ? 'Collapse' : 'Expand'} rules`}
          onClick={() => onToggle(rulesId)}
        >
          {isOpen ? '▼' : '▶'}
        </button>
        <button
          type="button"
          title="Rules"
          onClick={() => onToggle(rulesId)}
        >
          <KindMark kind="Rules" isFile={false} />
          <span className="tree-name">rules</span>
        </button>
      </div>
      {isOpen && (
        <ul>
          {rules.map((entry) => (
            <li key={entry.slug} data-depth={depth + 1}>
              <div className="tree-row">
                <span className="tree-twist-spacer" />
                <button
                  type="button"
                  title="Rule"
                  className={`rule-status ${entry.status}${
                    selectedId === nodeId && selectedRule === entry.slug
                      ? ' selected'
                      : ''
                  }`}
                  onClick={() => onSelect(nodeId, entry.slug)}
                >
                  <KindMark kind="Rule" isFile={false} />
                  <span className="tree-name">{entry.slug}</span>
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </li>
  );
}

function RelationshipRow({
  nodeId,
  kind,
  target,
  depth,
  practices,
  showRules,
  selectedId,
  expanded,
  nodesById,
  parentOf,
  stack,
  onToggle,
  onSelect,
}: {
  nodeId: string;
  kind: string;
  target: ListedRelationshipKind['targets'][number];
  depth: number;
  practices: string[] | null;
  showRules: boolean;
  selectedId: string | null;
  expanded: Set<string>;
  nodesById: Map<string, ListedTreeNode>;
  parentOf: Map<string, string>;
  stack: Set<string>;
  onToggle: (id: string) => void;
  onSelect: (id: string, ruleSlug?: string) => void;
}) {
  const targetNode = nodesById.get(target.node_id);
  const next = new Set(stack);
  next.add(target.node_id);
  const typeNodes = kind === 'invokes' ? invokeTypeNodes(target, nodesById, parentOf) : [];
  const properties = kind === 'invokes' || !targetNode ? [] : listedProperties(targetNode);
  const rules = showRules && targetNode && kind !== 'invokes' ? listedRules(targetNode) : [];
  const children = kind === 'invokes' ? typeNodes : (targetNode?.children ?? []);
  const canOpen =
    !stack.has(target.node_id) &&
    (children.length > 0 || properties.length > 0 || rules.length > 0);
  const rowId = `${nodeId}::rel::${kind}::${target.node_id}`;
  const isOpen = expanded.has(rowId);
  return (
    <li data-depth={depth} data-testid="tree-relationship">
      <div className="tree-row">
        {canOpen ? (
          <button
            type="button"
            className="tree-twist"
            data-testid="tree-expand"
            aria-expanded={isOpen}
            aria-label={`${isOpen ? 'Collapse' : 'Expand'} ${target.name}`}
            onClick={() => onToggle(rowId)}
          >
            {isOpen ? '▼' : '▶'}
          </button>
        ) : (
          <span className="tree-twist-spacer" />
        )}
        <button
          type="button"
          title={kind}
          className={selectedId === target.node_id ? 'selected' : ''}
          data-testid="tree-relationship-target"
          onClick={() => onSelect(target.node_id)}
        >
          <KindMark kind={practiceSectionMark(target.practice)} isFile={false} />
          <span className="tree-name">{kind}</span>
          <span className="tree-name">{invokeLabel(kind, target, nodesById)}</span>
        </button>
      </div>
      {isOpen && canOpen && (targetNode || typeNodes.length > 0) && (
        <ul>
          {children.map((child) => (
            <TreeRow
              key={child.node_id}
              node={child}
              depth={depth + 1}
              practices={practices}
              showRules={showRules}
              selectedId={selectedId}
              selectedRule={null}
              expanded={expanded}
              nodesById={nodesById}
              parentOf={parentOf}
              stack={next}
              onToggle={onToggle}
              onSelect={onSelect}
            />
          ))}
          {properties.length > 0 ? (
            <PropertiesGroup
              nodeId={target.node_id}
              properties={properties}
              depth={depth + 1}
              expanded={expanded}
              onToggle={onToggle}
            />
          ) : null}
          {rules.length > 0 ? (
            <RulesGroup
              nodeId={target.node_id}
              rules={rules}
              depth={depth + 1}
              selectedId={selectedId}
              selectedRule={null}
              expanded={expanded}
              onToggle={onToggle}
              onSelect={onSelect}
            />
          ) : null}
        </ul>
      )}
    </li>
  );
}

function TreeRow({
  node,
  depth,
  practices,
  showRules = true,
  selectedId,
  selectedRule,
  expanded,
  nodesById,
  parentOf,
  stack,
  callDepth = 1,
  onToggle,
  onSelect,
}: {
  node: ListedTreeNode;
  depth: number;
  practices: string[] | null;
  showRules?: boolean;
  selectedId: string | null;
  selectedRule: string | null;
  expanded: Set<string>;
  nodesById: Map<string, ListedTreeNode>;
  parentOf: Map<string, string>;
  stack?: Set<string>;
  callDepth?: number;
  onToggle: (id: string) => void;
  onSelect: (id: string, ruleSlug?: string) => void;
}) {
  const seen = stack ?? new Set<string>();
  const next = new Set(seen);
  next.add(node.node_id);
  const title = stepTitle(
    node.name,
    node.semantic_type,
    '',
    node.source?.text ?? node.origin?.text ?? '',
  );
  const calls = callDepth >= 5 ? [] : calledMembers(node, nodesById);
  const linked = linkedTypeNodes(node, nodesById, parentOf);
  const composed = composedByFolderRoot(node);
  const structural = node.children.filter((child) => !composed.has(child.node_id));
  const childNodes = calls.length > 0 || linked.length > 0 ? [...calls, ...linked] : structural;
  const shownCalls = new Set(calls.map((call) => call.node_id));
  const rules = showRules ? listedRules(node) : [];
  const properties = listedProperties(node);
  const relationships = flatRelationships(listedRelationships(node, practices)).filter((row) => {
    if (shownCalls.has(row.target.node_id) && row.kind === 'invokes') {
      return false;
    }
    if (linked.length === 0) {
      return true;
    }
    if (node.semantic_type === 'Operation') {
      return row.kind !== 'returns' && row.kind !== 'hasType' && row.kind !== 'hasParameter';
    }
    if (node.semantic_type === 'Property') {
      return row.kind !== 'hasType';
    }
    return true;
  });
  const hasChildren =
    childNodes.length > 0 ||
    properties.length > 0 ||
    rules.length > 0 ||
    relationships.length > 0;
  const isOpen = expanded.has(node.node_id);
  return (
    <li data-depth={depth}>
      <div className="tree-row">
        {hasChildren ? (
          <button
            type="button"
            className="tree-twist"
            data-testid="tree-expand"
            aria-expanded={isOpen}
            aria-label={`${isOpen ? 'Collapse' : 'Expand'} ${title}`}
            onClick={() => onToggle(node.node_id)}
          >
            {isOpen ? '▼' : '▶'}
          </button>
        ) : (
          <span className="tree-twist-spacer" />
        )}
        <button
          type="button"
          title={kindLabel(node.semantic_type, node.is_file)}
          className={[
            selectedId === node.node_id && !selectedRule ? 'selected' : '',
            node.failed > 0 ? 'tree-violating' : '',
          ]
            .filter(Boolean)
            .join(' ')}
          onClick={() => onSelect(node.node_id)}
        >
          <KindMark kind={node.semantic_type} isFile={node.is_file} />
          <span className="tree-name">{title}</span>
          {node.total > 0 || node.failed > 0 ? (
            <span className="tree-counts" data-testid="tree-rule-counts">
              ({node.failed}/{node.total})
            </span>
          ) : null}
        </button>
      </div>
      {hasChildren && isOpen && (
        <ul>
          {childNodes.map((child) =>
            seen.has(child.node_id) ? null : (
              <TreeRow
                key={child.node_id}
                node={child}
                depth={depth + 1}
                practices={practices}
                showRules={showRules}
                selectedId={selectedId}
                selectedRule={selectedRule}
                expanded={expanded}
                nodesById={nodesById}
                parentOf={parentOf}
                stack={next}
                callDepth={
                  child.semantic_type === 'Operation' || child.semantic_type === 'Property'
                    ? callDepth + 1
                    : callDepth
                }
                onToggle={onToggle}
                onSelect={onSelect}
              />
            ),
          )}
          {properties.length > 0 ? (
            <PropertiesGroup
              nodeId={node.node_id}
              properties={properties}
              depth={depth + 1}
              expanded={expanded}
              onToggle={onToggle}
            />
          ) : null}
          {relationships.map((row) => {
            const member = row.kind === 'invokes' ? asMemberNode(row.target, nodesById) : null;
            if (member) {
              if (
                node.semantic_type === 'Operation' &&
                member.semantic_type === 'Property' &&
                isSimpleProperty(member.source?.text ?? '')
              ) {
                return null;
              }
              if (seen.has(member.node_id)) {
                return null;
              }
              return (
                <TreeRow
                  key={member.node_id}
                  node={member}
                  depth={depth + 1}
                  practices={practices}
                  showRules={showRules}
                  selectedId={selectedId}
                  selectedRule={selectedRule}
                  expanded={expanded}
                  nodesById={nodesById}
                  parentOf={parentOf}
                  stack={next}
                  callDepth={callDepth + 1}
                  onToggle={onToggle}
                  onSelect={onSelect}
                />
              );
            }
            return (
              <RelationshipRow
                key={`${row.kind}:${row.target.node_id}`}
                nodeId={node.node_id}
                kind={row.kind}
                target={row.target}
                depth={depth + 1}
                practices={practices}
                showRules={showRules}
                selectedId={selectedId}
                expanded={expanded}
                nodesById={nodesById}
                parentOf={parentOf}
                stack={next}
                onToggle={onToggle}
                onSelect={onSelect}
              />
            );
          })}
          {rules.length > 0 ? (
            <RulesGroup
              nodeId={node.node_id}
              rules={rules}
              depth={depth + 1}
              selectedId={selectedId}
              selectedRule={selectedRule}
              expanded={expanded}
              onToggle={onToggle}
              onSelect={onSelect}
            />
          ) : null}
        </ul>
      )}
    </li>
  );
}

export function PracticeGraphTree({
  roots,
  nodes = [],
  practices = null,
  showRules = true,
  selectedId,
  selectedRule = null,
  onSelect,
}: {
  roots: ListedTreeNode[];
  nodes?: RelatedNode[];
  practices?: string[] | null;
  showRules?: boolean;
  selectedId: string | null;
  selectedRule?: string | null;
  onSelect: (id: string, ruleSlug?: string) => void;
}) {
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set());
  const rootKey = roots.map((node) => node.node_id).join('|');
  useEffect(() => {
    const ids = rootKey ? rootKey.split('|').filter(Boolean) : [];
    setExpanded(ids.length === 1 ? new Set(ids) : new Set());
  }, [rootKey]);
  function onToggle(id: string) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }
  const nodesById = new Map<string, ListedTreeNode>();
  const parentOf = new Map<string, string>();
  const remember = (node: ListedTreeNode, parentId?: string) => {
    if (parentId && !parentOf.has(node.node_id)) {
      parentOf.set(node.node_id, parentId);
    }
    const existing = nodesById.get(node.node_id);
    if (!existing || (existing.children.length === 0 && node.children.length > 0)) {
      nodesById.set(node.node_id, node);
    }
    for (const child of node.children) {
      remember(child, node.node_id);
    }
  };
  for (const node of nodes) {
    remember(listedTreeNode(node));
  }
  for (const root of roots) {
    remember(root);
  }
  return (
    <ul className="tree">
      {roots.map((node) => (
        <TreeRow
          key={node.node_id}
          node={node}
          depth={0}
          practices={practices}
          showRules={showRules}
          selectedId={selectedId}
          selectedRule={selectedRule}
          expanded={expanded}
          nodesById={nodesById}
          parentOf={parentOf}
          onToggle={onToggle}
          onSelect={onSelect}
        />
      ))}
    </ul>
  );
}
