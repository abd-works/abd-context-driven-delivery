import { useEffect, useRef, useState } from 'react';
import wordmarkBlack from './brand/abd.works.wordmark.black.svg?url';
import wordmarkWhite from './brand/abd.works.wordmark.white.svg?url';
import type { CddProgress } from '@cdd/cdd-shared';
import type { ExplorerEntryData, FilterData, GraphRuleData, NodeSourceData } from '@cdd/harness/graph/graph';
import { nodeFilter, type FilterSelection } from './filter/filter-selection';
import { FilterView } from './filter/FilterView';
import { GraphApi } from './graph/graph-api';
import { GraphClient } from './graph/GraphClient';
import { GraphView } from './graph/GraphView';
import { childrenOf, isRule, ruleHits, selectionForRule, type GraphSelection, type TreeItem } from './graph/graph-selection';
import { SourceView, type SourceRule } from './source/SourceView';
import { normalizeInventoryBundle } from './inventory-bundle';
import { overlayPathLabel } from './labels/overlay-labels';
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
const NO_CHOICES: FilterData = { node_types: [], offered_node_types: [], relationships: [], rules: [] };

// A page opened with ?folder= (the chat bar names the session's workpath) loads that folder; one opened on a project
// (?project=, from a ticket's graph widget) shows the graph of the session open there, loaded on its practice roots; a
// page opened with neither shows the folder a person last chose.
const api = new GraphApi();
const graphs = new GraphClient(api);
const FOLDER_QUERY = 'folder';

function openedOnFolder(): string {
  return new URLSearchParams(window.location.search).get(FOLDER_QUERY)?.trim() ?? '';
}

export function App() {
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme ?? '');
  const [folder, setFolder] = useState(() => openedOnFolder() || api.project || (window.localStorage.getItem(LAST_FOLDER) ?? ''));
  const [loadedFolder, setLoadedFolder] = useState('');
  const [filtersOpen, setFiltersOpen] = useState(true);
  const [selection, setSelection] = useState<FilterSelection>(EMPTY);
  const [trees, setTrees] = useState<ExplorerEntryData[]>([]);
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
  // Why the source pane shows no source for the selected node: the graph holds none, or reading it failed.
  const [sourceNote, setSourceNote] = useState('');
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
    const saved = (openedOnFolder() || api.project || window.localStorage.getItem(LAST_FOLDER))?.trim();
    if (saved) {
      void load(saved);
    }
  }, []);

  // The session open in the project can change while the page is open, as when the board makes another ticket active, so
  // a page opened on a project reads it again whenever the person comes back to it; nothing is pushed to it.
  useEffect(() => {
    if (!api.project) {
      return;
    }
    const reread = () => {
      if (!loadingRef.current) {
        void load(api.project);
      }
    };
    window.addEventListener('focus', reread);
    return () => window.removeEventListener('focus', reread);
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

  // The project's open session loads on the roots its practices name, and holds only the practices it works on; a chosen
  // folder loads every practice from that folder.
  async function read(root: string, force: boolean) {
    if (api.project) {
      setPractices((await graphs.practiceNames()) ?? []);
      await graphs.loadPracticeRoots();
      return;
    }
    await graphs.loadWorkingCopy(root, await practiceRoots(root), root, readSavedOverlays(), force);
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
      await read(trimmed, force);
      if (generation !== loadGeneration.current) {
        return;
      }
      const bundle = normalizeInventoryBundle(await graphs.inventory());
      if (generation !== loadGeneration.current) {
        return;
      }
      const synced = { ...next, overlays: bundle.overlays?.length ? bundle.overlays : next.overlays };
      setAvailableOverlays(bundle.available_overlays ?? []);
      await offerChoices(synced);
      await showFilter(synced);
      setLoadedFolder(trimmed);
      if (!api.project) {
        window.localStorage.setItem(LAST_FOLDER, trimmed);
      }
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
    setSourceNote('');
    try {
      const opened = await graphs.source(selection.nodeId);
      const shown = opened?.text != null && opened.file != null ? opened : null;
      setSource(shown);
      if (!shown) setSourceNote('The graph holds no source for this node. Load the folder again if it should.');
    } catch (cause) {
      setSource(null);
      setSourceNote(`The source did not open: ${cause instanceof Error ? cause.message : String(cause)}`);
    }
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
      setAvailableOverlays(bundle.available_overlays ?? []);
      // The overlays change the node types the practices hold, so the node choice starts again from every one offered.
      const applied = { ...next, overlays: bundle.overlays?.length ? bundle.overlays : overlays, node_types: [] };
      await showFilter(chosen(applied, await offerChoices(applied)));
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


  // Python's Filter works out what the filter offers: the node types the practices hold, and the relationships and rules
  // of the node types chosen. practicesBefore names the practices chosen before a change of practice.
  async function offerChoices(next: FilterSelection, practicesBefore?: string[]): Promise<FilterData> {
    const choices = (await graphs.filterChoices(next.practices, next.node_types, practicesBefore)) ?? NO_CHOICES;
    setNodeTypes(choices.offered_node_types);
    setRelationships(choices.relationships);
    setRules(choices.rules);
    return choices;
  }

  // Python's Filter keeps the nodes the selection matches, with the way to each, in every practice it names.
  async function showFilter(resolved: FilterSelection) {
    setSelection(resolved);
    setTrees((await graphs.explorerTrees(nodeFilter(resolved))) ?? []);
  }

  async function applyFilter(next: FilterSelection) {
    if (!folder.trim()) {
      setSelection(next);
      return;
    }
    if (joined(next.practices) !== joined(selection.practices)) {
      await showFilter(chosen(next, await offerChoices(next, selection.practices)));
    } else if (joined(next.node_types) !== joined(selection.node_types)) {
      await showFilter(chosen(next, await offerChoices(next)));
    } else {
      await showFilter(next);
    }
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
              title="Select the session path, the folder the session works in, to load the Knowledge Graph"
              onClick={() => void browse()}
            >
              Session path
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
              placeholder="Session path"
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
            note={sourceNote}
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

function joined(values: string[]): string {
  return values.join('\n');
}

// The selection with the node types, relationships, and rules Python's Filter chose for it.
function chosen(next: FilterSelection, choices: FilterData): FilterSelection {
  return { ...next, node_types: choices.node_types, relationships: choices.relationships, rules: choices.rules };
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
  return overlays.some((item) => overlayPathLabel(item) === name || item === name);
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
