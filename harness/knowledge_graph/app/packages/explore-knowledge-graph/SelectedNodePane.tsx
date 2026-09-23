import type { ListedRule, ListedTreeNode, SourceRangeDto } from './knowledge-graph';
import { SourceSnippetEditor } from './SourceSnippetEditor';

type SelectedNode = {
  name: string;
  practice: string;
  stage: string;
  semantic_type: string;
  rules: ListedRule[];
};

export function SelectedNodePane({
  selectedNode,
  selectedTree,
  selectedRule,
  sourceFile,
  violations = false,
}: {
  selectedNode: SelectedNode | null;
  selectedTree?: ListedTreeNode | null;
  selectedRule: ListedRule | null;
  sourceFile: SourceRangeDto | null;
  violations?: boolean;
}) {
  const sections = selectedTree
    ? flattenSections(selectedTree, violations)
    : selectedNode
      ? [
          {
            node_id: selectedNode.name,
            name: selectedNode.name,
            path: selectedNode.name,
            semantic_type: selectedNode.semantic_type,
            source: sourceFile,
            origin: sourceFile,
            rules: selectedRule ? [selectedRule] : selectedNode.rules,
          },
        ]
      : [];
  if (sections.length === 0) {
    return (
      <p className="empty-state">
        Select a node to open its source and nested rules.
      </p>
    );
  }
  return (
    <div className="selected-node-pane" data-testid="selected-subtree">
      {sections.map((section, index) => (
        <NodeSection
          key={section.node_id}
          nested={index > 0}
          name={section.name}
          path={section.path}
          semanticType={section.semantic_type}
          rules={
            violations ? violatingRules(section.rules) : section.rules
          }
          source={section.source}
          origin={section.origin}
        />
      ))}
    </div>
  );
}

function flattenSections(
  node: ListedTreeNode,
  violations: boolean,
): Array<{
  node_id: string;
  name: string;
  path: string;
  semantic_type: string;
  source: SourceRangeDto | null;
  origin: SourceRangeDto | null;
  rules: ListedRule[];
}> {
  const children = violations
    ? node.children.filter(
        (child) =>
          child.semantic_type !== 'Operation' && child.semantic_type !== 'Property'
            ? true
            : child.rules.some((rule) => rule.status === 'violating') ||
              child.failed > 0,
      )
    : node.children;
  return [
    {
      node_id: node.node_id,
      name: node.name,
      path: node.path,
      semantic_type: node.semantic_type,
      source: node.source,
      origin: node.origin,
      rules: node.rules,
    },
    ...children.flatMap((child) => flattenSections(child, violations)),
  ];
}

function NodeSection({
  nested = false,
  name,
  path,
  semanticType,
  rules,
  source,
  origin,
}: {
  nested?: boolean;
  name: string;
  path: string;
  semanticType: string;
  rules: ListedRule[];
  source: SourceRangeDto | null;
  origin: SourceRangeDto | null;
}) {
  const shown = source?.text ? source : nested ? null : origin?.text ? origin : null;
  return (
    <div
      className="node-report"
      data-testid={nested ? 'child-node-report' : 'source-section'}
    >
      <h2>{name}</h2>
      <p className="report-meta">{semanticType}</p>
      {shown ? (
        <SourceSnippetEditor source={shown} excerpt={!nested} />
      ) : null}
      {rules.length > 0 ? (
        <div className="rule-report" data-testid="rule-report">
          {rules.map((entry) => (
            <article key={entry.slug} className={`rule-card ${entry.status}`}>
              <h3>
                {entry.slug}{' '}
                <span className={`rule-status ${entry.status}`}>{entry.status}</span>
              </h3>
              {entry.body ? <p>{entry.body}</p> : null}
              {entry.message ? <p className="violation">{entry.message}</p> : null}
              {entry.status === 'violating' || entry.message ? (
                <button
                  type="button"
                  className="copy-prompt"
                  data-testid="copy-info-to-prompt"
                  onClick={() =>
                    void navigator.clipboard.writeText(
                      violationPrompt({
                        path,
                        semanticType,
                        source: source?.file ? source : origin,
                        rule: entry,
                      }),
                    )
                  }
                >
                  Copy info to prompt
                </button>
              ) : null}
            </article>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function violatingRules(rules: ListedRule[]): ListedRule[] {
  return rules.filter((rule) => rule.status === 'violating');
}

function violationPrompt({
  path,
  semanticType,
  source,
  rule,
}: {
  path: string;
  semanticType: string;
  source: SourceRangeDto | null;
  rule: ListedRule;
}): string {
  const file = source?.file
    ? source.start_line >= 1
      ? `${source.file}:${source.start_line}-${source.end_line}`
      : source.file
    : '';
  const snippet = source?.text ? `\n\nSource:\n${source.text}` : '';
  return [
    `Fix this Knowledge Graph rule violation.`,
    `Node: ${path} (${semanticType})`,
    file ? `File: ${file}` : '',
    `Rule: ${rule.slug}`,
    rule.body,
    `Violation: ${rule.message}`,
    snippet,
  ]
    .filter((line) => line)
    .join('\n');
}

