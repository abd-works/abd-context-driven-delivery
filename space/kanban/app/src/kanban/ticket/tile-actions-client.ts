import type { FidelityProgressData } from '@cdd/space/kanban/fidelity-progress'
import type { FormatChoiceData, StageWorkData } from '@cdd/space/kanban/ticket'

import { ACTION_STANDINGS, countOf, STEP_FAILED } from '../shared/board-brand'
import type { BoardPage } from '../board/board-page'
import type { Tile } from '../shared/board-store'
import type { FidelityProgressClient } from './fidelity-progress-client'
import type { TicketClient } from './ticket-client'
import { headPlace, slugsOf } from './tile-client'
import { chosenFormats } from './tile-formats'

// The work an action bar acts on, as Python sends it: a stage's work taken together (StageWork) on a stage head, one
// fidelity's progress (FidelityProgress) on a tile. Both answer the same fields.
type BarWork = StageWorkData | FidelityProgressData

export type ChipFace = FormatChoiceData & { hint: string; isOn: boolean; isDone: boolean; count: string }
export type StepFace = { mark: string; color: string; hint: string; text: string }
export type TileBar = {
  chips: ChipFace[]
  isLocked: boolean
  runOff: boolean
  validateOff: boolean
  validate: StepFace
  report: FidelityProgressClient | undefined
  hasViolations: boolean
}

// A tile can hold several fidelities: its link opens the report of the one left with violations, else the first report.
function reportOf(progress: FidelityProgressClient[]): FidelityProgressClient | undefined {
  const reported = progress.filter(entry => entry.reportFile)
  return reported.find(entry => entry.state === 'violations') ?? reported[0]
}

function chipFaceOf(tile: Tile, choice: FormatChoiceData): ChipFace {
  const { made, offered } = choice
  const isOn = choice.is_chosen
  const standing = made === 0 ? 'not done' : made === offered ? 'done' : `${made} of ${offered} done`
  const count = made > 0 && made < offered ? `${made} of ${offered}` : ''
  return { ...choice, isOn, isDone: made > 0, count, hint: `${choice.label}: ${standing}${isOn ? ', selected' : ''}` }
}

const stepFaceOf = (standing: string, name: string): StepFace => {
  const { mark, color, label } = ACTION_STANDINGS[standing]!
  return { mark, color, hint: `${name}: ${label}`, text: '' }
}

function validateFaceOf(work: BarWork): StepFace {
  if (!work.has_violations) return stepFaceOf(work.actions.validate, 'Validate')
  const text = work.violation_count ? countOf(work.violation_count, 'violation') : 'violations'
  return { mark: STEP_FAILED, color: 'var(--violations)', hint: text, text }
}

// What an open action bar offers, and what its controls send to the chat.
export class TileActionsClient {
  constructor(private readonly page: BoardPage) {}

  private get chat(): BoardPage['chat'] {
    return this.page.chat
  }

  private save(tile: Tile, change: Partial<Tile>): void {
    this.page.tiles.change(tile.ticket, tile.place, open => ({ ...open, ...change, isPinned: true }))
  }

  chooseAction(tile: Tile, action: string): void {
    this.save(tile, { action })
  }

  // A press chooses the chip's formats in the ticket's session, or leaves them out, and the bar shows the chips Python
  // answers once the board is read again: the commands the bar runs name the formats chosen, so a chip shows pressed only
  // when a Run pressed then sends its formats.
  async toggleFormat(tile: Tile, chip: string): Promise<void> {
    const choice = tile.choices.find(each => each.label === chip)
    if (!choice) return
    const choices = await tile.ticket.chooseFormats(slugsOf(tile.fidelities), chip, !choice.is_chosen)
    if (!choices) return
    await this.page.reader.refresh()
    this.save(tile, { choices })
  }

  // A stage head's bar acts on the ticket's work in that stage, which Python answers taken together; a tile's bar acts
  // on its one fidelity.
  private workOf(ticket: TicketClient, tile: Tile): BarWork | undefined {
    if (tile.place === headPlace(tile.stage.name)) return ticket.work.workIn(tile.stage)
    return ticket.work.progressOn(tile.fidelities)[0]?.toJSON()
  }

  // Python says which actions have something to work on; Render waits for output to convert.
  private allows(ticket: TicketClient, work: BarWork | undefined, action: string): boolean {
    return !ticket.isLocked && Boolean(work?.allowed_actions.includes(action))
  }

  private canRun(ticket: TicketClient, tile: Tile, work: BarWork | undefined): boolean {
    if (!this.chat.canSend || !tile.fidelities.length) return false
    if (!chosenFormats(tile.choices).length) return false
    return this.allows(ticket, work, tile.action)
  }

  // ticket is the tile's ticket as the board shows it now, which holds the fidelities' latest progress.
  barOf(ticket: TicketClient, tile: Tile): TileBar {
    const work = this.workOf(ticket, tile)
    const validate = work ? validateFaceOf(work) : stepFaceOf('to_do', 'Validate')
    return {
      chips: tile.choices.map(choice => chipFaceOf(tile, choice)),
      isLocked: ticket.isLocked,
      runOff: !this.canRun(ticket, tile, work),
      // Validate runs in the chat.
      validateOff: !this.chat.canSend || !this.allows(ticket, work, 'validate'),
      validate,
      report: reportOf(ticket.work.progressOn(tile.fidelities)),
      hasViolations: validate.text !== '',
    }
  }

  // Python gives one command naming every fidelity the bar acts on, the ticket's session, and, for an action that takes
  // them, the formats the chips chose in the session, so a stage's work stays a single turn.
  async run(tile: Tile): Promise<void> {
    await this.sendFor(tile, this.commandOf(tile, tile.action))
  }

  validate(tile: Tile): Promise<void> {
    return this.sendFor(tile, this.commandOf(tile, 'validate'))
  }

  // The command as the board shows it now: a chip pressed since the tile opened read the board again, and the command
  // names the formats the press chose.
  private commandOf(tile: Tile, action: string): string {
    const shown = this.page.board.tickets.find(ticket => ticket.address === tile.ticket.address) ?? tile.ticket
    return this.workOf(shown, tile)?.commands[action] ?? ''
  }

  // The command goes to the tile's ticket's own chat.
  private sendFor(tile: Tile, command: string): Promise<void> {
    return tile.ticket.chat.command(command)
  }
}
