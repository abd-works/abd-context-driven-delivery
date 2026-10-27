/**
 * app.ts — Express app factory for the wires feature package.
 */
import express from 'express';
import cors from 'cors';
import {
  RecipientRepositoryServer,
  createRecipientsRouter,
} from './recipients/recipient-server';

export function createApp(): express.Application {
  const app = express();
  app.use(cors());
  app.use(express.json());

  const repo = new RecipientRepositoryServer(/* db */);
  app.use('/api/recipients', createRecipientsRouter(repo));

  return app;
}
