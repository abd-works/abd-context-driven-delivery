import type { Request } from 'express'
import { z } from 'zod'

import { BacklogItemTools, type BacklogItem } from '@cdd/harness/kanban/backlog-item'

import type { CddConnectionNode } from '../../cdd/cdd-connection-node'

const BacklogItemAddress = z.object({ title: z.string().min(1) })
const NewBacklogItem = BacklogItemAddress.extend({ text: z.string().default('') })

export class BacklogItemNode extends BacklogItemTools {
  static fromRequest(cdd: CddConnectionNode, req: Request): BacklogItemNode {
    return new BacklogItemNode(cdd, BacklogItemAddress.parse(req.params).title)
  }

  static addRequested(cdd: CddConnectionNode, req: Request): Promise<BacklogItem> {
    const { title, text } = NewBacklogItem.parse(req.body)
    return BacklogItemTools.add(cdd, title, text)
  }
}
