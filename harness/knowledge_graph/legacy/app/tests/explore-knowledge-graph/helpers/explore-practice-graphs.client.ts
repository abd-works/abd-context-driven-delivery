import {
  ExplorePracticeGraphsBaseHelper,
  KEEP_OPERATIONS_SMALL_FOCUSED,
  SEEDED_GRAPH_ID,
  seededKnowledgeGraph,
} from './explore-practice-graphs.base';
import { KnowledgeGraphsClient } from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph-client';
import { workspaceFiles } from '../examples/knowledge-graph.examples';

export class ExplorePracticeGraphsClientHelper extends ExplorePracticeGraphsBaseHelper {
  private client: KnowledgeGraphsClient | null = null;

  async seed(): Promise<void> {
    const seed = seededKnowledgeGraph();
    globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes('/scan')) {
        const body = JSON.parse(String(init?.body ?? '{}')) as {
          folder?: string;
          files?: { relativePath: string; text: string }[];
        };
        const { knowledgeGraphFromWorkspace } = await import(
          '../../../packages/explore-knowledge-graph/knowledge-graph/workspace'
        );
        const scanned = knowledgeGraphFromWorkspace(
          body.folder ?? 'workspace',
          body.files ?? workspaceFiles(),
          seed.id,
        );
        return new Response(JSON.stringify(scanned.present()), {
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/select-node') || url.includes('/follow-relationship')) {
        const body = JSON.parse(String(init?.body ?? '{}')) as {
          node_id?: string;
          to_id?: string;
        };
        const { KnowledgeGraph } = await import(
          '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph'
        );
        const graph = KnowledgeGraph.fromDto(seed).selectNode(
          body.node_id ?? body.to_id ?? '',
        );
        return new Response(JSON.stringify(graph.present()), {
          headers: { 'Content-Type': 'application/json' },
        });
      }
      const params = new URL(url, 'http://local.test').searchParams;
      const { KnowledgeGraph } = await import(
        '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph'
      );
      let graph = KnowledgeGraph.fromDto(seed);
      graph = graph.filterGraph({
        violations: params.get('violations') === 'true',
        rule: params.get('rule') ?? undefined,
      });
      return new Response(JSON.stringify(graph.present()), {
        headers: { 'Content-Type': 'application/json' },
      });
    }) as typeof fetch;
    await this.browse();
  }

  async cleanup(): Promise<void> {
    this.client = null;
    this.listed = null;
  }

  async browse(): Promise<void> {
    this.client = await KnowledgeGraphsClient.load(SEEDED_GRAPH_ID);
    this.listed = this.client.presentation;
  }

  async selectNode(nodeId: string): Promise<void> {
    this.client = await this.client!.selectNode(nodeId);
    this.listed = this.client.presentation;
  }

  async followRelationship(toId: string): Promise<void> {
    this.client = await this.client!.followRelationship(toId);
    this.listed = this.client.presentation;
  }

  async filterGraph(): Promise<void> {
    this.client = await KnowledgeGraphsClient.load(SEEDED_GRAPH_ID, {
      violations: true,
      rule: KEEP_OPERATIONS_SMALL_FOCUSED,
    });
    this.listed = this.client.presentation;
  }

  async selectFolder(): Promise<void> {
    this.client = await KnowledgeGraphsClient.scan({
      folder: 'workspace',
      files: workspaceFiles(),
    });
    this.listed = this.client.presentation;
  }
}
