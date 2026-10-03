/**
 * app.ts — Express app factory for the {{epicSlug}} feature package.
 */
import express from 'express';
import cors from 'cors';
import {
  {{DomainName}}RepositoryServer,
  create{{DomainName}}sRouter,
} from './{{domainName}}/{{domainName}}-server';

export async function createApp(): Promise<express.Application> {
  const app = express();
  app.use(cors());
  app.use(express.json());

  const repo = await {{DomainName}}RepositoryServer.open('data/{{domainNames}}.json');
  app.use('/api/{{domainNames}}', create{{DomainName}}sRouter(repo));

  return app;
}
