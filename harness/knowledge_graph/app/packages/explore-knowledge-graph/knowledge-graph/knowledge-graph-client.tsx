import { useCallback, useEffect, useState } from 'react';
import {
  KnowledgeGraph,
  KnowledgeGraphSchema,
  type GraphFilter,
  type SourceRangeDto,
} from './knowledge-graph';
import { type WorkspaceFile } from './workspace';

function hydrate(raw: unknown): KnowledgeGraph {
  const parsed = KnowledgeGraphSchema.parse(
    (raw as { knowledge_graph?: unknown }).knowledge_graph ?? raw,
  );
  return KnowledgeGraph.fromDto(parsed);
}

export class KnowledgeGraphHttpClient {
  static async scan(input: {
    folder: string;
    files?: WorkspaceFile[];
  }): Promise<ReturnType<KnowledgeGraph['present']>> {
    const response = await fetch('/api/knowledge-graphs/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    return response.json() as Promise<ReturnType<KnowledgeGraph['present']>>;
  }

  static async loadGraph(
    id: string,
    filter: GraphFilter = {},
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    const params = new URLSearchParams();
    if (filter.practice) params.set('practice', filter.practice);
    if (filter.connectorKind) params.set('connector_kind', filter.connectorKind);
    if (filter.node) params.set('node', filter.node);
    if (filter.violations) params.set('violations', 'true');
    if (filter.rule) params.set('rule', filter.rule);
    const query = params.toString();
    const suffix = query ? `?${query}` : '';
    const response = await fetch(`/api/knowledge-graphs/${id}${suffix}`);
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
  ) {}

  static async scan(input: {
    folder: string;
    files?: WorkspaceFile[];
  }): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.scan(input);
    const graph = hydrate(raw);
    return new KnowledgeGraphsClient(graph.id, graph.present());
  }

  static async load(
    id: string,
    filter: GraphFilter = {},
  ): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.loadGraph(id, filter);
    const graph = hydrate(raw);
    const viewed = graph.filterGraph(filter);
    return new KnowledgeGraphsClient(id, viewed.present());
  }

  async selectNode(nodeId: string): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.selectNode(this.graphId, nodeId);
    const graph = hydrate(raw).selectNode(nodeId);
    return new KnowledgeGraphsClient(this.graphId, graph.present());
  }

  async followRelationship(toId: string): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.followRelationship(this.graphId, toId);
    const graph = hydrate(raw).followRelationship(toId);
    return new KnowledgeGraphsClient(this.graphId, graph.present());
  }

  async filterGraph(filter: GraphFilter): Promise<KnowledgeGraphsClient> {
    return KnowledgeGraphsClient.load(this.graphId, filter);
  }
}

export function useKnowledgeGraph(id: string) {
  const [client, setClient] = useState<KnowledgeGraphsClient | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!id) {
      return;
    }
    setLoading(true);
    KnowledgeGraphsClient.load(id)
      .then(setClient)
      .finally(() => setLoading(false));
  }, [id]);

  const selectNode = useCallback((nodeId: string) => {
    setClient((prev) => {
      if (!prev) return prev;
      void prev.selectNode(nodeId).then(setClient);
      return prev;
    });
  }, []);

  const followRelationship = useCallback((toId: string) => {
    setClient((prev) => {
      if (!prev) return prev;
      void prev.followRelationship(toId).then(setClient);
      return prev;
    });
  }, []);

  const filterGraph = useCallback((filter: GraphFilter) => {
    setClient((prev) => {
      if (!prev) return prev;
      void prev.filterGraph(filter).then(setClient);
      return prev;
    });
  }, []);

  const selectFolder = useCallback(
    (input: { folder: string; files?: WorkspaceFile[] }) => {
      setLoading(true);
      KnowledgeGraphsClient.scan(input)
        .then(setClient)
        .finally(() => setLoading(false));
    },
    [],
  );

  return {
    loading,
    folder: client?.presentation.folder ?? '',
    listedNodes: client?.presentation.listed_nodes ?? [],
    selectedNode: client?.presentation.selected_node ?? null,
    sourceFile: client?.presentation.source_file as SourceRangeDto | null,
    selectNode,
    followRelationship,
    filterGraph,
    selectFolder,
  };
}
