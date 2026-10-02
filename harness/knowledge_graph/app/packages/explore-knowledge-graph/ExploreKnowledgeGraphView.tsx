import { type ChangeEvent, useEffect, useState } from 'react';
import { useKnowledgeGraph } from './use-knowledge-graph';
import { KnowledgeGraphNode } from './knowledge-graph/knowledge-graph';
import {
  isScanSourcePath,
  pickerRelativePath,
  PICKER_UPLOAD_LIMIT,
  scanSourceFiles,
  type WorkspaceFile,
} from '../../../legacy/app/packages/explore-knowledge-graph/knowledge-graph/workspace';
import wordmarkBlack from './brand/abd.works.wordmark.black.svg?url';
import wordmarkWhite from './brand/abd.works.wordmark.white.svg?url';

type FilterPick = {
  practices: string[];
  stages: string[];
  node_types: string[];
  relationship_types: string[];
  rules: string[];
  violations: boolean;
};

const EMPTY_PICK: FilterPick = {
  practices: [],
  stages: [],
  node_types: [],
  relationship_types: [],
  rules: [],
  violations: false,
};

/**
 * ExploreKnowledgeGraphView — feature view.
 * Sources: harness/knowledge_graph/.context/knowledge-graph-explorer-sketch.md
 */
export function ExploreKnowledgeGraphView({ graphId = '' }: { graphId?: string }) {
  const [filtersOpen, setFiltersOpen] = useState(true);
  const {
    loading,
    workStatus,
    folder: scannedFolder,
    listedTree,
    filterOptions,
    members,
    selectedNode,
    selectNode,
    selectFolder,
    refreshGraph,
    createDatabase,
    refreshMaster,
    reloadWorkingCopy,
    scanError,
  } = useKnowledgeGraph(graphId);
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
    let folderName = 'workspace';
    const source: File[] = [];
    for (const file of Array.from(list)) {
      const mapped = pickerRelativePath(file.webkitRelativePath || file.name);
      folderName = mapped.folder;
      if (isScanSourcePath(mapped.relativePath)) {
        source.push(file);
      }
    }
    setFolder(folderName);
    if (source.length === 0 || source.length > PICKER_UPLOAD_LIMIT) {
      selectFolder({ folder: folderName });
      return;
    }
    const picked: WorkspaceFile[] = [];
    for (const file of source) {
      const mapped = pickerRelativePath(file.webkitRelativePath || file.name);
      picked.push({
        relativePath: mapped.relativePath,
        text: await file.text(),
      });
    }
    selectFolder({ folder: folderName, files: scanSourceFiles(picked) });
  }

  const [picked, setPicked] = useState<FilterPick>(EMPTY_PICK);
  const engineering = theme === 'engineering';
  const selectedId = selectedNode?.nodeId ?? '';

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
            <div className="database-actions" aria-busy={loading}>
              <button
                type="button"
                className="btn-refresh"
                data-testid="create-database"
                disabled={loading || !folder}
                onClick={() => createDatabase(folder)}
              >
                Create database
              </button>
              <button
                type="button"
                className="btn-refresh"
                data-testid="refresh-master"
                disabled={loading || !folder}
                onClick={() => refreshMaster(folder)}
              >
                Refresh master
              </button>
              <button
                type="button"
                className="btn-refresh"
                data-testid="reload-working-copy"
                disabled={loading || !folder}
                onClick={() => reloadWorkingCopy(folder)}
              >
                Reload working copy
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
            {workStatus ? (
              <p
                className={`work-progress is-${workStatus.phase}`}
                data-testid="work-progress"
                aria-live="polite"
              >
                {workStatus.phase === 'working'
                  ? `${workStatus.action}… ${workStatus.seconds}s`
                  : workStatus.phase === 'done'
                    ? `${workStatus.action} done`
                    : workStatus.detail || `${workStatus.action} failed`}
              </p>
            ) : null}
          </div>
        </header>
        <div className="toolbar">
          <div className="folder-scan">
            <span className="btn-primary">
              Repo folder
              <input
                data-testid="working-folder"
                type="file"
                multiple
                title="Select a repo folder to load the Knowledge Graph"
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
            <button
              type="button"
              className="filter-toggle"
              data-testid="toggle-filters"
              aria-expanded={filtersOpen}
              aria-label={filtersOpen ? 'Collapse filters' : 'Expand filters'}
              onClick={() => setFiltersOpen((open) => !open)}
            >
              {filtersOpen ? '▼' : '▶'}
            </button>
            {folder ? (
              <input
                className="chosen-folder"
                data-testid="chosen-folder"
                value={folder}
                spellCheck={false}
                onChange={(event: ChangeEvent<HTMLInputElement>) => {
                  setFolder(event.target.value);
                }}
                onBlur={() => {
                  const next = folder.trim();
                  if (next && !sameFolder(next, scannedFolder)) {
                    selectFolder({ folder: next });
                  }
                }}
                onKeyDown={(event) => {
                  if (event.key !== 'Enter') {
                    return;
                  }
                  const next = folder.trim();
                  if (next) {
                    selectFolder({ folder: next });
                  }
                }}
              />
            ) : null}
          </div>
          <div className="filters" hidden={!filtersOpen}>
            <FilterSelect
              label="Practice"
              testId="filter-practice"
              options={filterOptions.practices}
              selected={picked.practices}
              onChange={(practices) => setPicked((prev) => ({ ...prev, practices, node_types: [] }))}
            />
            <FilterSelect
              label="Stage"
              testId="filter-stage"
              options={typesFor(picked.practices, members, filterOptions.stages, 'stage')}
              selected={picked.stages}
              onChange={(stages) => setPicked((prev) => ({ ...prev, stages }))}
            />
            <FilterSelect
              label="Node"
              testId="filter-node"
              options={typesFor(picked.practices, members, filterOptions.node_types, 'type')}
              selected={picked.node_types}
              onChange={(node_types) => setPicked((prev) => ({ ...prev, node_types }))}
            />
            <FilterSelect
              label="Connector"
              testId="filter-connector"
              options={filterOptions.relationship_types}
              selected={picked.relationship_types}
              onChange={(relationship_types) => setPicked((prev) => ({ ...prev, relationship_types }))}
            />
            <FilterSelect
              label="Rule"
              testId="filter-rule"
              options={filterOptions.rules}
              selected={picked.rules}
              onChange={(rules) => setPicked((prev) => ({ ...prev, rules }))}
            />
            <div className="filter-extras">
              <button
                type="button"
                className={picked.violations ? 'is-active' : undefined}
                onClick={() => setPicked((prev) => ({ ...prev, violations: !prev.violations }))}
              >
                Violations
              </button>
            </div>
          </div>
        </div>
        <div className="split">
          <div className="panel" data-testid="practice-graph-tree">
            {loading && listedTree.length === 0 && (
              <p className="empty-state" data-testid="graph-loading">
                {workStatus
                  ? `${workStatus.action}… ${workStatus.seconds}s`
                  : 'Loading KnowledgeGraph...'}
              </p>
            )}
            {!loading && scanError && listedTree.length === 0 && (
              <p className="empty-state" data-testid="scan-error">
                {scanError}
              </p>
            )}
            <ul className="tree">
              {listedTree.map((node) => (
                <TreeNode
                  key={node.nodeId || node.name}
                  node={node}
                  depth={0}
                  picked={picked}
                  selectedId={selectedId}
                  onSelect={selectNode}
                />
              ))}
            </ul>
          </div>
          <div className="panel" data-testid="source-file">
            {selectedNode ? (
              <SourcePane node={selectedNode} folder={folder} />
            ) : (
              <p className="empty-state">Select a node</p>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}

function FilterSelect({
  label,
  testId,
  options,
  selected,
  onChange,
}: {
  label: string;
  testId: string;
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}) {
  return (
    <div className="filter-list">
      <div className="filter-heading">
        <span className="filter-label">{label}</span>
        <div className="filter-actions">
          <button type="button" onClick={() => onChange(options)}>
            All
          </button>
          <button type="button" onClick={() => onChange([])}>
            None
          </button>
        </div>
      </div>
      <select
        multiple
        data-testid={testId}
        value={selected}
        onChange={(event) => {
          onChange(Array.from(event.target.selectedOptions).map((option) => option.value));
        }}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}

function TreeNode({
  node,
  depth,
  picked,
  selectedId,
  onSelect,
}: {
  node: KnowledgeGraphNode;
  depth: number;
  picked: FilterPick;
  selectedId: string;
  onSelect: (nodeId: string) => void;
}) {
  const children = (node.children ?? []).filter((child) => shown(child, picked));
  if (!shown(node, picked)) {
    return null;
  }
  const kind = node.nodeType?.name ?? '';
  const selected = node.nodeId === selectedId;
  return (
    <li
      data-depth={depth}
      data-node-id={node.nodeId}
      data-kind={kind}
      className={selected ? 'is-selected' : undefined}
      onClick={(event) => {
        event.stopPropagation();
        onSelect(node.nodeId);
      }}
    >
      <div className="tree-row">
        <button
          type="button"
          className={[selected ? 'selected' : '', hitsViolation(node, picked) ? 'tree-violating' : '']
            .filter(Boolean)
            .join(' ') || undefined}
          title={kind}
          onClick={(event) => {
            event.stopPropagation();
            onSelect(node.nodeId);
          }}
        >
          <span className="node-name">{node.name}</span>
        </button>
      </div>
      {visibleHits(node, picked).map((hit) => (
        <span key={hit.slug} className={`rule-status ${hit.status}`}>
          {hit.slug}
        </span>
      ))}
      {children.length > 0 ? (
        <ul>
          {children.map((child) => (
            <TreeNode
              key={child.nodeId || child.name}
              node={child}
              depth={depth + 1}
              picked={picked}
              selectedId={selectedId}
              onSelect={onSelect}
            />
          ))}
        </ul>
      ) : null}
    </li>
  );
}

function SourcePane({ node, folder }: { node: KnowledgeGraphNode; folder: string }) {
  const file = node.source?.file ?? '';
  const [text, setText] = useState('');

  useEffect(() => {
    const initial = node.source?.text ?? '';
    setText(initial);
    if (!file || !folder || initial) {
      return;
    }
    const start = Number(node.source?.startLine) || 1;
    const end = Number(node.source?.endLine) || start + 80;
    let cancel = false;
    fetch('/api/knowledge-graphs/source', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        folder,
        ranges: [{ file, start_line: start, end_line: end }],
      }),
    })
      .then((response) => response.json())
      .then((body: { ranges?: Array<{ text?: string }> }) => {
        if (!cancel) {
          setText(body.ranges?.[0]?.text ?? node.name);
        }
      })
      .catch(() => {
        if (!cancel) {
          setText(node.name);
        }
      });
    return () => {
      cancel = true;
    };
  }, [node, file, folder]);

  return (
    <section className="knowledge-graph-panel" data-open="true" data-file={file}>
      <p className="source-path">{file || node.name}</p>
      <pre className="panel-source">{text || node.name}</pre>
    </section>
  );
}

