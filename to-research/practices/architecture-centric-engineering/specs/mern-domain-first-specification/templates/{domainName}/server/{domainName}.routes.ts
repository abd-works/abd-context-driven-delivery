/**
 * {{domainName}}.routes.ts — Express router factory.
 *
 * Route paths use kebab-case of the domain verb.
 * Every route must have a corresponding API function in the client's {{domainName}}.api.ts.
 */
import { Router } from 'express';
import { {{DomainName}}sRepository } from './{{domainName}}.repository';
import { {{DomainName}}s, Create{{DomainName}}InputSchema } from '@{{appName}}/{{domainNames}}-shared';

export function create{{DomainName}}sRouter(repo: {{DomainName}}sRepository): Router {
  const router = Router();

  router.get('/', async (req, res) => {
    const all = await repo.findAll();
    const activeOnly = req.query.active_only === 'true';
    let collection = new {{DomainName}}s(all);
    if (activeOnly) {
      collection = collection.filterByStatus('Active');
    }
    res.json(collection.toArray());
  });

  router.get('/:id', async (req, res) => {
    const item = await repo.findById(req.params.id);
    if (!item) {
      res.status(404).json({ error: 'Not found' });
      return;
    }
    res.json(item);
  });

  router.post('/', async (req, res) => {
    const validation = Create{{DomainName}}InputSchema.safeParse(req.body);
    if (!validation.success) {
      res.status(400).json({ error: validation.error.issues[0].message });
      return;
    }
    const created = await repo.save(validation.data);
    res.status(201).json(created);
  });

  return router;
}
