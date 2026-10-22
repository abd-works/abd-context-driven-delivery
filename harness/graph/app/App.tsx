import { useEffect, useRef, useState } from 'react';
import wordmarkBlack from './brand/abd.works.wordmark.black.svg?url';
import wordmarkWhite from './brand/abd.works.wordmark.white.svg?url';
import { FilterClient, type FilterSelection, type GraphTree, type InventoryBundle, type PracticeInventory } from './filter/FilterClient';
import { FilterView } from './filter/FilterView';
import { GraphClient } from './graph/GraphClient';
import { GraphView } from './graph/GraphView';
import { ruleHits, selectionForRule, type GraphSelection } from './graph/graph-selection';
import { SourceClient, type SourceText } from './source/SourceClient';
import { SourceView, type SourceRule } from './source/SourceView';
import { normalizeInventoryBundle } from './inventory-bundle';
import type { ViolationFocus } from './source/violation-prompt';

const PRACTICES = ['clean_engineering', 'stories', 'ddd', 'bdd', 'ux'];
const LAST_FOLDER = 'cdd-graph-folder';
const LAST_OVERLAYS = 'cdd-graph-overlays';
const EMPTY: FilterSelection = {
  practices: [],
  overlays: [],
  node_types: [],
  relationships: [],
  rules: [],
  violations: false,
};

