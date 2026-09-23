import { useEffect, useState } from 'react';
import type { ListedTreeNode } from './knowledge-graph';

function kindLabel(kind: string, isFile: boolean): string {
  if (isFile && kind === 'Module') {
    return 'File';
  }
  if (kind === 'OoadClass') {
    return 'Class';
  }
  return kind || 'Node';
}

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
      {!['PracticeGraph', 'File', 'Module', 'Package', 'Class', 'Operation', 'Rule', 'Rules'].includes(
        label,
      ) && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="8" cy="8" r="4.5" />
        </g>
      )}
    </svg>
  );
}

function listedRules(node: ListedTreeNode) {
  return node.rules;
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
  const rules = listedRules(node);
  const hasChildren = node.children.length > 0 || rules.length > 0;
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
            aria-label={`${isOpen ? 'Collapse' : 'Expand'} ${node.name}`}
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
          <span className="tree-name">{node.name}</span>
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
