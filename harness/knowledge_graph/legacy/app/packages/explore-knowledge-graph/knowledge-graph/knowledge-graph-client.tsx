import { useCallback, useEffect, useRef, useState } from 'react';
import {
  PRACTICES,
  RELATIONSHIP_KINDS,
  STAGES,
} from './catalog';
import {
  KnowledgeGraph,
  type GraphFilter,
  type KnowledgeGraphDto,
  type SourceRangeDto,
} from './knowledge-graph';
import { type WorkspaceFile } from './workspace';
import { sourcesMissingText, sourceKey, withSourceText } from '../source-text';

const SCAN_ROOT_KEY = 'kg-scan-root-v2';
const SCAN_GRAPH_ID_KEY = 'kg-scan-graph-id-v2';
const GRAPH_DEADLINE_MS = 45_000;
const DATABASE_DEADLINE_MS = 90_000;

async function postJson(
  url: string,
  body: unknown,
  deadlineMs: number,
  label: string,
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), deadlineMs);
  try {
    return await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error(
        `${label} stopped after ${deadlineMs / 1000}s with no result`,
      );
    }
    throw new Error('Could not reach the explorer API on port 3001');
  } finally {
    clearTimeout(timer);
  }
}

function rememberScan(graphId: string, folder: string) {
  if (typeof window === 'undefined') {
    return;
  }
  if (graphId) {
    window.localStorage.setItem(SCAN_GRAPH_ID_KEY, graphId);
  }
  if (folder) {
    window.localStorage.setItem(SCAN_ROOT_KEY, folder);
  }
}

function graphFromRaw(raw: unknown): KnowledgeGraph {
  const body = raw as { knowledge_graph?: KnowledgeGraphDto };
  return KnowledgeGraph.fromDto(
    (body.knowledge_graph ?? raw) as KnowledgeGraphDto,
  );
}

export class KnowledgeGraphHttpClient {
  static async scan(
    input: {
      folder?: string;
      files?: WorkspaceFile[];
      force?: boolean;
    } = {},
    label = 'Load Knowledge Graph',
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    const response = await postJson(
      '/api/knowledge-graphs/scan',
      input,
      GRAPH_DEADLINE_MS,
      label,
    );
    if (!response.ok) {
      const detail = (await response.json().catch(() => ({}))) as {
        error?: string;
      };
      throw new Error(detail.error ?? 'Could not scan KnowledgeGraph');
    }
    return response.json() as Promise<ReturnType<KnowledgeGraph['present']>>;
  }

  static async loadGraph(
    id: string,
    filter: GraphFilter = {},
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    const params = new URLSearchParams();
    appendList(params, 'practice', filter.practices, filter.practice);
    appendList(params, 'stage', filter.stages, filter.fidelity);
    appendList(params, 'node_type', filter.nodeTypes, filter.nodeType);
    appendList(
      params,
      'relationship_type',
      filter.relationshipTypes,
      filter.relationshipType,
    );
    if (filter.connectorKind) params.set('connector_kind', filter.connectorKind);
    if (filter.node) params.set('node', filter.node);
    if (filter.violations) params.set('violations', 'true');
    appendList(params, 'rule', filter.rules, filter.rule);
    appendList(params, 'rule_source', filter.ruleSources);
    const query = params.toString();
    const suffix = query ? `?${query}` : '';
    const response = await fetch(`/api/knowledge-graphs/${id}${suffix}`);
    if (!response.ok) {
      throw new Error(`KnowledgeGraph ${id} not found`);
    }
    return response.json() as Promise<ReturnType<KnowledgeGraph['present']>>;
  }

