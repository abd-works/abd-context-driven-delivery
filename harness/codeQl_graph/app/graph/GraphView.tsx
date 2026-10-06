import { useState } from 'react';
import { KindMark } from '../kind-mark';
import type { GraphTree } from '../filter/FilterClient';

type GraphViewProps = {
  trees: GraphTree[];
  loading: boolean;
  loadingLabel?: string;
  error: string;
  selectedId: string;
  onSelect: (nodeId: string) => void;
};

export function GraphView({ trees, loading, loadingLabel, error, selectedId, onSelect }: GraphViewProps) {
  return (
    <div className="panel" data-testid="practice-graph-tree">
      {loading ? (
        <p className="empty-state work-progress is-working" data-testid="extraction-progress">
          {loadingLabel ?? 'Loading the graph…'}
        </p>
      ) : null}
      {error ? (
        <p className="empty-state" data-testid="scan-error">
          {error}
        </p>
      ) : null}
      <ul className="tree">
        {trees.map((node) => (
          <TreeNode key={node.node_id || node.name} node={node} selectedId={selectedId} onSelect={onSelect} />
        ))}
      </ul>
    </div>
  );
}

function TreeNode({
  node,
  selectedId,
  onSelect,
}: {
  node: GraphTree;
  selectedId: string;
  onSelect: (nodeId: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const children = (node.children ?? []).filter(
    (child) => child.name !== 'belongsTo' && child.type !== 'belongsTo' && child.name !== 'scopes' && child.type !== 'scopes',
  );
  const selected = node.node_id === selectedId;
  return (
    <li data-node-id={node.node_id} data-kind={node.type} className={selected ? 'is-selected' : undefined}>
      <div className="tree-row">
        {children.length > 0 ? (
          <button
            type="button"
            className="tree-twist"
            aria-expanded={open}
            aria-label={`${open ? 'Collapse' : 'Expand'} ${node.name}`}
            onClick={() => setOpen((value) => !value)}
          >
            {open ? '▼' : '▶'}
          </button>
        ) : (
          <span className="tree-twist-spacer" />
        )}
        <button
          type="button"
          className={selected ? 'selected' : ''}
          onClick={() => onSelect(node.node_id)}
        >
          <KindMark kind={node.type} isFile={false} />
          <span className="node-name">{node.name}</span>
        </button>
      </div>
      {open && children.length > 0 ? (
        <ul>
          {children.map((child) => (
            <TreeNode key={child.node_id || child.name} node={child} selectedId={selectedId} onSelect={onSelect} />
          ))}
        </ul>
      ) : null}
    </li>
  );
}
