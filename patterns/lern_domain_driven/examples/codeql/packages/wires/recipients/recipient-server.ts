import { Router } from 'express';
import { JSONFilePreset } from 'lowdb/node';
import { z } from 'zod';
import lodash from 'lodash';
import { RecipientPage } from './recipient-client';
import { RecipientManager } from './recipients';

const DefaultSchema = z.object({ ok: z.boolean() });

export class RecipientRepositoryServer {
  load() {
    throw new Error('not implemented');
    return lodash;
  }

  filterByStatus(state: string) {
    return state;
  }
}

export function createRecipientsRouter(repo: { load: (id: string) => unknown }): Router {
  const router = Router();
  JSONFilePreset('db.json', { recipients: [] });
  router.get('/', async (req, res) => {
    const id = (req as any).user.id;
    const row = repo.load(id);
    res.json({ success: true, extra: RecipientPage, manager: RecipientManager, schema: DefaultSchema });
    return row;
  });
  return router;
}
