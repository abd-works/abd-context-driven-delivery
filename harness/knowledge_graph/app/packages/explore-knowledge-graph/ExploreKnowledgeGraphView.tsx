import { type ChangeEvent, useEffect, useRef, useState } from 'react';
import Editor, { type OnMount } from '@monaco-editor/react';
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

function pickFromLocation(): FilterPick {
  if (typeof window === 'undefined') {
    return EMPTY_PICK;
  }
  const params = new URLSearchParams(window.location.search);
  const rule = params.get('rule');
  return {
    ...EMPTY_PICK,
    violations: params.get('violations') === '1',
    rules: rule ? [rule] : [],
  };
}

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

  const [picked, setPicked] = useState<FilterPick>(pickFromLocation);
  const engineering = theme === 'engineering';
  const selectedId = selectedNode?.nodeId ?? '';

  const [showRules, setShowRules] = useState(false);
  const [openIds, setOpenIds] = useState<Set<string>>(new Set());
  const treeKey = listedTree.map((node) => node.nodeId).join('|');
  const filterKey = [
    picked.violations ? '1' : '0',
    picked.rules.join(','),
    picked.practices.join(','),
    picked.node_types.join(','),
    picked.stages.join(','),
  ].join('|');

  useEffect(() => {
    const next = new Set<string>();
    if (listedTree.length === 1 && listedTree[0]?.nodeId) {
      next.add(listedTree[0].nodeId);
    }
    if (filterKey !== '0||||') {
      expandShown(listedTree, picked, next);
    }
    if (showRules) {
      openAllRules(listedTree, next);
    }
    setOpenIds(next);
  }, [treeKey, filterKey, showRules]);

  useEffect(() => {
    if (!picked.violations) {
      return;
    }
    const current = findNode(listedTree, selectedId);
    if (current && violates(current, picked)) {
      return;
    }
    const match = firstViolating(listedTree, picked);
    if (match) {
      selectNode(match.nodeId);
    }
  }, [picked, listedTree, selectedId, selectNode]);

  function toggleOpen(id: string) {
    setOpenIds((prev) => {
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
            <input
              className="chosen-folder"
              data-testid="chosen-folder"
              value={folder}
              placeholder="Repository folder"
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
              <FilterSwitch
                label="Violations"
                pressed={picked.violations}
                onClick={() => setPicked((prev) => ({ ...prev, violations: !prev.violations }))}
              />
              <FilterSwitch
                label="Show rules"
                pressed={showRules}
                onClick={() => setShowRules((on) => !on)}
              />
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
                  showRules={showRules}
                  selectedId={selectedId}
                  openIds={openIds}
                  onToggle={toggleOpen}
                  onSelect={selectNode}
                />
              ))}
            </ul>
          </div>
          <div className="panel" data-testid="source-file">
            {selectedNode ? (
              <SourcePane node={selectedNode} folder={folder} picked={picked} showRules={showRules} />
            ) : (
              <p className="empty-state">Select a node</p>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}

function FilterSwitch({
  label,
  pressed,
  onClick,
}: {
  label: string;
  pressed: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      className={pressed ? 'filter-switch is-on' : 'filter-switch'}
      aria-pressed={pressed}
      onClick={onClick}
    >
      <span className="filter-switch-label">{label}</span>
      <span className="filter-switch-track" aria-hidden="true">
        <span className="filter-switch-knob" />
      </span>
    </button>
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
  showRules,
  selectedId,
  openIds,
  onToggle,
  onSelect,
}: {
  node: KnowledgeGraphNode;
  depth: number;
  picked: FilterPick;
  showRules: boolean;
  selectedId: string;
  openIds: Set<string>;
  onToggle: (id: string) => void;
  onSelect: (nodeId: string) => void;
}) {
  const children = (node.children ?? []).filter((child) => shown(child, picked));
  if (!shown(node, picked)) {
    return null;
  }
  const rules = rulesFor(node, picked, showRules);
  const links = node.relationships ?? [];
  const rulesId = `${node.nodeId}::rules`;
  const linksId = `${node.nodeId}::relationships`;
  const open = openIds.has(node.nodeId);
  const rulesOpen = openIds.has(rulesId);
  const linksOpen = openIds.has(linksId);
  const canOpen = children.length > 0 || rules.length > 0 || links.length > 0;
  const kind = node.nodeType?.name ?? '';
  const selected = node.nodeId === selectedId;
  return (
    <li
      data-depth={depth}
      data-node-id={node.nodeId}
      data-kind={kind}
      className={selected ? 'is-selected' : undefined}
    >
      <div className="tree-row">
        {canOpen ? (
          <button
            type="button"
            className="tree-twist"
            data-testid="tree-expand"
            aria-expanded={open}
            aria-label={`${open ? 'Collapse' : 'Expand'} ${node.name}`}
            onClick={(event) => {
              event.stopPropagation();
              onToggle(node.nodeId);
            }}
          >
            {open ? '▼' : '▶'}
          </button>
        ) : (
          <span className="tree-twist-spacer" />
        )}
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
      {open && canOpen ? (
        <ul>
          {children.map((child) => (
            <TreeNode
              key={child.nodeId || child.name}
              node={child}
              depth={depth + 1}
              picked={picked}
              showRules={showRules}
              selectedId={selectedId}
              openIds={openIds}
              onToggle={onToggle}
              onSelect={onSelect}
            />
          ))}
          {rules.length > 0 ? (
            <li data-depth={depth + 1} data-testid="tree-rules">
              <div className="tree-row">
                <button
                  type="button"
                  className="tree-twist"
                  data-testid="tree-expand-rules"
                  aria-expanded={rulesOpen}
                  aria-label={`${rulesOpen ? 'Collapse' : 'Expand'} rules`}
                  onClick={(event) => {
                    event.stopPropagation();
                    onToggle(rulesId);
                  }}
                >
                  {rulesOpen ? '▼' : '▶'}
                </button>
                <button type="button" title="Rules" onClick={() => onToggle(rulesId)}>
                  <span className="node-name">rules</span>
                </button>
              </div>
              {rulesOpen ? (
                <ul>
                  {rules.map((hit) => (
                    <li key={hit.slug} data-depth={depth + 2}>
                      <div className="tree-row">
                        <span className="tree-twist-spacer" />
                        <span className={`rule-status ${hit.status}`}>{hit.slug}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : null}
            </li>
          ) : null}
          {links.length > 0 ? (
            <li data-depth={depth + 1} data-testid="tree-relationships">
              <div className="tree-row">
                <button
                  type="button"
                  className="tree-twist"
                  data-testid="tree-expand-relationships"
                  aria-expanded={linksOpen}
                  aria-label={`${linksOpen ? 'Collapse' : 'Expand'} relationships`}
                  onClick={(event) => {
                    event.stopPropagation();
                    onToggle(linksId);
                  }}
                >
                  {linksOpen ? '▼' : '▶'}
                </button>
                <button type="button" title="Relationships" onClick={() => onToggle(linksId)}>
                  <span className="node-name">relationships</span>
                </button>
              </div>
              {linksOpen ? (
                <ul>
                  {links.map((link) => (
                    <li key={`${link.kind}:${link.nodeId}`} data-depth={depth + 2}>
                      <div className="tree-row">
                        <span className="tree-twist-spacer" />
                        <button
                          type="button"
                          data-testid="tree-relationship-target"
                          title={link.kind}
                          onClick={(event) => {
                            event.stopPropagation();
                            onSelect(link.nodeId);
                          }}
                        >
                          <span className="node-name">{link.kind}</span>
                          <span className="node-name">{link.name}</span>
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : null}
            </li>
          ) : null}
        </ul>
      ) : null}
    </li>
  );
}

function SourcePane({
  node,
  folder,
  picked,
  showRules,
}: {
  node: KnowledgeGraphNode;
  folder: string;
  picked: FilterPick;
  showRules: boolean;
}) {
  const file = node.source?.file ?? '';
  const [text, setText] = useState('');
  const editorRef = useRef<Parameters<OnMount>[0] | null>(null);
  const marks = useRef<{ clear: () => void } | null>(null);

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
          setText(body.ranges?.[0]?.text || node.name);
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

  function paint(editor: Parameters<OnMount>[0], value: string) {
    marks.current?.clear();
    const lines = Math.max(1, value.split('\n').length);
    marks.current = editor.createDecorationsCollection([
      {
        range: {
          startLineNumber: 1,
          startColumn: 1,
          endLineNumber: lines,
          endColumn: 1,
        },
        options: { isWholeLine: true, className: 'source-highlight' },
      },
    ]);
  }

  const onMount: OnMount = (editor) => {
    editorRef.current = editor;
    paint(editor, text);
  };

  useEffect(() => {
    if (editorRef.current) {
      paint(editorRef.current, text);
    }
  }, [text]);

  const hits = showRules
    ? picked.violations || picked.rules.length
      ? visibleHits(node, picked)
      : node.ruleHits
    : [];
  return (
    <section className="knowledge-graph-panel" data-open="true" data-file={file}>
      <p className="source-path">{file || node.name}</p>
      <div className="panel-source" data-testid="source-excerpt">
        <Editor
          height="360px"
          language={languageFor(file)}
          theme={document.documentElement.dataset.theme === 'engineering' ? 'vs-dark' : 'vs'}
          value={text}
          onMount={onMount}
          loading={<pre className="source-highlight">{text}</pre>}
          options={{
            readOnly: true,
            domReadOnly: true,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontFamily: "'JetBrains Mono', ui-monospace, monospace",
            fontSize: 13,
            wordWrap: 'on',
          }}
        />
      </div>
      {hits.length > 0 ? (
        <ul className="rule-list">
          {hits.map((hit) => (
            <li key={hit.slug} className={`rule-status ${hit.status}`}>
              {hit.slug}
              {hit.message ? ` — ${hit.message}` : ''}
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}

function expandShown(nodes: KnowledgeGraphNode[], picked: FilterPick, open: Set<string>): void {
  for (const node of nodes) {
    if (!shown(node, picked)) {
      continue;
    }
    const children = (node.children ?? []).filter((child) => shown(child, picked));
    if (children.length > 0) {
      open.add(node.nodeId);
      expandShown(children, picked, open);
    }
  }
}

function openAllRules(nodes: KnowledgeGraphNode[], open: Set<string>): void {
  for (const node of nodes) {
    const children = node.children ?? [];
    if (node.ruleHits.length > 0) {
      open.add(node.nodeId);
      open.add(`${node.nodeId}::rules`);
    }
    if (children.length > 0) {
      open.add(node.nodeId);
      openAllRules(children, open);
    }
  }
}

function rulesFor(
  node: KnowledgeGraphNode,
  picked: FilterPick,
  showRules: boolean,
): { slug: string; status: string; message: string }[] {
  if (!showRules) {
    return [];
  }
  if (picked.violations || picked.rules.length > 0) {
    return visibleHits(node, picked);
  }
  return node.ruleHits;
}

function languageFor(file: string): string {
  const name = file.replaceAll('\\', '/').split('/').pop() ?? '';
  const ext = name.includes('.') ? name.slice(name.lastIndexOf('.') + 1) : '';
  const languages: Record<string, string> = {
    py: 'python',
    ts: 'typescript',
    tsx: 'typescript',
    js: 'javascript',
    jsx: 'javascript',
    json: 'json',
    css: 'css',
    html: 'html',
    md: 'markdown',
  };
  return languages[ext] ?? 'plaintext';
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

function findNode(nodes: KnowledgeGraphNode[], nodeId: string): KnowledgeGraphNode | null {
  for (const node of nodes) {
    if (node.nodeId === nodeId) {
      return node;
    }
    const child = findNode(node.children ?? [], nodeId);
    if (child) {
      return child;
    }
  }
  return null;
}

function firstViolating(nodes: KnowledgeGraphNode[], picked: FilterPick): KnowledgeGraphNode | null {
  for (const node of nodes) {
    if (violates(node, picked)) {
      return node;
    }
    const child = firstViolating(node.children ?? [], picked);
    if (child) {
      return child;
    }
  }
  return null;
}

function visibleHits(
  node: KnowledgeGraphNode,
  picked: FilterPick,
): { slug: string; status: string; message: string }[] {
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