function shown(node: KnowledgeGraphNode, picked: FilterPick): boolean {
  if (picked.violations) {
    return violates(node, picked) || (node.children ?? []).some((child) => shown(child, picked));
  }
  if (matches(node, picked)) {
    return true;
  }
  return (node.children ?? []).some((child) => shown(child, picked));
}

function violates(node: KnowledgeGraphNode, picked: FilterPick): boolean {
  return node.ruleHits.some((hit) => {
    if (hit.status !== 'violating') {
      return false;
    }
    return picked.rules.length === 0 || picked.rules.includes(hit.slug);
  });
}

function hitsViolation(node: KnowledgeGraphNode, picked: FilterPick): boolean {
  return picked.violations && violates(node, picked);
}

function visibleHits(node: KnowledgeGraphNode, picked: FilterPick): { slug: string; status: string }[] {
  if (!picked.violations && picked.rules.length === 0) {
    return [];
  }
  return node.ruleHits.filter((hit) => {
    if (picked.rules.length && !picked.rules.includes(hit.slug)) {
      return false;
    }
    if (picked.violations) {
      return hit.status === 'violating';
    }
    return true;
  });
}

function typesFor(
  practices: string[],
  members: { practice: string; type: string }[],
  fallback: string[],
  field: 'type' | 'stage',
): string[] {
  if (!practices.length || field === 'stage') {
    return fallback;
  }
  const found = members
    .filter((member) => practices.includes(member.practice))
    .map((member) => member.type);
  return found.length ? [...new Set(found)] : fallback;
}

function matches(node: KnowledgeGraphNode, picked: FilterPick): boolean {
  const active = Object.values(picked).some((values) => values.length > 0);
  if (!active) {
    return true;
  }
  if (picked.practices.length && !picked.practices.includes(node.practice)) {
    return false;
  }
  if (picked.stages.length && !picked.stages.includes(node.stage)) {
    return false;
  }
  if (picked.node_types.length && !picked.node_types.includes(node.nodeType?.name ?? '')) {
    return false;
  }
  return true;
}

function sameFolder(left: string, right: string): boolean {
  return left.replaceAll('/', '\\').toLowerCase() === right.replaceAll('/', '\\').toLowerCase();
}