  static async readSource(
    folder: string,
    ranges: SourceRangeDto[],
  ): Promise<SourceRangeDto[]> {
    const response = await fetch('/api/knowledge-graphs/source', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        folder,
        ranges: ranges.map((range) => ({
          file: range.file,
          start_line: range.start_line,
          end_line: range.end_line,
        })),
      }),
    });
    if (!response.ok) {
      throw new Error('Could not read source');
    }
    const body = (await response.json()) as { ranges?: SourceRangeDto[] };
    return body.ranges ?? [];
  }

  static async selectNode(
    id: string,
    nodeId: string,
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    const response = await fetch(`/api/knowledge-graphs/${id}/select-node`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ node_id: nodeId }),
    });
    return response.json() as Promise<ReturnType<KnowledgeGraph['present']>>;
  }

  static async followRelationship(
    id: string,
    toId: string,
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    const response = await fetch(`/api/knowledge-graphs/${id}/follow-relationship`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to_id: toId }),
    });
    return response.json() as Promise<ReturnType<KnowledgeGraph['present']>>;
  }

  static async createDatabase(
    folder: string,
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    return KnowledgeGraphHttpClient._databaseOp(
      '/api/knowledge-graphs/create-database',
      folder,
      'Create database',
    );
  }

  static async refreshMaster(
    folder: string,
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    return KnowledgeGraphHttpClient._databaseOp(
      '/api/knowledge-graphs/refresh-master',
      folder,
      'Refresh master',
    );
  }

  static async reloadWorkingCopy(
    folder: string,
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    return KnowledgeGraphHttpClient._databaseOp(
      '/api/knowledge-graphs/reload-working-copy',
      folder,
      'Reload working copy',
    );
  }

  private static async _databaseOp(
    url: string,
    folder: string,
    label: string,
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    const response = await postJson(
      url,
      { folder },
      DATABASE_DEADLINE_MS,
      label,
    );
    if (!response.ok) {
      const detail = (await response.json().catch(() => ({}))) as {
        error?: string;
      };
      throw new Error(detail.error ?? 'Database operation failed');
    }
    return response.json() as Promise<ReturnType<KnowledgeGraph['present']>>;
  }
}

export class KnowledgeGraphClient extends KnowledgeGraph {
  cardCssClass(isSelected: boolean): string {
    return `graph-node${isSelected ? ' selected' : ''}`;
  }
}

function takePresentation(
  raw: ReturnType<KnowledgeGraph['present']>,
  graph: KnowledgeGraph,
  graphId?: string,
): KnowledgeGraphsClient {
  return new KnowledgeGraphsClient(graphId ?? graph.id, raw, graph);
}

async function hydrateSelection(graph: KnowledgeGraph, folder: string): Promise<void> {
  const gaps = graph.selectionSourceRanges();
  if (gaps.length === 0) {
    return;
  }
  try {
    graph.hydrateSource(await KnowledgeGraphHttpClient.readSource(folder, gaps));
  } catch {
    /* pane still opens; nested bodies stay empty if the file cannot be read */
  }
}

async function fillSourceTree(
  folder: string,
  tree: ReturnType<KnowledgeGraph['present']>['selected_tree'],
): Promise<ReturnType<KnowledgeGraph['present']>['selected_tree']> {
  if (!folder || !tree) {
    return tree;
  }
  const gaps = sourcesMissingText(tree);
  if (gaps.length === 0) {
    return tree;
  }
  try {
    const ranges = await KnowledgeGraphHttpClient.readSource(folder, gaps);
    const texts = new Map(ranges.map((range) => [sourceKey(range), range.text ?? '']));
    return withSourceText(tree, texts);
  } catch {
    return tree;
  }
}

export class KnowledgeGraphsClient {
  constructor(
    readonly graphId: string,
    readonly presentation: ReturnType<KnowledgeGraph['present']>,
    readonly graph: KnowledgeGraph,
  ) {}

