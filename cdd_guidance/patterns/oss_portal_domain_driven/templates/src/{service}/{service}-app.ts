// Cloud Run boot for {service}: internal ingress only, so the service is reachable through Apigee and never from a
// browser (pack §2.2, §3.2). Secrets are read from Secret Manager here, at start-up (OP-08).
import express from 'express';
import { {{aggregate}}ServiceRoutes } from './{aggregate}/{aggregate}-service-routes';
import { errorCatalogueMiddleware } from './errors';

export async function serviceApp(): Promise<express.Express> {
  const app = express();
  app.use(express.json({ limit: '1mb' }));
  app.use('/v1/{{serviceBasePath}}', {{aggregate}}ServiceRoutes(await repositories()));
  app.use(errorCatalogueMiddleware); // the uniform sanitised error contract (§3.3 step 7)
  return app;
}
