import { useEffect, useRef, useState } from 'react';
import { KindMark } from '../kind-mark';
import type { GraphTree } from '../filter/FilterClient';
import { queryProgress } from './query-progress';

type GraphViewProps = {
  trees: GraphTree[];
  loading: boolean;
  loadingLabel?: string;
  loadingLog?: string[];
  error: string;
  selectedId: string;
  onSelect: (nodeId: string) => void;
};

function elapsedLabel(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return `${minutes}:${rest.toString().padStart(2, '0')}`;
}

export function GraphView({ trees, loading, loadingLabel, loadingLog = [], error, selectedId, onSelect }: GraphViewProps) {
  const progress = queryProgress(loadingLog);
  const log = useRef<HTMLOListElement>(null);
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    if (!loading) {
      setElapsed(0);
      return;
    }
    const started = Date.now();
    const id = window.setInterval(() => setElapsed(Math.floor((Date.now() - started) / 1000)), 1000);
    return () => window.clearInterval(id);
  }, [loading]);
  useEffect(() => {
    const list = log.current;
    if (list) {
      list.scrollTop = list.scrollHeight;
    }
  }, [progress.headline, progress.steps.length, loadingLog.length, elapsed]);
  const active =
    progress.steps.length === 0 || progress.steps[progress.steps.length - 1]?.name !== progress.headline.split(' ').at(-1);
  const headline = progress.headline === 'Loading the graph…' ? loadingLabel ?? progress.headline : progress.headline;
  const shown = elapsed > 0 ? `${headline} · ${elapsedLabel(elapsed)}` : headline;
  return (
    <div className="panel" data-testid="practice-graph-tree">
      {loading ? (
        <div className="empty-state work-progress is-working" data-testid="extraction-progress">
          <p className="query-now">{shown}</p>
          {loadingLog.length > 0 ? (
            <ol className="loading-log" data-testid="loading-log" ref={log}>
              {progress.steps.map((step) => (
                <li key={`${step.index}-${step.name}`}>
                  {step.index}/{step.total} {step.name}
                </li>
              ))}
              {progress.steps.length === 0
                ? loadingLog.slice(-12).map((line, index) => <li key={`${index}-${line}`}>{line}</li>)
                : null}
              {active && progress.detail ? <li className="is-current">{progress.detail}</li> : null}
            </ol>
          ) : null}
        </div>
      ) : null}
      {error ? (
        <div className="scan-error empty-state" data-testid="scan-error">
          <button type="button" className="copy-diagnosis" onClick={() => void navigator.clipboard.writeText(error)}>
            Copy for AI
          </button>
          <pre>{error}</pre>
        </div>
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
  ownerId,
}: {
  node: GraphTree;
  selectedId: string;
  onSelect: (nodeId: string) => void;
  ownerId?: string;
}) {
  const [open, setOpen] = useState(false);
  const children = (node.children ?? []).filter(
    (child) => child.name !== 'belongsTo' && child.type !== 'belongsTo' && child.name !== 'scopes' && child.type !== 'scopes',
  );
  const selected = node.node_id === selectedId;
  const rule = node.type === 'Rule';
  const rulesHolder = node.type === 'rules';
  const violating = (node.children ?? []).some(
    (child) => child.name === 'rules' && (child.children ?? []).some((hit) => hit.status === 'violating'),
  );
  const selectId = rule ? ownerId || node.node_id : node.node_id;
  return (
    <li
      data-node-id={node.node_id}
      data-kind={node.type}
      data-testid={rulesHolder ? 'tree-rules' : undefined}
      className={selected ? 'is-selected' : undefined}
    >
      <div className="tree-row">
        {children.length > 0 ? (
          <button
            type="button"
            className="tree-twist"
            data-testid={rulesHolder ? 'tree-expand-rules' : 'tree-expand'}
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
          className={[selected ? 'selected' : '', rule ? `rule-status ${node.status ?? ''}` : '', violating ? 'tree-violating' : '']
            .filter(Boolean)
            .join(' ')}
          onClick={() => onSelect(selectId)}
        >
          <KindMark kind={rule ? 'Rule' : rulesHolder ? 'Rules' : node.type} isFile={false} />
          <span className="node-name">{node.name}</span>
        </button>
      </div>
      {open && children.length > 0 ? (
        <ul>
          {children.map((child) => (
            <TreeNode
              key={child.node_id || child.name}
              node={child}
              selectedId={selectedId}
              onSelect={onSelect}
              ownerId={child.type === 'rules' || rule ? ownerId || node.node_id : undefined}
            />
          ))}
        </ul>
      ) : null}
    </li>
  );
}
