/**
 * app.ts — Express app factory for the {{epicSlug}} feature package.
 *
 * Creates the HTTP app and mounts this feature's domain routers. Process
 * listen lives in `serve.ts` so tests can import `createApp` without binding
 * a port. There is no separate app-server package.
 */
import express from 'express';
import cors from 'cors';
import {
  {{DomainName}}RepositoryServer,
  create{{DomainName}}sRouter,
} from './{{domainName}}/{{domainName}}-server';

export function createApp(): express.Application {
  const app = express();
  app.use(cors());
  app.use(express.json());

  const repo = new {{DomainName}}RepositoryServer(/* db */);
  app.use('/api/{{domainNames}}', create{{DomainName}}sRouter(repo));

  return app;
}
