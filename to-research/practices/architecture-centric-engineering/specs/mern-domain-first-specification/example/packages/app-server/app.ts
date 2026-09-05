import express from 'express';
import cors from 'cors';
import { RecipientRouter, RecipientRepositoryServer } from '@channelone/recipients-server';

// Composition root: create Express app, instantiate repos, mount domain routers.
export function createApp(): express.Application {
  const app = express();
  app.use(cors());
  app.use(express.json());

  const recipientsRepo = new RecipientRepositoryServer(/* db */);
  app.use('/api/recipients', RecipientRouter.create(recipientsRepo));

  return app;
}
