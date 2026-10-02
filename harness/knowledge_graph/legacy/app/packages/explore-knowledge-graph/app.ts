import express from 'express';
import cors from 'cors';
import {
  KnowledgeGraphRepositoryServer,
  createKnowledgeGraphsRouter,
} from './knowledge-graph/knowledge-graph-server';

export async function createApp(
  repo?: KnowledgeGraphRepositoryServer,
): Promise<express.Application> {
  const app = express();
  app.use(cors());
  app.use(express.json({ limit: '2mb' }));
  const store = repo ?? KnowledgeGraphRepositoryServer.openMemory();
  app.use('/api/knowledge-graphs', createKnowledgeGraphsRouter(store));
  return app;
}
