import type { APIRequestContext } from '@playwright/test';
import {
  ExplorePracticeGraphsBaseHelper,
  KEEP_OPERATIONS_SMALL_FOCUSED,
  passingLoadOperation,
  SEEDED_GRAPH_ID,
} from './explore-practice-graphs.base';
import { workspaceFiles } from '../examples/knowledge-graph.examples';

export class ExplorePracticeGraphsE2eHelper extends ExplorePracticeGraphsBaseHelper {
  graphId = SEEDED_GRAPH_ID;

  async seed(request: APIRequestContext): Promise<void> {
    const response = await request.post('http://localhost:3001/api/knowledge-graphs/scan', {
      data: {
        folder: 'workspace',
        files: workspaceFiles(),
      },
    });
    const body = (await response.json()) as {
      knowledge_graph?: { id?: string };
      id?: string;
    };
    this.graphId = body.knowledge_graph?.id ?? body.id ?? this.graphId;
  }

  async cleanup(): Promise<void> {
    this.listed = null;
  }

  graphQuery(): string {
    return `/?id=${this.graphId}`;
  }

  ruleSlug(): string {
    return KEEP_OPERATIONS_SMALL_FOCUSED;
  }

  passingName(): string {
    return passingLoadOperation.name;
  }
}
