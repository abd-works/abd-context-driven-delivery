import { type ChangeEvent, useEffect, useRef, useState } from 'react';
import Editor, { type OnMount } from '@monaco-editor/react';
import { useKnowledgeGraph } from './use-knowledge-graph';
import {
  KnowledgeGraphCallSource,
  KnowledgeGraphNode,
  editorHeight,
  includedPracticeIds,
  isStoryNode,
  practiceId,
  practiceRootLabels,
  retainedTree,
} from './knowledge-graph/knowledge-graph';
import { KindMark, kindLabel } from './kind-mark';
import {
  type KnowledgeGraphFilterOptions,
  type PracticeMember,
} from './knowledge-graph/knowledge-graph-client';
import { CONNECTORS_BY_TYPE, nodeTypesFor, stagesForPractices } from '../../../legacy/app/packages/explore-knowledge-graph/knowledge-graph/catalog';
import { pickerRelativePath } from '../../../legacy/app/packages/explore-knowledge-graph/knowledge-graph/workspace';
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

  function pickFolder(list: FileList | null) {
    if (!list || list.length === 0) {
      return;
    }
    let folderName = 'workspace';
    const paths: string[] = [];
    for (const file of Array.from(list)) {
      const mapped = pickerRelativePath(file.webkitRelativePath || file.name);
      folderName = mapped.folder;
      if (mapped.relativePath && keepUploadPath(mapped.relativePath)) {
        paths.push(mapped.relativePath);
      }
    }
    setFolder(folderName);
    selectFolder({ folder: folderName, paths });
  }

  const [picked, setPicked] = useState<FilterPick>(pickFromLocation);
  const optionKey = [
    filterOptions.practices.join('\n'),
    filterOptions.stages.join('\n'),
    filterOptions.node_types.join('\n'),
    filterOptions.relationship_types.join('\n'),
    filterOptions.rules.join('\n'),
  ].join('\u0000');
  useEffect(() => {
    if (!filterOptions.practices.length && !filterOptions.rules.length) {
      return;
    }
    setPicked((prev) => {
      if (prev.practices.length) {
        return prev;
      }
      return {
        practices: filterOptions.practices,
        stages: filterOptions.stages,
        node_types: filterOptions.node_types,
        relationship_types: filterOptions.relationship_types,
        rules: prev.rules.length
          ? prev.rules.filter((rule) => filterOptions.rules.includes(rule))
          : filterOptions.rules,
        violations: prev.violations,
      };
    });
  }, [optionKey]);
  const engineering = theme === 'engineering';
  const selectedId = selectedNode?.nodeId ?? '';

  const [showRules, setShowRules] = useState(false);
  const [openIds, setOpenIds] = useState<Set<string>>(new Set());
  const forest = practiceForest(listedTree, picked, filterOptions);
  const treeKey = `${listedTree.map((node) => node.nodeId).join('|')}|${forest.map((node) => node.nodeId).join('|')}`;
  const filterKey = [
    picked.violations ? '1' : '0',
    picked.rules.join(','),
    picked.practices.join(','),
    picked.node_types.join(','),
    picked.stages.join(','),
  ].join('|');

  useEffect(() => {
    const next = new Set<string>();
    if (forest.length > 0) {
      for (const node of forest) {
        if (node.nodeId) {
          next.add(node.nodeId);
        }
      }
    }
    if (filtersNarrow(picked, filterOptions)) {
      expandShown(forest, picked, filterOptions, next);
    }
    if (showRules) {
      openAllRules(forest, next);
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
              onChange={(practices) =>
                setPicked((prev) => ({
                  ...prev,
                  ...applyPractice(practices, members, filterOptions),
                }))
              }
            />
            <FilterSelect
              label="Stage"
              testId="filter-stage"
              options={stageOptions(picked, members, filterOptions)}
              selected={picked.stages}
              onChange={(stages) =>
                setPicked((prev) => ({
                  ...prev,
                  ...applyStage(prev, stages, members, filterOptions),
                }))
              }
            />
            <FilterSelect
              label="Node"
              testId="filter-node"
              options={nodeOptions(picked, members, filterOptions)}
              selected={picked.node_types}
              onChange={(node_types) =>
                setPicked((prev) => ({
                  ...prev,
                  ...applyNode(prev, node_types, members, filterOptions),
                }))
              }
            />
            <FilterSelect
              label="Connector"
              testId="filter-connector"
              options={connectorOptions(picked, members, filterOptions)}
              selected={picked.relationship_types}
              onChange={(relationship_types) => setPicked((prev) => ({ ...prev, relationship_types }))}
            />
            <FilterSelect
              label="Rule"
              testId="filter-rule"
              options={ruleOptions(picked, members, filterOptions)}
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
            {!loading && scanError ? (
              <p className="empty-state" data-testid="scan-error">
                {scanError}
              </p>
            ) : null}
            <ul className="tree">
              {forest.map((node) => (
                <TreeNode
                  key={node.nodeId || node.name}
                  node={node}
                  depth={0}
                  picked={picked}
                  options={filterOptions}
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
  options,
  showRules,
  selectedId,
  openIds,
  onToggle,
  onSelect,
}: {
  node: KnowledgeGraphNode;
  depth: number;
  picked: FilterPick;
  options: KnowledgeGraphFilterOptions;
  showRules: boolean;
  selectedId: string;
  openIds: Set<string>;
  onToggle: (id: string) => void;
  onSelect: (nodeId: string) => void;
}) {
  const children = (node.children ?? []).filter((child) => shown(child, picked, options));
  if (!shown(node, picked, options)) {
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
          title={kindLabel(kind, false)}
          onClick={(event) => {
            event.stopPropagation();
            onSelect(node.nodeId);
          }}
        >
          <KindMark kind={kind} isFile={false} />
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
              options={options}
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
                  <KindMark kind="Rules" isFile={false} />
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
                  <KindMark kind="Relationships" isFile={false} />
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
                          title={kindLabel(link.kind, false)}
                          onClick={(event) => {
                            event.stopPropagation();
                            onSelect(link.nodeId);
                          }}
                        >
                          <KindMark kind="Relationship" isFile={false} />
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

const GLYPH_MARGIN = 2;
const SNIPPET_LINE_HEIGHT = 20;

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
  const [openFolds, setOpenFolds] = useState<number[]>([]);
  const [mounted, setMounted] = useState(false);
  const editorRef = useRef<Parameters<OnMount>[0] | null>(null);
  const decorations = useRef<{ clear: () => void } | null>(null);
  const hideSource = useRef({ id: 'call-folds' });
  const prepared = preparedSource(node, text);
  const foldsRef = useRef(prepared.folds);
  const lineMap = useRef(prepared.lineNumbers);
  foldsRef.current = prepared.folds;
  lineMap.current = prepared.lineNumbers;
  const lineCount = Math.max(1, prepared.text ? prepared.text.split('\n').length : 1);
  const height = Math.min(520, editorHeight(lineCount, prepared.folds, openFolds) + 16);
  const startLine = Number(node.source?.startLine) || 1;

  useEffect(() => {
    setOpenFolds([]);
  }, [node.nodeId]);

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

  useEffect(() => {
    const editor = editorRef.current;
    if (!editor) {
      return;
    }
    if (editor.getValue() !== prepared.text) {
      editor.setValue(prepared.text);
    }
    editor.updateOptions({
      glyphMargin: prepared.folds.length > 0,
      lineNumbers: (line) => {
        const mapped = lineMap.current[line - 1];
        return mapped ? String(startLine + Number(mapped) - 1) : '';
      },
    });
    applyCallFolds(editor, prepared.folds, openFolds, hideSource.current, decorations);
  }, [prepared.text, prepared.folds, openFolds, startLine, mounted]);

  const onMount: OnMount = (editor) => {
    editorRef.current = editor;
    setMounted(true);
    const nodeEl = editor.getDomNode();
    nodeEl?.addEventListener(
      'mousedown',
      (event) => {
        const target = editor.getTargetAtClientPoint(event.clientX, event.clientY);
        const line = target?.position?.lineNumber ?? target?.range?.startLineNumber;
        const markHit =
          event.target instanceof Element &&
          event.target.closest('.codicon-folding-collapsed, .codicon-folding-expanded, .call-fold, .class-fold') !==
            null;
        if (!line || !target || (target.type !== GLYPH_MARGIN && !markHit)) {
          return;
        }
        const fold = foldsRef.current.find((entry) => entry.glyph === line);
        if (!fold) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        setOpenFolds((current) => {
          const next = current.includes(fold.start)
            ? current.filter((start) => start !== fold.start)
            : [...current, fold.start];
          applyCallFolds(editor, foldsRef.current, next, hideSource.current, decorations);
          return next;
        });
      },
      true,
    );
  };

  const hits = showRules
    ? picked.violations || picked.rules.length
      ? visibleHits(node, picked)
      : node.ruleHits
    : [];
  return (
    <section className="knowledge-graph-panel source-snippet" data-open="true" data-file={file}>
      <p className="source-path">{file || node.name}</p>
      <div className="panel-source" data-testid="source-excerpt">
        <div data-testid="source-editor" style={{ height }}>
          <Editor
            height={height}
            language={languageFor(file)}
            theme={document.documentElement.dataset.theme === 'engineering' ? 'vs-dark' : 'vs'}
            value={prepared.text}
            onMount={onMount}
            loading={<pre className="source-highlight">{prepared.text}</pre>}
            options={{
              readOnly: true,
              domReadOnly: true,
              folding: false,
              showFoldingControls: 'never',
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              automaticLayout: true,
              wordWrap: 'off',
              fontFamily: "'JetBrains Mono', ui-monospace, monospace",
              fontSize: 13,
              lineHeight: SNIPPET_LINE_HEIGHT,
              glyphMargin: prepared.folds.length > 0,
              lineNumbers: (line) => {
                const mapped = lineMap.current[line - 1];
                return mapped ? String(startLine + Number(mapped) - 1) : '';
              },
              padding: { top: 8, bottom: 8 },
            }}
          />
        </div>
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

function expandShown(
  nodes: KnowledgeGraphNode[],
  picked: FilterPick,
  options: KnowledgeGraphFilterOptions,
  open: Set<string>,
): void {
  for (const node of nodes) {
    if (!shown(node, picked, options)) {
      continue;
    }
    const children = (node.children ?? []).filter((child) => shown(child, picked, options));
    if (children.length > 0 && node.nodeType?.name !== 'OoadClass') {
      open.add(node.nodeId);
      expandShown(children, picked, options, open);
    }
  }
}

function openAllRules(nodes: KnowledgeGraphNode[], open: Set<string>): void {
  for (const node of nodes) {
    const children = node.children ?? [];
    const classNode = node.nodeType?.name === 'OoadClass';
    if (node.ruleHits.length > 0) {
      if (!classNode) {
        open.add(node.nodeId);
      }
      open.add(`${node.nodeId}::rules`);
    }
    if (children.length > 0 && !classNode) {
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

function storiesInView(picked: FilterPick, options: KnowledgeGraphFilterOptions): boolean {
  if (!restricts(picked.practices, options.practices)) {
    return true;
  }
  return includedPracticeIds(picked.practices).includes('stories');
}

function shown(
  node: KnowledgeGraphNode,
  picked: FilterPick,
  options: KnowledgeGraphFilterOptions,
): boolean {
  if (node.nodeType?.name === 'File') {
    return false;
  }
  if (isStoryNode(node) && !storiesInView(picked, options)) {
    return false;
  }
  if (picked.violations) {
    return violates(node, picked) || (node.children ?? []).some((child) => shown(child, picked, options));
  }
  if (matches(node, picked, options)) {
    return true;
  }
  return (node.children ?? []).some((child) => shown(child, picked, options));
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

function matches(
  node: KnowledgeGraphNode,
  picked: FilterPick,
  options: KnowledgeGraphFilterOptions,
): boolean {
  if (!practiceAllowed(node.practice, picked, options)) {
    return false;
  }
  if (restricts(picked.stages, options.stages) && node.nodeType?.name !== 'Practice' && !picked.stages.includes(node.stage)) {
    return false;
  }
  if (
    restricts(picked.node_types, options.node_types) &&
    node.nodeType?.name !== 'Practice' &&
    !picked.node_types.includes(node.nodeType?.name ?? '')
  ) {
    return false;
  }
  return true;
}

function practiceAllowed(
  nodePractice: string,
  picked: FilterPick,
  options: KnowledgeGraphFilterOptions,
): boolean {
  if (!nodePractice) {
    return true;
  }
  if (!restricts(picked.practices, options.practices)) {
    return true;
  }
  return includedPracticeIds(picked.practices).includes(practiceId(nodePractice));
}

function practiceForest(
  nodes: KnowledgeGraphNode[],
  picked: FilterPick,
  options: KnowledgeGraphFilterOptions,
): KnowledgeGraphNode[] {
  if (!nodes.length) {
    return nodes;
  }
  const selected = restricts(picked.practices, options.practices) ? picked.practices : [];
  const labels = practiceRootLabels(selected);
  const showCleanEngineering = labels.includes('Clean Engineering');
  const roots: KnowledgeGraphNode[] = [];
  for (const label of labels) {
    const id =
      label === 'Clean Engineering'
        ? 'clean_engineering'
        : label === 'Domain Driven Design'
          ? 'ddd'
          : label === 'BDD'
            ? 'bdd'
            : 'stories';
    const includeCleanEngineering = id === 'ddd' && !showCleanEngineering;
    const children = retainedTree(nodes, [id], includeCleanEngineering);
    if (!children.length) {
      continue;
    }
    const root = new KnowledgeGraphNode();
    root.name = label;
    root.nodeId = `practice:${id}`;
    root.practice = id;
    root.nodeType = { name: 'Practice' } as KnowledgeGraphNode['nodeType'];
    root.children = children;
    roots.push(root);
  }
  return roots.length ? roots : nodes;
}

type SourceFold = { start: number; end: number; kind: 'class' | 'call'; glyph: number };

function preparedSource(node: KnowledgeGraphNode, text: string): { text: string; folds: SourceFold[]; lineNumbers: string[] } {
  const kind = node.nodeType?.name ?? '';
  const lines = text ? text.split('\n') : [''];
  if (kind === 'OoadClass') {
    return { text, folds: memberFolds(node, lines.length), lineNumbers: lines.map((_, index) => String(index + 1)) };
  }
  if ((kind === 'Operation' || kind === 'Property') && text.trim()) {
    return callLayout(node, text);
  }
  return { text, folds: [], lineNumbers: lines.map((_, index) => String(index + 1)) };
}

function memberFolds(node: KnowledgeGraphNode, lineCount: number): SourceFold[] {
  const base = Number(node.source?.startLine) || 1;
  const folds: SourceFold[] = [];
  if (lineCount > 1) {
    folds.push({ start: 2, end: lineCount, kind: 'class', glyph: 1 });
  }
  for (const child of node.children ?? []) {
    const type = child.nodeType?.name ?? '';
    if (type !== 'Operation' && type !== 'Property') {
      continue;
    }
    const start = Number(child.source?.startLine) || 0;
    const end = Number(child.source?.endLine) || start;
    if (start < base) {
      continue;
    }
    const signature = start - base + 1;
    const last = Math.min(lineCount, Math.max(start, end) - base + 1);
    if (last <= signature || signature <= 1) {
      continue;
    }
    folds.push({ start: signature + 1, end: last, kind: 'class', glyph: signature });
  }
  return folds;
}

function callLayout(node: KnowledgeGraphNode, text: string): { text: string; folds: SourceFold[]; lineNumbers: string[] } {
  const prepared = new KnowledgeGraphCallSource(text, node.source?.file ?? '', 1, text.split('\n').length, 'typescript');
  prepared.source();
  const bodies = memberBodies(node);
  const output: string[] = [];
  const lineNumbers: string[] = [];
  const folds: SourceFold[] = [];
  prepared.text.split('\n').forEach((line, index) => {
    output.push(line);
    lineNumbers.push(String(index + 1));
    const calls = prepared.calls.filter((call) => call.line === index + 1);
    if (!calls.length) {
      return;
    }
    const callLine = output.length;
    let inserted = false;
    let sawCall = false;
    for (const call of calls) {
      const operation = String(call.operation ?? '');
      if (operation.includes('.')) {
        sawCall = true;
      }
      const body = bodies.get(memberName(operation));
      if (!body) {
        continue;
      }
      for (const nestedLine of body.split('\n')) {
        output.push(nestedLine.length ? `    ${nestedLine}` : '    ');
        lineNumbers.push('');
      }
      inserted = true;
    }
    if (inserted && output.length > callLine) {
      folds.push({
        start: callLine + 1,
        end: output.length,
        kind: sawCall ? 'call' : 'class',
        glyph: callLine,
      });
    }
  });
  return { text: output.join('\n'), folds, lineNumbers };
}

function memberBodies(node: KnowledgeGraphNode): Map<string, string> {
  const bodies = new Map<string, string>();
  const visit = (current: KnowledgeGraphNode) => {
    for (const child of current.children ?? []) {
      const type = child.nodeType?.name ?? '';
      const source = child.source?.text ?? '';
      if ((type === 'Operation' || type === 'Property') && source && !bodies.has(memberName(child.name))) {
        bodies.set(memberName(child.name), source);
      }
      visit(child);
    }
  };
  visit(node);
  return bodies;
}

function memberName(name: string): string {
  const dot = name.lastIndexOf('.');
  return dot >= 0 ? name.slice(dot + 1) : name;
}

function applyCallFolds(
  editor: Parameters<OnMount>[0],
  folds: SourceFold[],
  openFolds: number[],
  source: object,
  decorations: { current: { clear: () => void } | null },
) {
  const open = new Set(openFolds);
  const ranges = folds
    .filter((fold) => !open.has(fold.start) && fold.end >= fold.start)
    .filter(
      (fold) =>
        !folds.some(
          (other) =>
            other !== fold &&
            other.start <= fold.start &&
            other.end >= fold.end &&
            !open.has(other.start),
        ),
    )
    .map((fold) => ({
      startLineNumber: fold.start,
      startColumn: 1,
      endLineNumber: fold.end + 1,
      endColumn: 1,
    }));
  (
    editor as Parameters<OnMount>[0] & {
      setHiddenAreas(ranges: object[], source?: object): void;
    }
  ).setHiddenAreas(ranges, source);
  decorations.current?.clear();
  decorations.current = editor.createDecorationsCollection(
    folds.map((fold) => ({
      range: {
        startLineNumber: fold.glyph,
        startColumn: 1,
        endLineNumber: fold.glyph,
        endColumn: 1,
      },
      options: {
        glyphMarginClassName: glyphClass(fold.kind, open.has(fold.start)),
        glyphMarginHoverMessage: { value: hoverLabel(fold.kind, open.has(fold.start)) },
      },
    })),
  );
}

function glyphClass(kind: SourceFold['kind'], open: boolean): string {
  const icon = open ? 'codicon-folding-expanded' : 'codicon-folding-collapsed';
  if (kind === 'class') {
    return `codicon ${icon} class-fold${open ? ' class-fold-open' : ''}`;
  }
  return `codicon ${icon} call-fold${open ? ' call-fold-open' : ''}`;
}

function hoverLabel(kind: SourceFold['kind'], open: boolean): string {
  const noun = kind === 'class' ? 'class' : 'call';
  return open ? `Collapse ${noun}` : `Expand ${noun}`;
}

function filtersNarrow(picked: FilterPick, options: KnowledgeGraphFilterOptions): boolean {
  return (
    picked.violations ||
    restricts(picked.practices, options.practices) ||
    restricts(picked.stages, options.stages) ||
    restricts(picked.node_types, options.node_types) ||
    restricts(picked.rules, options.rules)
  );
}

function restricts(selected: string[], universe: string[]): boolean {
  return selected.length > 0 && selected.length < universe.length;
}

function keepOrder(universe: string[], found: string[]): string[] {
  const have = new Set(found.filter(Boolean));
  return universe.filter((item) => have.has(item));
}

function membersIn(
  members: PracticeMember[],
  practices: string[] | null,
  stages: string[] | null,
  types: string[] | null,
): PracticeMember[] {
  return members.filter((member) => {
    if (practices && !practices.includes(member.practice)) {
      return false;
    }
    if (stages && !stages.includes(member.stage)) {
      return false;
    }
    if (types && !types.includes(member.type)) {
      return false;
    }
    return true;
  });
}

function applyPractice(
  practices: string[],
  members: PracticeMember[],
  options: KnowledgeGraphFilterOptions,
): Omit<FilterPick, 'violations'> {
  const practiceLimit = restricts(practices, options.practices) ? practices : null;
  const rows = membersIn(members, practiceLimit, null, null);
  const stages = practiceLimit ? stagesForPractices(practiceLimit) : options.stages;
  return {
    practices,
    stages,
    node_types: practiceLimit ? listedTypes(practiceLimit, stages) : options.node_types,
    relationship_types: connectorChoices(practiceLimit, null, options),
    rules: practiceLimit ? keepOrder(options.rules, rows.flatMap((member) => member.rules)) : options.rules,
  };
}

function stageOptions(
  picked: FilterPick,
  members: PracticeMember[],
  options: KnowledgeGraphFilterOptions,
): string[] {
  return applyPractice(picked.practices, members, options).stages;
}

function applyStage(
  picked: FilterPick,
  stages: string[],
  members: PracticeMember[],
  options: KnowledgeGraphFilterOptions,
): Pick<FilterPick, 'stages' | 'node_types' | 'relationship_types' | 'rules'> {
  const practiceLimit = restricts(picked.practices, options.practices) ? picked.practices : null;
  const stageLimit = restricts(stages, practiceLimit ? stagesForPractices(practiceLimit) : options.stages)
    ? stages
    : null;
  const rows = membersIn(members, practiceLimit, stageLimit, null);
  const narrowed = Boolean(practiceLimit || stageLimit);
  return {
    stages,
    node_types: practiceLimit ? listedTypes(practiceLimit, stageLimit ?? stages) : options.node_types,
    relationship_types: connectorChoices(practiceLimit, null, options),
    rules: narrowed ? keepOrder(options.rules, rows.flatMap((member) => member.rules)) : options.rules,
  };
}

function listedTypes(practices: string[], stages: string[] | null): string[] {
  return nodeTypesFor(practices, stages);
}

function nodeOptions(
  picked: FilterPick,
  _members: PracticeMember[],
  options: KnowledgeGraphFilterOptions,
): string[] {
  const practiceLimit = restricts(picked.practices, options.practices) ? picked.practices : null;
  if (!practiceLimit) {
    return options.node_types;
  }
  const availableStages = stagesForPractices(practiceLimit);
  const stageLimit = restricts(picked.stages, availableStages) ? picked.stages : null;
  return listedTypes(practiceLimit, stageLimit);
}

function applyNode(
  picked: FilterPick,
  nodeTypes: string[],
  members: PracticeMember[],
  options: KnowledgeGraphFilterOptions,
): Pick<FilterPick, 'node_types' | 'relationship_types' | 'rules'> {
  const practiceLimit = restricts(picked.practices, options.practices) ? picked.practices : null;
  const stageLimit = restricts(picked.stages, options.stages) ? picked.stages : null;
  const typeLimit = restricts(nodeTypes, practiceLimit ? nodeTypesFor(practiceLimit, null) : options.node_types)
    ? nodeTypes
    : null;
  const rows = membersIn(members, practiceLimit, stageLimit, typeLimit);
  const narrowed = Boolean(practiceLimit || stageLimit || typeLimit);
  return {
    node_types: nodeTypes,
    relationship_types: connectorChoices(practiceLimit, typeLimit, options),
    rules: narrowed ? keepOrder(options.rules, rows.flatMap((member) => member.rules)) : options.rules,
  };
}

function connectorChoices(
  practices: string[] | null,
  nodeTypes: string[] | null,
  options: KnowledgeGraphFilterOptions,
): string[] {
  if (!nodeTypes) {
    return options.relationship_types;
  }
  const found = nodeTypes.flatMap((type) => CONNECTORS_BY_TYPE[type] ?? []);
  const ordered = keepOrder(options.relationship_types, found);
  return ordered.length ? ordered : options.relationship_types;
}

function connectorOptions(
  picked: FilterPick,
  _members: PracticeMember[],
  options: KnowledgeGraphFilterOptions,
): string[] {
  const practiceLimit = restricts(picked.practices, options.practices) ? picked.practices : null;
  const practiceTypes = practiceLimit ? nodeTypesFor(practiceLimit, null) : options.node_types;
  const typeLimit = restricts(picked.node_types, practiceTypes) ? picked.node_types : null;
  return connectorChoices(practiceLimit, typeLimit, options);
}

function ruleOptions(
  picked: FilterPick,
  members: PracticeMember[],
  options: KnowledgeGraphFilterOptions,
): string[] {
  return applyNode(picked, picked.node_types, members, options).rules;
}

const UPLOAD_SKIP = new Set([
  'node_modules',
  'dist',
  'build',
  'coverage',
  '.codeql',
  '.codeql-db',
]);

function keepUploadPath(relativePath: string): boolean {
  return relativePath.split('/').every((part) => part.length > 0 && !UPLOAD_SKIP.has(part));
}

function sameFolder(left: string, right: string): boolean {
  return left.replaceAll('/', '\\').toLowerCase() === right.replaceAll('/', '\\').toLowerCase();
}
