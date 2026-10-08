import { useEffect, useState } from 'react';
import wordmarkBlack from './brand/abd.works.wordmark.black.svg?url';
import wordmarkWhite from './brand/abd.works.wordmark.white.svg?url';
import { DataManagementClient } from './data-management/DataManagementClient';
import { DataManagementView, type Staleness } from './data-management/DataManagementView';
import { FilterClient, type FilterSelection, type GraphTree, type PracticeInventory } from './filter/FilterClient';
import { FilterView } from './filter/FilterView';
import { GraphClient } from './graph/GraphClient';
import { GraphView } from './graph/GraphView';
import { SourceClient, type SourceText } from './source/SourceClient';
import { SourceView } from './source/SourceView';

const PRACTICES = ['clean_engineering', 'stories', 'ddd', 'bdd', 'ux'];
const LAST_FOLDER = 'cdd-graph-folder';
const EMPTY: FilterSelection = {
  practices: [],
  node_types: [],
  relationships: [],
  rules: [],
  violations: false,
};

const graphs = new GraphClient();
const filters = new FilterClient();
const sources = new SourceClient();
const data = new DataManagementClient();

export function App() {
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme ?? '');
  const [folder, setFolder] = useState(() => window.localStorage.getItem(LAST_FOLDER) ?? '');
  const [loadedFolder, setLoadedFolder] = useState('');
  const [filtersOpen, setFiltersOpen] = useState(true);
  const [selection, setSelection] = useState<FilterSelection>(EMPTY);
  const [trees, setTrees] = useState<GraphTree[]>([]);
  const [catalog, setCatalog] = useState<Record<string, PracticeInventory>>({});
  const [nodeTypes, setNodeTypes] = useState<string[]>([]);
  const [relationships, setRelationships] = useState<string[]>([]);
  const [rules, setRules] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingLabel, setLoadingLabel] = useState('Loading the graph…');
  const [loadingLog, setLoadingLog] = useState<string[]>([]);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');
  const [staleness, setStaleness] = useState<Staleness | null>(null);
  const [selectedId, setSelectedId] = useState('');
  const [source, setSource] = useState<SourceText | null>(null);
  const engineering = theme === 'engineering';

  function applyTheme(next: '' | 'engineering') {
    setTheme(next);
    if (next) {
      document.documentElement.dataset.theme = next;
    } else {
      delete document.documentElement.dataset.theme;
    }
    window.localStorage.setItem('kg-theme', next);
  }

  useEffect(() => {
    const saved = window.localStorage.getItem(LAST_FOLDER)?.trim();
    if (saved) {
      void load(saved);
    }
  }, []);

  useEffect(() => {
    let stop = false;
    async function tick() {
      while (!stop) {
        try {
          const response = await fetch('/api/progress');
          const body = (await response.json()) as { messages?: string[] };
          if (Array.isArray(body.messages) && body.messages.length > 0) {
            setLoadingLog(body.messages);
          }
        } catch (cause) {
          const message = cause instanceof Error ? cause.message : String(cause);
          setLoadingLog((current) => {
            const line = `error: Progress check failed: ${message}`;
            return current[current.length - 1] === line ? current : [...current, line];
          });
        }
        await new Promise((resolve) => setTimeout(resolve, 400));
      }
    }
    void tick();
    return () => {
      stop = true;
    };
  }, []);

  function practiceRoots(root: string): Record<string, string> {
    return Object.fromEntries(PRACTICES.map((name) => [name, root]));
  }

  async function browse() {
    const chosen = await graphs.chooseFolder();
    if (!chosen) {
      return;
    }
    setFolder(chosen);
    await load(chosen);
  }

  async function load(root: string, next = selection) {
    const trimmed = root.trim();
    if (!trimmed) {
      return;
    }
    setLoading(true);
    setLoadingLabel('Loading the graph…');
    setLoadingLog([]);
    setError('');
    try {
      await graphs.load(trimmed, practiceRoots(trimmed));
      const inventory = await graphs.inventory();
      const report = await data.staleness(trimmed, practiceRoots(trimmed));
      setCatalog(inventory);
      const shown = next.practices.length ? next.practices : Object.keys(inventory);
      setTrees(shown.map((name) => inventory[name]?.tree).filter((tree): tree is GraphTree => Boolean(tree)));
      setNodeTypes(unique(shown.flatMap((name) => inventory[name]?.node_types ?? [])));
      setRelationships(visibleRelationships(unique(shown.flatMap((name) => inventory[name]?.edge_types ?? []))));
      setRules(unique(shown.flatMap((name) => inventory[name]?.rules ?? [])));
      setLoadedFolder(trimmed);
      window.localStorage.setItem(LAST_FOLDER, trimmed);
      setStaleness(report);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
      try {
        setStaleness(await data.staleness(trimmed, practiceRoots(trimmed)));
      } catch {
        setStaleness(null);
      }
    } finally {
      setLoading(false);
    }
  }

  async function choose(nodeId: string) {
    setSelectedId(nodeId);
    setSource(await sources.open(nodeId));
  }

  async function applyFilter(next: FilterSelection) {
    if (!folder.trim()) {
      setSelection(next);
      return;
    }
    const practiceChanged = joined(next.practices) !== joined(selection.practices);
    const nodeChanged = joined(next.node_types) !== joined(selection.node_types);
    let resolved = next;
    if (practiceChanged) {
      resolved = practiceSelection(selection, next, catalog);
      const scope = resolved.practices.length ? resolved.practices : Object.keys(catalog);
      setNodeTypes(listed(scope, catalog, 'node_types'));
      setRelationships(visibleRelationships(listed(scope, catalog, 'edge_types')));
      setRules(listed(scope, catalog, 'rules'));
    } else if (nodeChanged) {
      const choices = await filters.choices(next);
      resolved = { ...next, relationships: choices.relationships, rules: choices.rules };
      setRelationships(visibleRelationships(choices.relationships));
      setRules(choices.rules);
    }
    setSelection(resolved);
    const rows = await filters.nodes(resolved);
    const names = new Set(rows.map((row) => row.node_id));
    const inventory = await graphs.inventory();
    const shown = resolved.practices.length ? resolved.practices : Object.keys(inventory);
    setTrees(
      shown
        .map((name) => keep(inventory[name]?.tree, names, resolved.node_types))
        .filter((tree): tree is GraphTree => Boolean(tree)),
    );
  }

  return (
    <main className="explore-knowledge-graph">
      <div className="knowledge-graph-explorer">
        <header className="site-nav">
          <div className="nav-brand">
            <a className="nav-logo" href="/" aria-label="abd.works">
              <img src={engineering ? wordmarkWhite : wordmarkBlack} alt="abd.works" />
            </a>
            <p className="page-hero-label">Knowledge graph</p>
          </div>
          <div className="nav-actions">
            <div className="mode-toggle" role="group" aria-label="Theme">
              <button type="button" className={engineering ? '' : 'is-active'} onClick={() => applyTheme('')}>
                <span className="mode-label">Executive</span>
                <span className="mode-icon" aria-hidden="true">☀</span>
              </button>
              <button type="button" className={engineering ? 'is-active' : ''} onClick={() => applyTheme('engineering')}>
                <span className="mode-label">Engineering</span>
                <span className="mode-icon" aria-hidden="true">☾</span>
              </button>
            </div>
            <DataManagementView
              loading={loading}
              folder={folder}
              status={status}
              staleness={staleness}
              onCreate={() =>
                runStatus(
                  data.createDatabase(folder, practiceRoots(folder)).then((message) => load(folder).then(() => message)),
                  'Creating the CodeQL database…',
                )
              }
              onMerge={() =>
                runStatus(
                  data.mergeWorkingToMaster().then((message) => load(folder).then(() => message)),
                  'Merging the working copy onto master…',
                )
              }
              onReload={() =>
                runStatus(
                  data.reloadWorkingCopy(folder, practiceRoots(folder)).then((message) => load(folder).then(() => message)),
                  'Reloading the working copy…',
                )
              }
              onSerialize={() =>
                runStatus(
                  data.serializeGraphCache(folder, practiceRoots(folder)).then(async (message) => {
                    setStaleness(await data.staleness(folder, practiceRoots(folder)));
                    return message;
                  }),
                  'Serializing the graph cache…',
                )
              }
            />
          </div>
        </header>
        <div className="toolbar">
          <div className="folder-scan">
            <button
              type="button"
              className="btn-primary"
              data-testid="working-folder"
              title="Select a repo folder to load the Knowledge Graph"
              onClick={() => void browse()}
            >
              Repo folder
            </button>
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
              onChange={(event) => setFolder(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') {
                  void load(folder);
                }
              }}
              onBlur={() => {
                const trimmed = folder.trim();
                if (trimmed && trimmed !== loadedFolder) {
                  void load(trimmed);
                }
              }}
            />
          </div>
          <FilterView
            open={filtersOpen}
            selection={selection}
            practices={PRACTICES}
            nodeTypes={nodeTypes}
            relationships={relationships}
            rules={rules}
            onChange={(next) => {
              void applyFilter(next);
            }}
          />
        </div>
        <div className="split">
          <GraphView
            trees={trees}
            loading={loading || (trees.length === 0 && loadingLog.length > 0)}
            loadingLabel={loadingLabel}
            loadingLog={loadingLog}
            error={error}
            selectedId={selectedId}
            onSelect={(nodeId) => void choose(nodeId)}
          />
          <SourceView source={source} />
        </div>
      </div>
    </main>
  );

  function runStatus(work: Promise<string>, label: string) {
    setLoading(true);
    setLoadingLabel(label);
    setError('');
    work
      .then((message) => setStatus(message))
      .catch((cause: unknown) => setError(cause instanceof Error ? cause.message : String(cause)))
      .finally(() => setLoading(false));
  }
}

