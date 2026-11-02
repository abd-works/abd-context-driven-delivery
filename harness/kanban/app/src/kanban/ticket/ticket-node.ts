import type { Request } from 'express'
import { z } from 'zod'

import { TicketTools, type FileTextData, type ReportData, type Ticket } from '@cdd/harness/kanban/ticket'

import type { CddConnectionNode } from '../../cdd/cdd-connection-node'

const TicketAddress = z.object({ ticket: z.string().min(1) })
const Leaving = z.object({ leaving: z.array(z.string()).optional() })
const Activation = Leaving.extend({ opening: z.array(z.string()).optional() })
const PracticeChoice = z.object({ practice: z.string().min(1), is_enabled: z.boolean() })
const Fidelities = z.object({ fidelities: z.array(z.string()) })
const GenerateChoice = Fidelities.extend({ formats: z.array(z.string()) })
const FileAddress = z.object({ path: z.string().min(1) })
const ReportAddress = z.object({ fidelity: z.string().min(1) })

export class TicketNode extends TicketTools {
  static fromRequest(cdd: CddConnectionNode, req: Request): TicketNode {
    return new TicketNode(cdd, TicketAddress.parse(req.params).ticket)
  }

  closeRequested(req: Request): Promise<Ticket> {
    return this.close(Leaving.parse(req.body).leaving)
  }

  activateRequested(req: Request): Promise<Ticket> {
    const { leaving, opening } = Activation.parse(req.body)
    return this.activate(leaving, opening)
  }

  enablePracticeRequested(req: Request): Promise<Ticket> {
    const { practice, is_enabled: isEnabled } = PracticeChoice.parse(req.body)
    return this.enablePractice(practice, isEnabled)
  }

  generateCommandsRequested(req: Request): Promise<string[]> {
    const { fidelities, formats } = GenerateChoice.parse(req.body)
    return this.generateCommands(fidelities, formats)
  }

  filesRequested(req: Request): ReturnType<TicketTools['files']> {
    return this.files(Fidelities.parse(req.body).fidelities)
  }

  readFileRequested(req: Request): Promise<FileTextData> {
    return this.readFile(FileAddress.parse(req.query).path)
  }

  reportRequested(req: Request): Promise<ReportData> {
    return this.report(ReportAddress.parse(req.query).fidelity)
  }
}
