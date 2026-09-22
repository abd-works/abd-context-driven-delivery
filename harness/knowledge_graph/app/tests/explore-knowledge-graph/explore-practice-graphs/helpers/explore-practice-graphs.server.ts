import request from 'supertest';
import type { Express } from 'express';
import { createApp } from '../../../../packages/explore-knowledge-graph/app';
import { KnowledgeGraphRepositoryServer } from '../../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph-server';
import {
  ExplorePracticeGraphsBaseHelper,
  KEEP_OPERATIONS_SMALL_FOCUSED,
  seededKnowledgeGraph,
  SEEDED_GRAPH_ID,
} from './explore-practice-graphs.base';
import { FIXTURE_WORKSPACE } from '../examples/knowledge-graph.examples';

export class ExplorePracticeGraphsServerHelper extends ExplorePracticeGraphsBaseHelper {
  app: Express | null = null;
  private repo: KnowledgeGraphRepositoryServer | null = null;

  async seed(): Promise<void> {
    this.repo = KnowledgeGraphRepositoryServer.openMemory([seededKnowledgeGraph()]);
    this.app = await createApp(this.repo);
  }

  async cleanup(): Promise<void> {
    this.graph = null;
    this.listed = null;
    this.app = null;
    this.repo = null;
  }

  async browse(): Promise<void> {
    const response = await request(this.app!).get(`/api/knowledge-graphs/${SEEDED_GRAPH_ID}`);
    this.listed = response.body;
  }

  async selectNode(nodeId: string): Promise<void> {
    const response = await request(this.app!).post(
      `/api/knowledge-graphs/${SEEDED_GRAPH_ID}/select-node`,
    ).send({ node_id: nodeId });
    this.listed = response.body;
  }

  async followRelationship(toId: string): Promise<void> {
    const response = await request(this.app!).post(
      `/api/knowledge-graphs/${SEEDED_GRAPH_ID}/follow-relationship`,
    ).send({ to_id: toId });
    this.listed = response.body;
  }

  async filterGraph(): Promise<void> {
    const response = await request(this.app!).get(
      `/api/knowledge-graphs/${SEEDED_GRAPH_ID}?violations=true&rule=${KEEP_OPERATIONS_SMALL_FOCUSED}`,
    );
    this.listed = response.body;
  }

  async selectFolder(folder: string = FIXTURE_WORKSPACE): Promise<void> {
    const response = await request(this.app!).post('/api/knowledge-graphs/scan').send({
      folder,
    });
    this.listed = response.body;
  }
}
