// The aggregate's BFF routes: the only server the browser calls.
import { Router } from 'express';
import { {{Aggregate}}Bff, {{Aggregate}}Gateway } from './{aggregate}-bff';

export function {{aggregate}}BffRoutes(): Router {
  const router = Router();
  router.post('/bff/{{aggregates}}/:id/submit', async (req, res, next) => {
    try {
      const submitted = await {{Aggregate}}Bff.submit(req.params.id, new {{Aggregate}}Gateway(req.portalSession));
      res.json({ destination: submitted.destination() });
    } catch (error) {
      next(error);
    }
  });
  return router;
}
