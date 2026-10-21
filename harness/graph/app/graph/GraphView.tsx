import { useEffect, useRef, useState } from 'react';
import { KindMark } from '../kind-mark';
import type { GraphTree } from '../filter/FilterClient';
import { ruleHits, selectionForRule, type GraphSelection } from './graph-selection';
import { queryProgress } from './query-progress';

type GraphViewProps = {
  trees: GraphTree[];
  loading: boolean;
  loadingLabel?: string;
  loadingLog?: string[];
  error: string;
  selectedId: string;
  activeRule: string;
  onSelect: (selection: GraphSelection) => void;
};

function elapsedLabel(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return `${minutes}:${rest.toString().padStart(2, '0')}`;
}

export function GraphView({ trees, loading, loadingLabel, loadingLog = [], error, selectedId, activeRule, onSelect }: GraphViewProps) {
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
  const fraction = progress.total > 0 ? Math.min(100, Math.round((100 * progress.index) / progress.total)) : 0;
  return (
    <div className="panel" data-testid="practice-graph-tree">
      {loading ? (
        <div className="empty-state work-progress is-working" data-testid="extraction-progress">
          <p className="query-now">{shown}</p>
          {progress.total > 0 ? (
            <div
              className="load-meter"
              data-testid="load-meter"
              role="progressbar"
              aria-valuenow={progress.index}
              aria-valuemin={0}
              aria-valuemax={progress.total}
              aria-label={headline}
            >
              <span style={{ width: `${fraction}%` }} />
            </div>
          ) : null}
          <ol className="loading-log" data-testid="loading-log" ref={log}>
            {progress.steps.map((step) => (
              <li key={`${step.index}-${step.name}`}>
                {step.index}/{step.total} {step.name}
              </li>
            ))}
            {progress.steps.length === 0
              ? (loadingLog.length > 0 ? loadingLog.slice(-12) : [shown]).map((line, index) => (
                  <li key={`${index}-${line}`}>{line}</li>
                ))
              : null}
            {active && progress.detail ? <li className="is-current">{progress.detail}</li> : null}
          </ol>
        </div>
      ) : null}
      {error && !loading ? (
        <div className="scan-error empty-state" data-testid="scan-error">
          <button type="button" className="copy-diagnosis" onClick={() => void navigator.clipboard.writeText(error)}>
            Copy for AI
          </button>
          <pre>{error}</pre>
        </div>
      ) : null}
      <ul className="tree">
        {trees.map((node) => (
          <TreeNode key={node.node_id || node.name} node={node} selectedId={selectedId} activeRule={activeRule} onSelect={onSelect} />
        ))}
      </ul>
    </div>
  );
}

function TreeNode({
  node,
  selectedId,
  activeRule,
  onSelect,
  ownerId,
}: {
  node: GraphTree;
  selectedId: string;
  activeRule: string;
  onSelect: (selection: GraphSelection) => void;
  ownerId?: string;
}) {
  const [open, setOpen] = useState(false);
  const children = (node.children ?? []).filter(
    (child) => child.name !== 'belongsTo' && child.type !== 'belongsTo' && child.name !== 'scopes' && child.type !== 'scopes',
  );
  const rule = node.type === 'Rule';
  const rulesHolder = node.type === 'rules';
  const selected = rule ? ownerId === selectedId && node.name === activeRule : node.node_id === selectedId;
  const violating = (node.children ?? []).some(
    (child) => child.name === 'rules' && (child.children ?? []).some((hit) => hit.status === 'violating'),
  );
  const hits = ruleHits(node);
  const violationHint = rule && node.status === 'violating' && hits.length > 0 ? hits.map((hit) => hit.message).join('\n') : undefined;
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
          title={violationHint}
          data-testid={rule ? (violationHint ? 'tree-violation-rule' : 'tree-rule') : undefined}
          onClick={() => onSelect(rule ? selectionForRule(ownerId || node.node_id, node) : { nodeId: node.node_id })}
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
              activeRule={activeRule}
              onSelect={onSelect}
              ownerId={child.type === 'rules' || child.type === 'Rule' ? ownerId || node.node_id : undefined}
            />
          ))}
        </ul>
      ) : null}
    </li>
  );
}
