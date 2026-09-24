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

const SCAN_ROOT_KEY = 'kg-scan-root-v2';
const SCAN_GRAPH_ID_KEY = 'kg-scan-graph-id-v2';

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
  static async scan(input: {
    folder?: string;
    files?: WorkspaceFile[];
    force?: boolean;
  } = {}): Promise<ReturnType<KnowledgeGraph['present']>> {
    let response: Response;
    try {
      response = await fetch('/api/knowledge-graphs/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      });
    } catch {
      throw new Error('Could not reach the explorer API on port 3001');
    }
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
    const query = params.toString();
    const suffix = query ? `?${query}` : '';
    const response = await fetch(`/api/knowledge-graphs/${id}${suffix}`);
    if (!response.ok) {
      throw new Error(`KnowledgeGraph ${id} not found`);
    }
    return response.json() as Promise<ReturnType<KnowledgeGraph['present']>>;
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
    return KnowledgeGraphHttpClient._databaseOp('/api/knowledge-graphs/create-database', folder);
  }

  static async refreshMaster(
    folder: string,
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    return KnowledgeGraphHttpClient._databaseOp('/api/knowledge-graphs/refresh-master', folder);
  }

  static async reloadWorkingCopy(
    folder: string,
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    return KnowledgeGraphHttpClient._databaseOp(
      '/api/knowledge-graphs/reload-working-copy',
      folder,
    );
  }

  private static async _databaseOp(
    url: string,
    folder: string,
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    let response: Response;
    try {
      response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder }),
      });
    } catch {
      throw new Error('Could not reach the explorer API on port 3001');
    }
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
    return new KnowledgeGraphsClient(graph.id, graph.present(), graph);
  }

  static async createDatabase(folder: string): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.createDatabase(folder);
    const graph = graphFromRaw(raw);
    rememberScan(graph.id, graph.folder);
    return new KnowledgeGraphsClient(graph.id, graph.present(), graph);
  }

  static async refreshMaster(folder: string): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.refreshMaster(folder);
    const graph = graphFromRaw(raw);
    rememberScan(graph.id, graph.folder);
    return new KnowledgeGraphsClient(graph.id, graph.present(), graph);
  }

  static async reloadWorkingCopy(folder: string): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.reloadWorkingCopy(folder);
    const graph = graphFromRaw(raw);
    rememberScan(graph.id, graph.folder);
    return new KnowledgeGraphsClient(graph.id, graph.present(), graph);
  }

  static async load(
    id: string,
    filter: GraphFilter = {},
  ): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.loadGraph(id, filter);
    const graph = graphFromRaw(raw).filterGraph(filter);
    rememberScan(id, graph.folder);
    return new KnowledgeGraphsClient(id, graph.present(), graph);
  }

  async selectNode(
    nodeId: string,
    ruleSlug?: string,
  ): Promise<KnowledgeGraphsClient> {
    const graph = this.graph.selectNode(nodeId, ruleSlug);
    return new KnowledgeGraphsClient(this.graphId, graph.present(), graph);
  }

  async followRelationship(toId: string): Promise<KnowledgeGraphsClient> {
    const graph = this.graph.followRelationship(toId);
    return new KnowledgeGraphsClient(this.graphId, graph.present(), graph);
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
  } | null>(null);
  const request = useRef(0);

  const take = useCallback((
    work: Promise<KnowledgeGraphsClient>,
    action?: string,
  ) => {
    const token = ++request.current;
    setLoading(true);
    setScanError('');
    if (action) {
      setWorkStatus({ action, phase: 'working' });
    }
    work
      .then((next) => {
        if (token === request.current) {
          setClient(next);
          if (action) {
            setWorkStatus({ action, phase: 'done' });
          }
        }
      })
      .catch((error: unknown) => {
        if (token === request.current) {
          setScanError(
            error instanceof Error ? error.message : 'Could not scan KnowledgeGraph',
          );
          if (action) {
            setWorkStatus({ action, phase: 'failed' });
          }
        }
      })
      .finally(() => {
        if (token === request.current) {
          setLoading(false);
        }
      });
  }, []);

  useEffect(() => {
    if (id) {
      take(KnowledgeGraphsClient.load(id));
      return;
    }
    take(KnowledgeGraphsClient.scan({ folder: lastScanFolder() }));
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
      take(KnowledgeGraphsClient.scan(input), 'Load Knowledge Graph');
    },
    [take],
  );

  const refreshGraph = useCallback(() => {
    const lastFolder = lastScanFolder();
    take(KnowledgeGraphsClient.scan({ folder: lastFolder, force: true }), 'Refresh');
  }, [take]);

  const createDatabase = useCallback(() => {
    take(KnowledgeGraphsClient.createDatabase(lastScanFolder()), 'Create database');
  }, [take]);

  const refreshMaster = useCallback(() => {
    take(KnowledgeGraphsClient.refreshMaster(lastScanFolder()), 'Refresh master');
  }, [take]);

  const reloadWorkingCopy = useCallback(() => {
    take(
      KnowledgeGraphsClient.reloadWorkingCopy(lastScanFolder()),
      'Reload working copy',
    );
  }, [take]);

  return {
    loading,
    workStatus,
    scanError,
    folder: client?.presentation.folder ?? '',
    listedNodes: client?.presentation.listed_nodes ?? [],
    listedTree: client?.presentation.listed_tree ?? [],
    filterOptions: client?.presentation.filter_options ?? {
      practices: [...PRACTICES],
      stages: [...STAGES],
      node_types: [],
      relationship_types: [...RELATIONSHIP_KINDS],
      rules: [],
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
