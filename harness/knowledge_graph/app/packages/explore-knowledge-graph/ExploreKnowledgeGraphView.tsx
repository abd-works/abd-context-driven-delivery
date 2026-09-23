import { type ChangeEvent, useEffect, useState } from 'react';
import { useKnowledgeGraph } from './knowledge-graph/knowledge-graph-client';
import { PracticeGraphTree } from './PracticeGraphTree';
import {
  pickerRelativePath,
  scanSourceFiles,
  type WorkspaceFile,
} from './knowledge-graph/workspace';
import wordmarkBlack from './brand/abd.works.wordmark.black.svg?url';
import wordmarkWhite from './brand/abd.works.wordmark.white.svg?url';

/**
 * ExploreKnowledgeGraphView — feature view.
 * Sources: harness/knowledge_graph/.context/knowledge-graph-explorer-sketch.md
 */
export function ExploreKnowledgeGraphView({ graphId = '' }: { graphId?: string }) {
  const {
    loading,
    folder: scannedFolder,
    listedNodes,
    listedTree,
    selectedNode,
    selectedRule,
    sourceFile,
    selectNode,
    followRelationship,
    filterGraph,
    selectFolder,
    filterOptions,
    refreshGraph,
  } = useKnowledgeGraph(graphId);
  const [practices, setPractices] = useState<string[] | null>(null);
  const [stages, setStages] = useState<string[] | null>(null);
  const [nodeTypes, setNodeTypes] = useState<string[] | null>(null);
  const [relationshipTypes, setRelationshipTypes] = useState<string[] | null>(
    null,
  );
  const [rules, setRules] = useState<string[] | null>(null);
  const [violations, setViolations] = useState(false);
  const [folder, setFolder] = useState(scannedFolder);
  const [theme, setTheme] = useState(
    () => document.documentElement.dataset.theme ?? '',
  );

  useEffect(() => {
    if (scannedFolder) {
      setFolder(scannedFolder);
    }
  }, [scannedFolder]);

  function applyTheme(next: '' | 'engineering') {
    setTheme(next);
    if (next) {
      document.documentElement.dataset.theme = next;
    } else {
      delete document.documentElement.dataset.theme;
    }
    window.localStorage.setItem('kg-theme', next);
  }

  async function pickFolder(list: FileList | null) {
    if (!list || list.length === 0) {
      return;
    }
    const picked: WorkspaceFile[] = [];
    let folderName = 'workspace';
    for (const file of Array.from(list)) {
      const mapped = pickerRelativePath(file.webkitRelativePath || file.name);
      folderName = mapped.folder;
      picked.push({
        relativePath: mapped.relativePath,
        text: await file.text(),
      });
    }
    const files = scanSourceFiles(picked);
    setFolder(folderName);
    selectFolder({ folder: folderName, files });
  }

  function applyFilters(next: {
    practices?: string[] | null;
    stages?: string[] | null;
    nodeTypes?: string[] | null;
    relationshipTypes?: string[] | null;
    rules?: string[] | null;
    violations?: boolean;
  }) {
    const practiceValues = 'practices' in next ? next.practices! : practices;
    const stageValues = 'stages' in next ? next.stages! : stages;
    const nodeTypeValues = 'nodeTypes' in next ? next.nodeTypes! : nodeTypes;
    const relationshipValues =
      'relationshipTypes' in next ? next.relationshipTypes! : relationshipTypes;
    const ruleValues = 'rules' in next ? next.rules! : rules;
    const violationsValue = next.violations ?? violations;
    filterGraph({
      practices: practiceValues ?? undefined,
      stages: stageValues ?? undefined,
      nodeTypes: nodeTypeValues ?? undefined,
      relationshipTypes: relationshipValues ?? undefined,
      rules: ruleValues ?? undefined,
      violations: violationsValue,
    });
  }

  const engineering = theme === 'engineering';
  const reportRules = selectedRule
    ? [selectedRule]
    : selectedNode?.rules ?? [];

  return (
    <main className="explore-knowledge-graph">
      <div className="knowledge-graph-explorer">
        <header className="site-nav">
          <div className="nav-brand">
            <a className="nav-logo" href="/" aria-label="abd.works">
              <img
                src={engineering ? wordmarkWhite : wordmarkBlack}
                alt="abd.works"
              />
            </a>
            <p className="page-hero-label">Knowledge graph</p>
          </div>
          <div className="nav-actions">
            <div className="mode-toggle" role="group" aria-label="Theme">
              <button
                type="button"
                className={engineering ? '' : 'is-active'}
                onClick={() => applyTheme('')}
              >
                <span className="mode-label">Executive</span>
                <span className="mode-icon" aria-hidden="true">
                  ☀
                </span>
              </button>
              <button
                type="button"
                className={engineering ? 'is-active' : ''}
                onClick={() => applyTheme('engineering')}
              >
                <span className="mode-label">Engineering</span>
                <span className="mode-icon" aria-hidden="true">
                  ☾
                </span>
              </button>
            </div>
            <button
              type="button"
              className="btn-refresh"
              data-testid="refresh-graph"
              disabled={loading}
              onClick={() => refreshGraph()}
            >
              Refresh
            </button>
          </div>
        </header>
        <div className="toolbar">
          <div className="folder-scan">
            <span className="btn-primary">
              Working folder
              <input
                data-testid="working-folder"
                type="file"
                multiple
                title="Select the folder that is the PracticeGraph root"
                onChange={(event) => {
                  void pickFolder(event.target.files);
                  event.target.value = '';
                }}
                {...({
                  webkitdirectory: '',
                  directory: '',
                } as Record<string, string>)}
              />
            </span>
            {folder ? (
              <span className="chosen-folder" data-testid="chosen-folder">
                {folder}
              </span>
            ) : null}
          </div>
          <div className="filters">
            <FilterList
              label="practice"
              values={practices}
              options={filterOptions.practices}
              onChange={(next) => {
                setPractices(next);
                setRules(null);
                applyFilters({ practices: next, rules: null });
              }}
            />
            <FilterList
              label="stage"
              values={stages}
              options={filterOptions.stages}
              onChange={(next) => {
                setStages(next);
                setRules(null);
                applyFilters({ stages: next, rules: null });
              }}
            />
            <FilterList
              label="node type"
              values={nodeTypes}
              options={filterOptions.node_types}
              onChange={(next) => {
                setNodeTypes(next);
                applyFilters({ nodeTypes: next });
              }}
            />
            <FilterList
              label="relationship"
              values={relationshipTypes}
              options={filterOptions.relationship_types}
              onChange={(next) => {
                setRelationshipTypes(next);
                applyFilters({ relationshipTypes: next });
              }}
            />
            <FilterList
              label="rule"
              values={rules}
              options={filterOptions.rules ?? []}
              onChange={(next) => {
                setRules(next);
                applyFilters({ rules: next });
              }}
            />
            <div className="filter-extras">
              <label>
                violations
                <input
                  type="checkbox"
                  checked={violations}
                  onChange={(event) => {
                    const next = event.target.checked;
                    setViolations(next);
                    applyFilters({ violations: next });
                  }}
                />
              </label>
            </div>
          </div>
        </div>
        <div className="split">
          <nav className="panel tree" data-testid="practice-graph-tree">
            {loading && <p className="empty-state">Loading KnowledgeGraph...</p>}
            {!loading && listedNodes.length === 0 && (
              <p className="empty-state">
                Select a working folder. That folder is the PracticeGraph root; classes load from it.
                A file in the tree only opens source.
              </p>
            )}
            <PracticeGraphTree
              key={folder}
              roots={listedTree}
              selectedId={selectedNode?.node_id ?? null}
              selectedRule={selectedRule?.slug ?? null}
              onSelect={selectNode}
            />
          </nav>
          <section className="panel" data-testid="source-file">
            {selectedNode ? (
              <div className="rule-report">
                <h2>{selectedNode.name}</h2>
                <p className="report-meta">
                  {[
                    selectedNode.practice,
                    selectedNode.stage,
                    selectedNode.semantic_type,
                  ]
                    .filter(Boolean)
                    .join(' · ')}
                </p>
                {reportRules.length === 0 && (
                  <p className="empty-state">No rules on this node.</p>
                )}
                {reportRules.map((entry) => (
                  <article
                    key={entry.slug}
                    className={`rule-card ${entry.status}`}
                  >
                    <h3>
                      {entry.slug}{' '}
                      <span className={`rule-status ${entry.status}`}>
                        {entry.status}
                      </span>
                    </h3>
                    {entry.body ? <p>{entry.body}</p> : null}
                    {entry.message ? (
                      <p className="violation">{entry.message}</p>
                    ) : null}
                  </article>
                ))}
                {sourceFile ? (
                  <pre className="source-file">
                    <h2>{sourceFile.file}</h2>
                    <code data-start-line={sourceFile.start_line}>
                      {sourceFile.text}
                    </code>
                  </pre>
                ) : null}
              </div>
            ) : (
              <p className="empty-state">
                Select a node or a rule to open its report. A folder stays on the tree.
              </p>
            )}
          </section>
        </div>
        {selectedNode && !selectedNode.is_file && (
          <button
            type="button"
            hidden
            onClick={() =>
              selectedNode && followRelationship(selectedNode.node_id)
            }
          >
            follow
          </button>
        )}
      </div>
    </main>
  );
}