const graphs = new GraphClient();
const filters = new FilterClient();
const sources = new SourceClient();

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
  const [availableOverlays, setAvailableOverlays] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingLabel, setLoadingLabel] = useState('Loading the graph…');
  const [loadingLog, setLoadingLog] = useState<string[]>([]);
  const [error, setError] = useState('');
  const [selectedId, setSelectedId] = useState('');
  const [activeRule, setActiveRule] = useState('');
  const [violation, setViolation] = useState<ViolationFocus | null>(null);
  const [source, setSource] = useState<SourceText | null>(null);
  const loadGeneration = useRef(0);
  const loadingRef = useRef(false);
  loadingRef.current = loading;
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
            if (loadingRef.current) {
              const last = body.messages[body.messages.length - 1].replace(/^load:\s*/, '');
              if (last) {
                setLoadingLabel(last);
              }
            }
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

  async function load(root: string, next = selection, force = false) {
    const trimmed = root.trim();
    if (!trimmed) {
      return;
    }
    const generation = loadGeneration.current + 1;
    loadGeneration.current = generation;
    setLoading(true);
    setLoadingLabel('Loading the graph…');
    setLoadingLog([]);
    setError('');
    try {
      await graphs.load(trimmed, practiceRoots(trimmed), readSavedOverlays(), force);
      if (generation !== loadGeneration.current) {
        return;
      }
      const bundle = normalizeInventoryBundle(await graphs.inventory());
      if (generation !== loadGeneration.current) {
        return;
      }
      const synced = { ...next, overlays: bundle.overlays };
      adoptInventory(bundle, synced);
      setSelection(synced);
      await applyFilter(synced, bundle.practices);
      setLoadedFolder(trimmed);
      window.localStorage.setItem(LAST_FOLDER, trimmed);
      window.localStorage.setItem(LAST_OVERLAYS, JSON.stringify(bundle.overlays));
      setLoadingLog([]);
    } catch (cause) {
      if (generation !== loadGeneration.current) {
        return;
      }
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      if (generation === loadGeneration.current) {
        setLoading(false);
      }
    }
  }

  async function choose(selection: GraphSelection) {
    setSelectedId(selection.nodeId);
    setActiveRule(selection.rule ?? '');
    setViolation(selection.violation ?? null);
    const opened = await sources.open(selection.nodeId);
    setSource(opened?.text != null && opened.file != null ? opened : null);
  }

  function adoptInventory(bundle: InventoryBundle, filter: FilterSelection) {
    setCatalog(bundle.practices);
    setAvailableOverlays(bundle.available_overlays ?? []);
    const shown = filter.practices.length ? filter.practices : Object.keys(bundle.practices);
    setTrees(shown.map((name) => bundle.practices[name]?.tree).filter((tree): tree is GraphTree => Boolean(tree)));
    setNodeTypes(unique(shown.flatMap((name) => bundle.practices[name]?.node_types ?? [])));
    setRelationships(visibleRelationships(unique(shown.flatMap((name) => bundle.practices[name]?.edge_types ?? []))));
    setRules(unique(shown.flatMap((name) => bundle.practices[name]?.rules ?? [])));
  }

  async function applyOverlays(overlays: string[]) {
    const next = { ...selection, overlays };
    if (!folder.trim()) {
      setSelection(next);
      return;
    }
    setLoading(true);
    setLoadingLabel('Applying pattern overlays…');
    setError('');
    try {
      const bundle = normalizeInventoryBundle(await filters.applyOverlays(overlays));
      const scope = next.practices.length ? next.practices : Object.keys(bundle.practices);
      const refreshed = overlayFilterRefresh(selection, { ...next, practices: scope }, bundle.practices);
      adoptInventory(bundle, refreshed);
      setSelection(refreshed);
      await applyFilter(refreshed, bundle.practices);
      window.localStorage.setItem(LAST_OVERLAYS, JSON.stringify(bundle.overlays));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setLoading(false);
    }
  }

  async function addOverlayFolder() {
    try {
      const picked = await graphs.chooseOverlayFolder();
      if (!picked.trim()) {
        return;
      }
      if (selection.overlays.includes(picked)) {
        return;
      }
      await applyOverlays([...selection.overlays, picked]);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    }
  }

  function removeOverlay(overlay: string) {
    void applyOverlays(selection.overlays.filter((item) => item !== overlay));
  }

  function addNamedOverlay(name: string) {
    if (overlayIsActive(selection.overlays, name)) {
      return;
    }
    void applyOverlays([...selection.overlays, name]);
  }

  async function applyFilter(next: FilterSelection, practices = catalog) {
    if (!folder.trim()) {
      setSelection(next);
      return;
    }
    const practiceChanged = joined(next.practices) !== joined(selection.practices);
    const nodeChanged = joined(next.node_types) !== joined(selection.node_types);
    let resolved = next;
    if (practiceChanged) {
      resolved = practiceSelection(selection, next, practices);
      const scope = resolved.practices.length ? resolved.practices : Object.keys(practices);
      setNodeTypes(listed(scope, practices, 'node_types'));
      setRelationships(visibleRelationships(listed(scope, practices, 'edge_types')));
      setRules(listed(scope, practices, 'rules'));
    } else if (nodeChanged) {
      const choices = await filters.choices(next);
      resolved = { ...next, relationships: choices.relationships, rules: choices.rules };
      setRelationships(visibleRelationships(choices.relationships));
      setRules(choices.rules);
    }
    setSelection(resolved);
    const rows = await filters.nodes(resolved);
    const names = new Set(rows.map((row) => row.node_id));
    const bundle = normalizeInventoryBundle(await graphs.inventory());
    const shown = resolved.practices.length ? resolved.practices : Object.keys(bundle.practices);
    setTrees(
      shown
        .map((name) => keep(bundle.practices[name]?.tree, names, resolved.node_types, resolved.violations))
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
            <button
              type="button"
              className="btn-refresh"
              data-testid="force-reload"
              title="Force reload"
              disabled={loading || !folder.trim()}
              onClick={() => void load(folder, selection, true)}
            >
              Force reload
            </button>
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
            availableOverlays={availableOverlays}
            onAddOverlay={() => {
              void addOverlayFolder();
            }}
            onAddNamedOverlay={addNamedOverlay}
            onRemoveOverlay={removeOverlay}
          />
        </div>
        <div className="split">
          <GraphView
            trees={trees}
            loading={loading}
            loadingLabel={loadingLabel}
            loadingLog={loadingLog}
            error={error}
            selectedId={selectedId}
            activeRule={activeRule}
            onSelect={(selection) => void choose(selection)}
          />
          <SourceView
            source={source}
            violation={violation}
            rules={rulesOn(findNode(trees, selectedId))}
            activeRule={activeRule}
            onSelectRule={(name) => {
              const node = findNode(trees, selectedId);
              const rule = node?.children.find((child) => child.type === 'rules')?.children.find((child) => child.name === name);
              if (rule) {
                void choose(selectionForRule(selectedId, rule));
              }
            }}
          />
        </div>
      </div>
    </main>
  );
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

function overlayFilterRefresh(
  previous: FilterSelection,
  next: FilterSelection,
  catalog: Record<string, PracticeInventory>,
): FilterSelection {
  const scope = next.practices.length ? next.practices : Object.keys(catalog);
  const nodes = listed(scope, catalog, 'node_types');
  const edges = visibleRelationships(listed(scope, catalog, 'edge_types'));
  const rules = listed(scope, catalog, 'rules');
  return {
    ...next,
    node_types: mergeNewCatalogItems(previous.node_types, nodes),
    relationships: mergeNewCatalogItems(previous.relationships, edges),
    rules: mergeNewCatalogItems(previous.rules, rules),
  };
}

function readSavedOverlays(): string[] {
  try {
    const raw = window.localStorage.getItem(LAST_OVERLAYS);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as unknown;
    return Array.isArray(parsed) ? parsed.map(String) : [];
  } catch {
    return [];
  }
}

function overlayIsActive(overlays: string[], name: string): boolean {
  return overlays.some((item) => overlayLabel(item) === name || item === name);
}

function overlayLabel(path: string): string {
  const trimmed = path.replace(/[/\\]+$/, '');
  const parts = trimmed.split(/[/\\]/);
  return parts[parts.length - 1] || path;
}

function mergeNewCatalogItems(current: string[], available: string[]): string[] {
  const kept = current.filter((item) => available.includes(item));
  for (const item of available) {
    if (!kept.includes(item)) {
      kept.push(item);
    }
  }
  return kept;
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

function keep(
  node: GraphTree | undefined,
  ids: Set<string>,
  types: string[],
  violationsOnly = false,
): GraphTree | null {
  if (!node) {
    return null;
  }
  const rules = node.children.filter((child) => child.type === 'rules');
  const children = node.children
    .filter((child) => child.type !== 'rules')
    .map((child) => keep(child, ids, types, violationsOnly))
    .filter((child): child is GraphTree => Boolean(child));
  const holder = node.type === node.name;
  if (holder) {
    return children.length > 0 ? { ...node, children } : null;
  }
  const selectedType = types.length === 0 || types.includes(node.type) || node.type === 'Practice';
  if (!selectedType) {
    return children.length > 0 ? { ...node, children } : null;
  }
  const selectedId = violationsOnly ? ids.has(node.node_id) : ids.size === 0 || ids.has(node.node_id);
  if (node.type !== 'Practice' && !selectedId && children.length === 0) {
    return null;
  }
  if (node.type !== 'Practice' && !selectedId) {
    return { ...node, children };
  }
  return { ...node, children: [...children, ...rules] };
}

function findNode(nodes: GraphTree[], id: string): GraphTree | null {
  for (const node of nodes) {
    if (node.node_id === id) {
      return node;
    }
    const child = findNode(node.children ?? [], id);
    if (child) {
      return child;
    }
  }
  return null;
}

function rulesOn(node: GraphTree | null): SourceRule[] {
  const holder = node?.children.find((child) => child.type === 'rules');
  return (holder?.children ?? []).map((rule) => ({
    name: rule.name,
    status: rule.status,
    messages: ruleHits(rule).map((hit) => hit.message).filter(Boolean),
  }));
}