function visibleRelationships(values: string[]): string[] {
  return values.filter((value) => value !== 'belongsTo' && value !== 'scopes');
}

function unique(values: string[]): string[] {
  return [...new Set(values)];
}

function joined(values: string[]): string {
  return values.join('\n');
}

function listed(
  practices: string[],
  catalog: Record<string, PracticeInventory>,
  field: 'node_types' | 'edge_types' | 'rules',
): string[] {
  return unique(practices.flatMap((name) => catalog[name]?.[field] ?? []));
}

function practiceSelection(
  previous: FilterSelection,
  next: FilterSelection,
  catalog: Record<string, PracticeInventory>,
): FilterSelection {
  const scope = next.practices.length ? next.practices : Object.keys(catalog);
  const nodes = listed(scope, catalog, 'node_types');
  const edges = visibleRelationships(listed(scope, catalog, 'edge_types'));
  const rules = listed(scope, catalog, 'rules');
  const added = next.practices.filter((name) => !previous.practices.includes(name));
  if (previous.practices.length === 0 || next.practices.length === 0) {
    return { ...next, node_types: nodes, relationships: edges, rules };
  }
  return {
    ...next,
    node_types: mergeKept(previous.node_types, nodes, added.flatMap((name) => catalog[name]?.node_types ?? [])),
    relationships: mergeKept(
      previous.relationships,
      edges,
      visibleRelationships(added.flatMap((name) => catalog[name]?.edge_types ?? [])),
    ),
    rules: mergeKept(previous.rules, rules, added.flatMap((name) => catalog[name]?.rules ?? [])),
  };
}

function mergeKept(current: string[], available: string[], added: string[]): string[] {
  const kept = current.filter((item) => available.includes(item));
  for (const item of added) {
    if (available.includes(item) && !kept.includes(item)) {
      kept.push(item);
    }
  }
  return kept;
}

function keep(node: GraphTree | undefined, ids: Set<string>, types: string[]): GraphTree | null {
  if (!node) {
    return null;
  }
  const rules = node.children.filter((child) => child.type === 'rules');
  const children = node.children
    .filter((child) => child.type !== 'rules')
    .map((child) => keep(child, ids, types))
    .filter((child): child is GraphTree => Boolean(child));
  const holder = node.type === node.name;
  if (holder) {
    return children.length > 0 ? { ...node, children } : null;
  }
  const selectedType = types.length === 0 || types.includes(node.type) || node.type === 'Practice';
  if (!selectedType) {
    return children.length > 0 ? { ...node, children } : null;
  }
  const selectedId = ids.size === 0 || ids.has(node.node_id);
  if (node.type !== 'Practice' && !selectedId && children.length === 0) {
    return null;
  }
  if (node.type !== 'Practice' && !selectedId) {
    return { ...node, children };
  }
  return { ...node, children: [...children, ...rules] };
}
