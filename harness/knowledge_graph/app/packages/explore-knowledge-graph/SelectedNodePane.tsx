import { useState } from 'react';
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
  const [showGuidance, setShowGuidance] = useState(true);
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
  const panePrompt = paneCopyText(sections, violations);
  return (
    <div className="selected-node-pane" data-testid="selected-subtree">
      <div className="pane-actions">
        <label className="guidance-toggle" data-testid="toggle-guidance">
          guidance
          <input
            type="checkbox"
            checked={showGuidance}
            onChange={(event) => setShowGuidance(event.target.checked)}
          />
        </label>
        {panePrompt ? (
          <button
            type="button"
            className="copy-prompt"
            data-testid="copy-pane-to-prompt"
            onClick={() => void navigator.clipboard.writeText(panePrompt)}
          >
            Copy pane to prompt
          </button>
        ) : null}
      </div>
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
          showGuidance={showGuidance}
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
  showGuidance = true,
}: {
  nested?: boolean;
  name: string;
  path: string;
  semanticType: string;
  rules: ListedRule[];
  source: SourceRangeDto | null;
  origin: SourceRangeDto | null;
  showGuidance?: boolean;
}) {
  const shown =
    showGuidance && (source?.text ? source : nested ? null : origin?.text ? origin : null);
  const listed = showGuidance ? rules : violatingRules(rules);
  if (!showGuidance && listed.length === 0) {
    return null;
  }
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
      {listed.length > 0 ? (
        <div className="rule-report" data-testid="rule-report">
          {listed.map((entry) => (
            <article key={entry.slug} className={`rule-card ${entry.status}`}>
              <h3>
                {entry.slug}{' '}
                <span className={`rule-status ${entry.status}`}>{entry.status}</span>
              </h3>
              {showGuidance && (entry.practice || entry.fidelity) ? (
                <p className="report-meta">
                  {[entry.practice, entry.fidelity].filter(Boolean).join(' · ')}
                </p>
              ) : null}
              {showGuidance && entry.body ? <p>{entry.body}</p> : null}
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

const VIOLATION_TASK_PROCESS = [
  'Fix the following violations, follow this process',
  '- save the below as a violation task list.',
  '- use a non-blocking sub agent if available to you',
  '- fix each violation as a separate turn, check off each fix as you do so',
  '- ignore violations that are marked as fixed',
].join('\n');

function paneCopyText(
  sections: Array<{
    path: string;
    semantic_type: string;
    source: SourceRangeDto | null;
    origin: SourceRangeDto | null;
    rules: ListedRule[];
  }>,
  violations: boolean,
): string {
  const prompts: string[] = [];
  for (const section of sections) {
    const rules = violations ? violatingRules(section.rules) : section.rules;
    const source = section.source?.file ? section.source : section.origin;
    for (const rule of rules) {
      if (rule.status !== 'violating' && !rule.message) {
        continue;
      }
      prompts.push(
        violationPrompt({
          path: section.path,
          semanticType: section.semantic_type,
          source,
          rule,
        }),
      );
    }
  }
  if (prompts.length === 0) {
    return '';
  }
  return [VIOLATION_TASK_PROCESS, ...prompts].join('\n\n---\n\n');
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
  return [
    `Fix this Violation.`,
    `[ ] done`,
    `Node: ${path} (${semanticType})`,
    file ? `File: ${file}` : '',
    `Rule: ${rule.slug}`,
    rule.practice ? `Practice: ${rule.practice}` : '',
    rule.fidelity ? `Fidelity: ${rule.fidelity}` : '',
    rule.body,
    `Violation: ${rule.message}`,
  ]
    .filter((line) => line)
    .join('\n');
}

