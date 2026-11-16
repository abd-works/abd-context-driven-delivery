import { useEffect, useState } from 'react';
import { KindMark } from '../labels/kind-mark';
import type { ExplorerEntryData } from '@cdd/harness/graph/graph';
import { childrenLeftOut, childrenOf, isRule, ruleHits, selectionForRule, type GraphSelection, type TreeItem } from './graph-selection';
import { reasonOf } from './graph-failures';
import { failures } from './graph-page';
import { LoadProgressView } from './LoadProgressView';

type GraphViewProps = {
  trees: ExplorerEntryData[];
  loading: boolean;
  loadingLabel?: string;
  loadingLog?: string[];
  error: string;
  selectedId: string;
  activeRule: string;
  onSelect: (selection: GraphSelection) => void;
  // Reads the entries a closed entry left out, the first time a person opens it.
  onOpenBranch: (nodeId: string) => Promise<void>;
};

export function GraphView({ trees, loading, loadingLabel, loadingLog = [], error, selectedId, activeRule, onSelect, onOpenBranch }: GraphViewProps) {
  return (
    <div className="panel" data-testid="practice-graph-tree">
      {loading ? <LoadProgressView loadingLabel={loadingLabel} loadingLog={loadingLog} /> : null}
      {error && !loading ? (
        <div className="scan-error empty-state" data-testid="scan-error">
          <button type="button" className="copy-diagnosis" onClick={() => void copyDiagnosis(error)}>
            Copy for AI
          </button>
          <pre>{error}</pre>
        </div>
      ) : null}
      <ul className="tree">
        {trees.map((node) => (
          <TreeNode key={node.node_id || node.name} node={node} selectedId={selectedId} activeRule={activeRule} onSelect={onSelect} onOpenBranch={onOpenBranch} />
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
  onOpenBranch,
  ownerId,
}: {
  node: TreeItem;
  selectedId: string;
  activeRule: string;
  onSelect: (selection: GraphSelection) => void;
  onOpenBranch: (nodeId: string) => Promise<void>;
  ownerId?: string;
}) {
  const [open, setOpen] = useState(false);
  const children = childrenOf(node);
  const leftOut = childrenLeftOut(node);
  // An open entry whose answer left its children out reads them: when a person opens it, and when new trees, after a
  // change of filter, arrive under an entry already open.
  useEffect(() => {
    if (open && leftOut > 0) void onOpenBranch(node.node_id);
  }, [open, leftOut, node.node_id]);
  const toggle = () => setOpen((value) => !value);
  const rule = node.type === 'Rule';
  const rulesHolder = node.type === 'rules';
  const selected = rule ? ownerId === selectedId && node.name === activeRule : node.node_id === selectedId;
  const violating = children.some(
    (child) => child.name === 'rules' && childrenOf(child).some((hit) => isRule(hit) && hit.status === 'violating'),
  );
  const hits = isRule(node) ? ruleHits(node) : [];
  const violationHint = isRule(node) && node.status === 'violating' && hits.length > 0 ? hits.map((hit) => hit.message).join('\n') : undefined;
  return (
    <li
      data-node-id={node.node_id}
      data-kind={node.type}
      data-testid={rulesHolder ? 'tree-rules' : undefined}
      className={selected ? 'is-selected' : undefined}
    >
      <div className="tree-row">
        {children.length > 0 || leftOut > 0 ? (
          <button
            type="button"
            className="tree-twist"
            data-testid={rulesHolder ? 'tree-expand-rules' : 'tree-expand'}
            aria-expanded={open}
            aria-label={`${open ? 'Collapse' : 'Expand'} ${node.name}`}
            onClick={toggle}
          >
            {open ? '▼' : '▶'}
          </button>
        ) : (
          <span className="tree-twist-spacer" />
        )}
        <button
          type="button"
          className={[selected ? 'selected' : '', isRule(node) ? `rule-status ${node.status}` : '', violating ? 'tree-violating' : '']
            .filter(Boolean)
            .join(' ')}
          title={violationHint}
          data-testid={rule ? (violationHint ? 'tree-violation-rule' : 'tree-rule') : undefined}
          onClick={() => onSelect(rule && isRule(node) ? selectionForRule(ownerId || node.node_id, node) : { nodeId: node.node_id })}
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
              onOpenBranch={onOpenBranch}
              ownerId={child.type === 'rules' || child.type === 'Rule' ? ownerId || node.node_id : undefined}
            />
          ))}
        </ul>
      ) : null}
    </li>
  );
}

// The diagnosis copied for a person to paste to an agent; a copy the browser refuses is shown and sent to the chat.
async function copyDiagnosis(error: string) {
  try {
    await navigator.clipboard.writeText(error);
  } catch (cause) {
    failures.fail(`The diagnosis was not copied: ${reasonOf(cause)}`, 'Copy for AI in the Graph app');
  }
}
