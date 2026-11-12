// citizen-portal-app: Angular SSR and the Node Backend-for-Frontend (§3.1, §3.2). The browser gets an opaque HttpOnly,
// Secure, SameSite=Lax session cookie; tokens stay in the server-side session.
import express from 'express';
import { portalSession } from './session';
import { angularSsr } from './ssr';
import { {{aggregate}}BffRoutes } from '@src/{service}/{aggregate}/{aggregate}-bff-routes';

export function portalServer(): express.Express {
  const app = express();
  app.use(portalSession({ cookie: { httpOnly: true, secure: true, sameSite: 'lax' } }));
  app.use(express.json({ limit: '1mb' }));
  app.use({{aggregate}}BffRoutes());
  app.get('*', angularSsr());
  return app;
}
