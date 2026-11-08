import { useEffect, useRef, useState } from 'react';
import wordmarkBlack from './brand/abd.works.wordmark.black.svg?url';
import wordmarkWhite from './brand/abd.works.wordmark.white.svg?url';
import type { CddProgress } from '@cdd/cdd-shared';
import type { ExplorerEntryData, GraphRuleData, InventoryData, PracticeInventoryData, NodeSourceData } from '@cdd/harness/graph/graph';
import { nodeFilter, type FilterSelection } from './filter/filter-selection';
import { FilterView } from './filter/FilterView';
import { GraphClient } from './graph/GraphClient';
import { GraphView } from './graph/GraphView';
import { childrenOf, isRule, ruleHits, selectionForRule, type GraphSelection, type TreeItem } from './graph/graph-selection';
import { SourceView, type SourceRule } from './source/SourceView';
import { normalizeInventoryBundle } from './inventory-bundle';
import { overlayPathLabel } from './overlay-labels';
import type { ViolationFocus } from './source/violation-prompt';

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

export function App() {
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme ?? '');
  const [folder, setFolder] = useState(() => window.localStorage.getItem(LAST_FOLDER) ?? '');
  const [loadedFolder, setLoadedFolder] = useState('');
  const [filtersOpen, setFiltersOpen] = useState(true);
  const [selection, setSelection] = useState<FilterSelection>(EMPTY);
  const [trees, setTrees] = useState<ExplorerEntryData[]>([]);
  const [catalog, setCatalog] = useState<Record<string, PracticeInventoryData>>({});
  const [practices, setPractices] = useState<string[]>([]);
  const [nodeTypes, setNodeTypes] = useState<string[]>([]);
  const [relationships, setRelationships] = useState<string[]>([]);
  const [rules, setRules] = useState<string[]>([]);
  const [availableOverlays, setAvailableOverlays] = useState<string[]>([]);
  const [overlayApplying, setOverlayApplying] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingLabel, setLoadingLabel] = useState('Loading the graph…');
  const [loadingLog, setLoadingLog] = useState<string[]>([]);
  const [error, setError] = useState('');
  const [selectedId, setSelectedId] = useState('');
  const [activeRule, setActiveRule] = useState('');
  const [violation, setViolation] = useState<ViolationFocus | null>(null);
  const [source, setSource] = useState<NodeSourceData | null>(null);
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
          const steps = (await graphs.api.post<CddProgress[]>('/cdd/progress', {})) ?? [];
          const newest = steps[steps.length - 1]?.message;
          if (newest) {
            setLoadingLog((current) => (current[current.length - 1] === newest ? current : [...current, newest]));
            if (loadingRef.current) {
              setLoadingLabel(newest);
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

  // Every practice the graph can load, each opened on the folder the page loads.
  async function practiceRoots(root: string): Promise<Record<string, string>> {
    const names = (await graphs.practiceNames()) ?? [];
    setPractices(names);
    return Object.fromEntries(names.map((name) => [name, root]));
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
      await graphs.loadWorkingCopy(trimmed, await practiceRoots(trimmed), trimmed, readSavedOverlays(), force);
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
    const opened = await graphs.source(selection.nodeId);
    setSource(opened?.text != null && opened.file != null ? opened : null);
  }

  function adoptInventory(bundle: InventoryData, filter: FilterSelection) {
    setCatalog(bundle.practices);
    setAvailableOverlays(bundle.available_overlays ?? []);
    const overlays = bundle.overlays?.length ? bundle.overlays : filter.overlays;
    const merged = { ...filter, overlays };
    const shown = merged.practices.length ? merged.practices : Object.keys(bundle.practices);
    setTrees(shown.map((name) => bundle.practices[name]?.tree).filter((tree): tree is ExplorerEntryData => Boolean(tree)));
    setNodeTypes(unique(shown.flatMap((name) => bundle.practices[name]?.node_types ?? [])));
    setRelationships(unique(shown.flatMap((name) => bundle.practices[name]?.edge_types ?? [])));
    setRules(unique(shown.flatMap((name) => bundle.practices[name]?.rules ?? [])));
    setSelection(merged);
  }

  async function applyOverlays(overlays: string[]) {
    const next = { ...selection, overlays };
    if (!folder.trim()) {
      setSelection(next);
      return;
    }
    setOverlayApplying(true);
    setLoading(true);
    setLoadingLabel('Applying pattern overlays…');
    setError('');
    try {
      const bundle = normalizeInventoryBundle(await graphs.setOverlays(overlays));
      const scope = next.practices.length ? next.practices : Object.keys(bundle.practices);
      const refreshed = overlayFilterRefresh(selection, { ...next, practices: scope }, bundle.practices, bundle.overlays);
      adoptInventory(bundle, refreshed);
      await applyFilter(refreshed, bundle.practices);
      window.localStorage.setItem(LAST_OVERLAYS, JSON.stringify(bundle.overlays));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setOverlayApplying(false);
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
      setRelationships(listed(scope, practices, 'edge_types'));
      setRules(listed(scope, practices, 'rules'));
    } else if (nodeChanged) {
      const choices = (await graphs.filterChoices(next.practices, next.node_types)) ?? { node_types: [], relationships: [], rules: [] };
      resolved = { ...next, relationships: choices.relationships, rules: choices.rules };
      setRelationships(choices.relationships);
      setRules(choices.rules);
    }
    setSelection(resolved);
    // Python's Filter keeps the nodes the selection matches, with the way to each, in every practice it names.
    setTrees((await graphs.explorerTrees(nodeFilter(resolved))) ?? []);
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
            practices={practices}
            nodeTypes={nodeTypes}
            relationships={relationships}
            rules={rules}
            onChange={(next) => {
              void applyFilter(next);
            }}
            availableOverlays={availableOverlays}
            overlayApplying={overlayApplying}
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
              const rule = rulesUnder(node).find((child) => child.name === name);
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

function unique(values: string[]): string[] {
  return [...new Set(values)];
}

function joined(values: string[]): string {
  return values.join('\n');
}

function listed(
  practices: string[],
  catalog: Record<string, PracticeInventoryData>,
  field: 'node_types' | 'edge_types' | 'rules',
): string[] {
  return unique(practices.flatMap((name) => catalog[name]?.[field] ?? []));
}

function overlayFilterRefresh(
  previous: FilterSelection,
  next: FilterSelection,
  catalog: Record<string, PracticeInventoryData>,
  activeOverlays: string[] = next.overlays,
): FilterSelection {
  const scope = next.practices.length ? next.practices : Object.keys(catalog);
  const nodes = listed(scope, catalog, 'node_types');
  const edges = listed(scope, catalog, 'edge_types');
  const rules = listed(scope, catalog, 'rules');
  return {
    ...next,
    overlays: activeOverlays.length ? activeOverlays : next.overlays,
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
  return overlayPathLabel(path);
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
  catalog: Record<string, PracticeInventoryData>,
): FilterSelection {
  const scope = next.practices.length ? next.practices : Object.keys(catalog);
  const nodes = listed(scope, catalog, 'node_types');
  const edges = listed(scope, catalog, 'edge_types');
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
      added.flatMap((name) => catalog[name]?.edge_types ?? []),
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

function findNode(nodes: TreeItem[], id: string): TreeItem | null {
  for (const node of nodes) {
    if (node.node_id === id) {
      return node;
    }
    const child = findNode(childrenOf(node), id);
    if (child) {
      return child;
    }
  }
  return null;
}

function rulesUnder(node: TreeItem | null): GraphRuleData[] {
  const holder = node ? childrenOf(node).find((child) => child.type === 'rules') : undefined;
  return holder ? childrenOf(holder).filter(isRule) : [];
}

function rulesOn(node: TreeItem | null): SourceRule[] {
  return rulesUnder(node).map((rule) => ({
    name: rule.name,
    status: rule.status,
    messages: ruleHits(rule).map((hit) => hit.message).filter(Boolean),
  }));
}
