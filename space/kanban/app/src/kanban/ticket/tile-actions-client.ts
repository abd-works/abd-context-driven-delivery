import type { FormatChoiceData } from '@cdd/space/kanban/ticket'

import { ACTION_STANDINGS, countOf, STEP_FAILED } from '../board/board-brand'
import type { BoardPage } from '../board/board-page'
import type { Tile } from '../board/board-store'
import type { FidelityProgressClient } from './fidelity-progress-client'
import type { TicketClient, WorkStanding } from './ticket-client'
import { headPlace } from './tile-client'
import { chosenFormats } from './tile-formats'

export type ChipFace = FormatChoiceData & { hint: string; isOn: boolean; isDone: boolean; count: string }
export type StepFace = { mark: string; color: string; hint: string; text: string }
export type TileBar = {
  chips: ChipFace[]
  isLocked: boolean
  runOff: boolean
  validateOff: boolean
  reviewOff: boolean
  validate: StepFace
  review: StepFace
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
  const isOn = tile.picked.includes(choice.label)
  const standing = made === 0 ? 'not done' : made === offered ? 'done' : `${made} of ${offered} done`
  const count = made > 0 && made < offered ? `${made} of ${offered}` : ''
  return { ...choice, isOn, isDone: made > 0, count, hint: `${choice.label}: ${standing}${isOn ? ', selected' : ''}` }
}

const stepFaceOf = (standing: string, name: string): StepFace => {
  const { mark, color, label } = ACTION_STANDINGS[standing]!
  return { mark, color, hint: `${name}: ${label}`, text: '' }
}

function validateFaceOf(work: WorkStanding): StepFace {
  if (!work.hasViolations) return stepFaceOf(work.actions.validate, 'Validate')
  const text = work.violationCount ? countOf(work.violationCount, 'violation') : 'violations'
  return { mark: STEP_FAILED, color: 'var(--violations)', hint: text, text }
}

// What an open action bar offers, and what its controls send to the chat.
export class TileActionsClient {
  constructor(private readonly page: BoardPage) {}

  private get chat(): BoardPage['chat'] {
    return this.page.chat
  }

  private save(tile: Tile, change: Partial<Tile>): void {
    this.page.tiles.change(tile.ticket.name, tile.place, open => ({ ...open, ...change, isPinned: true }))
  }

  chooseAction(tile: Tile, action: string): void {
    this.save(tile, { action })
  }

  toggleFormat(tile: Tile, chip: string): void {
    this.save(tile, { picked: tile.picked.includes(chip) ? tile.picked.filter(entry => entry !== chip) : [...tile.picked, chip] })
  }

  // A stage head's bar acts on the ticket's work in that stage, which Python answers taken together; a tile's bar acts
  // on its one fidelity.
  private workOf(ticket: TicketClient, tile: Tile): WorkStanding | undefined {
    if (tile.place === headPlace(tile.stage.name)) return ticket.workIn(tile.stage)
    return ticket.progressOn(tile.fidelities)[0]
  }

  // Python says which actions have something to work on; Render waits for output to convert.
  private allows(ticket: TicketClient, work: WorkStanding | undefined, action: string): boolean {
    return !ticket.isLocked && Boolean(work?.allowedActions.includes(action))
  }

  private canRun(ticket: TicketClient, tile: Tile, work: WorkStanding | undefined): boolean {
    if (!this.chat.canSend || !tile.fidelities.length) return false
    if (!chosenFormats(tile.choices, tile.picked).length) return false
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
      // Validate runs in the chat; a review is the person's own approval, so it needs no chat.
      validateOff: !this.chat.canSend || !this.allows(ticket, work, 'validate'),
      reviewOff: !this.allows(ticket, work, 'review'),
      validate,
      review: stepFaceOf(work?.actions.review ?? 'to_do', 'Review'),
      report: reportOf(ticket.progressOn(tile.fidelities)),
      hasViolations: validate.text !== '',
    }
  }

  // Python gives one command naming every fidelity the bar acts on, and the ticket's session, so a stage's work stays a
  // single turn. The chips add the formats a person picked to an action that takes them.
  async run(tile: Tile): Promise<void> {
    const command = this.commandOf(tile, tile.action)
    // The stage says which of its actions take the formats chosen; every other one writes or reads files without one.
    if (!tile.stage.actionsWithFormats.includes(tile.action)) return this.sendFor(tile, command)
    const formats = chosenFormats(tile.choices, tile.picked)
    this.save(tile, { picked: [] })
    await this.sendFor(tile, `${command} format=${formats.join(',')}`)
  }

  validate(tile: Tile): Promise<void> {
    return this.sendFor(tile, this.commandOf(tile, 'validate'))
  }

  private commandOf(tile: Tile, action: string): string {
    return this.workOf(tile.ticket, tile)?.commands[action] ?? ''
  }

  // The command goes to the tile's ticket's own chat.
  private sendFor(tile: Tile, command: string): Promise<void> {
    return tile.ticket.chat.command(command)
  }

  // The ticket writes the review to its session log, and the board read after it shows the fidelity done.
  async review(tile: Tile): Promise<void> {
    await Promise.all(tile.ticket.progressOn(tile.fidelities).map(progress => progress.finishReview()))
    await this.page.reader.refresh()
  }
}
