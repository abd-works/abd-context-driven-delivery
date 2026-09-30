import { useEffect, useState } from 'react';
import {
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
  return node.rules ?? [];
}

function listedProperties(node: ListedTreeNode) {
  return Object.entries(node.properties ?? {}).filter(([, value]) => value);
}

function listedRelationships(node: ListedTreeNode) {
  return node.relationships ?? [];
}

function relatedCount(groups: ListedRelationshipKind[]) {
  return groups.reduce((sum, group) => sum + group.targets.length, 0);
}

const PRACTICE_SECTION_ORDER = ['stories', 'clean_engineering', 'ddd', 'ux', 'bdd'];

function practiceSectionLabel(practice: string): string {
  if (practice === 'clean_engineering') {
    return 'ce';
  }
  return practice;
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

function relationshipSections(nodePractice: string, relationships: ListedRelationshipKind[]) {
  const byPractice = new Map<string, ListedRelationshipKind[]>();
  for (const group of relationships) {
    const targetsByPractice = new Map<string, ListedRelationshipKind['targets']>();
    for (const target of group.targets) {
      if (target.semantic_type === 'Example' && group.kind !== 'demonstratedThrough') {
        continue;
      }
      const samePractice = !target.practice || target.practice === nodePractice;
      const key =
        target.semantic_type === 'Example' && samePractice
          ? 'examples'
          : target.practice && !samePractice
            ? target.practice
            : 'internal';
      const list = targetsByPractice.get(key) ?? [];
      list.push(target);
      targetsByPractice.set(key, list);
      if (key === 'examples') {
        const internal = targetsByPractice.get('internal') ?? [];
        internal.push(target);
        targetsByPractice.set('internal', internal);
      }
    }
    for (const [practice, targets] of targetsByPractice) {
      if (targets.length === 0) {
        continue;
      }
      const groups = byPractice.get(practice) ?? [];
      groups.push({ kind: group.kind, targets });
      byPractice.set(practice, groups);
    }
  }
  const keys = [...byPractice.keys()].filter((key) => key !== 'internal' && key !== 'examples');
  keys.sort((left, right) => {
    const leftRank = PRACTICE_SECTION_ORDER.indexOf(left);
    const rightRank = PRACTICE_SECTION_ORDER.indexOf(right);
    const ranked =
      (leftRank === -1 ? PRACTICE_SECTION_ORDER.length : leftRank) -
      (rightRank === -1 ? PRACTICE_SECTION_ORDER.length : rightRank);
    return ranked || left.localeCompare(right);
  });
  if ((byPractice.get('examples') ?? []).some((group) => group.targets.length > 0)) {
    keys.push('examples');
  }
  if ((byPractice.get('internal') ?? []).some((group) => group.targets.length > 0)) {
    keys.push('internal');
  }
  return keys.map((practice) => ({
    practice,
    label: practiceSectionLabel(practice),
    mark: practiceSectionMark(practice),
    relationships: (byPractice.get(practice) ?? []).filter((group) => group.targets.length > 0),
  }));
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

function RelationshipsGroup({
  nodeId,
  section,
  depth,
  selectedId,
  expanded,
  onToggle,
  onSelect,
}: {
  nodeId: string;
  section: ReturnType<typeof relationshipSections>[number];
  depth: number;
  selectedId: string | null;
  expanded: Set<string>;
  onToggle: (id: string) => void;
  onSelect: (id: string, ruleSlug?: string) => void;
}) {
  const relationships = section.relationships;
  const exampleTargets =
    section.practice === 'examples'
      ? relationships
          .flatMap((group) => group.targets)
          .filter(
            (target, index, all) =>
              all.findIndex((other) => other.node_id === target.node_id) === index,
          )
      : [];
  const relationshipsId = `${nodeId}::relationships::${section.practice}`;
  const isOpen = expanded.has(relationshipsId);
  const count =
    section.practice === 'examples' ? exampleTargets.length : relatedCount(relationships);
  if (count === 0) {
    return null;
  }
  return (
    <li data-depth={depth} data-testid="tree-relationships" data-practice={section.practice}>
      <div className="tree-row">
        <button
          type="button"
          className="tree-twist"
          data-testid="tree-expand-relationships"
          aria-expanded={isOpen}
          aria-label={`${isOpen ? 'Collapse' : 'Expand'} ${section.label}`}
          onClick={() => onToggle(relationshipsId)}
        >
          {isOpen ? '▼' : '▶'}
        </button>
        <button
          type="button"
          title={section.label}
          onClick={() => onToggle(relationshipsId)}
        >
          <KindMark kind={section.mark} isFile={false} />
          <span className="tree-name">{section.label}</span>
          <span className="tree-counts" data-testid="tree-relationship-counts">
            ({count})
          </span>
        </button>
      </div>
      {isOpen && section.practice === 'examples' && (
        <ul>
          {exampleTargets.map((target) => (
            <li key={target.node_id} data-depth={depth + 1}>
              <div className="tree-row">
                <span className="tree-twist-spacer" />
                <button
                  type="button"
                  title={kindLabel(target.semantic_type, false)}
                  className={selectedId === target.node_id ? 'selected' : ''}
                  data-testid="tree-relationship-target"
                  onClick={() => onSelect(target.node_id)}
                >
                  <KindMark kind={target.semantic_type} isFile={false} />
                  <span className="tree-name">{target.name}</span>
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
      {isOpen && section.practice !== 'examples' && (
        <ul>
          {relationships.map((group) => {
            if (group.targets.length === 0) {
              return null;
            }
            const kindId = `${relationshipsId}::${group.kind}`;
            const kindOpen = expanded.has(kindId);
            return (
              <li key={group.kind} data-depth={depth + 1} data-testid="tree-relationship-kind">
                <div className="tree-row">
                  <button
                    type="button"
                    className="tree-twist"
                    data-testid="tree-expand-relationship-kind"
                    aria-expanded={kindOpen}
                    aria-label={`${kindOpen ? 'Collapse' : 'Expand'} ${group.kind}`}
                    onClick={() => onToggle(kindId)}
                  >
                    {kindOpen ? '▼' : '▶'}
                  </button>
                  <button
                    type="button"
                    title="Relationship"
                    onClick={() => onToggle(kindId)}
                  >
                    <KindMark kind="Relationship" isFile={false} />
                    <span className="tree-name">{group.kind}</span>
                    <span className="tree-counts">({group.targets.length})</span>
                  </button>
                </div>
                {kindOpen && (
                  <ul>
                    {group.targets.map((target) => (
                      <li key={target.node_id} data-depth={depth + 2}>
                        <div className="tree-row">
                          <span className="tree-twist-spacer" />
                          <button
                            type="button"
                            title={kindLabel(target.semantic_type, false)}
                            className={
                              selectedId === target.node_id ? 'selected' : ''
                            }
                            data-testid="tree-relationship-target"
                            onClick={() => onSelect(target.node_id)}
                          >
                            <KindMark
                              kind={target.semantic_type}
                              isFile={false}
                            />
                            <span className="tree-name">{target.name}</span>
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </li>
  );
}

function TreeRow({
  node,
  depth,
  selectedId,
  selectedRule,
  expanded,
  onToggle,
  onSelect,
}: {
  node: ListedTreeNode;
  depth: number;
  selectedId: string | null;
  selectedRule: string | null;
  expanded: Set<string>;
  onToggle: (id: string) => void;
  onSelect: (id: string, ruleSlug?: string) => void;
}) {
  const title = stepTitle(
    node.name,
    node.semantic_type,
    '',
    node.source?.text ?? node.origin?.text ?? '',
  );
  const rules = listedRules(node);
  const properties = listedProperties(node);
  const relationships = relationshipSections(node.practice, listedRelationships(node));
  const hasChildren =
    node.children.length > 0 ||
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
          {node.children.map((child) => (
            <TreeRow
              key={child.node_id}
              node={child}
              depth={depth + 1}
              selectedId={selectedId}
              selectedRule={selectedRule}
              expanded={expanded}
              onToggle={onToggle}
              onSelect={onSelect}
            />
          ))}
          {properties.length > 0 ? (
            <PropertiesGroup
              nodeId={node.node_id}
              properties={properties}
              depth={depth + 1}
              expanded={expanded}
              onToggle={onToggle}
            />
          ) : null}
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
          {relationships.map((section) => (
            <RelationshipsGroup
              key={section.practice}
              nodeId={node.node_id}
              section={section}
              depth={depth + 1}
              selectedId={selectedId}
              expanded={expanded}
              onToggle={onToggle}
              onSelect={onSelect}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export function PracticeGraphTree({
  roots,
  selectedId,
  selectedRule = null,
  onSelect,
}: {
  roots: ListedTreeNode[];
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
  return (
    <ul className="tree">
      {roots.map((node) => (
        <TreeRow
          key={node.node_id}
          node={node}
          depth={0}
          selectedId={selectedId}
          selectedRule={selectedRule}
          expanded={expanded}
          onToggle={onToggle}
          onSelect={onSelect}
        />
      ))}
    </ul>
  );
}
