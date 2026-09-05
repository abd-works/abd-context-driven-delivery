import { Router, Request } from 'express';
import { SelectRecipientsSchema, RecipientRepository } from '@channelone/recipients-shared';
import { RecipientsServer } from './RecipientsServer';

declare global {
  namespace Express {
    interface Request {
      user?: { enterpriseId: string; token: string };
    }
  }
}

export class RecipientRouter {
  static create(repo: RecipientRepository): Router {
    const router = Router();

    router.get('/', async (req: Request, res) => {
      const enterpriseId = req.user?.enterpriseId ?? '';
      const activeOnly = req.query.activeOnly === 'true';

      const recipients = await RecipientsServer.loadByEnterprise(enterpriseId, repo, { activeOnly });
      res.json({ recipients, total: recipients.length });
    });

    router.post('/select', async (req, res) => {
      const result = SelectRecipientsSchema.safeParse(req.body);
      if (!result.success) {
        return res.status(400).json({ errors: result.error.issues });
      }
      const selected = await RecipientsServer.selectByIds(result.data.recipientIds, repo);
      res.json({ selected });
    });

    return router;
  }
}
