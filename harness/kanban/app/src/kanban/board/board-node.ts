import type { Request } from 'express'
import { z } from 'zod'

import { BoardTools, type Board, type HelpData } from '@cdd/harness/kanban/board'

const WipLimit = z.object({ stage: z.string().min(1), limit: z.number().int().positive() })
const HelpAddress = z.object({ practice: z.string().min(1), fidelity: z.string().default('') })

export class BoardNode extends BoardTools {
  setWipLimitRequested(req: Request): Promise<Board> {
    const { stage, limit } = WipLimit.parse(req.body)
    return this.setWipLimit(stage, limit)
  }

  helpRequested(req: Request): Promise<HelpData> {
    const { practice, fidelity } = HelpAddress.parse(req.query)
    return this.help(practice, fidelity)
  }
}