function FilterList({
  label,
  values,
  options,
  onChange,
}: {
  label: string;
  values: string[] | null;
  options: string[];
  onChange: (next: string[] | null) => void;
}) {
  const [sort, setSort] = useState<'none' | 'asc' | 'desc'>('none');
  const shown = sortedOptions(options, sort);
  const selected = values === null ? options : values;
  return (
    <div className="filter-list">
      <div className="filter-heading">
        <span className="filter-label">{label}</span>
        <div className="filter-actions">
          <button type="button" onClick={() => onChange(null)}>
            All
          </button>
          <button type="button" onClick={() => onChange([])}>
            None
          </button>
          <button
            type="button"
            aria-label={`Sort ${label} A to Z`}
            className={sort === 'asc' ? 'is-active' : ''}
            onClick={() => setSort('asc')}
          >
            ↑
          </button>
          <button
            type="button"
            aria-label={`Sort ${label} Z to A`}
            className={sort === 'desc' ? 'is-active' : ''}
            onClick={() => setSort('desc')}
          >
            ↓
          </button>
          <button
            type="button"
            aria-label={`No sort for ${label}`}
            className={sort === 'none' ? 'is-active' : ''}
            onClick={() => setSort('none')}
          >
            −
          </button>
        </div>
      </div>
      <select
        multiple
        size={6}
        value={selected}
        onChange={(event: ChangeEvent<HTMLSelectElement>) => {
          onChange(
            Array.from(event.target.selectedOptions, (option) => option.value),
          );
        }}
      >
        {shown.map((name) => (
          <option key={name} value={name}>
            {name}
          </option>
        ))}
      </select>
    </div>
  );
}

function sortedOptions(
  options: string[],
  sort: 'none' | 'asc' | 'desc',
): string[] {
  if (sort === 'none') {
    return options;
  }
  const copy = [...options];
  copy.sort((left, right) => left.localeCompare(right));
  return sort === 'desc' ? copy.reverse() : copy;
}
