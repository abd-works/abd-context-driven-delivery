// The aggregate's routes on {service}, reached only through Apigee at /v1/{{serviceBasePath}}/{{aggregates}}.
import { Router } from 'express';
import { {{Aggregate}}Service, {{Aggregate}}RepositorySql } from './{aggregate}-service';

export function {{aggregate}}ServiceRoutes(repositories: { {{aggregate}}: {{Aggregate}}RepositorySql; events: EventPublisher }): Router {
  const router = Router();
  router.post('/{{aggregates}}/:id/submit', async (req, res, next) => {
    try {
      const submitted = await {{Aggregate}}Service.submit(req.params.id, repositories.{{aggregate}}, repositories.events);
      res.json({ id: submitted.id, status: submitted.status }); // only the fields the screen needs
    } catch (error) {
      next(error); // the error-catalogue middleware sends the sanitised contract
    }
  });
  return router;
}
