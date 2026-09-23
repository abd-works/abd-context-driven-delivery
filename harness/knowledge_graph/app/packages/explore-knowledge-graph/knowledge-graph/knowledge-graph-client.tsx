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

const SCAN_ROOT_KEY = 'kg-scan-root';
const SCAN_GRAPH_ID_KEY = 'kg-scan-graph-id';

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
    const response = await fetch('/api/knowledge-graphs/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    if (!response.ok) {
      throw new Error('Could not scan KnowledgeGraph');
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
  const request = useRef(0);

  const take = useCallback((work: Promise<KnowledgeGraphsClient>) => {
    const token = ++request.current;
    setLoading(true);
    work
      .then((next) => {
        if (token === request.current) {
          setClient(next);
        }
      })
      .finally(() => {
        if (token === request.current) {
          setLoading(false);
        }
      });
  }, []);

  useEffect(() => {
    take(openLastGraph(id));
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
      take(KnowledgeGraphsClient.scan(input));
    },
    [take],
  );

  const refreshGraph = useCallback(() => {
    const lastFolder =
      (typeof window !== 'undefined'
        ? window.localStorage.getItem(SCAN_ROOT_KEY)
        : '') ?? '';
    take(KnowledgeGraphsClient.scan({ folder: lastFolder, force: true }));
  }, [take]);

  return {
    loading,
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
    selectedRule: client?.presentation.selected_rule ?? null,
    sourceFile: client?.presentation.source_file as SourceRangeDto | null,
    selectNode,
    followRelationship,
    filterGraph,
    selectFolder,
    refreshGraph,
  };
}

async function openLastGraph(
  id: string,
  options: { rescan?: boolean; folder?: string } = {},
): Promise<KnowledgeGraphsClient> {
  const lastFolder =
    options.folder ??
    (typeof window !== 'undefined'
      ? window.localStorage.getItem(SCAN_ROOT_KEY) ?? ''
      : '');
  const lastId =
    typeof window !== 'undefined'
      ? window.localStorage.getItem(SCAN_GRAPH_ID_KEY) ?? ''
      : '';
  if (id) {
    return KnowledgeGraphsClient.load(id);
  }
  if (lastId) {
    try {
      return await KnowledgeGraphsClient.load(lastId);
    } catch {
      // Last graph is gone from the server; rebuild from the last folder.
    }
  }
  return KnowledgeGraphsClient.scan({ folder: lastFolder });
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
