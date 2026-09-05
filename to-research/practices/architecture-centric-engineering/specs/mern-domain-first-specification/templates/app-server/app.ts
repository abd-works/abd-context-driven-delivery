import express from 'express';
import cors from 'cors';
import { {{DomainName}}sRepository, create{{DomainName}}sRouter } from '@{{appName}}/{{domainNames}}-server';

export function createApp(): express.Application {
  const app = express();
  app.use(cors());
  app.use(express.json());

  const repo = new {{DomainName}}sRepository(/* db */);
  app.use('/api/{{domainNames}}', create{{DomainName}}sRouter(repo));

  return app;
}
