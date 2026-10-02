import { useEffect, useMemo, useState } from 'react';
import { callBodiesIn, classBodiesIn, directCallsIn, type CallBody, type ClassBody } from './call-expansion';
import { KnowledgeGraphHttpClient } from './knowledge-graph/knowledge-graph-client';
import {
  stepTitle,
  type ListedRule,
  type ListedTreeNode,
  type SourceRangeDto,
} from './knowledge-graph/knowledge-graph';
import { kindLabel } from './PracticeGraphTree';
import { SourceSnippetEditor } from './SourceSnippetEditor';
import { sourcesMissingText, sourceKey, withSourceText } from './source-text';

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
  folder = '',
  violations = false,
  showRules = true,
}: {
  selectedNode: SelectedNode | null;
  selectedTree?: ListedTreeNode | null;
  selectedRule: ListedRule | null;
  sourceFile: SourceRangeDto | null;
  folder?: string;
  violations?: boolean;
  showRules?: boolean;
}) {
  const selectedId = selectedTree?.node_id ?? selectedNode?.name ?? '';
  const [opened, setOpened] = useState<{ id: string; tree: ListedTreeNode } | null>(null);
  const tree = opened?.id === selectedId ? opened.tree : selectedTree;
  useEffect(() => {
    const gaps = sourcesMissingText(selectedTree);
    if (!folder || !selectedTree || gaps.length === 0) {
      return;
    }
    let cancel = false;
    KnowledgeGraphHttpClient.readSource(folder, gaps)
      .then((ranges) => {
        if (cancel || !selectedTree) {
          return;
        }
        const texts = new Map(ranges.map((range) => [sourceKey(range), range.text ?? '']));
        setOpened({ id: selectedTree.node_id, tree: withSourceText(selectedTree, texts) });
      })
      .catch(() => {
        if (!cancel) {
          setOpened(null);
        }
      });
    return () => {
      cancel = true;
    };
  }, [folder, selectedTree]);
  const [openState, setOpenState] = useState<{
    id: string;
    sourcesOpen: boolean | null;
    overrides: Record<string, boolean>;
  }>({ id: '', sourcesOpen: null, overrides: {} });
  const sourcesOpen = openState.id === selectedId ? openState.sourcesOpen : null;
  const sourceOverrides = openState.id === selectedId ? openState.overrides : {};
  const rootType = selectedTree?.semantic_type ?? selectedNode?.semantic_type ?? '';
  const calls = useMemo(
    () => (tree ? callBodiesIn(tree) : undefined),
    [tree],
  );
  const classes = useMemo(
    () => (tree ? classBodiesIn(tree) : undefined),
    [tree],
  );
  const anchored = useMemo(
    () =>
      tree && (rootType === 'Step' || rootType === 'Example')
        ? directCallsIn(tree)
        : undefined,
    [tree, rootType],
  );
  const listClasses = rootType === 'Step' || rootType === 'Example';
  const sections = tree
    ? flattenSections(
        tree,
        violations,
        rootType === 'Operation' || rootType === 'Property' ? '1' : '',
      )
    : selectedNode
      ? [
          {
            sectionKey: selectedNode.name,
            number: '',
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
  const visibleSections = showRules
    ? sections
    : sections.map((section) => ({ ...section, rules: [] }));
  if (visibleSections.length === 0) {
    return (
      <p className="empty-state">
        Select a node to open its source and nested rules.
      </p>
    );
  }
  const panePrompt = paneCopyText(visibleSections, violations);
  const nestsCalls = rootType === 'Operation' || rootType === 'Property';
  const sourceIsOpen = (section: (typeof visibleSections)[number]) => {
    if (section.sectionKey in sourceOverrides) {
      return sourceOverrides[section.sectionKey];
    }
    if (sourcesOpen === false) {
      return false;
    }
    if (sourcesOpen === true) {
      return true;
    }
    return section.semantic_type === 'Operation' || section.semantic_type === 'Property'
      ? true
      : !(nestsCalls && section.semantic_type === 'OoadClass');
  };
  const hasSource = visibleSections.some(
    (section) => section.source?.text || section.origin?.text,
  );
  const allSourcesClosed =
    hasSource &&
    visibleSections
      .filter((section) => section.source?.text || section.origin?.text)
      .every((section) => !sourceIsOpen(section));
  return (
    <div className="selected-node-pane" data-testid="selected-subtree">
      {panePrompt || hasSource ? (
      <div className="pane-actions">
          {hasSource ? (
            <button
              type="button"
              className="pane-tool pane-toggle-all"
              data-testid="pane-toggle-all"
              aria-expanded={!allSourcesClosed}
              onClick={() => {
                setOpenState({
                  id: selectedId,
                  sourcesOpen: allSourcesClosed,
                  overrides: {},
                });
              }}
            >
              {allSourcesClosed ? 'Expand all' : 'Collapse all'}
            </button>
          ) : null}
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
      ) : null}
      {visibleSections.map((section, index) => (
        <NodeSection
          key={section.sectionKey}
          nested={index > 0}
          number={section.number}
          name={section.name}
          path={section.path}
          semanticType={section.semantic_type}
          rules={
            violations ? violatingRules(section.rules) : section.rules
          }
          source={section.source}
          origin={section.origin}
          sourceOpen={sourceIsOpen(section)}
          onToggleSource={() =>
            setOpenState({
              id: selectedId,
              sourcesOpen,
              overrides: {
                ...sourceOverrides,
                [section.sectionKey]: !sourceIsOpen(section),
              },
            })
          }
          collapseAll={
            index === 0 && hasSource
              ? {
                  closed: allSourcesClosed,
                  onToggle: () => {
                    setOpenState({
                      id: selectedId,
                      sourcesOpen: allSourcesClosed,
                      overrides: {},
                    });
                  },
                }
              : null
          }
          selectedRuleSlug={selectedRule?.slug ?? null}
          calls={index === 0 ? calls : undefined}
          classes={index === 0 ? classes : undefined}
          anchored={index === 0 ? anchored : undefined}
          listClasses={index === 0 && listClasses}
        />
      ))}
    </div>
  );
}

function excerptSource(node: ListedTreeNode): SourceRangeDto | null {
  if (node.source?.text) {
    return node.source;
  }
  if (node.semantic_type === 'Step' || node.semantic_type === 'Example') {
    return { file: '', start_line: 1, end_line: 1, text: node.name };
  }
  return node.source;
}

function flattenSections(
  node: ListedTreeNode,
  violations: boolean,
  number = '',
  keyPrefix = 'root',
  includeSelf = true,
): Array<{
  sectionKey: string;
  number: string;
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
  const callable = node.semantic_type === 'Operation' || node.semantic_type === 'Property';
  const inline =
    callable || node.semantic_type === 'Step' || node.semantic_type === 'Example';
  let callCount = 0;
  const own = includeSelf
    ? [
        {
          sectionKey: `${keyPrefix}:${node.node_id}`,
          number: callable ? number : '',
          node_id: node.node_id,
          name: node.name,
          path: node.path,
          semantic_type: node.semantic_type,
          source: excerptSource(node),
          origin: node.origin,
          rules: node.rules,
        },
      ]
    : [];
  if (inline && includeSelf) {
    return own;
  }
  return [
    ...own,
    ...children.flatMap((child, index) => {
      const childCallable =
        child.semantic_type === 'Operation' || child.semantic_type === 'Property';
      const childNumber = childCallable ? `${number}.${++callCount}` : '';
      return flattenSections(
        child,
        violations,
        childNumber,
        `${keyPrefix}.${index}`,
        !(callable && childCallable),
      );
    }),
  ];
}

function NodeSection({
  nested = false,
  number = '',
  name,
  path,
  semanticType,
  rules,
  source,
  origin,
  sourceOpen = true,
  onToggleSource,
  collapseAll = null,
  selectedRuleSlug = null,
  calls,
  classes,
  anchored,
  listClasses = false,
}: {
  nested?: boolean;
  number?: string;
  name: string;
  path: string;
  semanticType: string;
  rules: ListedRule[];
  source: SourceRangeDto | null;
  origin: SourceRangeDto | null;
  sourceOpen?: boolean;
  onToggleSource?: () => void;
  collapseAll?: { closed: boolean; onToggle: () => void } | null;
  selectedRuleSlug?: string | null;
  calls?: ReturnType<typeof callBodiesIn>;
  classes?: ClassBody[];
  anchored?: CallBody[];
  listClasses?: boolean;
}) {
  const shown = source?.text ? source : nested ? null : origin?.text ? origin : null;
  const typeLabel = kindLabel(semanticType, false);
  const title = stepTitle(name, semanticType, '', shown?.text ?? source?.text ?? origin?.text ?? '');
  const heading = number ? `${number}${number.includes('.') ? '' : '.'} ${title}` : title;
  const allToggle = collapseAll ? (
    <button
      type="button"
      className="source-toggle pane-source-toggle"
      data-testid="toggle-all-sources"
      aria-expanded={!collapseAll.closed}
      aria-label={collapseAll.closed ? 'Expand all' : 'Collapse all'}
      onClick={collapseAll.onToggle}
    >
      {collapseAll.closed ? '▶' : '▼'}
    </button>
  ) : null;
  return (
    <div
      className="node-report"
      data-nested={nested ? 'true' : 'false'}
      data-kind={semanticType}
      data-testid={nested ? 'child-node-report' : 'source-section'}
    >
      {shown ? (
        <SourceSnippetEditor
          source={shown}
          label={heading}
          typeLabel={typeLabel}
          excerpt={!nested}
          open={sourceOpen}
          onToggle={collapseAll ? collapseAll.onToggle : onToggleSource}
          toggleTestId={collapseAll ? 'toggle-all-sources' : 'toggle-source'}
          toggleLabel={
            collapseAll
              ? collapseAll.closed
                ? 'Expand all'
                : 'Collapse all'
              : semanticType === 'OoadClass'
                ? sourceOpen
                  ? 'Collapse class'
                  : 'Expand class'
                : undefined
          }
          mark={semanticType === 'OoadClass' ? 'class' : 'chevron'}
          calls={calls}
          classes={classes}
          anchored={anchored}
          listClasses={listClasses}
        />
      ) : (
        <h2 className="node-heading">
          {allToggle}
          {heading} <span className="source-type">({typeLabel})</span>
        </h2>
      )}
      {rules.length > 0 ? (
        <RuleReport
          rules={rules}
          path={path}
          semanticType={semanticType}
          source={source}
          origin={origin}
          selectedRuleSlug={selectedRuleSlug}
        />
      ) : null}
    </div>
  );
}

function RuleReport({
  rules,
  path,
  semanticType,
  source,
  origin,
  selectedRuleSlug,
}: {
  rules: ListedRule[];
  path: string;
  semanticType: string;
  source: SourceRangeDto | null;
  origin: SourceRangeDto | null;
  selectedRuleSlug: string | null;
}) {
  const [open, setOpen] = useState(
    Boolean(selectedRuleSlug && rules.some((entry) => entry.slug === selectedRuleSlug)),
  );
  return (
    <div className="rule-report" data-testid="rule-report">
      <button
        type="button"
        className="rules-toggle"
        data-testid="expand-pane-rules"
        aria-expanded={open}
        onClick={() => setOpen((current) => !current)}
      >
        <span aria-hidden="true">{open ? '▼' : '▶'}</span>
        rules ({rules.length})
      </button>
      {open ? (
        <article className="rule-card" data-testid="rule-section">
          {rules.map((entry) => (
            <div key={entry.slug} className={`rule-line ${entry.status}`}>
              <h3>
                {entry.slug}{' '}
                <span className={`rule-status ${entry.status}`}>{entry.status}</span>
              </h3>
              {entry.practice || entry.fidelity ? (
                <p className="report-meta">
                  {[entry.practice, entry.fidelity].filter(Boolean).join(' · ')}
                </p>
              ) : null}
              {entry.body ? <p>{entry.body}</p> : null}
              {entry.message ? <p className="violation">{entry.message}</p> : null}
              {entry.status === 'violating' || entry.message ? (
                <div className="copy-prompt-actions">
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
                  <button
                    type="button"
                    className="copy-prompt"
                    data-testid="copy-this-rule-is-wrong-prompt"
                    onClick={() =>
                      void navigator.clipboard.writeText(
                        wrongRulePrompt({
                          path,
                          semanticType,
                          source: source?.file ? source : origin,
                          rule: entry,
                        }),
                      )
                    }
                  >
                    Copy this rule is wrong prompt
                  </button>
                </div>
              ) : null}
            </div>
          ))}
        </article>
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

function sourceFileLabel(source: SourceRangeDto | null): string {
  if (!source?.file) {
    return '';
  }
  return source.start_line >= 1
    ? `${source.file}:${source.start_line}-${source.end_line}`
    : source.file;
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
  const file = sourceFileLabel(source);
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

function wrongRulePrompt({
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
  const file = sourceFileLabel(source);
  return [
    'The following rule is wrong. We need to fix the rule. I will explain why the rule is wrong.',
    `Rule: ${rule.slug}`,
    rule.practice ? `Practice: ${rule.practice}` : '',
    rule.fidelity ? `Fidelity: ${rule.fidelity}` : '',
    `Node: ${path} (${semanticType})`,
    file ? `File: ${file}` : '',
    rule.body,
    rule.message ? `Violation: ${rule.message}` : '',
  ]
    .filter((line) => line)
    .join('\n');
}