  static async scan(input: {
    folder?: string;
    files?: WorkspaceFile[];
    force?: boolean;
  } = {}): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.scan(input);
    const graph = graphFromRaw(raw);
    rememberScan(graph.id, graph.folder);
    return takePresentation(raw, graph);
  }

  static async createDatabase(folder: string): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.createDatabase(folder);
    const graph = graphFromRaw(raw);
    rememberScan(graph.id, graph.folder);
    return takePresentation(raw, graph);
  }

  static async refreshMaster(folder: string): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.refreshMaster(folder);
    const graph = graphFromRaw(raw);
    rememberScan(graph.id, graph.folder);
    return takePresentation(raw, graph);
  }

  static async reloadWorkingCopy(folder: string): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.reloadWorkingCopy(folder);
    const graph = graphFromRaw(raw);
    rememberScan(graph.id, graph.folder);
    return takePresentation(raw, graph);
  }

  static async load(
    id: string,
    filter: GraphFilter = {},
  ): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.loadGraph(id, filter);
    const graph = graphFromRaw(raw).filterGraph(filter);
    rememberScan(id, graph.folder);
    return takePresentation(raw, graph, id);
  }

  async selectNode(
    nodeId: string,
    ruleSlug?: string,
  ): Promise<KnowledgeGraphsClient> {
    const graph = this.graph.selectNode(nodeId, ruleSlug);
    return this._withSelection(graph);
  }

  async followRelationship(toId: string): Promise<KnowledgeGraphsClient> {
    const graph = this.graph.followRelationship(toId);
    return this._withSelection(graph);
  }

  private async _withSelection(graph: KnowledgeGraph): Promise<KnowledgeGraphsClient> {
    const folder = this.presentation.folder;
    if (folder) {
      await hydrateSelection(graph, folder);
      await hydrateSelection(graph, folder);
    }
    const pane = graph.presentSelection();
    const selected_tree = await fillSourceTree(folder, pane.selected_tree);
    return new KnowledgeGraphsClient(
      this.graphId,
      {
        ...this.presentation,
        ...pane,
        selected_tree,
        source_file: selected_tree?.source ?? pane.source_file,
      },
      graph,
    );
  }

  async filterGraph(filter: GraphFilter): Promise<KnowledgeGraphsClient> {
    const graph = this.graph.filterGraph(filter);
    return new KnowledgeGraphsClient(this.graphId, graph.present(), graph);
  }
}

