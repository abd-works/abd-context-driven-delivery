import { useCallback, useEffect, useState } from 'react';
import {
  KnowledgeGraph,
  KnowledgeGraphSchema,
  type GraphFilter,
  type SourceRangeDto,
} from './knowledge-graph';

function hydrate(raw: unknown): KnowledgeGraph {
  const parsed = KnowledgeGraphSchema.parse(
    (raw as { knowledge_graph?: unknown }).knowledge_graph ?? raw,
  );
  return KnowledgeGraph.fromDto(parsed);
}

export class KnowledgeGraphHttpClient {
  static async scan(
    folder: string,
  ): Promise<ReturnType<KnowledgeGraph['present']>> {
    const response = await fetch('/api/knowledge-graphs/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folder }),
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

  static async scan(folder: string): Promise<KnowledgeGraphsClient> {
    const raw = await KnowledgeGraphHttpClient.scan(folder);
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

  const selectFolder = useCallback((folder: string) => {
    setLoading(true);
    KnowledgeGraphsClient.scan(folder)
      .then(setClient)
      .finally(() => setLoading(false));
  }, []);

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

export function KnowledgeGraphExplorerView({ graphId = '' }: { graphId?: string }) {
  const {
    loading,
    folder: scannedFolder,
    listedNodes,
    selectedNode,
    sourceFile,
    selectNode,
    followRelationship,
    filterGraph,
    selectFolder,
  } = useKnowledgeGraph(graphId);
  const [rule, setRule] = useState('');
  const [violations, setViolations] = useState(false);
  const [folder, setFolder] = useState(scannedFolder);

  useEffect(() => {
    if (scannedFolder) {
      setFolder(scannedFolder);
    }
  }, [scannedFolder]);

  return (
    <div className="knowledge-graph-explorer">
      <header>
        <h1>KnowledgeGraph</h1>
        <form
          className="folder-scan"
          onSubmit={(event) => {
            event.preventDefault();
            if (folder.trim()) {
              selectFolder(folder.trim());
            }
          }}
        >
          <label>
            folder
            <input
              data-testid="working-folder"
              value={folder}
              onChange={(event) => setFolder(event.target.value)}
              placeholder="C:\\path\\to\\workspace"
            />
          </label>
          <button type="submit" data-testid="scan-folder">
            Scan
          </button>
        </form>
        <div className="filters">
          <label>
            violations
            <input
              type="checkbox"
              checked={violations}
              onChange={(event) => {
                const next = event.target.checked;
                setViolations(next);
                filterGraph({ violations: next, rule: rule || undefined });
              }}
            />
          </label>
          <label>
            rule
            <input
              value={rule}
              onChange={(event) => setRule(event.target.value)}
              onBlur={() =>
                filterGraph({ violations, rule: rule || undefined })
              }
            />
          </label>
        </div>
      </header>
      <div className="split">
        <nav className="tree" data-testid="practice-graph-tree">
          {loading && <p>Loading KnowledgeGraph...</p>}
          {!loading && listedNodes.length === 0 && (
            <p>Select a folder to scan</p>
          )}
          <ul>
            {listedNodes.map((node) => (
              <li key={node.node_id}>
                <button
                  type="button"
                  className={
                    selectedNode?.node_id === node.node_id ? 'selected' : ''
                  }
                  onClick={() => selectNode(node.node_id)}
                >
                  {node.name}
                </button>
                <ul>
                  {Object.entries(node.rule_statuses).map(([slug, status]) => (
                    <li key={slug}>
                      {slug} {status}
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        </nav>
        <section className="source" data-testid="source-file">
          {sourceFile ? (
            <pre>
              <h2>{sourceFile.file}</h2>
              <code data-start-line={sourceFile.start_line}>
                {sourceFile.text}
              </code>
            </pre>
          ) : (
            <p>No source file</p>
          )}
        </section>
      </div>
      {selectedNode && !selectedNode.is_file && (
        <button
          type="button"
          hidden
          onClick={() =>
            selectedNode && followRelationship(selectedNode.node_id)
          }
        >
          follow
        </button>
      )}
    </div>
  );
}