export function useKnowledgeGraph(id: string) {
  const [client, setClient] = useState<KnowledgeGraphsClient | null>(null);
  const [loading, setLoading] = useState(false);
  const [scanError, setScanError] = useState('');
  const [workStatus, setWorkStatus] = useState<{
    action: string;
    phase: 'working' | 'done' | 'failed';
    seconds: number;
    detail: string;
  } | null>(null);
  const request = useRef(0);

  const take = useCallback((
    work: Promise<KnowledgeGraphsClient>,
    action?: string,
  ) => {
    const token = ++request.current;
    const started = Date.now();
    setLoading(true);
    setScanError('');
    if (action) {
      setWorkStatus({ action, phase: 'working', seconds: 0, detail: '' });
    }
    const clock = action
      ? window.setInterval(() => {
          if (token !== request.current) {
            window.clearInterval(clock);
            return;
          }
          setWorkStatus((current) =>
            current?.phase === 'working' && current.action === action
              ? {
                  ...current,
                  seconds: Math.floor((Date.now() - started) / 1000),
                }
              : current,
          );
        }, 1000)
      : 0;
    work
      .then((next) => {
        if (token === request.current) {
          setClient(next);
          if (action) {
            setWorkStatus({
              action,
              phase: 'done',
              seconds: Math.floor((Date.now() - started) / 1000),
              detail: '',
            });
          }
        }
      })
      .catch((error: unknown) => {
        if (token === request.current) {
          const detail =
            error instanceof Error ? error.message : 'Could not scan KnowledgeGraph';
          setScanError(detail);
          if (action) {
            setWorkStatus({
              action,
              phase: 'failed',
              seconds: Math.floor((Date.now() - started) / 1000),
              detail,
            });
          }
        }
      })
      .finally(() => {
        if (clock) {
          window.clearInterval(clock);
        }
        if (token === request.current) {
          setLoading(false);
        }
      });
  }, []);

  useEffect(() => {
    if (id) {
      take(KnowledgeGraphsClient.load(id), 'Load Knowledge Graph');
      return;
    }
    take(
      KnowledgeGraphsClient.scan(
        { folder: lastScanFolder() },
        'Load Knowledge Graph',
      ),
      'Load Knowledge Graph',
    );
  }, [id, take]);

  const selectNode = useCallback((nodeId: string, ruleSlug?: string) => {
    setClient((prev) => {
      if (!prev) return prev;
      void prev.selectNode(nodeId, ruleSlug).then((next) => {
        setClient((current) =>
          current?.graphId === prev.graphId ? next : current,
        );
      });
      return prev;
    });
  }, []);

  const followRelationship = useCallback((toId: string) => {
    setClient((prev) => {
      if (!prev) return prev;
      void prev.followRelationship(toId).then((next) => {
        setClient((current) =>
          current?.graphId === prev.graphId ? next : current,
        );
      });
      return prev;
    });
  }, []);

  const filterGraph = useCallback((filter: GraphFilter) => {
    setClient((prev) => {
      if (!prev) return prev;
      void prev.filterGraph(filter).then((next) => {
        setClient((current) =>
          current?.graphId === prev.graphId ? next : current,
        );
      });
      return prev;
    });
  }, []);

  const selectFolder = useCallback(
    (input: { folder?: string; files?: WorkspaceFile[] } = {}) => {
      take(
        KnowledgeGraphsClient.scan(
          { ...input, force: true },
          'Load Knowledge Graph',
        ),
        'Load Knowledge Graph',
      );
    },
    [take],
  );

  const refreshGraph = useCallback(() => {
    const lastFolder = lastScanFolder();
    take(
      KnowledgeGraphsClient.scan({ folder: lastFolder, force: true }, 'Refresh'),
      'Refresh',
    );
  }, [take]);

  const createDatabase = useCallback((root?: string) => {
    take(
      KnowledgeGraphsClient.createDatabase(root || lastScanFolder()),
      'Create database',
    );
  }, [take]);

  const refreshMaster = useCallback((root?: string) => {
    take(
      KnowledgeGraphsClient.refreshMaster(root || lastScanFolder()),
      'Refresh master',
    );
  }, [take]);

  const reloadWorkingCopy = useCallback((root?: string) => {
    take(
      KnowledgeGraphsClient.reloadWorkingCopy(root || lastScanFolder()),
      'Reload working copy',
    );
  }, [take]);

  return {
    loading,
    workStatus,
    scanError,
    folder: client?.presentation.folder ?? '',
    listedTree: client?.presentation.listed_tree ?? [],
    filterOptions: client?.presentation.filter_options ?? {
      practices: [...PRACTICES],
      stages: [...STAGES],
      node_types: [],
      relationship_types: [...RELATIONSHIP_KINDS],
      rules: [],
      rule_sources: ['base', 'project'],
    },
    selectedNode: client?.presentation.selected_node ?? null,
    selectedTree: client?.presentation.selected_tree ?? null,
    selectedRule: client?.presentation.selected_rule ?? null,
    sourceFile: client?.presentation.source_file as SourceRangeDto | null,
    selectNode,
    followRelationship,
    filterGraph,
    selectFolder,
    refreshGraph,
    createDatabase,
    refreshMaster,
    reloadWorkingCopy,
  };
}

function lastScanFolder(): string {
  if (typeof window === 'undefined') {
    return '';
  }
  return window.localStorage.getItem(SCAN_ROOT_KEY) ?? '';
}

function appendList(
  params: URLSearchParams,
  key: string,
  values?: string[],
  fallback?: string,
) {
  const items = values && values.length > 0 ? values : fallback ? [fallback] : [];
  for (const item of items) {
    params.append(key, item);
  }
}
